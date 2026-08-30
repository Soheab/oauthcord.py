from typing import Literal, NotRequired, TypedDict

from ..base import Snowflake
from ..presence import ActivityResponse
from .user import AvatarDecorationDataResponse, RPCUserResponse

Status = Literal["online", "idle", "dnd", "invisible", "offline"]


class RPCPartialGuildMemberResponse(TypedDict):
    user: RPCUserResponse
    nick: str | None
    status: Status
    activity: ActivityResponse | None


class RPCGuildMemberResponse(TypedDict):
    user_id: Snowflake
    nick: str | None
    guild_id: Snowflake
    avatar: str | None
    avatar_decoration_data: AvatarDecorationDataResponse | None
    banner: NotRequired[str | None]
    bio: NotRequired[str | None]
    pronouns: NotRequired[str | None]
    color_string: NotRequired[str | None]
