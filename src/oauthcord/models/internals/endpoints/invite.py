from typing import TYPE_CHECKING

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import invite as invite_types
    from .base import ValidToken


class InviteHTTPClientMixin(BaseHTTPClient):
    async def accept_invite(
        self,
        token: ValidToken,
        *,
        code: str,
        session_id: str | None = None,
    ) -> invite_types.InviteResponse:
        data: invite_types.AcceptInviteRequest = {}
        if session_id is not None:
            data["session_id"] = session_id

        return await self.request(
            Route("POST", f"/invites/{code}"),
            token=token,
            json=data,
        )
