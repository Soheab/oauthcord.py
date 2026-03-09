from typing import TYPE_CHECKING

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import guild as guild_types
    from .base import ValidToken


class GuildHTTPClientMixin(BaseHTTPClient):
    async def get_current_user_guilds(
        self,
        token: ValidToken,
        *,
        limit: int | None = None,
        with_counts: bool = False,
    ) -> guild_types.CurrentUserGuildsResponse:
        data: guild_types.CurrentUserGuildsRequest = {}
        if limit is not None:
            data["limit"] = limit
        if with_counts:
            data["with_counts"] = with_counts
        return await self.request(
            Route("GET", "/users/@me/guilds"),
            token=token,
            params=data,
        )
