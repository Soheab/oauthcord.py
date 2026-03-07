from typing import NotRequired, TypedDict

from .base import Snowflake
from .user import PartialUserResponse


class CurrentAuthApplicationResponse(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
    description: str
    hook: bool
    bot_public: bool
    bot_require_code_grant: bool
    verify_key: str


CurrentAuthUserResponse = PartialUserResponse


class CurrentAuthResponse(TypedDict):
    application: CurrentAuthApplicationResponse
    scopes: list[str]
    expires: str  # iso # when the access token expires
    user: NotRequired[CurrentAuthUserResponse]
