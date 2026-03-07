from typing import Literal, NotRequired, TypedDict

from .base import Locale, Snowflake

NameplatePallete = Literal[
    "crimson",
    "berry",
    "sky",
    "teal",
    "forest",
    "bubble_gum",
    "violet",
    "cobalt",
    "clover",
    "lemon",
    "white",
]
DisplayNameFont = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
DisplayNameEffect = Literal[1, 2, 3, 4, 5]

PremiumType = Literal[0, 1, 2, 3]


class AvatarDecorationDataResponse(TypedDict):
    asset: str
    sku_id: Snowflake


class _CollectibleResponse(TypedDict):
    sku_id: Snowflake
    asset: str
    label: str


class _CollectibleNameplateResponse(_CollectibleResponse):
    palette: NameplatePallete


class CollectablesResponse(TypedDict):
    nameplate: _CollectibleNameplateResponse


class DisplayNameStyleResponse(TypedDict):
    font_id: DisplayNameFont
    effect_id: DisplayNameEffect
    colors: list[int]


class PrimaryGuildResponse(TypedDict):
    identity_guild_id: Snowflake | None
    identity_enabled: bool | None
    """
    whether the user is displaying the primary guild's server tag. 
    This can be null if the system clears the identity, e.g. 
    the server no longer supports tags. This will be false if 
    the user manually removes their tag.
    """
    tag: str | None
    badge: str | None


class PartialUserResponse(TypedDict):
    id: Snowflake
    username: str
    avatar: str | None
    discriminator: str
    public_flags: int
    global_name: str | None


class GuildMemberWithUserResponse(PartialUserResponse):
    flags: int
    banner: str | None
    accent_color: int | None
    avatar_decoration_data: AvatarDecorationDataResponse | None
    collectibles: CollectablesResponse | None
    display_name_styles: DisplayNameStyleResponse | None
    banner_color: str | None
    clan: PrimaryGuildResponse | None
    primary_guild: PrimaryGuildResponse | None


class CurrentUserResponse(GuildMemberWithUserResponse):
    email: NotRequired[str]  # required email scope
    mfa_enabled: bool
    locale: Locale
    premium_type: PremiumType


class ModifyCurrentUserAccountRequest(TypedDict):
    global_name: NotRequired[str | None]


ModifyCurrentUserAccountResponse = PartialUserResponse


class HarvestMetadataResponse(TypedDict):
    user_is_staff: bool
    sla_email_sent: bool
    bypass_cooldown: bool
    is_provisional: NotRequired[bool]
    backend_attempts: NotRequired[dict[str, int]]


class HarvestResponse(TypedDict):
    harvest_id: Snowflake
    user_id: Snowflake
    email: str
    state: str
    status: int
    created_at: str
    completed_at: str | None
    polled_at: str | None
    backends: dict[str, str]
    updated_at: str
    shadow_run: bool
    harvest_metadata: HarvestMetadataResponse


class CreateUserHarvestRequest(TypedDict):
    backends: NotRequired[list[str] | None]
    email: NotRequired[str]


GetUserHarvestResponse = HarvestResponse | None
CreateUserHarvestResponse = HarvestResponse
