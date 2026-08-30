from __future__ import annotations

from typing import TYPE_CHECKING, override

from ...models._base import BaseModel
from ...models.user import AvatarDecorationData

if TYPE_CHECKING:
    from ...internals._types.rpc.member import RPCGuildMemberResponse

__all__ = ("RPCGuildMember",)


class RPCGuildMember(BaseModel["RPCGuildMemberResponse"]):
    """Represents a partial guild member as sent by RPC's
    ``CURRENT_GUILD_MEMBER_UPDATE`` event."""

    __slots__ = (
        "avatar",
        "avatar_decoration_data",
        "banner",
        "bio",
        "color_string",
        "guild_id",
        "nick",
        "pronouns",
        "user_id",
    )

    @override
    def _initialize(self, data: RPCGuildMemberResponse) -> None:
        self.user_id: int = int(data["user_id"])
        self.guild_id: int = int(data["guild_id"])
        self.nick: str | None = data.get("nick")
        self.avatar: str | None = data.get("avatar")
        self.avatar_decoration_data: AvatarDecorationData | None = (
            self._initialize_other(
                AvatarDecorationData,
                data.get("avatar_decoration_data"),
                optional=True,
            )
        )
        self.banner: str | None = data.get("banner")
        self.bio: str | None = data.get("bio")
        self.pronouns: str | None = data.get("pronouns")
        self.color_string: str | None = data.get("color_string")
