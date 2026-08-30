"""Command types for the ``AUTHORIZE`` and ``AUTHENTICATE`` RPC commands.

See https://docs.discord.food/topics/rpc#authorize.
"""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from ..base import Snowflake
from ..current_auth_info import CurrentAuthResponse


class AuthorizeRequest(TypedDict):
    client_id: Snowflake
    response_type: NotRequired[Literal["code"]]
    redirect_uri: NotRequired[str]  # only applicable to the ws transport
    scopes: NotRequired[list[str]]
    code_challenge: NotRequired[str]
    code_challenge_method: NotRequired[Literal["S256"]]
    state: NotRequired[str]
    nonce: NotRequired[str]  # only for authorization code grants with openid
    permissions: NotRequired[str]
    guild_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake]
    prompt: NotRequired[str]  # default consent
    disable_guild_select: NotRequired[bool]
    integration_type: NotRequired[int]
    pid: NotRequired[int]


class AuthorizeResponse(TypedDict):
    code: str


class AuthenticateRequest(TypedDict):
    access_token: str


class AuthenticateResponse(CurrentAuthResponse):
    access_token: str
