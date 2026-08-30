from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import current_auth_info as current_auth_types
    from .base import ValidAccessToken


class CurrentAuthHTTPClientMixin(BaseHTTPClient):
    async def get_current_authorization_information(
        self,
        token: ValidAccessToken,
    ) -> current_auth_types.CurrentAuthResponse:
        return await self.request(
            Route("GET", "/oauth2/@me"),
            token=token,
        )
