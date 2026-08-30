"""RPC event (``DISPATCH``) payload types.

Every event listed in ``RPCEvent``/``_RPCEvent`` (see
:mod:`oauthcord.client.rpc.enums`) has an ``...EventData`` type describing the inner
``data`` payload of its ``DISPATCH`` packet, and, where the event is subscribable
with arguments, an ``...EventArgs`` type for the ``SUBSCRIBE``/``UNSUBSCRIBE`` args.

``READY`` and ``ERROR`` are non-subscription events (sent unprompted / on error) and
so have no args type. ``AUTHORIZE_REQUEST``'s inner payload is always ``None``.

See https://docs.discord.food/topics/rpc#rpc-events.
"""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from ..base import Snowflake
from ..entitlement import EntitlementResponse
from ..presence import ActivityResponse
from .channels import PartialRPCChannelResponse
from .guild import RPCGuildResponse
from .member import RPCGuildMemberResponse
from .message import RPCMessageResponse
from .relationship import RPCRelationshipResponse
from .user import RPCActivityParticipantResponse, RPCUserResponse
from .voice import (
    RPCVoiceInputModeRequest,
    RPCVoiceSettingsResponse,
    RPCVoiceStateResponse,
)

EventNameType = Literal[
    "READY",
    "ERROR",
    "CURRENT_USER_UPDATE",
    "CURRENT_GUILD_MEMBER_UPDATE",
    "GUILD_STATUS",
    "GUILD_CREATE",
    "CHANNEL_CREATE",
    "RELATIONSHIP_UPDATE",
    "VOICE_CHANNEL_SELECT",
    "VOICE_STATE_CREATE",
    "VOICE_STATE_DELETE",
    "VOICE_STATE_UPDATE",
    "VOICE_SETTINGS_UPDATE",
    "VOICE_SETTINGS_UPDATE_2",
    "VOICE_CONNECTION_STATUS",
    "SPEAKING_START",
    "SPEAKING_STOP",
    "ACTIVITY_JOIN",
    "ACTIVITY_JOIN_REQUEST",
    "ACTIVITY_SPECTATE",
    "ACTIVITY_INVITE",
    "ACTIVITY_PIP_MODE_UPDATE",
    "ACTIVITY_LAYOUT_MODE_UPDATE",
    "THERMAL_STATE_UPDATE",
    "ORIENTATION_UPDATE",
    "ACTIVITY_INSTANCE_PARTICIPANTS_UPDATE",
    "NOTIFICATION_CREATE",
    "MESSAGE_CREATE",
    "MESSAGE_UPDATE",
    "MESSAGE_DELETE",
    "OVERLAY_UPDATE",
    "ENTITLEMENT_CREATE",
    "ENTITLEMENT_DELETE",
    "SCREENSHARE_STATE_UPDATE",
    "VIDEO_STATE_UPDATE",
    "AUTHORIZE_REQUEST",
    "QUEST_ENROLLMENT_STATUS_UPDATE",
]


class SubscribeRequest(TypedDict):
    """Event subscription arguments; which keys apply depends on the event."""

    guild_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake | None]


class SubscribeResponse(TypedDict):
    evt: str


UnsubscribeRequest = SubscribeRequest
UnsubscribeResponse = SubscribeResponse


class ChannelSubscriptionEventArgs(TypedDict):
    """Subscription arguments shared by events keyed on a required channel ID."""

    channel_id: Snowflake


class GuildSubscriptionEventArgs(TypedDict):
    """Subscription arguments shared by events keyed on a guild ID."""

    guild_id: Snowflake


# -- Ready ---------------------------------------------------------------


class ClientEnvironmentConfigResponse(TypedDict):
    cdn_host: NotRequired[str]
    api_endpoint: str
    environment: str  # always "production"


class ReadyEventData(TypedDict):
    v: int
    config: ClientEnvironmentConfigResponse
    user: NotRequired[RPCUserResponse]  # only present in the IPC transport


# -- Error -----------------------------------------------------------------


class ErrorEventData(TypedDict):
    code: int
    message: str


# -- Current user / guild member -------------------------------------------

CurrentUserUpdateEventData = RPCUserResponse

CurrentGuildMemberUpdateEventArgs = GuildSubscriptionEventArgs
CurrentGuildMemberUpdateEventData = RPCGuildMemberResponse


# -- Guilds ------------------------------------------------------------------

GuildStatusEventArgs = GuildSubscriptionEventArgs


class GuildStatusEventData(TypedDict):
    guild: RPCGuildResponse


GuildCreateEventData = RPCGuildResponse
ChannelCreateEventData = PartialRPCChannelResponse
RelationshipUpdateEventData = RPCRelationshipResponse


# -- Voice -------------------------------------------------------------------


class VoiceChannelSelectEventData(TypedDict):
    channel_id: Snowflake | None
    guild_id: NotRequired[Snowflake | None]


VoiceStateCreateEventArgs = ChannelSubscriptionEventArgs
VoiceStateCreateEventData = RPCVoiceStateResponse

VoiceStateDeleteEventArgs = ChannelSubscriptionEventArgs
VoiceStateDeleteEventData = RPCVoiceStateResponse

VoiceStateUpdateEventArgs = ChannelSubscriptionEventArgs
VoiceStateUpdateEventData = RPCVoiceStateResponse

VoiceSettingsUpdateEventData = RPCVoiceSettingsResponse


class VoiceSettingsUpdate2EventData(TypedDict):
    input_mode: RPCVoiceInputModeRequest
    local_mutes: list[Snowflake]
    local_volumes: dict[Snowflake, float]
    self_mute: bool
    self_deaf: bool


VoiceConnectionState = Literal[
    "DISCONNECTED",
    "AWAITING_ENDPOINT",
    "AUTHENTICATING",
    "CONNECTING",
    "VOICE_DISCONNECTED",
    "VOICE_CONNECTING",
    "VOICE_CONNECTED",
    "NO_ROUTE",
    "ICE_CHECKING",
    "DTLS_CONNECTING",
]


class VoiceConnectionPingResponse(TypedDict):
    time: int
    value: int


class VoiceConnectionStatusEventData(TypedDict):
    state: VoiceConnectionState
    hostname: str
    pings: list[VoiceConnectionPingResponse]  # max 200
    average_ping: NotRequired[int]
    last_ping: NotRequired[int]


class SpeakingSubscriptionEventArgs(TypedDict):
    channel_id: Snowflake | None


SpeakingStartEventArgs = SpeakingSubscriptionEventArgs
SpeakingStopEventArgs = SpeakingSubscriptionEventArgs


class SpeakingStartEventData(TypedDict):
    channel_id: Snowflake
    user_id: Snowflake


class SpeakingStopEventData(TypedDict):
    channel_id: Snowflake
    user_id: Snowflake


# -- Activities ----------------------------------------------------------

JoinIntent = Literal[
    0,  # PLAY
    1,  # SPECTATE
]


class ActivityJoinEventData(TypedDict):
    secret: str
    intent: NotRequired[JoinIntent]


class ActivityJoinRequestEventData(TypedDict):
    user: RPCUserResponse
    activity: ActivityResponse
    type: Literal[3]  # always JOIN_REQUEST
    channel_id: Snowflake
    message_id: Snowflake


class ActivitySpectateEventData(TypedDict):
    secret: str


class ActivityInviteEventData(TypedDict):
    user: RPCUserResponse
    activity: ActivityResponse
    type: Literal[1]  # always JOIN
    channel_id: Snowflake
    message_id: Snowflake


class ActivityPipModeUpdateEventData(TypedDict):
    is_pip_mode: bool


LayoutMode = Literal[
    0,  # FOCUSED
    1,  # PIP
    2,  # GRID
]


class ActivityLayoutModeUpdateEventData(TypedDict):
    layout_mode: LayoutMode


ThermalState = Literal[
    0,  # NOMINAL
    1,  # FAIR
    2,  # SERIOUS
    3,  # CRITICAL
]


class ThermalStateUpdateEventData(TypedDict):
    thermal_state: ThermalState


class OrientationUpdateEventData(TypedDict):
    screen_orientation: int  # orientation state


class ActivityInstanceParticipantsUpdateEventData(TypedDict):
    participants: list[RPCActivityParticipantResponse]


# -- Notifications / messages ----------------------------------------------


class NotificationCreateEventData(TypedDict):
    channel_id: Snowflake
    message: RPCMessageResponse
    icon_url: str | None
    title: str
    body: str


MessageCreateEventArgs = ChannelSubscriptionEventArgs


class MessageCreateEventData(TypedDict):
    channel_id: Snowflake
    message: RPCMessageResponse


MessageUpdateEventArgs = ChannelSubscriptionEventArgs


class MessageUpdateEventData(TypedDict):
    channel_id: Snowflake
    message: RPCMessageResponse


MessageDeleteEventArgs = ChannelSubscriptionEventArgs


class PartialRPCMessageResponse(TypedDict):
    id: Snowflake


class MessageDeleteEventData(TypedDict):
    channel_id: Snowflake
    message: PartialRPCMessageResponse


# -- Overlay -----------------------------------------------------------------


class OverlayUpdateEventArgs(TypedDict):
    pid: int


class OverlayUpdateEventData(TypedDict):
    enabled: bool
    locked: bool


# -- Entitlements --------------------------------------------------------

EntitlementCreateEventData = EntitlementResponse
EntitlementDeleteEventData = EntitlementResponse


# -- Screenshare / video -------------------------------------------------


class ScreenshareApplicationResponse(TypedDict):
    name: str


class ScreenshareStateUpdateEventData(TypedDict):
    active: bool
    pid: int | None
    application: ScreenshareApplicationResponse | None


class VideoStateUpdateEventData(TypedDict):
    active: bool


# -- Authorize / quests -------------------------------------------------

type AuthorizeRequestEventData = None


class QuestEnrollmentStatusUpdateEventData(TypedDict):
    quest_id: Snowflake
    is_enrolled: bool


# -- Dispatch payload ---------------------------------------------------

RPCDispatchEventData = (
    ReadyEventData
    | ErrorEventData
    | CurrentUserUpdateEventData
    | CurrentGuildMemberUpdateEventData
    | GuildStatusEventData
    | GuildCreateEventData
    | ChannelCreateEventData
    | RelationshipUpdateEventData
    | VoiceChannelSelectEventData
    | VoiceStateCreateEventData
    | VoiceStateDeleteEventData
    | VoiceStateUpdateEventData
    | VoiceSettingsUpdateEventData
    | VoiceSettingsUpdate2EventData
    | VoiceConnectionStatusEventData
    | SpeakingStartEventData
    | SpeakingStopEventData
    | ActivityJoinEventData
    | ActivityJoinRequestEventData
    | ActivitySpectateEventData
    | ActivityInviteEventData
    | ActivityPipModeUpdateEventData
    | ActivityLayoutModeUpdateEventData
    | ThermalStateUpdateEventData
    | OrientationUpdateEventData
    | ActivityInstanceParticipantsUpdateEventData
    | NotificationCreateEventData
    | MessageCreateEventData
    | MessageUpdateEventData
    | MessageDeleteEventData
    | OverlayUpdateEventData
    | EntitlementCreateEventData
    | EntitlementDeleteEventData
    | ScreenshareStateUpdateEventData
    | VideoStateUpdateEventData
    | AuthorizeRequestEventData
    | QuestEnrollmentStatusUpdateEventData
)
"""The ``data`` of any ``DISPATCH`` payload, keyed by its ``evt``."""

InnerEventTypes = (
    ClientEnvironmentConfigResponse
    | VoiceConnectionPingResponse
    | ScreenshareApplicationResponse
    | PartialRPCMessageResponse
)
"""Non-``DISPATCH`` payload types nested inside ``RPCDispatchEventData`` members."""


class RPCDispatchPayload(TypedDict):
    cmd: Literal["DISPATCH"]
    evt: EventNameType
    data: RPCDispatchEventData
    nonce: None
