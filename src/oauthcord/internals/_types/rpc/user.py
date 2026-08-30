from __future__ import annotations

from typing import NotRequired, TypedDict

from ..base import Snowflake
from ..user import AvatarDecorationDataResponse, PremiumType


class RPCUserResponse(TypedDict):
    id: Snowflake
    username: str
    discriminator: str
    global_name: str | None
    avatar: str | None
    avatar_decoration_data: AvatarDecorationDataResponse | None
    bot: bool
    flags: int
    premium_type: PremiumType


class RPCActivityParticipantResponse(RPCUserResponse):
    nickname: NotRequired[str]


# -- Commands ----------------------------------------------------------------


class GetUserRequest(TypedDict):
    id: Snowflake  # arguments are not documented; the client expects the user ID


GetUserResponse = RPCUserResponse | None
