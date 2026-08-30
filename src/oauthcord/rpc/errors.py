"""Errors raised by the RPC (local IPC) client."""

from __future__ import annotations

from ..errors import OauthCordException
from .enums import RPCErrorCode

__all__ = (
    "RPCClientClosedError",
    "RPCConnectionError",
    "RPCConnectionLostError",
    "RPCError",
    "RPCHandshakeError",
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
    """Raised when the Discord RPC server returns an error response."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        try:
            self.error_code: RPCErrorCode | int = RPCErrorCode(code)
        except ValueError:
            self.error_code = code
        self.message = message

        super().__init__(f"RPC error {code}: {message}")


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
