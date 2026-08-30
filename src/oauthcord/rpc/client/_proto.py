from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from ...client._client import AuthorisedSession, Client
    from ...internals._types.rpc.payloads import RPCCommandResponse
    from ...internals.state import State
    from ..enums import SendableRPCCommand


class _RPCClientProto(Protocol):  # pyright: ignore[reportUnusedClass]
    client: Client

    @property
    def _model_state(self) -> State: ...

    async def _send_command(
        self,
        command: SendableRPCCommand | str,
        /,
        args: Any | None = None,
        *,
        evt: str | None = None,
    ) -> RPCCommandResponse: ...

    async def send_command(
        self,
        command: SendableRPCCommand | str,
        /,
        **args: Any,
    ) -> RPCCommandResponse: ...

    def _ensure_session(self) -> AuthorisedSession: ...
