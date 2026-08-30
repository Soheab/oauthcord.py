from __future__ import annotations

from typing import NotRequired, TypedDict

from ..base import Snowflake
from ..channels import ChannelType
from ..invite import InviteResponse
from .message import RPCMessageResponse
from .voice import RPCVoiceStateResponse


class RPCChannelResponse(TypedDict):
    id: Snowflake
    name: str
    type: ChannelType
    topic: str
    bitrate: NotRequired[int]
    user_limit: int
    guild_id: Snowflake
    position: int
    voice_states: RPCVoiceStateResponse | None


class RPCChannelWithMessagesResponse(RPCChannelResponse):
    messages: NotRequired[list[RPCMessageResponse]]


class PartialRPCChannelResponse(TypedDict):
    id: Snowflake
    name: str
    type: ChannelType


# -- Commands ----------------------------------------------------------------


class GetChannelRequest(TypedDict):
    channel_id: Snowflake


GetChannelResponse = RPCChannelWithMessagesResponse


class GetChannelsRequest(TypedDict):
    guild_id: Snowflake


class GetChannelsResponse(TypedDict):
    channels: list[PartialRPCChannelResponse]


class GetChannelPermissionsResponse(TypedDict):
    permissions: str


class CreateChannelInviteRequest(TypedDict):
    channel_id: Snowflake


CreateChannelInviteResponse = InviteResponse


class SelectVoiceChannelRequest(TypedDict):
    channel_id: Snowflake | None  # None disconnects
    timeout: NotRequired[int]  # seconds, max 60
    force: NotRequired[bool]
    navigate: NotRequired[bool]


SelectVoiceChannelResponse = RPCChannelResponse | None
GetSelectedVoiceChannelResponse = RPCChannelResponse | None


class SelectTextChannelRequest(TypedDict):
    channel_id: Snowflake | None  # None navigates to the "Friends" page
    timeout: NotRequired[int]  # seconds, max 60


SelectTextChannelResponse = RPCChannelWithMessagesResponse | None
