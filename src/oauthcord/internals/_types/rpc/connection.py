"""Command types for the connection RPC commands.

Covers the provider access token commands, ``NAVIGATE_TO_CONNECTIONS`` and
``INVITE_USER_EMBEDDED``.

See https://docs.discord.food/topics/rpc#get-provider-access-token.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict

from ..base import Snowflake
from ..connections import Service


class GetProviderAccessTokenRequest(TypedDict):
    provider: Service
    connection_redirect: NotRequired[str]


class GetProviderAccessTokenResponse(TypedDict):
    access_token: str


class MaybeGetProviderAccessTokenRequest(TypedDict):
    provider: Service


MaybeGetProviderAccessTokenResponse = GetProviderAccessTokenResponse
NavigateToConnectionsResponse = None


class InviteUserEmbeddedRequest(TypedDict):
    user_id: Snowflake
    content: NotRequired[str]


InviteUserEmbeddedResponse = None  # undocumented
