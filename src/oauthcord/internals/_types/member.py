from typing import NotRequired, TypedDict

from .base import Snowflake
from .user import (
    DisplayNameStyleResponse,
    PartialUserResponse,
)


class GuildMemberResponse(PartialUserResponse):
    communication_disabled_until: NotRequired[str | None]  # iso
    flags: int
    joined_at: str  # iso
    nick: NotRequired[str]
    pending: bool
    premium_since: NotRequired[str | None]  # iso
    roles: list[Snowflake]
    unusual_dm_activity_until: NotRequired[str | None]
    display_name_styles: NotRequired[DisplayNameStyleResponse | None]
    user: PartialUserResponse
    mute: NotRequired[bool]
    deaf: NotRequired[bool]
    bio: NotRequired[str | None]
    permissions: NotRequired[str]


class AddGuildMemberRequest(TypedDict):
    access_token: str
    nick: NotRequired[str | None]
    roles: NotRequired[list[Snowflake]]
    mute: NotRequired[bool]
    deaf: NotRequired[bool]
    flags: NotRequired[int]


# already in guild = 204
AddGuildMemberResponse = GuildMemberResponse | None
