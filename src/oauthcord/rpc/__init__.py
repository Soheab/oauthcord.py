# fmt: off
from .client import RPCClient
from .enums import *
from .errors import *
from .events import *
from .handler import EventsHandler, listens_to
from .models import *

__all__ = (  # noqa: RUF022
    # client
    "EventsHandler",
    "RPCClient",
    "listens_to",
    # enums
    "ActivityActionType",
    "ActivityHangStatusType",
    "ActivityPlatformType",
    "ActivityType",
    "CustomStatusLabelType",
    "RPCCloseCode",
    "RPCErrorCode",
    "RPCEvent",
    "ReceivedRPCEvent",
    "StatusDisplayType",
    "SubscribeableRPCEvent",
    "VoiceSettingsModeType",

    # events
    "Event",

    # errors
    "RPCClientClosedError",
    "RPCConnectionError",
    "RPCConnectionLostError",
    "RPCError",
    "RPCHandshakeError",
    "RPCSessionRequiredError",
    "RPCSocketNotFoundError",

    # models/activity
    "Activity",
    "ActivityAssets",
    "ActivityButton",
    "ActivityParty",
    "ActivitySecrets",
    "ActivityTimestamps",
    "ImageUpload",
    "ShareInteractionResult",
    "ShareLinkResult",

    # models/application
    "Ticket",

    # models/auth
    "RPCAuthentication",
    "RPCAuthenticationApplication",
    "RPCAuthenticationUser",

    # models/channels
    "ChannelPermissions",
    "RPCChannel",
    "RPCPartialChannel",

    # models/client
    "Image",
    "LocaleSettings",

    # models/connection
    "ProviderAccessToken",

    # models/events
    "ActivityInstanceParticipantsUpdate",
    "ActivityJoin",
    "ActivityInvite",
    "ActivityJoinRequest",
    "ActivityLayoutModeUpdate",
    "ActivityPipModeUpdate",
    "ActivitySpectate",
    "ClientEnvironmentConfig",
    "GuildStatus",
    "MessageEvent",
    "MessageDelete",
    "OrientationUpdate",
    "OverlayUpdate",
    "PartialRPCMessage",
    "QuestEnrollmentStatusUpdate",
    "ReadyEvent",
    "RPCErrorEvent",
    "ScreenshareApplication",
    "ScreenshareStateUpdate",
    "SpeakingStartData",
    "SpeakingStopData",
    "ThermalStateUpdate",
    "VideoStateUpdate",
    "VoiceChannelSelect",
    "VoiceConnectionPing",
    "VoiceConnectionStatus",
    "VoiceSettingsUpdate2",

    # models/guild
    "RPCGuild",

    # models/member
    "RPCGuildMember",

    # models/message
    "RPCMessage",

    # models/quest
    "QuestEnrollmentStatus",
    "TimerResult",

    # models/relationship
    "RPCRelationship",
    "RPCRelationshipPresence",

    # models/soundboard
    "SoundboardSound",

    # models/user
    "RPCActivityParticipant",
    "RPCUser",

    # models/voice
    "AvailableDevice",
    "Pan",
    "RPCVoiceState",
    "RemoteVoiceState",
    "ShortcutKeyCombo",
    "UserVoiceSettings",
    "VoiceIOSettings",
    "VoiceInputMode",
    "VoiceSettings",
    "VoiceSettingsMode",
)
