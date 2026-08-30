"""Discord RPC client.

Implements the local IPC protocol Discord's desktop client exposes, documented at
https://docs.discord.food/topics/rpc (community mirror of the removed official docs).

This connects to a Unix domain socket (Linux/macOS) or a named pipe (Windows) that the
Discord desktop application creates locally — it has nothing to do with the OAuth2 REST
API used by the rest of this library, and requires the Discord desktop client to be
running on the same machine.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import struct
import sys
import uuid
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self

from ... import utils
from ...client._client import AuthorisedSession
from ...enums import Scope
from ...internals.state import State
from ...models.access_token import AccessToken
from ...utils import _get_access_token
from ..enums import InternalRPCCommand, SendableRPCCommand
from ..errors import (
    RPCClientClosedError,
    RPCConnectionError,
    RPCConnectionLostError,
    RPCError,
    RPCHandshakeError,
    RPCSessionRequiredError,
    RPCSocketNotFoundError,
    RPCUnauthorizedError,
)
from ..events import RPCEventsManager
from ..handler import EventsHandler
from ..models.auth import RPCAuthentication
from ._commands import _RPCCommandsClient

if TYPE_CHECKING:
    from collections.abc import Sequence
    from types import TracebackType

    from ...client._client import AuthorisedSession, Client
    from ...enums import UnknownEnum
    from ...internals._types.rpc import (
        payloads as command_payloads,
    )

_log = logging.getLogger("rpc")

__all__ = (
    "RPCClient",
    "RPCClientClosedError",
    "RPCConnectionError",
    "RPCConnectionLostError",
    "RPCError",
    "RPCHandshakeError",
    "RPCSessionRequiredError",
    "RPCSocketNotFoundError",
)


class _RPCOpCode:
    """IPC frame opcodes used by the Discord RPC protocol."""

    HANDSHAKE = 0
    FRAME = 1
    CLOSE = 2
    PING = 3
    PONG = 4


class _ConnectionManager:
    __slots__ = ("_closed", "_connected", "_os", "_reader", "_writer")

    def __init__(
        self,
    ) -> None:
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

        self._closed: bool = False

    @property
    def connected(self) -> bool:
        """:class:`bool`: Whether the connection is currently open."""
        return (
            not self._closed and self._reader is not None and self._writer is not None
        )

    @property
    def closed(self) -> bool:
        """:class:`bool`: Whether the connection has been closed."""
        return self._closed

    @property
    def reader(self) -> asyncio.StreamReader:
        """The connected stream reader.

        Raises
        ------
        RPCConnectionError
            The client is not currently connected to a Discord IPC socket.
        """
        if self._reader is None:
            raise RPCConnectionError("Not connected to a Discord IPC socket")
        return self._reader

    @property
    def writer(self) -> asyncio.StreamWriter:
        """The connected stream writer.

        Raises
        ------
        RPCConnectionError
            The client is not currently connected to a Discord IPC socket.
        """
        if self._writer is None:
            raise RPCConnectionError("Not connected to a Discord IPC socket")
        return self._writer

    def _get_ipc_paths(self) -> list[str]:
        if sys.platform == "win32":
            return [r"\\?\pipe\discord-ipc-"]

        base = (
            os.environ.get("XDG_RUNTIME_DIR")
            or os.environ.get("TMPDIR")
            or os.environ.get("TMP")
            or os.environ.get("TEMP")
            or "/tmp"
        )
        # Some clients (Snap/Flatpak) nest the socket under one of these subdirectories.
        subdirs = ("", "app/com.discordapp.Discord", "snap.discord")
        paths: list[str] = []
        for subdir in subdirs:
            directory = os.path.join(base, subdir) if subdir else base
            paths.append(os.path.join(directory, "discord-ipc-"))
        return paths

    async def _connect_windows_pipe(
        self,
        path: str,
    ) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        transport, _ = await loop.create_pipe_connection(lambda: protocol, path)  # type: ignore[attr-defined]
        writer = asyncio.StreamWriter(transport, protocol, reader, loop)  # type: ignore[arg-type]
        return reader, writer

    async def connect(
        self, *, pipe: int | None = None
    ) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Connect to the local Discord client via IPC.

        Parameters
        ----------
        pipe: :class:`int` | :data:`None`
            Specific IPC pipe/socket index (``0``-``9``) to connect to. If :data:`None`,
            every index is tried in order.

        Raises
        ------
        RPCConnectionError
            No local Discord IPC socket could be found or connected to.
        """
        paths: list[str]
        if pipe is not None:
            paths = self._get_ipc_paths()
            paths = [p + str(pipe) for p in paths]
        else:
            paths = []
            paths.extend(p + str(i) for p in self._get_ipc_paths() for i in range(10))

        last_error: Exception | None = None
        for path in paths:
            try:
                if sys.platform == "win32":
                    reader, writer = await self._connect_windows_pipe(path)
                else:
                    reader, writer = await asyncio.open_unix_connection(path)
            except (OSError, NotImplementedError) as exc:
                last_error = exc
                continue
            else:
                _log.debug("Connected to Discord IPC socket at %s", path)
                self._reader = reader
                self._writer = writer
                return reader, writer

        raise RPCSocketNotFoundError() from last_error

    async def send(self, opcode: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode("utf-8")
        _log.debug("IPC send: opcode=%s payload=%s", opcode, payload)
        self.writer.write(struct.pack("<II", opcode, len(data)) + data)
        try:
            await self.writer.drain()
        except (ConnectionResetError, OSError) as exc:
            _log.debug("IPC send failed, connection lost: %s", exc)
            raise RPCConnectionLostError() from exc

    async def recv(self) -> tuple[int, dict[str, Any]]:
        header = await self.reader.readexactly(8)
        opcode, length = struct.unpack("<II", header)
        data = await self.reader.readexactly(length)
        payload = json.loads(data.decode("utf-8"))
        _log.debug("IPC recv: opcode=%s payload=%s", opcode, payload)
        return opcode, payload

    async def close(self) -> None:
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except OSError:
            pass
        finally:
            self._reader = None
            self._writer = None
            self._closed = True


# Discord's error code for a command needing an authenticated connection.
_RPC_UNAUTHORIZED_CODE = 4006


class RPCClient(_RPCCommandsClient):
    """Client for Discord's local RPC (IPC) protocol.

    This connects directly to the Discord desktop client running on the same machine —
    it is unrelated to the OAuth2 REST :class:`~oauthcord.client.Client`. Most commands
    require the connection to first be authenticated with an OAuth2 access token bearing
    the relevant ``rpc.*`` scopes (see :class:`~oauthcord.enums.Scope`).

    Parameters
    ----------
    client: :class:`~oauthcord.client.Client`
        OAuth2 client to identify as during the handshake and to exchange authorization
        codes with in :meth:`login`. Its ``client_id`` is used for the RPC handshake.
    pipe: :class:`int` | :data:`None`
        Specific IPC pipe/socket index (``0``-``9``) to connect to. If :data:`None`,
        every index is tried in order.
    clear_activity_on_close: :class:`bool`
        Whether to clear the local user's rich presence activity when this connection is
        closed. Defaults to :data:`False`.
    reconnect: :class:`bool`
        Whether to automatically try to re-establish the connection (redoing the
        handshake, and re-authenticating if this client was previously authenticated)
        when it's unexpectedly lost — e.g. because the Discord desktop client was
        restarted. Only connection-loss is retried; a socket that can't be found at all
        or a rejected handshake are not, since retrying those won't help on their own.
        Defaults to :data:`False`.
    max_reconnect_attempts: :class:`int`
        Maximum number of reconnect attempts before giving up and raising the original
        error. Only used if ``reconnect`` is :data:`True`. Defaults to ``5``.
    reconnect_backoff: :class:`float`
        Base delay in seconds between reconnect attempts, doubled after each failed
        attempt (``1s, 2s, 4s, ...``). Only used if ``reconnect`` is :data:`True`.
        Defaults to ``1.0``.
    handler: :class:`~oauthcord.rpc.EventsHandler` | :class:`type` | :data:`None`
        A subclass of :class:`~oauthcord.rpc.EventsHandler` whose overridden ``on_*``
        methods are called when the matching event arrives. Either the class itself
        (constructed with this client) or an already-built instance may be passed.
        Only methods the subclass actually overrides are registered; the inherited
        no-op stubs are ignored. Defaults to :data:`None`, meaning no handler.
    auto_subscribe: :class:`bool`
        Whether to automatically send ``SUBSCRIBE`` on connect for the events the
        ``handler`` overrides. Events Discord sends unprompted (``READY``, ``ERROR``,
        ``AUTHORIZE_REQUEST``) are never subscribed to, and events whose subscription
        requires a ``guild_id`` or ``channel_id`` are skipped — subscribe to those
        explicitly with :meth:`RPCEventsManager.subscribe`. Their handler methods are
        still registered either way. Only used if ``handler`` is given. Defaults to
        :data:`True`.
    login_timeout: :class:`float`
        How long to wait, in seconds, for :meth:`login` before reporting handler
        subscriptions that Discord refused because the connection is not
        authenticated. Those subscriptions are queued and flushed automatically
        once login happens; if it never does, the handlers would silently never
        fire, so this reports them instead. Set to ``0`` to disable the check.
        Defaults to ``30.0``.
    keep_alive: :class:`bool`
        Whether leaving an ``async with`` block should wait for the connection to
        close instead of closing it immediately. Use this to keep a session running
        until Discord goes away or the user interrupts, without writing your own
        wait loop; see :meth:`wait_until_closed`. Defaults to :data:`False`.

    Attributes
    ----------
    client: :class:`~oauthcord.client.Client`
        The OAuth2 client passed to the constructor.
    user: :class:`dict` | :data:`None`
        The connected user's data, populated after a successful handshake.

    Examples
    --------
    Handling events by subclassing :class:`~oauthcord.rpc.EventsHandler`::

        from oauthcord.rpc import EventsHandler, RPCClient

        class MyHandler(EventsHandler):
            async def on_ready(self, event) -> None:
                print("connected as", event.data.user)

            async def on_activity_join(self, event) -> None:
                print("joining with secret", event.data.secret)

        rpc = RPCClient(client, handler=MyHandler)
        async with rpc:
            await rpc.login(...)
    """

    RPC_VERSION: ClassVar[int] = 1

    __slots__ = (
        "_authorized",
        "_clear_activity_on_close",
        "_closed",
        "_closing",
        "_connection",
        "_events_manager",
        "_handler",
        "_keep_alive",
        "_listener_task",
        "_login_timeout",
        "_max_reconnect_attempts",
        "_pending",
        "_pipe",
        "_reconnect_backoff",
        "_reconnect_enabled",
        "_state",
        "_subscriptions",
        "client",
        "user",
    )

    def __init__(
        self,
        client: Client,
        *,
        pipe: int | None = None,
        clear_activity_on_close: bool = False,
        reconnect: bool = False,
        max_reconnect_attempts: int = 5,
        reconnect_backoff: float = 1.0,
        handler: EventsHandler | type[EventsHandler] | None = None,
        auto_subscribe: bool = True,
        keep_alive: bool = False,
        login_timeout: float = 30.0,
    ) -> None:
        self.client: Client = client
        self._pipe = pipe
        self._clear_activity_on_close = clear_activity_on_close
        self._reconnect_enabled = reconnect
        self._max_reconnect_attempts = max_reconnect_attempts
        self._reconnect_backoff = reconnect_backoff
        self._keep_alive = keep_alive
        self._login_timeout = login_timeout

        self._connection: _ConnectionManager = _ConnectionManager()
        self._pending: dict[str, asyncio.Future[Any]] = {}
        self._listener_task: asyncio.Task[None] | None = None

        self._closed = True
        self._closing = False
        self._authorized = False
        self._events_manager = RPCEventsManager(self)

        self._handler: EventsHandler | None = None
        if handler is not None:
            # Accept either an instance or the class itself.
            self._handler = handler(self) if isinstance(handler, type) else handler
            registered = self._events_manager.register_handler(self._handler)
            if not auto_subscribe:
                self._events_manager._pending_subscriptions.clear()
            _log.debug(
                "Registered handler %s for events: %s",
                type(self._handler).__name__,
                ", ".join(registered) or "(none overridden)",
            )

        self.user: dict[str, Any] | None = None

        # Our own state: models built from this connection bind to it, and it
        # gains the session once this connection authenticates.
        self._state: State = State(client.http)

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        # With keep_alive, leaving the block does not end the session: hold it
        # open until the connection drops or the user interrupts. Skipped when
        # the block is unwinding because of an error.
        if self._keep_alive and exc_type is None:
            await self.wait_until_closed()
        await self.close()

    async def wait_until_closed(self) -> None:
        """Block until this connection closes.

        Returns once the connection to Discord ends — because :meth:`close` was
        called, the desktop client went away, or the task was cancelled (a
        ``KeyboardInterrupt``/Ctrl+C). Events keep being delivered to handlers
        while this waits, so it is the usual way to keep a session running::

            async with RPCClient(client, handler=MyHandler) as rpc:
                await rpc.login(scopes=[...])
                await rpc.wait_until_closed()

        Passing ``keep_alive=True`` to :class:`RPCClient` does this for you when
        the ``async with`` block ends.
        """
        if self.closed:
            return

        task = self._listener_task
        if task is None:
            return

        try:
            # The listener runs for the lifetime of the connection, so awaiting
            # it is exactly "wait until this session ends".
            await asyncio.shield(task)
        except asyncio.CancelledError:
            # Ctrl+C, or someone cancelled us: fall through and let the caller
            # (or __aexit__) close the connection.
            pass

    @property
    def http(self):
        """:class:`~oauthcord.client.Client`: The OAuth2 client used for this RPC connection."""
        return self.client.http

    @property
    def _model_state(self) -> State:
        """:class:`State`: The state models created from this connection are bound to.

        Carries the authorised session once this connection has authenticated.
        """
        return self._state

    @property
    def session(self) -> AuthorisedSession | None:
        """:class:`~oauthcord.client.AuthorisedSession` | :data:`None`: The session used
        for this RPC connection, if authenticated.
        """
        return self._state._session

    @property
    def closed(self) -> bool:
        """:class:`bool`: Whether the connection has been closed."""
        return self._closed or bool(self._connection and self._connection.closed)

    @property
    def events(self) -> RPCEventsManager:
        """:class:`RPCEventsManager`: Event subscription manager for this connection."""
        return self._events_manager

    @property
    def handler(self) -> EventsHandler | None:
        """:class:`~oauthcord.rpc.EventsHandler` | :data:`None`: The events handler \
        this client was constructed with, or :data:`None` if none was given.

        When a class was passed as ``handler``, this is the instance built from it.
        """
        return self._handler

    def _ensure_session(self) -> AuthorisedSession:
        if self._state._session is None:
            raise RPCSessionRequiredError

        return self._state._session

    async def connect(self, *, pipe: int | None = None) -> None:
        """Connect to the local Discord client and perform the RPC handshake.

        Parameters
        ----------
        pipe: :class:`int` | :data:`None`
            Specific IPC pipe/socket index (``0``-``9``) to connect to. If :data:`None`,
            every index is tried in order.

            This overrides the ``pipe`` constructor argument for this call only.

        Raises
        ------
        RPCConnectionError
            No local Discord IPC socket could be found or connected to.
        """
        _log.debug("Connecting to local Discord IPC (pipe=%s)...", pipe)
        await self._connection.connect(pipe=pipe if pipe is not None else self._pipe)
        await self._connection.send(
            _RPCOpCode.HANDSHAKE,
            {
                "v": self.RPC_VERSION,
                "client_id": str(self.client.http.client_id),
            },
        )

        opcode, payload = await self._connection.recv()
        if opcode == _RPCOpCode.CLOSE or payload.get("evt") == "ERROR":
            # Discord reports handshake failures (e.g. an invalid client_id) either as
            # a FRAME with evt=ERROR and a "data" wrapper, or by closing the pipe
            # immediately with a CLOSE frame whose payload *is* the error directly.
            data = payload if opcode == _RPCOpCode.CLOSE else payload.get("data", {})
            _log.debug("RPC handshake rejected: %s", data)
            await self._connection.close()
            raise RPCHandshakeError(
                data.get("message", "Handshake with Discord IPC failed"),
                code=data.get("code"),
            )

        self.user = payload.get("data", {}).get("user")
        self._closed = False
        self._listener_task = asyncio.ensure_future(self._listen())
        await self._events_manager.start()
        _log.debug("RPC handshake complete, connected as %r", self.user)

    async def _reconnect(self) -> None:
        """Re-establish the connection after it was unexpectedly lost.

        Redoes the handshake and, if this client was previously authenticated,
        re-authenticates with the same access token. Retries up to
        ``max_reconnect_attempts`` times with exponential backoff, per the
        ``reconnect``/``max_reconnect_attempts``/``reconnect_backoff`` constructor
        options.

        Raises
        ------
        RPCConnectionError
            The connection could not be re-established within the configured number
            of attempts; the last error raised while retrying.
        """
        delay = self._reconnect_backoff
        last_error: Exception | None = None
        for attempt in range(1, self._max_reconnect_attempts + 1):
            _log.debug(
                "Reconnect attempt %d/%d...", attempt, self._max_reconnect_attempts
            )
            try:
                await self.connect()
                credential = self._state._session
                if credential is not None:
                    await self.authenticate(credential)
            except RPCConnectionError as exc:
                last_error = exc
                _log.debug("Reconnect attempt %d failed: %s", attempt, exc)
                if attempt < self._max_reconnect_attempts:
                    await asyncio.sleep(delay)
                    delay *= 2
            else:
                _log.debug("Reconnected to Discord IPC")
                return

        assert last_error is not None
        raise last_error

    async def close(self) -> None:
        """Close the connection to the local Discord client."""
        if self._closed:
            _log.debug("close() called on an already-closed RPCClient, ignoring")
            return

        _log.debug("Closing RPC connection")
        self._closing = True
        self._closed = True
        if self._clear_activity_on_close:
            try:
                await self.set_activity(None)
            except Exception:
                msg = "Ignoring error while clearing activity on close:"
                _log.exception(msg, exc_info=True)

        if self._listener_task is not None:
            self._listener_task.cancel()
            self._listener_task = None

        for future in self._pending.values():
            if not future.done():
                future.cancel()
        self._pending.clear()

        if not self._connection.closed:
            await self._connection.close()

        self._events_manager.close()
        self._closing = False

    async def _listen(self) -> None:
        if self.closed:
            _log.debug("Listener started on a closed RPCClient, exiting")
            return

        connection_lost = False
        try:
            while True:
                opcode, payload = await self._connection.recv()
                if opcode == _RPCOpCode.CLOSE:
                    _log.debug("Discord IPC connection closed by peer")
                    connection_lost = True
                    break
                if opcode == _RPCOpCode.PING:
                    await self._connection.send(_RPCOpCode.PONG, payload)
                    continue
                if opcode != _RPCOpCode.FRAME:
                    continue

                try:
                    await self._dispatch(payload)
                except Exception:
                    # A malformed payload or a failing parser must not take the
                    # listener down with it - that would strand every pending
                    # command with a misleading "connection lost" error.
                    _log.exception(
                        "Error while dispatching RPC payload, ignoring: %s", payload
                    )
        except (asyncio.IncompleteReadError, ConnectionResetError, OSError) as exc:
            _log.debug("RPC connection lost while listening: %s", exc)
            connection_lost = True
        finally:
            self._closed = True
            if self._pending:
                _log.debug(
                    "Failing %d pending RPC command(s) due to closed connection",
                    len(self._pending),
                )
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(RPCConnectionLostError())
            self._pending.clear()

        if connection_lost and self._reconnect_enabled and not self._closing:
            _log.debug(
                "Listener detected dropped connection, attempting to reconnect..."
            )
            try:
                await self._reconnect()
            except RPCConnectionError:
                _log.debug("Reconnect from listener failed, giving up")

    async def _dispatch(self, payload: dict[str, Any]) -> None:
        nonce = payload.get("nonce")
        if nonce is not None and nonce in self._pending:
            future = self._pending.pop(nonce)
            if future.done():
                return
            if payload.get("evt") == "ERROR":
                data = payload.get("data", {})
                _log.debug("RPC command error for nonce=%s: %s", nonce, data)
                code = data.get("code", 0)
                # A future can only be resolved once, so pick the exception
                # first and set it exactly once.
                if code == _RPC_UNAUTHORIZED_CODE:
                    future.set_exception(RPCUnauthorizedError())
                else:
                    future.set_exception(
                        RPCError(code, data.get("message", "Unknown error"))
                    )
            else:
                future.set_result(payload)
            return

        if payload.get("cmd") == "DISPATCH":
            event = payload.get("evt")
            if not event:
                return

            data = payload.get("data", {})
            guild_id = data.get("guild_id")
            channel_id = data.get("channel_id")
            await self.events.dispatch(
                event, data, guild_id=guild_id, channel_id=channel_id
            )

    async def _send_command(
        self,
        cmd: InternalRPCCommand | SendableRPCCommand | str,
        args: dict[str, Any] | None = None,
        *,
        evt: str | None = None,
    ) -> command_payloads.RPCCommandResponse:
        try:
            return await self._send_command_once(cmd, args, evt=evt)
        except RPCConnectionLostError:
            if not self._reconnect_enabled:
                raise
            _log.debug(
                "Connection lost while sending %r, attempting to reconnect...", cmd
            )
            await self._reconnect()
            return await self._send_command_once(cmd, args, evt=evt)

    async def _send_command_once(
        self,
        cmd: InternalRPCCommand | SendableRPCCommand | str,
        args: dict[str, Any] | None = None,
        *,
        evt: str | None = None,
    ) -> command_payloads.RPCCommandResponse:
        cmd = str(cmd)

        if self._connection.closed or self._closed:
            _log.debug("Refusing to send %r: client is not connected", cmd)
            raise RPCClientClosedError()

        nonce = str(uuid.uuid4())
        payload: dict[str, Any] = {"cmd": cmd, "args": args or {}, "nonce": nonce}
        if evt is not None:
            payload["evt"] = evt

        future: asyncio.Future[command_payloads.RPCIncomingPayload] = (
            asyncio.get_running_loop().create_future()
        )
        self._pending[nonce] = future
        _log.debug("Sending RPC command %r (nonce=%s)", cmd, nonce)
        try:
            await self._connection.send(_RPCOpCode.FRAME, payload)
        except BaseException:
            self._pending.pop(nonce, None)
            raise

        response = await future
        return response.get("data", {})

    # -- Authorization ----------------------------------------------------

    async def authorize(
        self,
        *,
        response_type: Literal["code"] = utils.NotSet,
        redirect_uri: str = utils.NotSet,
        scopes: list[str] = utils.NotSet,
        code_challenge: str = utils.NotSet,
        code_challenge_method: Literal["S256"] = utils.NotSet,
        state: str = utils.NotSet,
        nonce: str = utils.NotSet,
        permissions: str = utils.NotSet,
        guild_id: int | str = utils.NotSet,
        channel_id: int | str = utils.NotSet,
        prompt: str = utils.NotSet,
        disable_guild_select: bool = utils.NotSet,
        integration_type: int = utils.NotSet,
        pid: int = utils.NotSet,
    ) -> str:
        """Prompt the local user to authorize this application, returning an OAuth2 code.

        Exchange the returned code for an access token with
        :meth:`~oauthcord.client.Client.exchange_token`.

        Parameters
        ----------
        scopes: :class:`list`[:class:`str`]
            OAuth2 scopes to request authorization for.

        Returns
        -------
        :class:`str`
            An OAuth2 authorization code.
        """
        args: command_payloads.AuthorizeRequest = {
            "client_id": str(self.client.http.client_id)
        }
        if response_type is not utils.NotSet:
            args["response_type"] = response_type
        if redirect_uri is not utils.NotSet:
            args["redirect_uri"] = redirect_uri
        if scopes is not utils.NotSet:
            args["scopes"] = scopes
        if code_challenge is not utils.NotSet:
            args["code_challenge"] = code_challenge
        if code_challenge_method is not utils.NotSet:
            args["code_challenge_method"] = code_challenge_method
        if state is not utils.NotSet:
            args["state"] = state
        if nonce is not utils.NotSet:
            args["nonce"] = nonce
        if permissions is not utils.NotSet:
            args["permissions"] = permissions
        if guild_id is not utils.NotSet:
            args["guild_id"] = str(guild_id)
        if channel_id is not utils.NotSet:
            args["channel_id"] = str(channel_id)
        if prompt is not utils.NotSet:
            args["prompt"] = prompt
        if disable_guild_select is not utils.NotSet:
            args["disable_guild_select"] = disable_guild_select
        if integration_type is not utils.NotSet:
            args["integration_type"] = integration_type
        if pid is not utils.NotSet:
            args["pid"] = pid

        data: command_payloads.AuthorizeResponse = await self._send_command(
            InternalRPCCommand.AUTHORIZE,
            args,  # type: ignore
        )
        return data["code"]

    async def authenticate(
        self, access_token: str | AccessToken | AuthorisedSession
    ) -> RPCAuthentication:
        """Authenticate this connection using a previously obtained OAuth2 access token.

        Parameters
        ----------
        access_token: :class:`str` | :class:`~oauthcord.models.AccessToken` |
            :class:`~oauthcord.client.AuthorisedSession`
            OAuth2 access token to authenticate with.

        Returns
        -------
        :class:`~oauthcord.rpc.models.auth.RPCAuthentication`
            The authenticated user, granted scopes, application, and token details.
        """
        payload: command_payloads.AuthenticateRequest = {
            "access_token": _get_access_token(access_token),
        }
        data: command_payloads.AuthenticateResponse = await self._send_command(
            InternalRPCCommand.AUTHENTICATE,
            payload,  # pyright: ignore[reportArgumentType]
        )  # type: ignore

        authentication = RPCAuthentication(data=data)
        self.user = data.get("user", self.user)  # type: ignore
        self._authorized = True

        session = await AuthorisedSession.from_dict(self.client, authentication.token)
        self._state._session = session

        # Most events need an authenticated connection, so any handler
        # subscription Discord refused before now is retried here.
        await self._events_manager._subscribe_pending(authenticated=True)
        return authentication

    async def login(
        self,
        *,
        scopes: Sequence[Scope | UnknownEnum | str],
    ) -> AuthorisedSession:
        """Authorize, exchange, and authenticate this connection in one call.

        This runs :meth:`authorize` to get a code from the local Discord client, exchanges
        it for an access token with :attr:`client`, then calls :meth:`authenticate` with
        that token, leaving this connection authenticated for commands that require it
        (e.g. :meth:`get_guilds`).

        Parameters
        ----------
        scopes: :class:`Sequence`[:class:`Scope` | :class:`UnknownEnum` | :class:`str`]
            OAuth2 scopes to request authorization for.
        Returns
        -------
        :class:`~oauthcord.client.AuthorisedSession`
            The session created from the exchanged access token.
        """
        code = await self.authorize(
            scopes=[str(scope) for scope in Scope.from_list(scopes)]
        )
        session = await self.client.exchange_token(
            code,
        )
        await self.authenticate(session)
        return session
