from typing import NotRequired, TypedDict

from .base import Snowflake
from .user import (
    AvatarDecorationDataResponse,
    CollectablesResponse,
    DisplayNameStyleResponse,
    GuildMemberWithUserResponse,
)


class GuildMemberResponse(TypedDict):
    avatar: NotRequired[str | None]
    banner: NotRequired[str | None]
    communication_disabled_until: NotRequired[str | None]  # iso
    flags: int
    joined_at: str  # iso
    nick: NotRequired[str]
    pending: bool
    premium_since: NotRequired[str | None]  # iso
    roles: list[Snowflake]
    unusual_dm_activity_until: NotRequired[str | None]
    display_name_styles: NotRequired[DisplayNameStyleResponse | None]
    user: GuildMemberWithUserResponse
    mute: NotRequired[bool]
    deaf: NotRequired[bool]
    bio: NotRequired[str | None]
    permissions: NotRequired[str]
    avatar_decoration_data: AvatarDecorationDataResponse | None
    collectibles: CollectablesResponse | None


class AddGuildMemberRequest(TypedDict):
    access_token: str
    nick: NotRequired[str | None]
    roles: NotRequired[list[Snowflake]]
    mute: NotRequired[bool]
    deaf: NotRequired[bool]
    flags: NotRequired[int]


# already in guild = 204
AddGuildMemberResponse = GuildMemberResponse | None
