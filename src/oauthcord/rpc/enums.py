from enum import IntEnum, StrEnum

__all__ = (
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
)


class RPCCloseCode(IntEnum):
    CLOSE_NORMAL = 1000
    CLOSE_UNSUPPORTED = 1003
    CLOSE_ABNORMAL = 1006
    INVALID_CLIENTID = 4000
    INVALID_ORIGIN = 4001
    RATELIMITED = 4002
    TOKEN_REVOKED = 4003
    INVALID_VERSION = 4004
    INVALID_ENCODING = 4005


class RPCErrorCode(IntEnum):
    UNKNOWN_ERROR = 1000
    SERVICE_UNAVAILABLE = 1001
    TRANSACTION_ABORTED = 1002
    INVALID_PAYLOAD = 4000
    INVALID_COMMAND = 4002
    INVALID_GUILD = 4003
    INVALID_EVENT = 4004
    INVALID_CHANNEL = 4005
    INVALID_PERMISSIONS = 4006
    INVALID_CLIENTID = 4007
    INVALID_ORIGIN = 4008
    INVALID_TOKEN = 4009
    INVALID_USER = 4010
    INVALID_INVITE = 4011
    INVALID_ACTIVITY_JOIN_REQUEST = 4012
    INVALID_LOBBY = 4013
    INVALID_LOBBY_SECRET = 4014
    INVALID_ENTITLEMENT = 4015
    INVALID_GIFT_CODE = 4016
    INVALID_GUILD_TEMPLATE = 4017
    INVALID_SOUND = 4018
    INVALID_PROVIDER = 4019
    INVALID_CONNECTION_CALLBACK_STATE = 4020
    BAD_REQUEST_FOR_PROVIDER = 4021
    OAUTH2_ERROR = 5000
    SELECT_CHANNEL_TIMED_OUT = 5001
    GET_GUILD_TIMED_OUT = 5002
    SELECT_VOICE_FORCE_REQUIRED = 5003
    CAPTURE_SHORTCUT_ALREADY_LISTENING = 5004
    INVALID_ACTIVITY_SECRET = 5005
    NO_ELIGIBLE_ACTIVITY = 5006
    LOBBY_FULL = 5007
    PURCHASE_CANCELED = 5008
    PURCHASE_ERROR = 5009
    UNAUTHORIZED_FOR_ACHIEVEMENT = 5010
    RATE_LIMITED = 5011
    UNAUTHORIZED_FOR_APPLICATION = 5012
    NO_CONNECTION_FOUND = 5013


class RPCEvent:
    READY = "READY"  # (no scope; sent immediately after connecting)
    ERROR = "ERROR"  # (no scope; sent on error, including command responses)
    CURRENT_USER_UPDATE = "CURRENT_USER_UPDATE"  # rpc.local, identify
    CURRENT_GUILD_MEMBER_UPDATE = (
        "CURRENT_GUILD_MEMBER_UPDATE"  # identify and guilds.members.read
    )
    GUILD_STATUS = "GUILD_STATUS"  # rpc
    GUILD_CREATE = "GUILD_CREATE"  # rpc
    CHANNEL_CREATE = "CHANNEL_CREATE"  # rpc
    RELATIONSHIP_UPDATE = "RELATIONSHIP_UPDATE"  # relationships.read
    VOICE_CHANNEL_SELECT = "VOICE_CHANNEL_SELECT"  # rpc
    VOICE_STATE_CREATE = "VOICE_STATE_CREATE"  # rpc or rpc.voice.read
    VOICE_STATE_DELETE = "VOICE_STATE_DELETE"  # rpc or rpc.voice.read
    VOICE_STATE_UPDATE = "VOICE_STATE_UPDATE"  # rpc or rpc.voice.read
    VOICE_SETTINGS_UPDATE = "VOICE_SETTINGS_UPDATE"  # rpc or rpc.voice.read
    VOICE_SETTINGS_UPDATE_2 = "VOICE_SETTINGS_UPDATE_2"  # rpc.local
    VOICE_CONNECTION_STATUS = "VOICE_CONNECTION_STATUS"  # rpc or rpc.voice.read
    SPEAKING_START = "SPEAKING_START"  # rpc, rpc.voice.read, or rpc.local
    SPEAKING_STOP = "SPEAKING_STOP"  # rpc, rpc.voice.read, or rpc.local
    ACTIVITY_JOIN = "ACTIVITY_JOIN"  # rpc, rpc.authenticated, or rpc.local
    ACTIVITY_JOIN_REQUEST = "ACTIVITY_JOIN_REQUEST"  # rpc or rpc.local
    ACTIVITY_SPECTATE = "ACTIVITY_SPECTATE"  # rpc, rpc.authenticated, or rpc.local
    ACTIVITY_INVITE = "ACTIVITY_INVITE"  # rpc or rpc.local
    ACTIVITY_PIP_MODE_UPDATE = "ACTIVITY_PIP_MODE_UPDATE"  # (no scope documented)
    ACTIVITY_LAYOUT_MODE_UPDATE = "ACTIVITY_LAYOUT_MODE_UPDATE"  # (no scope documented)
    THERMAL_STATE_UPDATE = "THERMAL_STATE_UPDATE"  # rpc.authenticated (mobile only)
    ORIENTATION_UPDATE = "ORIENTATION_UPDATE"  # rpc.authenticated (mobile only)
    ACTIVITY_INSTANCE_PARTICIPANTS_UPDATE = (
        "ACTIVITY_INSTANCE_PARTICIPANTS_UPDATE"  # rpc.authenticated
    )
    NOTIFICATION_CREATE = "NOTIFICATION_CREATE"  # rpc and rpc.notifications.read
    MESSAGE_CREATE = (
        "MESSAGE_CREATE"  # rpc (also requires matching application_id or messages.read)
    )
    MESSAGE_UPDATE = (
        "MESSAGE_UPDATE"  # rpc (also requires matching application_id or messages.read)
    )
    MESSAGE_DELETE = (
        "MESSAGE_DELETE"  # rpc (also requires matching application_id or messages.read)
    )
    OVERLAY_UPDATE = "OVERLAY_UPDATE"  # rpc.local
    ENTITLEMENT_CREATE = "ENTITLEMENT_CREATE"  # rpc.authenticated, rpc.local
    ENTITLEMENT_DELETE = "ENTITLEMENT_DELETE"  # rpc.authenticated, rpc.local
    SCREENSHARE_STATE_UPDATE = (
        "SCREENSHARE_STATE_UPDATE"  # rpc.screenshare.read or rpc.local
    )
    VIDEO_STATE_UPDATE = "VIDEO_STATE_UPDATE"  # rpc.voice.read or rpc.local
    AUTHORIZE_REQUEST = "AUTHORIZE_REQUEST"  # (no scope documented)
    QUEST_ENROLLMENT_STATUS_UPDATE = "QUEST_ENROLLMENT_STATUS_UPDATE"  # identify


# for users
class SubscribeableRPCEvent(StrEnum):
    CURRENT_USER_UPDATE = "CURRENT_USER_UPDATE"  # rpc.local, identify
    CURRENT_GUILD_MEMBER_UPDATE = (
        "CURRENT_GUILD_MEMBER_UPDATE"  # identify and guilds.members.read
    )
    GUILD_STATUS = "GUILD_STATUS"  # rpc
    GUILD_CREATE = "GUILD_CREATE"  # rpc
    CHANNEL_CREATE = "CHANNEL_CREATE"  # rpc
    RELATIONSHIP_UPDATE = "RELATIONSHIP_UPDATE"  # relationships.read
    VOICE_CHANNEL_SELECT = "VOICE_CHANNEL_SELECT"  # rpc
    VOICE_STATE_CREATE = "VOICE_STATE_CREATE"  # rpc or rpc.voice.read
    VOICE_STATE_DELETE = "VOICE_STATE_DELETE"  # rpc or rpc.voice.read
    VOICE_STATE_UPDATE = "VOICE_STATE_UPDATE"  # rpc or rpc.voice.read
    VOICE_SETTINGS_UPDATE = "VOICE_SETTINGS_UPDATE"  # rpc or rpc.voice.read
    VOICE_SETTINGS_UPDATE_2 = "VOICE_SETTINGS_UPDATE_2"  # rpc.local
    VOICE_CONNECTION_STATUS = "VOICE_CONNECTION_STATUS"  # rpc or rpc.voice.read
    SPEAKING_START = "SPEAKING_START"  # rpc, rpc.voice.read, or rpc.local
    SPEAKING_STOP = "SPEAKING_STOP"  # rpc, rpc.voice.read, or rpc.local
    ACTIVITY_JOIN = "ACTIVITY_JOIN"  # rpc, rpc.authenticated, or rpc.local
    ACTIVITY_JOIN_REQUEST = "ACTIVITY_JOIN_REQUEST"  # rpc or rpc.local
    ACTIVITY_SPECTATE = "ACTIVITY_SPECTATE"  # rpc, rpc.authenticated, or rpc.local
    ACTIVITY_INVITE = "ACTIVITY_INVITE"  # rpc or rpc.local
    ACTIVITY_PIP_MODE_UPDATE = "ACTIVITY_PIP_MODE_UPDATE"  # (no scope documented)
    ACTIVITY_LAYOUT_MODE_UPDATE = "ACTIVITY_LAYOUT_MODE_UPDATE"  # (no scope documented)
    THERMAL_STATE_UPDATE = "THERMAL_STATE_UPDATE"  # rpc.authenticated (mobile only)
    ORIENTATION_UPDATE = "ORIENTATION_UPDATE"  # rpc.authenticated (mobile only)
    ACTIVITY_INSTANCE_PARTICIPANTS_UPDATE = (
        "ACTIVITY_INSTANCE_PARTICIPANTS_UPDATE"  # rpc.authenticated
    )
    NOTIFICATION_CREATE = "NOTIFICATION_CREATE"  # rpc and rpc.notifications.read
    MESSAGE_CREATE = (
        "MESSAGE_CREATE"  # rpc (also requires matching application_id or messages.read)
    )
    MESSAGE_UPDATE = (
        "MESSAGE_UPDATE"  # rpc (also requires matching application_id or messages.read)
    )
    MESSAGE_DELETE = (
        "MESSAGE_DELETE"  # rpc (also requires matching application_id or messages.read)
    )
    OVERLAY_UPDATE = "OVERLAY_UPDATE"  # rpc.local
    ENTITLEMENT_CREATE = "ENTITLEMENT_CREATE"  # rpc.authenticated, rpc.local
    ENTITLEMENT_DELETE = "ENTITLEMENT_DELETE"  # rpc.authenticated, rpc.local
    SCREENSHARE_STATE_UPDATE = (
        "SCREENSHARE_STATE_UPDATE"  # rpc.screenshare.read or rpc.local
    )
    VIDEO_STATE_UPDATE = "VIDEO_STATE_UPDATE"  # rpc.voice.read or rpc.local
    QUEST_ENROLLMENT_STATUS_UPDATE = "QUEST_ENROLLMENT_STATUS_UPDATE"  # identify


class ReceivedRPCEvent(StrEnum):
    READY = "READY"  # (no scope; sent immediately after connecting)
    ERROR = "ERROR"  # (no scope; sent on error, including command responses)
    AUTHORIZE_REQUEST = "AUTHORIZE_REQUEST"  # (no scope documented)


class RPCCommand(StrEnum):
    """IPC command names used by the Discord RPC protocol.

    Only includes commands usable by third-party applications over external IPC — this
    omits deprecated GameSDK networking commands and commands gated behind ``rpc.private``
    / ``rpc.private.limited`` scopes, which Discord only grants to its own first-party
    integrations. Each name is annotated with the OAuth2 scope(s) it requires, per
    https://docs.discord.food/topics/rpc#rpc-commands.
    """

    DISPATCH = "DISPATCH"  # (no scope; server -> client only)
    AUTHORIZE = "AUTHORIZE"  # (no scope; used to obtain one)
    AUTHENTICATE = "AUTHENTICATE"  # (no scope; used to obtain one)
    SUBSCRIBE = "SUBSCRIBE"  # (no scope; depends on the event)
    UNSUBSCRIBE = "UNSUBSCRIBE"  # (no scope; depends on the event)
    GET_GUILD = "GET_GUILD"  # rpc
    GET_GUILDS = "GET_GUILDS"  # rpc
    GET_CHANNEL = "GET_CHANNEL"  # rpc, guilds, or guilds.channels.read
    GET_CHANNELS = "GET_CHANNELS"  # rpc
    GET_CHANNEL_PERMISSIONS = (
        "GET_CHANNEL_PERMISSIONS"  # guilds.members.read or guilds.channels.read
    )
    CREATE_CHANNEL_INVITE = "CREATE_CHANNEL_INVITE"  # rpc
    GET_RELATIONSHIPS = "GET_RELATIONSHIPS"  # relationships.read
    GET_USER = "GET_USER"  # rpc.local or rpc.embedded_app
    SET_USER_VOICE_SETTINGS = "SET_USER_VOICE_SETTINGS"  # rpc or rpc.voice.write
    SET_USER_VOICE_SETTINGS_2 = "SET_USER_VOICE_SETTINGS_2"  # rpc.local
    PUSH_TO_TALK = "PUSH_TO_TALK"  # rpc and rpc.voice.write
    SELECT_VOICE_CHANNEL = "SELECT_VOICE_CHANNEL"  # rpc
    GET_SELECTED_VOICE_CHANNEL = "GET_SELECTED_VOICE_CHANNEL"  # rpc or rpc.voice.read
    SELECT_TEXT_CHANNEL = "SELECT_TEXT_CHANNEL"  # rpc
    GET_VOICE_SETTINGS = "GET_VOICE_SETTINGS"  # rpc or rpc.voice.read
    SET_VOICE_SETTINGS = "SET_VOICE_SETTINGS"  # rpc or rpc.voice.write
    SET_VOICE_SETTINGS_2 = "SET_VOICE_SETTINGS_2"  # rpc.local
    SET_ACTIVITY = "SET_ACTIVITY"  # rpc, rpc.activities.write, or rpc.local
    SEND_ACTIVITY_JOIN_INVITE = "SEND_ACTIVITY_JOIN_INVITE"  # rpc or rpc.local
    CLOSE_ACTIVITY_JOIN_REQUEST = "CLOSE_ACTIVITY_JOIN_REQUEST"  # rpc or rpc.local
    ACTIVITY_INVITE_USER = "ACTIVITY_INVITE_USER"  # rpc or rpc.local
    ACCEPT_ACTIVITY_INVITE = "ACCEPT_ACTIVITY_INVITE"  # rpc or rpc.local
    OPEN_INVITE_DIALOG = "OPEN_INVITE_DIALOG"  # rpc, rpc.local, or rpc.authenticated
    OPEN_SHARE_MOMENT_DIALOG = "OPEN_SHARE_MOMENT_DIALOG"  # rpc.authenticated
    SHARE_INTERACTION = "SHARE_INTERACTION"  # rpc.authenticated or rpc.local
    INITIATE_IMAGE_UPLOAD = (
        "INITIATE_IMAGE_UPLOAD"  # rpc, rpc.local, or rpc.authenticated
    )
    SHARE_LINK = "SHARE_LINK"  # rpc.authenticated
    OPEN_MESSAGE = "OPEN_MESSAGE"  # rpc.local
    SET_CERTIFIED_DEVICES = "SET_CERTIFIED_DEVICES"  # rpc or rpc.local
    GET_IMAGE = "GET_IMAGE"  # rpc.local
    SET_OVERLAY_LOCKED = "SET_OVERLAY_LOCKED"  # rpc.local
    OPEN_OVERLAY_ACTIVITY_INVITE = "OPEN_OVERLAY_ACTIVITY_INVITE"  # rpc.local
    OPEN_OVERLAY_GUILD_INVITE = "OPEN_OVERLAY_GUILD_INVITE"  # rpc.local
    OPEN_OVERLAY_VOICE_SETTINGS = "OPEN_OVERLAY_VOICE_SETTINGS"  # rpc.local
    VALIDATE_APPLICATION = "VALIDATE_APPLICATION"  # rpc.local
    GET_ENTITLEMENT_TICKET = "GET_ENTITLEMENT_TICKET"  # rpc.local
    GET_APPLICATION_TICKET = "GET_APPLICATION_TICKET"  # rpc.local
    START_PURCHASE = "START_PURCHASE"  # rpc.authenticated or rpc.local
    START_PREMIUM_PURCHASE = "START_PREMIUM_PURCHASE"  # rpc.authenticated or rpc.local
    GET_SKUS = "GET_SKUS"  # rpc.authenticated or rpc.local
    GET_ENTITLEMENTS = "GET_ENTITLEMENTS"  # rpc.authenticated or rpc.local
    GET_SKUS_EMBEDDED = "GET_SKUS_EMBEDDED"  # rpc.authenticated or rpc.local
    GET_ENTITLEMENTS_EMBEDDED = (
        "GET_ENTITLEMENTS_EMBEDDED"  # rpc.authenticated or rpc.local
    )
    USER_SETTINGS_GET_LOCALE = "USER_SETTINGS_GET_LOCALE"  # identify
    OPEN_EXTERNAL_LINK = "OPEN_EXTERNAL_LINK"  # rpc.authenticated or rpc.embedded_app
    GET_SOUNDBOARD_SOUNDS = "GET_SOUNDBOARD_SOUNDS"  # rpc or rpc.local
    PLAY_SOUNDBOARD_SOUND = "PLAY_SOUNDBOARD_SOUND"  # rpc and rpc.voice.write
    TOGGLE_VIDEO = "TOGGLE_VIDEO"  # rpc and rpc.video.write
    TOGGLE_SCREENSHARE = "TOGGLE_SCREENSHARE"  # rpc and rpc.screenshare.write
    GET_ACTIVITY_INSTANCE_CONNECTED_PARTICIPANTS = (
        "GET_ACTIVITY_INSTANCE_CONNECTED_PARTICIPANTS"  # rpc.authenticated
    )
    GET_PROVIDER_ACCESS_TOKEN = "GET_PROVIDER_ACCESS_TOKEN"  # rpc.authenticated
    MAYBE_GET_PROVIDER_ACCESS_TOKEN = (
        "MAYBE_GET_PROVIDER_ACCESS_TOKEN"  # rpc.authenticated
    )
    NAVIGATE_TO_CONNECTIONS = "NAVIGATE_TO_CONNECTIONS"  # rpc.authenticated
    INVITE_USER_EMBEDDED = "INVITE_USER_EMBEDDED"  # relationships.read
    REQUEST_PROXY_TICKET_REFRESH = "REQUEST_PROXY_TICKET_REFRESH"  # rpc.authenticated
    GET_QUEST_ENROLLMENT_STATUS = "GET_QUEST_ENROLLMENT_STATUS"  # identify
    QUEST_START_TIMER = "QUEST_START_TIMER"  # identify


class SendableRPCCommand(StrEnum):
    GET_GUILD = "GET_GUILD"  # rpc
    GET_GUILDS = "GET_GUILDS"  # rpc
    GET_CHANNEL = "GET_CHANNEL"  # rpc, guilds, or guilds.channels.read
    GET_CHANNELS = "GET_CHANNELS"  # rpc
    GET_CHANNEL_PERMISSIONS = (
        "GET_CHANNEL_PERMISSIONS"  # guilds.members.read or guilds.channels.read
    )
    CREATE_CHANNEL_INVITE = "CREATE_CHANNEL_INVITE"  # rpc
    GET_RELATIONSHIPS = "GET_RELATIONSHIPS"  # relationships.read
    GET_USER = "GET_USER"  # rpc.local or rpc.embedded_app
    SET_USER_VOICE_SETTINGS = "SET_USER_VOICE_SETTINGS"  # rpc or rpc.voice.write
    SET_USER_VOICE_SETTINGS_2 = "SET_USER_VOICE_SETTINGS_2"  # rpc.local
    PUSH_TO_TALK = "PUSH_TO_TALK"  # rpc and rpc.voice.write
    SELECT_VOICE_CHANNEL = "SELECT_VOICE_CHANNEL"  # rpc
    GET_SELECTED_VOICE_CHANNEL = "GET_SELECTED_VOICE_CHANNEL"  # rpc or rpc.voice.read
    SELECT_TEXT_CHANNEL = "SELECT_TEXT_CHANNEL"  # rpc
    GET_VOICE_SETTINGS = "GET_VOICE_SETTINGS"  # rpc or rpc.voice.read
    SET_VOICE_SETTINGS = "SET_VOICE_SETTINGS"  # rpc or rpc.voice.write
    SET_VOICE_SETTINGS_2 = "SET_VOICE_SETTINGS_2"  # rpc.local
    SET_ACTIVITY = "SET_ACTIVITY"  # rpc, rpc.activities.write, or rpc.local
    SEND_ACTIVITY_JOIN_INVITE = "SEND_ACTIVITY_JOIN_INVITE"  # rpc or rpc.local
    CLOSE_ACTIVITY_JOIN_REQUEST = "CLOSE_ACTIVITY_JOIN_REQUEST"  # rpc or rpc.local
    ACTIVITY_INVITE_USER = "ACTIVITY_INVITE_USER"  # rpc or rpc.local
    ACCEPT_ACTIVITY_INVITE = "ACCEPT_ACTIVITY_INVITE"  # rpc or rpc.local
    OPEN_INVITE_DIALOG = "OPEN_INVITE_DIALOG"  # rpc, rpc.local, or rpc.authenticated
    OPEN_SHARE_MOMENT_DIALOG = "OPEN_SHARE_MOMENT_DIALOG"  # rpc.authenticated
    SHARE_INTERACTION = "SHARE_INTERACTION"  # rpc.authenticated or rpc.local
    INITIATE_IMAGE_UPLOAD = (
        "INITIATE_IMAGE_UPLOAD"  # rpc, rpc.local, or rpc.authenticated
    )
    SHARE_LINK = "SHARE_LINK"  # rpc.authenticated
    OPEN_MESSAGE = "OPEN_MESSAGE"  # rpc.local
    SET_CERTIFIED_DEVICES = "SET_CERTIFIED_DEVICES"  # rpc or rpc.local
    GET_IMAGE = "GET_IMAGE"  # rpc.local
    SET_OVERLAY_LOCKED = "SET_OVERLAY_LOCKED"  # rpc.local
    OPEN_OVERLAY_ACTIVITY_INVITE = "OPEN_OVERLAY_ACTIVITY_INVITE"  # rpc.local
    OPEN_OVERLAY_GUILD_INVITE = "OPEN_OVERLAY_GUILD_INVITE"  # rpc.local
    OPEN_OVERLAY_VOICE_SETTINGS = "OPEN_OVERLAY_VOICE_SETTINGS"  # rpc.local
    VALIDATE_APPLICATION = "VALIDATE_APPLICATION"  # rpc.local
    GET_ENTITLEMENT_TICKET = "GET_ENTITLEMENT_TICKET"  # rpc.local
    GET_APPLICATION_TICKET = "GET_APPLICATION_TICKET"  # rpc.local
    START_PURCHASE = "START_PURCHASE"  # rpc.authenticated or rpc.local
    START_PREMIUM_PURCHASE = "START_PREMIUM_PURCHASE"  # rpc.authenticated or rpc.local
    GET_SKUS = "GET_SKUS"  # rpc.authenticated or rpc.local
    GET_ENTITLEMENTS = "GET_ENTITLEMENTS"  # rpc.authenticated or rpc.local
    GET_SKUS_EMBEDDED = "GET_SKUS_EMBEDDED"  # rpc.authenticated or rpc.local
    GET_ENTITLEMENTS_EMBEDDED = (
        "GET_ENTITLEMENTS_EMBEDDED"  # rpc.authenticated or rpc.local
    )
    USER_SETTINGS_GET_LOCALE = "USER_SETTINGS_GET_LOCALE"  # identify
    OPEN_EXTERNAL_LINK = "OPEN_EXTERNAL_LINK"  # rpc.authenticated or rpc.embedded_app
    GET_SOUNDBOARD_SOUNDS = "GET_SOUNDBOARD_SOUNDS"  # rpc or rpc.local
    PLAY_SOUNDBOARD_SOUND = "PLAY_SOUNDBOARD_SOUND"  # rpc and rpc.voice.write
    TOGGLE_VIDEO = "TOGGLE_VIDEO"  # rpc and rpc.video.write
    TOGGLE_SCREENSHARE = "TOGGLE_SCREENSHARE"  # rpc and rpc.screenshare.write
    GET_ACTIVITY_INSTANCE_CONNECTED_PARTICIPANTS = (
        "GET_ACTIVITY_INSTANCE_CONNECTED_PARTICIPANTS"  # rpc.authenticated
    )
    GET_PROVIDER_ACCESS_TOKEN = "GET_PROVIDER_ACCESS_TOKEN"  # rpc.authenticated
    MAYBE_GET_PROVIDER_ACCESS_TOKEN = (
        "MAYBE_GET_PROVIDER_ACCESS_TOKEN"  # rpc.authenticated
    )
    NAVIGATE_TO_CONNECTIONS = "NAVIGATE_TO_CONNECTIONS"  # rpc.authenticated
    INVITE_USER_EMBEDDED = "INVITE_USER_EMBEDDED"  # relationships.read
    REQUEST_PROXY_TICKET_REFRESH = "REQUEST_PROXY_TICKET_REFRESH"  # rpc.authenticated
    GET_QUEST_ENROLLMENT_STATUS = "GET_QUEST_ENROLLMENT_STATUS"  # identify
    QUEST_START_TIMER = "QUEST_START_TIMER"  # identify


class ReceivedRPCCommand(StrEnum):
    DISPATCH = "DISPATCH"  # (no scope; server -> client only)


class InternalRPCCommand(StrEnum):
    DISPATCH = "DISPATCH"  # (no scope; server -> client only)
    AUTHORIZE = "AUTHORIZE"  # (no scope; used to obtain one)
    AUTHENTICATE = "AUTHENTICATE"  # (no scope; used to obtain one)
    SUBSCRIBE = "SUBSCRIBE"  # (no scope; depends on the event)
    UNSUBSCRIBE = "UNSUBSCRIBE"  # (no scope; depends on the event)


class VoiceSettingsModeType(StrEnum):
    PUSH_TO_TALK = "PUSH_TO_TALK"
    VOICE_ACTIVITY = "VOICE_ACTIVITY"


class ShortcutKeyComboType(IntEnum):
    KEYBOARD_KEY = 0
    MOUSE_BUTTON = 1
    KEYBOARD_MODIFIER_KEY = 2
    GAMEPAD_BUTTON = 3


class ActivityType(IntEnum):
    PLAYING = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5
    HANGING = 6


class StatusDisplayType(IntEnum):
    NAME = 0
    STATE = 1
    DETAILS = 2


class ActivityPlatformType(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    DESKTOP = "desktop"
    XBOX = "xbox"
    SAMSUNG = "samsung"
    IOS = "ios"
    ANDROID = "android"
    EMBEDDED = "embedded"
    PS4 = "ps4"
    PS5 = "ps5"
    META_QUEST = "meta_quest"


class ActivityHangStatusType(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    CHILLING = "chilling"
    GAMING = "gaming"
    FOCUSING = "focusing"
    BRB = "brb"
    WATCHING = "watching"
    CUSTOM = "custom"


class ActivityActionType(IntEnum):
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    WATCH = 4
    JOIN_REQUEST = 5


class CustomStatusLabelType(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    LISTEN = "listen"
    WATCH = "watch"
    PLAY = "play"
    QUESTION = "question"
    THINK = "think"
    LOVE = "love"
    EXCITED = "excited"
    RECOMMEND = "recommend"
