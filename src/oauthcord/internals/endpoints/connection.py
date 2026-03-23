from typing import TYPE_CHECKING

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import connections as connection_types
    from .base import ValidToken


class ConnectionHTTPClientMixin(BaseHTTPClient):
    async def get_current_user_connections(
        self,
        token: ValidToken,
    ) -> list[connection_types.ConnectionResponse]:
        return await self.request(
            Route("GET", "/users/@me/connections"),
            token=token,
        )

    # connections scope
    async def get_user_linked_connections(
        self,
        token: ValidToken,
    ) -> list[connection_types.ConnectionResponse]:
        return await self.request(
            Route("GET", "/users/@me/linked-connections"),
            token=token,
        )
