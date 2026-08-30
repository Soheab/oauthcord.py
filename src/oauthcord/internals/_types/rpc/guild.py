from __future__ import annotations

from typing import NotRequired, TypedDict

from ..base import Snowflake


class RPCGuildResponse(TypedDict):
    id: str
    name: str
    icon_url: str | None


class RPCGetGuildResponse(RPCGuildResponse):
    vanity_url_code: str | None


RPCGetGuildsResponse = list[RPCGuildResponse]


# -- Commands ----------------------------------------------------------------


class GetGuildRequest(TypedDict):
    guild_id: Snowflake
    timeout: NotRequired[int]  # seconds, max 60


GetGuildResponse = RPCGuildResponse


class GetGuildsResponse(TypedDict):
    guilds: list[GetGuildResponse]
