from typing import NotRequired, TypedDict

from .base import Snowflake
from .user import GuildMemberWithUserResponse


class GuildMemberResponse(TypedDict):
    avatar: str | None
    banner: str | None
    communication_disabled_until: str | None  # iso
    flags: int
    joined_at: str  # iso
    nick: str
    pending: bool
    premium_since: str | None  # iso
    roles: list[str]
    unusual_dm_activity_until: str | None
    display_name_styles: str | None
    user: GuildMemberWithUserResponse
    mute: bool
    deaf: bool
    bio: str
    permissions: str


class AddGuildMemberRequest(TypedDict):
    access_token: str
    nick: NotRequired[str | None]
    roles: NotRequired[list[Snowflake]]
    mute: NotRequired[bool]
    deaf: NotRequired[bool]
    flags: NotRequired[int]


# already in guild = 204
AddGuildMemberResponse = GuildMemberResponse | None
