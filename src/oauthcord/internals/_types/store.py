from typing import Literal, NotRequired, TypedDict

from .application import PartialApplicationResponse
from .base import Locale, Snowflake
from .user import PartialUserResponse


class LocalizedString(TypedDict):
    default: str
    localizations: NotRequired[dict[Locale, str]]


SKUType = Literal[1, 2, 3, 4, 5, 6]
SKUProductLine = Literal[1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14]
SKUAccessType = Literal[1, 2, 3]
SKUFeature = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
SKUGenre = Literal[
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
]
ContentRatingAgency = Literal[1, 2]
ESRBContentRating = Literal[1, 2, 3, 4, 5, 6]
PEGIContentRating = Literal[1, 2, 3, 4, 5]
OperatingSystem = Literal[1, 2, 3]
StoreListingIconType = Literal[1, 2]
SubscriptionInterval = Literal[1, 2, 3]
SubscriptionPlanPurchaseType = Literal[0, 1, 2, 3, 4, 5, 6, 7]
ExternalSKUStrategyType = Literal[1, 2]


class StoreAssetResponse(TypedDict):
    id: Snowflake
    size: int
    mime_type: str
    width: int
    height: int
    filename: NotRequired[str]


class StoreListingIconResponse(TypedDict):
    type: StoreListingIconType
    store_asset_id: NotRequired[Snowflake]
    emoji: NotRequired[str]


class StoreListingBenefitResponse(TypedDict):
    id: Snowflake
    name: str
    description: str
    icon: StoreListingIconResponse


class StoreCarouselItemResponse(TypedDict):
    youtube_video_id: NotRequired[str]
    asset_id: NotRequired[Snowflake]
    thumbnail_asset_id: NotRequired[Snowflake]
    background_asset_id: NotRequired[Snowflake | None]
    label: NotRequired[str]
    label_icon_asset_id: NotRequired[Snowflake]


class StoreNoteResponse(TypedDict):
    user: NotRequired[PartialUserResponse | None]
    content: str


class SKUPricePremiumResponse(TypedDict):
    amount: int
    percentage: int


class SKUPriceResponse(TypedDict):
    currency: str
    currency_exponent: int
    amount: int
    sale_amount: NotRequired[int]
    sale_percentage: NotRequired[int]
    premium: NotRequired[dict[int, SKUPricePremiumResponse]]


class ContentRatingResponse(TypedDict):
    rating: ESRBContentRating | PEGIContentRating
    descriptors: list[int]


class SystemRequirementResponse(TypedDict):
    ram: NotRequired[int]
    disk: NotRequired[int]
    operating_system_version: NotRequired[LocalizedString]
    cpu: NotRequired[LocalizedString]
    gpu: NotRequired[LocalizedString]
    sound_card: NotRequired[LocalizedString]
    directx: NotRequired[LocalizedString]
    network: NotRequired[LocalizedString]
    notes: NotRequired[LocalizedString]


class SystemRequirementsResponse(TypedDict):
    minimum: NotRequired[SystemRequirementResponse]
    recommended: NotRequired[SystemRequirementResponse]


class ExternalSKUStrategyResponse(TypedDict):
    type: ExternalSKUStrategyType
    metadata: NotRequired[dict[str, str]]


class GuildPremiumFeaturesResponse(TypedDict):
    features: NotRequired[list[str]]
    additional_emoji_slots: NotRequired[int]
    additional_sticker_slots: NotRequired[int]
    additional_sound_slots: NotRequired[int]


class GuildPowerupMetadata(TypedDict):
    boost_price: int
    purchase_limit: int
    guild_features: GuildPremiumFeaturesResponse
    category_type: str
    static_image_url: str
    animated_image_url: str
    store_removal_date: NotRequired[str | None]


class PartialGuildPowerupMetadata(TypedDict):
    category_type: str
    static_image_url: str
    animated_image_url: str
    store_removal_date: NotRequired[str | None]


class GameServerPowerupMetadata(TypedDict):
    boost_price: int
    purchase_limit: int
    guild_features: GuildPremiumFeaturesResponse
    category_type: str
    available_providers: list[str]
    memory: int
    cpu: int
    storage: int
    max_slots: int
    memory_string: str
    player_string: str


class GuildMonetizationMetadata(TypedDict):
    powerup: NotRequired[GuildPowerupMetadata]
    game_server: NotRequired[GameServerPowerupMetadata]


class SocialLayerMetadata(TypedDict):
    carousel_items: list[StoreCarouselItemResponse]
    label: str
    expires_at: NotRequired[str | None]
    card_image_asset_id: NotRequired[Snowflake]
    card_background_image_asset_id: NotRequired[Snowflake]
    price_tier: NotRequired[int]


class TenantMetadata(TypedDict):
    guild_monetization: NotRequired[GuildMonetizationMetadata]
    social_layer: NotRequired[SocialLayerMetadata]


class SKU(TypedDict):
    id: Snowflake
    type: SKUType
    application_id: Snowflake
    application: NotRequired[PartialApplicationResponse | None]
    product_line: NotRequired[SKUProductLine | None]
    product_id: NotRequired[Snowflake | None]
    flags: int
    name: LocalizedString
    summary: NotRequired[LocalizedString | None]
    description: NotRequired[LocalizedString | None]
    legal_notice: NotRequired[LocalizedString | None]
    slug: str
    thumbnail_asset_id: NotRequired[Snowflake | None]
    dependent_sku_id: NotRequired[Snowflake | None]
    bundled_skus: NotRequired[list["SKU"]]
    bundled_sku_ids: NotRequired[list[Snowflake]]
    access_type: SKUAccessType
    manifest_labels: NotRequired[list[Snowflake] | None]
    features: list[SKUFeature]
    locales: NotRequired[list[str]]
    genres: NotRequired[list[SKUGenre]]
    available_regions: NotRequired[list[str]]
    content_rating: NotRequired[ContentRatingResponse]
    content_rating_agency: NotRequired[ContentRatingAgency]
    content_ratings: NotRequired[dict[ContentRatingAgency, ContentRatingResponse]]
    system_requirements: NotRequired[dict[OperatingSystem, SystemRequirementsResponse]]
    price: NotRequired[SKUPriceResponse]
    sale_price_tier: NotRequired[int]
    sale_price: NotRequired[dict[str, int]]
    created_at: str
    updated_at: str
    release_date: NotRequired[str | None]
    preorder_approximate_release_date: NotRequired[str | None]
    preorder_released_at: NotRequired[str | None]
    external_purchase_url: NotRequired[str | None]
    external_sku_strategies: NotRequired[
        dict[ExternalSKUStrategyType, ExternalSKUStrategyResponse]
    ]
    eligible_payment_gateways: NotRequired[list[int]]
    premium: bool
    show_age_gate: bool
    restricted: NotRequired[bool]
    exclusive: NotRequired[bool]
    deleted: NotRequired[bool]
    tenant_metadata: NotRequired[TenantMetadata]
    powerup_metadata: NotRequired[GuildPowerupMetadata]
    orbs_reward: NotRequired[int]


class GetApplicationSKUsRequest(TypedDict):
    country_code: NotRequired[str]
    localize: NotRequired[bool]
    with_bundled_skus: NotRequired[bool]


class CreateSKURequest(TypedDict):
    type: SKUType
    application_id: Snowflake
    name: LocalizedString
    flags: NotRequired[int]
    legal_notice: NotRequired[LocalizedString]
    dependent_sku_id: NotRequired[Snowflake]
    bundled_skus: NotRequired[list[Snowflake]]
    access_type: NotRequired[SKUAccessType]
    manifest_labels: NotRequired[list[Snowflake]]
    features: NotRequired[list[SKUFeature]]
    locales: NotRequired[list[str]]
    genres: NotRequired[list[SKUGenre]]
    content_ratings: NotRequired[dict[ContentRatingAgency, ContentRatingResponse]]
    system_requirements: NotRequired[dict[OperatingSystem, SystemRequirementsResponse]]
    price_tier: NotRequired[int]
    price: NotRequired[dict[str, int]]
    sale_price_tier: NotRequired[int]
    sale_price: NotRequired[dict[str, int]]
    release_date: NotRequired[str]


class ModifySKURequest(TypedDict):
    name: NotRequired[LocalizedString]
    flags: NotRequired[int]
    legal_notice: NotRequired[LocalizedString]
    dependent_sku_id: NotRequired[Snowflake]
    bundled_skus: NotRequired[list[Snowflake]]
    access_type: NotRequired[SKUAccessType]
    manifest_labels: NotRequired[list[Snowflake]]
    features: NotRequired[list[SKUFeature]]
    locales: NotRequired[list[str]]
    genres: NotRequired[list[SKUGenre]]
    content_ratings: NotRequired[dict[ContentRatingAgency, ContentRatingResponse]]
    system_requirements: NotRequired[dict[OperatingSystem, SystemRequirementsResponse]]
    price_tier: NotRequired[int]
    price: NotRequired[dict[str, int]]
    sale_price_tier: NotRequired[int]
    sale_price: NotRequired[dict[str, int]]
    release_date: NotRequired[str]


class GetSKURequest(TypedDict):
    country_code: NotRequired[str]
    localize: NotRequired[bool]


class StoreListingResponse(TypedDict):
    id: Snowflake
    sku: SKU
    child_skus: NotRequired[list[SKU]]
    alternative_skus: NotRequired[list[SKU]]
    summary: LocalizedString
    description: NotRequired[LocalizedString]
    tagline: NotRequired[LocalizedString | None]
    flavor_text: NotRequired[str | None]
    benefits: NotRequired[list[StoreListingBenefitResponse] | None]
    published: NotRequired[bool]
    carousel_items: NotRequired[list[StoreCarouselItemResponse] | None]
    staff_notes: NotRequired[StoreNoteResponse]
    guild: NotRequired[dict[str, object] | None]
    assets: NotRequired[list[StoreAssetResponse]]
    thumbnail: NotRequired[StoreAssetResponse]
    preview_video: NotRequired[StoreAssetResponse]
    header_background: NotRequired[StoreAssetResponse]
    header_logo_dark_theme: NotRequired[StoreAssetResponse]
    header_logo_light_theme: NotRequired[StoreAssetResponse]
    box_art: NotRequired[StoreAssetResponse]
    hero_background: NotRequired[StoreAssetResponse]
    hero_video: NotRequired[StoreAssetResponse]
    entitlement_branch_id: NotRequired[Snowflake | None]
    published_at: NotRequired[str | None]
    unpublished_at: NotRequired[str | None]
    powerup_metadata: NotRequired[PartialGuildPowerupMetadata | None]


class GetSKUStoreListingsRequest(TypedDict):
    country_code: NotRequired[str]
    localize: NotRequired[bool]


class CreateStoreListingRequest(TypedDict):
    application_id: Snowflake
    sku_id: Snowflake
    child_sku_ids: NotRequired[list[Snowflake]]
    summary: LocalizedString
    description: LocalizedString
    tagline: NotRequired[LocalizedString]
    published: NotRequired[bool]
    carousel_items: NotRequired[list[StoreCarouselItemResponse] | None]
    guild_id: NotRequired[Snowflake]
    thumbnail_asset_id: NotRequired[Snowflake]
    preview_video_asset_id: NotRequired[Snowflake]
    header_background_asset_id: NotRequired[Snowflake]
    header_logo_dark_theme_asset_id: NotRequired[Snowflake]
    header_logo_light_theme_asset_id: NotRequired[Snowflake]
    box_art_asset_id: NotRequired[Snowflake]
    hero_background_asset_id: NotRequired[Snowflake]
    hero_video_asset_id: NotRequired[Snowflake]


class ModifyStoreListingRequest(TypedDict):
    child_sku_ids: NotRequired[list[Snowflake]]
    summary: NotRequired[LocalizedString]
    description: NotRequired[LocalizedString]
    tagline: NotRequired[LocalizedString]
    published: NotRequired[bool]
    carousel_items: NotRequired[list[StoreCarouselItemResponse] | None]
    guild_id: NotRequired[Snowflake]
    thumbnail_asset_id: NotRequired[Snowflake]
    preview_video_asset_id: NotRequired[Snowflake]
    header_background_asset_id: NotRequired[Snowflake]
    header_logo_dark_theme_asset_id: NotRequired[Snowflake]
    header_logo_light_theme_asset_id: NotRequired[Snowflake]
    box_art_asset_id: NotRequired[Snowflake]
    hero_background_asset_id: NotRequired[Snowflake]
    hero_video_asset_id: NotRequired[Snowflake]


class GetStoreListingRequest(TypedDict):
    country_code: NotRequired[str]
    localize: NotRequired[bool]


class CountryPricesResponse(TypedDict):
    country_code: str
    prices: list["UnitPriceResponse"]


class SubscriptionPricesResponse(TypedDict):
    country_prices: CountryPricesResponse
    payment_source_prices: dict[Snowflake, list["UnitPriceResponse"]]


class UnitPriceResponse(TypedDict):
    currency: str
    amount: int
    exponent: int


class SubscriptionPlanResponse(TypedDict):
    id: Snowflake
    name: str
    sku_id: Snowflake
    interval: SubscriptionInterval
    interval_count: int
    tax_inclusive: bool
    price: NotRequired[int | dict[str, int]]
    currency: NotRequired[str]
    prices: NotRequired[dict[SubscriptionPlanPurchaseType, SubscriptionPricesResponse]]


class EULAResponse(TypedDict):
    id: Snowflake
    name: str
    content: str


class StorefrontLeaderboardResponse(TypedDict):
    title: NotRequired[str]
    description: NotRequired[str]
    background_image_asset_id: NotRequired[Snowflake]


class StorefrontPageSectionResponse(TypedDict):
    title: NotRequired[str]
    sku_ids: list[Snowflake]


class StorefrontPageResponse(TypedDict):
    title: NotRequired[str]
    leaderboard: NotRequired[StorefrontLeaderboardResponse]
    sku_ids: list[Snowflake]
    sections: NotRequired[list[StorefrontPageSectionResponse]]


class StorefrontResponse(TypedDict):
    application_id: Snowflake
    application: NotRequired[PartialApplicationResponse | None]
    title: str
    logo_asset_id: NotRequired[Snowflake]
    light_theme_logo_asset_id: NotRequired[Snowflake]
    pages: list[StorefrontPageResponse]
    store_listings: list[StoreListingResponse]
    assets: list[StoreAssetResponse]


class StorefrontCollectionResponse(TypedDict):
    id: Snowflake
    application_id: Snowflake
    name: str
    description: str
    product_ids: list[Snowflake]
    created_at: str
    updated_at: str
    tenant_metadata: dict[str, object]


class ProductOptionResponse(TypedDict):
    name: str
    option_values: list[str]


class GameServerInstructionsResponse(TypedDict):
    pc: list[str]


class GameServerPowerupProductMetadataResponse(TypedDict):
    instructions: GameServerInstructionsResponse
    deactivation_cooldown_period_days: int
    game_application_id: Snowflake
    provider: str
    disabled: bool
    early_access: bool
    can_market: bool


class GuildMonetizationProductMetadataResponse(TypedDict):
    game_server: NotRequired[GameServerPowerupProductMetadataResponse]


class ProductTenantMetadataResponse(TypedDict):
    guild_monetization: NotRequired[GuildMonetizationProductMetadataResponse]


class ProductSKUPlanFeatureResponse(TypedDict):
    title: str
    description: str


class ProductSKUTenantMetadataResponse(TypedDict):
    boost_price: int
    purchase_limit: int
    category_type: str
    plan_features: list[ProductSKUPlanFeatureResponse]


class ProductSKUOptionResponse(TypedDict):
    option_name: str
    option_value: str


class ProductSKUResponse(TypedDict):
    id: Snowflake
    type: SKUType
    product_line: SKUProductLine
    application_id: Snowflake
    name: str
    thumbnail_asset_id: Snowflake | None
    slug: str
    premium: bool
    selected_options: list[ProductSKUOptionResponse]
    product_id: Snowflake
    position: int
    tenant_metadata: ProductSKUTenantMetadataResponse


class StorefrontProductResponse(TypedDict):
    id: Snowflake
    application_id: Snowflake
    sku_ids: list[Snowflake]
    name: str
    options: list[ProductOptionResponse]
    created_at: str
    updated_at: str
    tenant_metadata: ProductTenantMetadataResponse
    skus: list[ProductSKUResponse]


GetApplicationSKUsResponse = list[SKU]
GetSKUResponse = SKU
ModifySKUResponse = SKU
GetSKUStoreListingsResponse = list[StoreListingResponse]
CreateStoreListingResponse = StoreListingResponse
GetStoreListingResponse = StoreListingResponse
ModifyStoreListingResponse = StoreListingResponse
DeleteStoreListingResponse = None
GetSubscriptionPlansResponse = list[SubscriptionPlanResponse]
GetApplicationStoreAssetsResponse = list[StoreAssetResponse]
CreateApplicationStoreAssetResponse = StoreAssetResponse
DeleteApplicationStoreAssetResponse = None
