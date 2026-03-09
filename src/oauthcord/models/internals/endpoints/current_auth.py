from typing import TYPE_CHECKING

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import current_auth_info as current_auth_types
    from .base import ValidToken


class CurrentAuthHTTPClientMixin(BaseHTTPClient):
    async def get_current_authorization_information(
        self,
        token: ValidToken,
    ) -> current_auth_types.CurrentAuthResponse:
        return await self.request(
            Route("GET", "/oauth2/@me"),
            token=token,
        )
