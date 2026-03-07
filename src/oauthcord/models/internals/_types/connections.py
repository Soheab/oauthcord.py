from typing import Literal, TypedDict

from .base import Snowflake

Service = Literal[
    "amazon-music",
    "battlenet",
    "bungie",
    "bluesky",
    "crunchyroll",
    "domain",
    "ebay",
    "epicgames",
    "facebook",
    "github",
    "instagram",
    "leagueoflegends",
    "mastodon",
    "paypal",
    "playstation",
    "reddit",
    "riotgames",
    "roblox",
    "spotify",
    "skype",
    "steam",
    "tiktok",
    "twitch",
    "twitter",
    "xbox",
    "youtube",
]
Visibility = Literal[0, 1]
IntegrationResponseType = Literal["twitch", "youtube", "discord", "guild_subscription"]


class ConnectionResponse(TypedDict):
    id: str
    name: str
    type: Service
    revoked: bool
    integrations: list[IntegrationResponse]
    verified: bool
    friend_sync: bool
    metadata_visibility: Visibility
    show_activity: bool
    two_way_link: bool
    visibility: Visibility


class IntegrationResponse(TypedDict):
    id: Snowflake
    type: IntegrationResponseType
    account: IntegrationAccountResponse
    guild: IntegrationGuildResponse


class IntegrationAccountResponse(TypedDict):
    id: str
    name: str


class IntegrationGuildResponse(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
