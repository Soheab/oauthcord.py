from __future__ import annotations

from collections.abc import Sequence
from enum import Enum, IntEnum, StrEnum
from typing import ClassVar, Literal, Self, overload
from weakref import WeakValueDictionary

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
    "ContentRatingAgency",
    "DisplayNameEffect",
    "DisplayNameFont",
    "ESRBContentDescriptor",
    "ESRBContentRating",
    "EmbedType",
    "EmbeddedActivityLabelType",
    "EmbeddedActivityOrientationLockStateType",
    "EmbeddedActivityPlatformType",
    "EmbeddedActivityReleasePhase",
    "EmbeddedActivitySurface",
    "EntitlementFulfillmentStatus",
    "EntitlementSourceType",
    "EntitlementType",
    "ExternalSKUStrategyType",
    "ForumLayoutType",
    "GiftStyle",
    "GuildPowerupCategoryType",
    "IntegrationInstallType",
    "IntegrationType",
    "InteractionContextType",
    "InviteTargetType",
    "InviteTargetUsersJobStatus",
    "InviteType",
    "Locale",
    "OperatingSystem",
    "PEGIContentDescriptor",
    "PEGIContentRating",
    "PermissionOverwriteType",
    "PollLayoutType",
    "PremiumType",
    "QuestPlatformType",
    "RelationshipType",
    "SKUAccessType",
    "SKUFeature",
    "SKUGenre",
    "SKUProductLine",
    "SKUType",
    "SafetyWarningType",
    "Scope",
    "Service",
    "SortOrderType",
    "StoreListingIconType",
    "SubscriptionInterval",
    "SubscriptionPlanPurchaseType",
    "UnknownEnum",
    "VideoQualityMode",
    "Visibility",
)


class UnknownEnum:
    """A stand-in for an enum member that this library does not recognise.

    Discord may add new values to any of its enumerations at any time. Rather
    than raising an error, such a value is wrapped in this class so that
    parsing never fails. Instances mimic an :class:`enum.Enum` member closely:
    they expose :attr:`name` and :attr:`value`, compare equal to their raw
    value, and are hashable.

    Instances are cached per value, so wrapping the same value twice returns
    the same object for as long as one of them is still referenced. The cache
    holds only weak references, so members that are no longer used elsewhere
    are garbage collected rather than accumulating forever.

    If you encounter this for a scope that Discord (or userdoccers_) documents,
    please open an issue at https://github.com/Soheab/oauthcord.py/issues so it
    can be added to :class:`Scope`.

    .. _userdoccers: https://docs.discord.food/topics/oauth2#oauth2-scopes

    Attributes
    ----------
    name: :class:`str`
        The raw value as a string. Mirrors :attr:`enum.Enum.name`.
    value: :class:`str` | :class:`int`
        The raw value as returned by Discord, with its original type
        preserved so it round-trips back to the API unchanged.
    """

    __members__: ClassVar[WeakValueDictionary[str | int, Self]] = WeakValueDictionary()

    __slots__ = ("__value__", "__weakref__")

    __value__: str | int

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # Each subclass gets its own cache so members of different
        # enumerations with the same raw value do not collide.
        cls.__members__ = WeakValueDictionary()

    def __new__(cls, value: str | int, /) -> Self:
        try:
            return cls.__members__[value]
        except KeyError:
            pass

        self = super().__new__(cls)
        object.__setattr__(self, "__value__", value)
        cls.__members__[value] = self
        return self

    @classmethod
    def _missing_(cls, value: object, /) -> Self:
        return cls(value if isinstance(value, int) else str(value))

    @property
    def name(self) -> str:
        """:class:`str`: The raw value as a string. Mirrors :attr:`enum.Enum.name`."""
        return str(self.__value__)

    @property
    def value(self) -> str | int:
        """:class:`str` | :class:`int`: The raw value as returned by Discord."""
        return self.__value__

    def __setattr__(self, name: str, value: object, /) -> None:
        raise AttributeError(f"cannot reassign member attribute {name!r}")

    def __delattr__(self, name: str, /) -> None:
        raise AttributeError(f"cannot delete member attribute {name!r}")

    def __str__(self) -> str:
        return str(self.__value__)

    def __int__(self) -> int:
        if isinstance(self.__value__, int):
            return self.__value__
        raise TypeError(f"Cannot convert {self.__class__.__name__} to int")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.__value__}: {self.__value__!r}>"

    def __format__(self, format_spec: str, /) -> str:
        return format(self.__value__, format_spec)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__value__ == other.__value__
        elif isinstance(other, str | int):
            return self.__value__ == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__value__)

    def __reduce__(self) -> tuple[type[Self], tuple[str | int]]:
        return (self.__class__, (self.__value__,))


# SOURCE: https://docs.discord.food/topics/oauth2#oauth2-scopes
class Scope(StrEnum):
    """Enumeration of the OAuth2 scopes that Discord supports.

    Any scope not listed here is returned as an :class:`UnknownEnum` rather
    than raising an error.
    """

    # OAuth2 Scopes
    # These are all the OAuth2 scopes that Discord supports.
    # Some scopes require approval from Discord to use.
    # Requesting them from a user without approval from Discord
    # can lead to unexpected OAuth2 flow errors.
    # bot and guilds.join require you to have a bot account linked to your application.
    # In order to add a user to a guild, your bot has to already belong to that guild.

    # Allows sending activity invites (Public: No)
    # ACTIVITIES_INVITES_WRITE = "activities.invites.write"
    # Allows retrieving user presence and activity data (Public: No)
    # ACTIVITIES_READ = "activities.read"
    # Allows updating user presence and creating headless sessions (Public: No)
    # ACTIVITIES_WRITE = "activities.write"
    # Allows reading branch and build data for the user's applications (Public: Yes)
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
    # Allow retrieving the user's premium type (nitro) (Public: Yes)
    # This requires discord's approval / is only for approved partners.
    IDENTITY_PREMIUM = "identify.premium"
    # When using RPC, allows reading messages from all client channels.
    # Otherwise this is restricted to application-managed group DMs. (Public: Yes)
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
    # When using RPC, allows controlling the local Discord client.
    # This also encompasses most RPC scopes below. (Public: No)
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
    # Includes: activities.invites.write, activities.read, activities.write,
    # application_identities.write, gateway.connect, identify, relationships.read,
    # relationships.write. (Public: No)
    SDK_SOCIAL_LAYER_PRESENCE = "sdk.social_layer_presence"
    # Includes all sdk.social_layer_presence scopes plus:
    # dm_channels.read, dm_channels.messages.read, dm_channels.messages.write,
    # guilds, guilds.channels.read, and lobbies.write. (Public: No)
    SDK_SOCIAL_LAYER = "sdk.social_layer"

    @classmethod
    def from_list(
        cls, scopes: Sequence[str | Scope | UnknownEnum], /
    ) -> list[Scope | UnknownEnum]:
        """Create this object from a serialized payload."""
        final: list[Scope | UnknownEnum] = []
        for scope in scopes:
            if isinstance(scope, (Scope, UnknownEnum)):
                final.append(scope)
                continue

            try:
                final.append(cls(scope))
            except ValueError:
                final.append(UnknownEnum(scope))

        return final

    @classmethod
    def from_str(cls, scope: str, /) -> list[Scope | UnknownEnum]:
        """Create this object from a serialized payload."""
        return cls.from_list(list(scope.split(" ")))

    @classmethod
    def to_str(cls, scopes: Sequence[Scope | UnknownEnum], /) -> str:
        return "+".join(str(scope) for scope in scopes)

    def __str__(self) -> str:
        return self.value


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
    DEFAULT = 11
    BANGERS = 1  # deprecated
    BIO_RHYME = 2  # deprecated
    CHERRY_BOMB = 3
    CHICLE = 4
    COMPAGNON = 5  # deprecated
    MUSEO_MODERNO = 6
    NEO_CASTEL = 7
    PIXELIFY = 8
    RIBES = 9  # deprecated
    SINISTRE = 10
    ZILLA_SLAB = 12
    PLAYPEN_SANS = 13
    ORBITRON = 14
    NEW_ROCKER = 15
    KALAM = 16

    @property
    def display_name(self) -> str:
        """:class:`str`: Return the display name of the font.

        If none is available, returns a title-cased version of the enum name
        with underscores replaced by spaces.
        """
        font_to_display_name = {
            DisplayNameFont.DEFAULT: "gg Sans",
            DisplayNameFont.BANGERS: "Bangers",  # N/A
            DisplayNameFont.BIO_RHYME: "BioRhyme",  # N/A
            DisplayNameFont.CHERRY_BOMB: "Sakura",
            DisplayNameFont.CHICLE: "Jellybean",
            DisplayNameFont.COMPAGNON: "Compagnon",  # N/A
            DisplayNameFont.MUSEO_MODERNO: "Modern",
            DisplayNameFont.NEO_CASTEL: "Medieval",
            DisplayNameFont.PIXELIFY: "8Bit",
            DisplayNameFont.RIBES: "Ribes",  # N/A
            DisplayNameFont.SINISTRE: "Vampyre",
            DisplayNameFont.ZILLA_SLAB: "Tempo",
            DisplayNameFont.PLAYPEN_SANS: "Monkey Bars",
            DisplayNameFont.ORBITRON: "Mainframe",
            DisplayNameFont.NEW_ROCKER: "Headbang",
            DisplayNameFont.KALAM: "Journal",
        }
        return font_to_display_name.get(
            self, self.name.lower().replace("_", " ").title()
        )

    @property
    def url(self) -> str | None:
        """:class:`str` | None: Return the URL to the font's source, if available. Otherwise, returns :data:`None`."""
        font_to_url = {
            DisplayNameFont.BANGERS: "https://fonts.google.com/specimen/Bangers",
            DisplayNameFont.BIO_RHYME: "https://fonts.google.com/specimen/BioRhyme",
            DisplayNameFont.CHERRY_BOMB: "https://fonts.google.com/specimen/Cherry+Bomb+One",
            DisplayNameFont.CHICLE: "https://fonts.google.com/specimen/Chicle",
            DisplayNameFont.COMPAGNON: "https://velvetyne.fr/fonts/compagnon/",
            DisplayNameFont.MUSEO_MODERNO: "https://fonts.google.com/specimen/MuseoModerno",
            DisplayNameFont.NEO_CASTEL: "https://maxlilllo.gumroad.com/l/neo-castel",
            DisplayNameFont.PIXELIFY: "https://fonts.google.com/specimen/Pixelify+Sans",
            DisplayNameFont.RIBES: "https://www.collletttivo.it/typefaces/ribes",
            DisplayNameFont.SINISTRE: "https://www.collletttivo.it/typefaces/sinistre",
            DisplayNameFont.ZILLA_SLAB: "https://fonts.google.com/specimen/Zilla+Slab",
            DisplayNameFont.PLAYPEN_SANS: "https://fonts.google.com/specimen/Playpen+Sans",
            DisplayNameFont.ORBITRON: "https://fonts.google.com/specimen/Orbitron",
            DisplayNameFont.NEW_ROCKER: "https://fonts.google.com/specimen/New+Rocker",
            DisplayNameFont.KALAM: "https://fonts.google.com/specimen/Kalam?preview.script=Latn",
        }
        return font_to_url.get(self)


class DisplayNameEffect(IntEnum):
    """Enumeration of Discord API values used by this wrapper."""

    SOLID = 1
    """Displays the first color provided"""
    GRADIENT = 2
    """Two color gradient"""
    NEON = 3
    """Glow around the name"""
    TOON = 4
    """Subtle vertical gradient and stroke"""
    POP = 5
    """Colored dropshadow"""
    GLOW = 6
    """Falls back to gradient"""
    PRISM = 7
    """Scrolling five color gradient"""
    GUMMY = 8
    """Four color pattern, letters squash and stretch"""
    TEST_1 = 1001
    """Falls back to solid"""
    TEST_2 = 1002
    """Falls back to solid"""
    TEST_3 = 1003
    """Falls back to solid"""
    TEST_4 = 1004
    """Falls back to solid"""

    @property
    def min_colors(self) -> int:
        """:class:`int`: The minimum number of colors this effect requires."""
        return 1

    @property
    def max_colors(self) -> int:
        """:class:`int`: The maximum number of colors this effect supports."""
        single_color_effects = {
            DisplayNameEffect.SOLID,
            DisplayNameEffect.NEON,
            DisplayNameEffect.TOON,
            DisplayNameEffect.POP,
            DisplayNameEffect.TEST_1,
            DisplayNameEffect.TEST_2,
            DisplayNameEffect.TEST_3,
            DisplayNameEffect.TEST_4,
        }
        return 1 if self in single_color_effects else 5


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


class SKUType(IntEnum):
    DURABLE_PRIMARY = 1
    DURABLE = 2
    CONSUMABLE = 3
    BUNDLE = 4
    SUBSCRIPTION = 5
    SUBSCRIPTION_GROUP = 6


class SKUProductLine(IntEnum):
    PREMIUM = 1
    PREMIUM_GUILD = 2
    ACTIVITY_IAP = 3
    GUILD_ROLE = 4
    GUILD_PRODUCT = 5
    APPLICATION = 6
    COLLECTIBLES = 7
    QUEST_IN_GAME_REWARD = 9
    QUEST_REWARD_CODE = 10
    FRACTIONAL_PREMIUM = 11
    VIRTUAL_CURRENCY = 12
    GUILD_POWERUP = 13
    SOCIAL_LAYER_GAME_ITEM = 14


class SKUAccessType(IntEnum):
    FULL = 1
    EARLY_ACCESS = 2
    VIP_ACCESS = 3


class SKUFeature(IntEnum):
    SINGLE_PLAYER = 1
    ONLINE_MULTIPLAYER = 2
    LOCAL_MULTIPLAYER = 3
    PVP = 4
    LOCAL_COOP = 5
    CROSS_PLATFORM = 6
    RICH_PRESENCE = 7
    DISCORD_GAME_INVITES = 8
    SPECTATOR_MODE = 9
    CONTROLLER_SUPPORT = 10
    CLOUD_SAVES = 11
    ONLINE_COOP = 12
    SECURE_NETWORKING = 13


class SKUGenre(IntEnum):
    ACTION = 1
    ACTION_RPG = 2
    BRAWLER = 3
    HACK_AND_SLASH = 4
    PLATFORMER = 5
    STEALTH = 6
    SURVIVAL = 7
    ADVENTURE = 8
    ACTION_ADVENTURE = 9
    METROIDVANIA = 10
    OPEN_WORLD = 11
    PSYCHOLOGICAL_HORROR = 12
    SANDBOX = 13
    SURVIVAL_HORROR = 14
    VISUAL_NOVEL = 15
    DRIVING_RACING = 16
    VEHICULAR_COMBAT = 17
    MASSIVELY_MULTIPLAYER = 18
    MMORPG = 19
    ROLE_PLAYING = 20
    DUNGEON_CRAWLER = 21
    ROGUELIKE = 22
    SHOOTER = 23
    LIGHT_GUN = 24
    SHOOT_EM_UP = 25
    FPS = 26
    DUAL_JOYSTICK_SHOOTER = 27
    SIMULATION = 28
    FLIGHT_SIMULATOR = 29
    TRAIN_SIMULATOR = 30
    LIFE_SIMULATOR = 31
    FISHING = 32
    SPORTS = 33
    BASEBALL = 34
    BASKETBALL = 35
    BILLIARDS = 36
    BOWLING = 37
    BOXING = 38
    FOOTBALL = 39
    GOLF = 40
    HOCKEY = 41
    SKATEBOARDING_SKATING = 42
    SNOWBOARDING_SKIING = 43
    SOCCER = 44
    TRACK_FIELD = 45
    SURFING_WAKEBOARDING = 46
    WRESTLING = 47
    STRATEGY = 48
    FOUR_X = 49
    ARTILLERY = 50
    RTS = 51
    TOWER_DEFENSE = 52
    TURN_BASED_STRATEGY = 53
    WARGAME = 54
    MOBA = 55
    FIGHTING = 56
    PUZZLE = 57
    CARD_GAME = 58
    EDUCATION = 59
    FITNESS = 60
    GAMBLING = 61
    MUSIC_RHYTHM = 62
    PARTY_MINI_GAME = 63
    PINBALL = 64
    TRIVIA_BOARD_GAME = 65
    TACTICAL = 66
    INDIE = 67
    ARCADE = 68
    POINT_AND_CLICK = 69


class ContentRatingAgency(IntEnum):
    ESRB = 1
    PEGI = 2

    @property
    def content_rating_type(self) -> type[ESRBContentRating | PEGIContentRating]:
        """Return a derived value from the current object."""
        if self is ContentRatingAgency.ESRB:
            return ESRBContentRating
        elif self is ContentRatingAgency.PEGI:
            return PEGIContentRating
        else:
            raise ValueError(f"Invalid content rating agency: {self}")

    @property
    def content_descriptor_type(
        self,
    ) -> type[ESRBContentDescriptor | PEGIContentDescriptor]:
        """Return a derived value from the current object."""
        if self is ContentRatingAgency.ESRB:
            return ESRBContentDescriptor
        elif self is ContentRatingAgency.PEGI:
            return PEGIContentDescriptor
        else:
            raise ValueError(f"Invalid content rating agency: {self}")


class ESRBContentRating(IntEnum):
    EVERYONE = 1
    EVERYONE_TEN_PLUS = 2
    TEEN = 3
    MATURE = 4
    ADULTS_ONLY = 5
    RATING_PENDING = 6


class PEGIContentRating(IntEnum):
    THREE = 1
    SEVEN = 2
    TWELVE = 3
    SIXTEEN = 4
    EIGHTEEN = 5


class ESRBContentDescriptor(IntEnum):
    ALCOHOL_REFERENCE = 1
    ANIMATED_BLOOD = 2
    BLOOD = 3
    BLOOD_AND_GORE = 4
    CARTOON_VIOLENCE = 5
    COMIC_MISCHIEF = 6
    CRUDE_HUMOR = 7
    DRUG_REFERENCE = 8
    FANTASY_VIOLENCE = 9
    INTENSE_VIOLENCE = 10
    LANGUAGE = 11
    LYRICS = 12
    MATURE_HUMOR = 13
    NUDITY = 14
    PARTIAL_NUDITY = 15
    REAL_GAMBLING = 16
    SEXUAL_CONTENT = 17
    SEXUAL_THEMES = 18
    SEXUAL_VIOLENCE = 19
    SIMULATED_GAMBLING = 20
    STRONG_LANGUAGE = 21
    STRONG_LYRICS = 22
    STRONG_SEXUAL_CONTENT = 23
    SUGGESTIVE_THEMES = 24
    TOBACCO_REFERENCE = 25
    USE_OF_ALCOHOL = 26
    USE_OF_DRUGS = 27
    USE_OF_TOBACCO = 28
    VIOLENCE = 29
    VIOLENT_REFERENCES = 30
    IN_GAME_PURCHASES = 31
    USERS_INTERACT = 32
    SHARES_LOCATION = 33
    UNRESTRICTED_INTERNET = 34
    MILD_BLOOD = 35
    MILD_CARTOON_VIOLENCE = 36
    MILD_FANTASY_VIOLENCE = 37
    MILD_LANGUAGE = 38
    MILD_LYRICS = 39
    MILD_SEXUAL_THEMES = 40
    MILD_SUGGESTIVE_THEMES = 41
    MILD_VIOLENCE = 42
    ANIMATED_VIOLENCE = 43


class PEGIContentDescriptor(IntEnum):
    VIOLENCE = 1
    BAD_LANGUAGE = 2
    FEAR = 3
    GAMBLING = 4
    SEX = 5
    DRUGS = 6
    DISCRIMINATION = 7


class OperatingSystem(IntEnum):
    WINDOWS = 1
    MACOS = 2
    LINUX = 3


class ExternalSKUStrategyType(IntEnum):
    CONSTANT = 1
    APPLE_STICKER = 2


class StoreListingIconType(IntEnum):
    STORE_ASSET = 1
    EMOJI = 2


class SubscriptionInterval(IntEnum):
    MONTH = 1
    YEAR = 2
    DAY = 3


class SubscriptionPlanPurchaseType(IntEnum):
    DEFAULT = 0
    GIFT = 1
    SALE = 2
    PREMIUM_TIER_1 = 3
    PREMIUM_TIER_2 = 4
    MOBILE = 5
    PREMIUM_TIER_0 = 6
    MOBILE_PREMIUM_TIER_2 = 7


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


class QuestPlatformType(IntEnum):
    """Quest reward code platform values."""

    CROSS_PLATFORM = 0
    XBOX = 1
    PLAYSTATION = 2
    SWITCH = 3
    PC = 4


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


class PollLayoutType(IntEnum):
    DEFAULT = 1


class GuildPowerupCategoryType(StrEnum):
    level = "level"
    perk = "perk"
    game_server = "game_server"


@overload
def to_enum[E: Enum](
    enum: type[E], value: Literal[None], /, *, unknown_ok: bool = ...
) -> None: ...


@overload
def to_enum[E: Enum](
    enum: type[E], value: str | int, /, *, unknown_ok: bool = ...
) -> E: ...


def to_enum[E: Enum](
    enum: type[E], value: str | int | None, /, *, unknown_ok: bool = True
) -> E | None:
    """Convert a raw value to a member of ``enum``.

    Parameters
    ----------
    enum: type[:class:`enum.Enum`]
        The enumeration to convert to.
    value: :class:`str` | :class:`int` | :data:`None`
        The raw value as returned by Discord. :data:`None` is passed through.
    unknown_ok: :class:`bool`
        Whether to wrap a value that is not a member of ``enum`` in an
        :class:`UnknownEnum` instead of raising. Defaults to ``True``,
        so that new values added by Discord never break parsing.

    Returns
    -------
    :class:`enum.Enum` | :data:`None`
        The matching member. If the value is unrecognised and ``unknown_ok``
        is ``True``, an :class:`UnknownEnum` standing in for that member is
        returned instead. It is typed as ``E`` so that model annotations stay
        readable; check with ``isinstance(value, UnknownEnum)`` if you need
        to handle values Discord added after this library was released.

    Raises
    ------
    ValueError
        The value is not a member of ``enum`` and ``unknown_ok`` is ``False``.
    """
    if value is None:
        return None

    try:
        return enum(value)
    except ValueError:
        try:
            return enum[value]  # type: ignore
        except KeyError:
            if unknown_ok:
                # Typed as E so callers are not forced to union every
                # annotation with UnknownEnum; see the docstring.
                return UnknownEnum(value)  # pyright: ignore[reportReturnType]
            raise ValueError(f"{value} is not a valid {enum.__name__}") from None
