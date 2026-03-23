from typing import NotRequired, TypedDict

from .base import Snowflake


class CurrentUserGuildResponse(TypedDict):
    id: Snowflake
    name: str
    icon: str
    banner: str
    owner: bool
    permissions: str
    features: list[str]


CurrentUserGuildsResponse = list[CurrentUserGuildResponse]


class CurrentUserGuildsRequest(TypedDict):
    before: NotRequired[Snowflake | None]
    after: NotRequired[Snowflake | None]
    limit: NotRequired[int | None]
    with_counts: NotRequired[bool | None]

