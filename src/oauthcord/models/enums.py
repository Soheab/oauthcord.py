from enum import Enum, IntEnum, StrEnum
from typing import Literal, overload

__all__ = (
    "ActivityLinkType",
    "ApplicationCommandHandlerType",
    "ApplicationCommandOptionType",
    "ApplicationCommandPermissionType",
    "ApplicationCommandType",
    "ApplicationSKUDistributor",
    "ApplicationType",
    "ChannelType",
    "CollectibleNameplatePalette",
    "DisplayNameEffect",
    "DisplayNameFont",
    "EmbedType",
    "EmbeddedActivityLabelType",
    "EmbeddedActivityOrientationLockStateType",
    "EmbeddedActivityPlatformType",
    "EmbeddedActivityReleasePhase",
    "EmbeddedActivitySurface",
    "EntitlementFulfillmentStatus",
    "EntitlementSourceType",
    "EntitlementType",
    "ForumLayoutType",
    "GiftStyle",
    "IntegrationInstallType",
    "IntegrationType",
    "InteractionContextType",
    "InviteTargetType",
    "InviteTargetUsersJobStatus",
    "InviteType",
    "Locale",
    "PermissionOverwriteType",
    "PremiumType",
    "RelationshipType",
    "SafetyWarningType",
    "Scope",
    "Service",
    "SortOrderType",
    "VideoQualityMode",
    "Visibility",
)


# SOURCE: https://docs.discord.food/topics/oauth2#oauth2-scopes
class Scope(StrEnum):
    # OAuth2 Scopes
    # These are all the OAuth2 scopes that Discord supports.
    # Some scopes require approval from Discord to use.
    # Requesting them from a user without approval from Discord will lead to unexpected error behavior in the OAuth2 flow.
    # bot and guilds.join require you to have a bot account linked to your application.
    # In order to add a user to a guild, your bot has to already belong to that guild.

    # Allows sending activity invites (Public: No)
    # ACTIVITIES_INVITES_WRITE = "activities.invites.write"
    # Allows retrieving user presence and activity data (Public: No)
    # ACTIVITIES_READ = "activities.read"
    # Allows updating user presence and creating headless sessions (Public: No)
    # ACTIVITIES_WRITE = "activities.write"
    # Allows reading branch and build data for the user's applications (Public: Yes)
    """Enumeration of Discord API values used by this wrapper."""

    APPLICATIONS_BUILDS_READ = "applications.builds.read"
    # Allows uploading builds to the user's applications (Public: No)
    # APPLICATIONS_BUILDS_UPLOAD = "applications.builds.upload"
    # Allows using commands in a guild/user context (Public: Yes)
    APPLICATIONS_COMMANDS = "applications.commands"
    # Allows updating the application's own command permissions in guilds the user has permissions in (Public: Yes)
    APPLICATIONS_COMMANDS_PERMISSIONS_UPDATE = (
        "applications.commands.permissions.update"
    )
    # Allows your app to update its own commands (Public: Yes)
    APPLICATIONS_COMMANDS_UPDATE = "applications.commands.update"
    # Allows managing entitlements for the user's applications (Public: Yes)
    APPLICATIONS_ENTITLEMENTS = "applications.entitlements"
    # Allows managing store data (SKUs, store listings, achievements, etc.) for the user's applications (Public: Yes)
    APPLICATIONS_STORE_UPDATE = "applications.store.update"
    # Allows managing application identities (Public: No)
    # APPLICATION_IDENTITY_WRITE = "application_identities.write"
    # Allows retrieving a user's connected accounts, both public and private (Public: Yes)
    CONNECTIONS = "connections"
    # Allows reading information about the user's DMs and group DMs (Public: No)
    DM_CHANNELS_READ = "dm_channels.read"
    # Allows reading messages from the user's DMs and group DMs (Public: No)
    # DM_CHANNELS_MESSAGES_READ = "dm_channels.messages.read"
    # Allows sending messages to the user's DMs (Public: No)
    # DM_CHANNELS_MESSAGES_WRITE = "dm_channels.messages.write"
    # Allows retrieving a user's email address (Public: Yes)
    EMAIL = "email"
    # Allows connecting to the gateway on behalf of the user (Public: No)
    # GATEWAY_CONNECT = "gateway.connect"
    # Allows adding users to managed group DMs (Public: Yes)
    GDM_JOIN = "gdm.join"
    # Allows retrieving the user's guilds (Public: Yes)
    GUILDS = "guilds"
    # Allows reading the channels in a user's guilds (Public: No)
    # GUILDS_CHANNELS_READ = "guilds.channels.read"
    # Allows joining users to a guild (Public: Yes)
    GUILDS_JOIN = "guilds.join"
    # Allows retrieving a user's member information in a guild (Public: Yes)
    GUILDS_MEMBERS_READ = "guilds.members.read"
    # Allows creating and managing lobbies (Public: No)
    LOBBIES_WRITE = "lobbies.write"
    # Allows retrieving the current user (Public: Yes)
    IDENTIFY = "identify"
    # When using RPC, allows reading messages from all client channels (otherwise restricted to application-managed group DMs) (Public: Yes)
    MESSAGES_READ = "messages.read"
    # Allows retrieving basic user information and includes an ID token in the token exchange (Public: Yes)
    OPENID = "openid"
    # Allows retrieving the user's country code (Public: No)
    # PAYMENT_SOURCES_COUNTRY_CODE = "payment_sources.country_code"
    # Allows retrieving user presence (Public: No)
    # PRESENCES_READ = "presences.read"
    # Allows updating user presence (Public: No)
    # PRESENCES_WRITE = "presences.write"
    # Allows retrieving a user's relationships (Public: Yes)
    RELATIONSHIPS_READ = "relationships.read"
    # Allows managing a user's relationships (Public: No)
    # RELATIONSHIPS_WRITE = "relationships.write"
    # Allows updating a user's connection and application-specific metadata (Public: Yes)
    ROLE_CONNECTIONS_WRITE = "role_connections.write"
    # When using RPC, allows controlling the local Discord client; also encompasses all of the below RPC scopes in the majority of scenarios (Public: No)
    # RPC = "rpc"
    # When using RPC, allows updating a user's activity (Public: Yes)
    RPC_ACTIVITIES_WRITE = "rpc.activities.write"
    # Allows accessing the REST API on behalf of the user (Public: No)
    # RPC_API = "rpc.api"
    # When using RPC, allows you to receive notifications pushed out to the user (Public: Yes)
    RPC_NOTIFICATIONS_READ = "rpc.notifications.read"
    # When using RPC, allows reading a user's screenshare status (Public: Yes)
    RPC_SCREENSHARE_READ = "rpc.screenshare.read"
    # When using RPC, allows updating a user's screenshare settings (Public: Yes)
    RPC_SCREENSHARE_WRITE = "rpc.screenshare.write"
    # When using RPC, allows reading a user's video status (Public: Yes)
    RPC_VIDEO_READ = "rpc.video.read"
    # When using RPC, allows updating a user's video settings (Public: Yes)
    RPC_VIDEO_WRITE = "rpc.video.write"
    # When using RPC, allows reading a user's voice settings and listening for voice events (Public: Yes)
    RPC_VOICE_READ = "rpc.voice.read"
    # When using RPC, allows updating a user's voice settings (Public: Yes)
    RPC_VOICE_WRITE = "rpc.voice.write"
    # Allows connecting to voice on the user's behalf and seeing all voice members in a guild (Public: No)
    # VOICE = "voice"
    # Creates an application-owned webhook in a user-selected channel and returns it in the token exchange (Public: Yes)
    WEBHOOK_INCOMING = "webhook.incoming"
    # Includes: activities.invites.write, activities.read, activities.write, application_identities.write, gateway.connect, identify, relationships.read, relationships.write (Public: No)
    SDK_SOCIAL_LAYER_PRESENCE = "sdk.social_layer_presence"
    # Includes everything in sdk.social_layer_presence, plus dm_channels.read, dm_channels.messages.read, dm_channels.messages.write, guilds, guilds.channels.read, lobbies.write (Public: No)
    SDK_SOCIAL_LAYER = "sdk.social_layer"

    @classmethod
    def from_list(cls, scopes: list[str], /) -> list[Scope]:
        """Create this object from a serialized payload."""
        return [cls(scope) for scope in scopes]

    @classmethod
    def from_str(cls, scope: str, /) -> list[Scope]:
        """Create this object from a serialized payload."""
        return cls.from_list([scope])

    @classmethod
    def to_str(cls, scopes: list[Scope], /) -> str:
        """Convert this object into a serialized or display-friendly representation."""
        return " ".join(scope.value for scope in scopes)


class Locale(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    INDONESIAN = "id"
    DANISH = "da"
    GERMAN = "de"
    ENGLISH_GB = "en-GB"
    ENGLISH_US = "en-US"
    SPANISH = "es-ES"
    SPANISH_LATAM = "es-419"
    FRENCH = "fr"
    CROATIAN = "hr"
    ITALIAN = "it"
    LITHUANIAN = "lt"
    HUNGARIAN = "hu"
    DUTCH = "nl"
    NORWEGIAN = "no"
    POLISH = "pl"
    PORTUGUESE_BR = "pt-BR"
    ROMANIAN = "ro"
    FINNISH = "fi"
    SWEDISH = "sv-SE"
    VIETNAMESE = "vi"
    TURKISH = "tr"
    CZECH = "cs"
    GREEK = "el"
    BULGARIAN = "bg"
    RUSSIAN = "ru"
    UKRAINIAN = "uk"
    HINDI = "hi"
    THAI = "th"
    CHINESE_CN = "zh-CN"
    JAPANESE = "ja"
    CHINESE_TW = "zh-TW"
    KOREAN = "ko"

    def get_native_name(self) -> str:
        """Return a derived value from the current object."""
        locale_to_native = {
            "id": "Bahasa Indonesia",
            "da": "Dansk",
            "de": "Deutsch",
            "en-GB": "English, UK",
            "en-US": "English, US",
            "es-ES": "Español",
            "es-419": "Español, LATAM",
            "fr": "Français",
            "hr": "Hrvatski",
            "it": "Italiano",
            "lt": "Lietuviškai",
            "hu": "Magyar",
            "nl": "Nederlands",
            "no": "Norsk",
            "pl": "Polski",
            "pt-BR": "Português do Brasil",
            "ro": "Română",
            "fi": "Suomi",
            "sv-SE": "Svenska",
            "vi": "Tiếng Việt",
            "tr": "Türkçe",
            "cs": "Čeština",
            "el": "Ελληνικά",
            "bg": "български",
            "ru": "Русский",
            "uk": "Українська",
            "hi": "हिन्दी",
            "th": "ไทย",
            "zh-CN": "中文",
            "ja": "日本語",
            "zh-TW": "繁體中文",
            "ko": "한국어",
        }
        return locale_to_native.get(self.value, self.value)


class PremiumType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
    NITRO_BASIC = 3


class DisplayNameFont(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    default = 11
    bangers = 1
    bio_rhyme = 2
    cherry_bomb = 3
    chicle = 4
    compagnon = 5
    museo_moderno = 6
    neo_castel = 7
    pixelify = 8
    ribes = 9
    sinistre = 10
    zilla_slab = 12


class DisplayNameEffect(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    solid = 1
    gradient = 2
    neon = 3
    toon = 4
    pop = 5
    glow = 6


class CollectibleNameplatePalette(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    CRIMSON = "crimson"
    BERRY = "berry"
    SKY = "sky"
    TEAL = "teal"
    FOREST = "forest"
    BUBBLE_GUM = "bubble_gum"
    VIOLET = "violet"
    COBALT = "cobalt"
    CLOVER = "clover"
    LEMON = "lemon"
    WHITE = "white"


class Service(StrEnum):
    AMAZON_MUSIC = "amazon-music"
    BATTLENET = "battlenet"
    BUNGIE = "bungie"
    BLUESKY = "bluesky"
    CRUNCHYROLL = "crunchyroll"
    DOMAIN = "domain"
    EBAY = "ebay"
    EPICGAMES = "epicgames"
    FACEBOOK = "facebook"
    GITHUB = "github"
    INSTAGRAM = "instagram"
    LEAGUEOFLEGENDS = "leagueoflegends"
    MASTODON = "mastodon"
    PAYPAL = "paypal"
    PLAYSTATION = "playstation"
    REDDIT = "reddit"
    RIOTGAMES = "riotgames"
    ROBLOX = "roblox"
    SPOTIFY = "spotify"
    SKYPE = "skype"
    STEAM = "steam"
    TIKTOK = "tiktok"
    TWITCH = "twitch"
    TWITTER = "twitter"
    XBOX = "xbox"
    YOUTUBE = "youtube"


class Visibility(IntEnum):
    NONE = 0
    EVERYONE = 1


class IntegrationType(StrEnum):
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    DISCORD = "discord"
    GUILD_SUBSCRIPTION = "guild_subscription"


class ApplicationType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    DEPRECATED_GAME = 1
    MUSIC = 2
    TICKETED_EVENTS = 3
    CREATOR_MONETIZATION = 4
    GAME = 5


class ApplicationSKUDistributor(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    DISCORD = "discord"
    STEAM = "steam"
    TWITCH = "twitch"
    UPLAY = "uplay"
    BATTLENET = "battlenet"
    ORIGIN = "origin"
    GOG = "gog"
    EPIC = "epic"
    MICROSOFT = "microsoft"
    IGDB = "igdb"
    GLYPH = "glyph"
    GOOGLE_PLAY = "google_play"
    NVIDIA_GDN_APP = "nvidia_gdn_app"
    GOP = "gop"
    ROBLOX = "roblox"
    GDCO = "gdco"
    XBOX = "xbox"
    PLAYSTATION = "playstation"


class EmbeddedActivityPlatformType(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    WEB = "web"
    ANDROID = "android"
    IOS = "ios"


class EmbeddedActivityOrientationLockStateType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    UNLOCKED = 1
    PORTRAIT = 2
    LANDSCAPE = 3


class EmbeddedActivityLabelType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    NONE = 0
    NEW = 1
    UPDATED = 2


class EmbeddedActivityReleasePhase(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    IN_DEVELOPMENT = "in_development"
    ACTIVITIES_TEAM = "activities_team"
    EMPLOYEE_RELEASE = "employee_release"
    SOFT_LAUNCH = "soft_launch"
    SOFT_LAUNCH_MULTI_GEO = "soft_launch_multi_geo"
    GLOBAL_LAUNCH = "global_launch"


class EmbeddedActivitySurface(StrEnum):
    """Enumeration of Discord API values used by this wrapper."""

    VOICE_LAUNCHER = "voice_launcher"
    TEXT_LAUNCHER = "text_launcher"


class ActivityLinkType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    MANAGED_LINK = 0
    QUICK_LINK = 1


class EntitlementType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    PURCHASE = 1
    PREMIUM_SUBSCRIPTION = 2
    DEVELOPER_GIFT = 3
    TEST_MODE_PURCHASE = 4
    FREE_PURCHASE = 5
    USER_GIFT = 6
    PREMIUM_PURCHASE = 7
    APPLICATION_SUBSCRIPTION = 8
    FREE_STAFF_PURCHASE = 9
    QUEST_REWARD = 10
    FRACTIONAL_REDEMPTION = 11
    VIRTUAL_CURRENCY_REDEMPTION = 12
    GUILD_POWERUP = 13


class EntitlementFulfillmentStatus(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    UNKNOWN = 0
    FULFILLMENT_NOT_NEEDED = 1
    FULFILLMENT_NEEDED = 2
    FULFILLED = 3
    FULFILLMENT_FAILED = 4
    UNFULFILLMENT_NEEDED = 5
    UNFULFILLED = 6
    UNFULFILLMENT_FAILED = 7
    UNFULFILLMENT_NEEDED_MANUAL = 8


class EntitlementSourceType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    QUEST_REWARD = 1
    DEVELOPER_GIFT = 2
    INVOICE = 3
    REVERSE_TRIAL = 4
    USER_GIFT = 5
    GUILD_POWERUP = 6
    HOLIDAY_PROMOTION = 7
    FRACTIONAL_PREMIUM_GIVEBACK = 8
    SUBSCRIPTION = 9
    SUBSCRIPTION_MEMBER = 11


class GiftStyle(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    SNOWGLOBE = 1
    BOX = 2
    CUP = 3
    STANDARD_BOX = 4
    CAKE = 5
    CHEST = 6
    COFFEE = 7
    SEASONAL_STANDARD_BOX = 8
    SEASONAL_CAKE = 9
    SEASONAL_CHEST = 10
    SEASONAL_COFFEE = 11
    NITROWEEN_STANDARD = 12


class InviteType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    GUILD = 0
    GROUP_DM = 1
    FRIEND = 2


class InviteTargetType(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    STREAM = 1
    EMBEDDED_APPLICATION = 2
    ROLE_SUBSCRIPTIONS = 3
    CREATOR_PAGE = 4
    LOBBY = 5


class InviteTargetUsersJobStatus(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    UNSPECIFIED = 0
    PROCESSING = 1
    COMPLETED = 2
    FAILED = 3


class ApplicationCommandOptionType(IntEnum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10
    ATTACHMENT = 11


class ApplicationCommandHandlerType(IntEnum):
    APP_HANDLER = 1
    DISCORD_LAUNCH_ACTIVITY = 2
    APP_HANDLER_LAUNCH_ACTIVITY = 3


class ApplicationCommandType(IntEnum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3
    PRIMARY_ENTRY_POINT = 4


class ChannelType(IntEnum):
    # Documented channel types
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15
    GUILD_MEDIA = 16

    # Undocumented / internal channel types
    GUILD_STORE = 6
    GUILD_LFG = 7
    LFG_GROUP_DM = 8
    THREAD_ALPHA = 9
    LOBBY = 17
    EPHEMERAL_DM = 18


class VideoQualityMode(IntEnum):
    AUTO = 1
    FULL = 2


class ForumLayoutType(IntEnum):
    NOT_SET = 0
    LIST_VIEW = 1
    GALLERY_VIEW = 2


class SortOrderType(IntEnum):
    LATEST_ACTIVITY = 0
    CREATION_DATE = 1


class SafetyWarningType(IntEnum):
    STRANGER_DANGER = 1
    INAPPROPRIATE_CONVERSATION_TIER_1 = 2
    INAPPROPRIATE_CONVERSATION_TIER_2 = 3
    LIKELY_ATO = 4


class PermissionOverwriteType(IntEnum):
    ROLE = 0
    MEMBER = 1


class IntegrationInstallType(IntEnum):
    GUILD_INSTALL = 0
    USER_INSTALL = 1


class InteractionContextType(IntEnum):
    GUILD = 0
    BOT_DM = 1
    PRIVATE_CHANNEL = 2


class ApplicationCommandPermissionType(IntEnum):
    ROLE = 1
    USER = 2
    CHANNEL = 3


class EmbedType(StrEnum):
    AGE_VERIFICATION_SYSTEM_NOTIFICATION = "age_verification_system_notification"
    ARTICLE = "article"
    AUTO_MODERATION_MESSAGE = "auto_moderation_message"
    AUTO_MODERATION_NOTIFICATION = "auto_moderation_notification"
    GIFT = "gift"
    GIFV = "gifv"
    IMAGE = "image"
    LINK = "link"
    POLL_RESULT = "poll_result"
    POST_PREVIEW = "post_preview"
    RICH = "rich"
    SAFETY_POLICY_NOTICE = "safety_policy_notice"
    SAFETY_SYSTEM_NOTIFICATION = "safety_system_notification"
    VIDEO = "video"


class RelationshipType(IntEnum):
    NONE = 0
    FRIEND = 1
    BLOCKED = 2
    INCOMING_REQUEST = 3
    OUTGOING_REQUEST = 4
    IMPLICIT = 5
    SUGGESTION = 6


@overload
def to_enum[E: Enum](enum: type[E], value: Literal[None], /) -> None: ...


@overload
def to_enum[E: Enum](enum: type[E], value: str | int, /) -> E: ...


def to_enum[E: Enum](enum: type[E], value: str | int | None, /) -> E | None:
    if value is None:
        return None

    try:
        return enum(value)
    except ValueError:
        try:
            return enum[value]  # type: ignore
        except KeyError:
            raise ValueError(f"{value} is not a valid {enum.__name__}")
