from typing import TYPE_CHECKING

from ...flags import MemberFlags
from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import member as member_types
    from .base import ValidToken


class MemberHTTPClientMixin(BaseHTTPClient):
    async def get_current_guild_member(
        self,
        token: ValidToken,
        *,
        guild_id: str | int,
    ) -> member_types.GuildMemberResponse:
        return await self.request(
            Route("GET", f"/users/@me/guilds/{guild_id}/member"),
            token=token,
        )

    async def add_user_to_guild(
        self,
        token: ValidToken,
        *,
        bot_token: str,
        guild_id: int,
        user_id: int,
        nick: str | None = None,
        roles: list[str | int] | None = None,
        deaf: bool | None = None,
        mute: bool | None = None,
        bypass_verification: bool | None = None,
    ) -> member_types.AddGuildMemberResponse:
        data: member_types.AddGuildMemberRequest = {
            "access_token": self._parse_token(token),
        }
        if nick is not None:
            data["nick"] = nick
        if roles is not None:
            data["roles"] = roles
        if deaf is not None:
            data["deaf"] = deaf
        if mute is not None:
            data["mute"] = mute
        if bypass_verification is not None:
            member_flags = MemberFlags(0)
            member_flags.bypasses_verification = True
            data["flags"] = member_flags.value

        return await self.request(
            Route("PUT", f"/guilds/{guild_id}/members/{user_id}"),
            data=data,
            headers={"Authorization": f"Bot {bot_token}"},
        )
