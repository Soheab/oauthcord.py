"""Errors raised by the RPC (local IPC) client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..errors import OauthCordException
from .enums import RPCErrorCode

if TYPE_CHECKING:
    from ..internals._types.rpc.events import ErrorEventData

__all__ = (
    "RPCClientClosedError",
    "RPCConnectionError",
    "RPCConnectionLostError",
    "RPCError",
    "RPCHandshakeError",
    "RPCHandshakeTimeoutError",
    "RPCSessionRequiredError",
    "RPCSocketNotFoundError",
    "RPCSubscriptionError",
)


class RPCConnectionError(OauthCordException):
    """Base class for errors relating to the local Discord IPC connection."""


class RPCSessionRequiredError(OauthCordException):
    """Raised when an RPC result requires an authorized OAuth2 session."""

    def __init__(self) -> None:
        super().__init__(
            "This RPC method requires an AuthorisedSession to construct its result. "
            "Call `await RPCClient.login(...)`, or pass an AuthorisedSession to "
            "`await RPCClient.authenticate(session)`, before calling this method. "
            "Authenticating with a bare access-token string is insufficient."
        )


class RPCSocketNotFoundError(RPCConnectionError):
    """Raised when no local Discord IPC socket/pipe could be found.

    This almost always means the Discord desktop client isn't running on this
    machine, or (rarely) that it's running under a sandbox/container that hides its
    IPC socket from this process.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message
            or (
                "Could not find a local Discord IPC socket. Make sure the Discord "
                "desktop client (not the browser) is running and you are logged in."
            )
        )


class RPCHandshakeError(RPCConnectionError):
    """Raised when Discord rejects the initial RPC handshake.

    Usually means ``client_id`` doesn't match a real application, or Discord's RPC
    server refused the connection for another reason it reported directly.
    """

    def __init__(self, message: str, code: int | None = None) -> None:
        self.code = code
        hint = (
            " Double-check that the client_id passed to Client matches an "
            "application at https://discord.com/developers/applications."
        )
        super().__init__(f"{message}. {hint}")


class RPCHandshakeTimeoutError(RPCConnectionError):
    """Raised when Discord never answers the initial RPC handshake.

    Discord serves one IPC connection per application at a time and silently
    ignores a second handshake for the same ``client_id``, so this usually means
    another connection for this application is already open on that pipe. It
    also delays handshakes for a while after an application reconnects rapidly.
    """

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        super().__init__(
            f"Discord did not answer the RPC handshake within {timeout:g}s. Another "
            "connection for this application may already be open; close it first, "
            "or wait a little if this application just reconnected."
        )


class RPCClientClosedError(RPCConnectionError):
    """Raised when a command is sent on an :class:`RPCClient` that isn't connected.

    This means :meth:`RPCClient.connect` was never called, or the client was already
    closed (e.g. via :meth:`RPCClient.close`, ``async with`` exit, or a prior dropped
    connection) before this command was sent.
    """

    def __init__(self) -> None:
        super().__init__(
            "Not connected to Discord. Call `await RPCClient.connect()` (or use "
            "`async with RPCClient(...)`) before sending commands, and avoid reusing "
            "a client after it has been closed."
        )


class RPCConnectionLostError(RPCConnectionError):
    """Raised when a live connection to Discord drops unexpectedly.

    This means the IPC socket was open and working, but Discord closed it (e.g. the
    Discord desktop client was closed/restarted, crashed, or the OS tore down the
    pipe/socket) while a command was in flight or being sent.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message
            or (
                "Connection to Discord closed unexpectedly. This usually means the "
                "Discord desktop client was closed or restarted — reconnect with a "
                "new RPCClient before sending further commands."
            )
        )


class RPCError(OauthCordException):
    """Raised when the Discord RPC server returns an error response.

    Attributes
    ----------
    code: :class:`int`
        The raw error code.
    error_code: :class:`RPCErrorCode` | :class:`int`
        The error code as an :class:`RPCErrorCode`, or the raw code if unknown.
    message: :class:`str`
        Discord's error message.
    command: :class:`str` | :data:`None`
        The command that failed, e.g. ``"AUTHORIZE"``, if Discord reported it.
    data: :class:`dict` | :data:`None`
        The full error payload, including any fields beyond ``code`` and
        ``message`` that Discord sent.
    """

    def __init__(
        self,
        code: int,
        message: str,
        *,
        command: str | None = None,
        data: ErrorEventData | None = None,
    ) -> None:
        self.code = code
        try:
            self.error_code: RPCErrorCode | int = RPCErrorCode(code)
        except ValueError:
            self.error_code = code
        self.message = message
        self.command = command
        self.data = data

        source = f" from {command}" if command else ""
        super().__init__(f"RPC error {code}{source}: {message}")


class RPCUnauthorizedError(RPCError):
    """Raised when a command is sent on an :class:`RPCClient` that isn't authorized.

    This means :meth:`RPCClient.login` or :meth:`RPCClient.authenticate` was never
    called, or the client was already closed (e.g. via :meth:`RPCClient.close`,
    ``async with`` exit, or a prior dropped connection) before this command was sent.
    """

    def __init__(self) -> None:
        super().__init__(
            code=4006,
            message=(
                "Not authorized to send this RPC command. Call `await RPCClient.login(...)` "
                "or `await RPCClient.authenticate(session)` before sending commands that "
                "require authorization."
            ),
        )


class RPCSubscriptionError(RPCError):
    """Raised when Discord refuses to subscribe to an event.

    Almost always because the connection is not authenticated yet: most RPC
    events require :meth:`RPCClient.login` (or :meth:`RPCClient.authenticate`)
    to have run first. If it is raised *after* authenticating, the granted
    scopes do not cover that event.

    Because handler subscriptions are sent while connecting, this surfaces from
    :meth:`RPCClient.connect` / ``async with``. Either authenticate before
    subscribing, or pass ``auto_subscribe=False`` to :class:`RPCClient` and
    subscribe yourself after :meth:`RPCClient.login`.
    """

    def __init__(self, event_name: str, authenticated: bool = False) -> None:
        self.event_name: str = event_name
        self.authenticated: bool = authenticated

        if authenticated:
            reason = (
                "the authorised scopes do not cover it. Request the scope that "
                "event requires when calling `login()`"
            )
        else:
            reason = (
                "it requires an authenticated connection. Call "
                "`await RPCClient.login(...)` before subscribing, or pass "
                "`auto_subscribe=False` to RPCClient and subscribe after logging in"
            )

        super().__init__(
            code=4006,
            message=f"Cannot subscribe to {event_name}: {reason}.",
        )
