"""The general Discord activity (rich presence) object.

This is Discord's full activity shape, used everywhere an activity is sent or
received — including over RPC, whose ``SET_ACTIVITY`` takes this same object and only
narrows ``type`` (see :mod:`.rpc.activity`).

See https://docs.discord.food/resources/presence#activity-object and
https://discord.com/developers/docs/events/gateway-events#activity-object.
"""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from .base import Snowflake

ActivityType = Literal[
    0,  # PLAYING
    1,  # STREAMING
    2,  # LISTENING
    3,  # WATCHING
    4,  # CUSTOM
    5,  # COMPETING
    6,  # HANG
]
ActivityPlatformType = Literal[
    "desktop",
    "xbox",
    "samsung",
    "ios",
    "android",
    "embedded",
    "ps4",
    "ps5",
    "meta_quest",
]
ActivityHangStatusType = Literal[
    "chilling",
    "gaming",
    "focusing",
    "brb",
    "watching",
    "custom",
]
ActivityActionType = Literal[
    1,  # JOIN
    2,  # SPECTATE (deprecated)
    3,  # LISTEN
    5,  # JOIN_REQUEST
]
CustomStatusLabelType = Literal[
    "question",
    "think",
    "love",
    "excited",
    "recommend",
]
StatusDisplayType = Literal[
    0,  # NAME
    1,  # STATE
    2,  # DETAILS
]


class ActivityTimestampsRequest(TypedDict):
    start: NotRequired[int]  # unix ms
    end: NotRequired[int]  # unix ms


ActivityTimestampsResponse = ActivityTimestampsRequest


class ActivityEmojiRequest(TypedDict):
    name: str
    id: NotRequired[Snowflake]
    animated: NotRequired[bool]


ActivityEmojiResponse = ActivityEmojiRequest


class ActivityPartyRequest(TypedDict):
    id: NotRequired[str]  # max 128 characters
    size: NotRequired[list[int]]  # [current_size, max_size]


ActivityPartyResponse = ActivityPartyRequest


class ActivityAssetsRequest(TypedDict):
    large_image: NotRequired[str]  # max 313 characters
    large_text: NotRequired[str]  # max 128 characters
    large_url: NotRequired[str]  # max 256 characters
    small_image: NotRequired[str]  # max 313 characters
    small_text: NotRequired[str]  # max 128 characters
    small_url: NotRequired[str]  # max 256 characters
    invite_cover_image: NotRequired[str]  # max 313 characters


ActivityAssetsResponse = ActivityAssetsRequest


class ActivitySecretsRequest(TypedDict):
    join: NotRequired[str]  # max 128 characters
    spectate: NotRequired[str]  # deprecated, max 128 characters
    match: NotRequired[str]  # max 128 characters


ActivitySecretsResponse = ActivitySecretsRequest


class ActivityButtonRequest(TypedDict):
    """Buttons are sent as objects but received as a list of labels."""

    label: str  # 1-32 characters
    url: str  # 1-512 characters


ActivityButtonResponse = list[str]  # labels


class ActivityMetadataRequest(TypedDict):
    """A convention followed by official clients; not enforced by the API."""

    button_urls: NotRequired[list[str]]  # max 2
    artist_ids: NotRequired[list[str]]
    album_id: NotRequired[str]
    context_uri: NotRequired[str]
    type: NotRequired[Literal["track", "episode"]]


ActivityMetadataResponse = ActivityMetadataRequest


class ActivityRequest(TypedDict):
    name: str  # 1-128 characters
    type: ActivityType
    url: NotRequired[str | None]  # max 512 characters, must be http(s)
    platform: NotRequired[str]
    supported_platforms: NotRequired[list[str]]  # max 10
    timestamps: NotRequired[ActivityTimestampsRequest]
    application_id: NotRequired[Snowflake]
    parent_application_id: NotRequired[Snowflake]
    status_display_type: NotRequired[int | None]
    details: NotRequired[str | None]  # max 128 characters
    details_url: NotRequired[str | None]  # max 256 characters
    state: NotRequired[str | None]  # max 128 characters
    state_url: NotRequired[str | None]  # max 256 characters
    sync_id: NotRequired[str]
    flags: NotRequired[int]
    buttons: NotRequired[list[ActivityButtonRequest]]  # max 2
    emoji: NotRequired[ActivityEmojiRequest | None]
    party: NotRequired[ActivityPartyRequest]
    assets: NotRequired[ActivityAssetsRequest]
    secrets: NotRequired[ActivitySecretsRequest]  # send-only
    metadata: NotRequired[ActivityMetadataRequest]  # send-only
    instance: NotRequired[bool]


class ActivityResponse(TypedDict):
    id: str
    name: str  # 1-128 characters
    type: ActivityType
    url: NotRequired[str | None]  # max 512 characters
    created_at: int  # unix ms, received only
    session_id: NotRequired[str | None]  # received only
    platform: NotRequired[str]
    supported_platforms: NotRequired[list[str]]  # max 10
    timestamps: NotRequired[ActivityTimestampsResponse]
    application_id: NotRequired[Snowflake]
    parent_application_id: NotRequired[Snowflake]
    status_display_type: NotRequired[int | None]
    details: NotRequired[str | None]  # max 128 characters
    details_url: NotRequired[str | None]  # max 256 characters
    state: NotRequired[str | None]  # max 128 characters
    state_url: NotRequired[str | None]  # max 256 characters
    sync_id: NotRequired[str]
    flags: NotRequired[int]
    buttons: NotRequired[ActivityButtonResponse]  # max 2
    emoji: NotRequired[ActivityEmojiResponse | None]
    party: NotRequired[ActivityPartyResponse]
    assets: NotRequired[ActivityAssetsResponse]
    secrets: NotRequired[ActivitySecretsResponse]
    instance: NotRequired[bool]
