import datetime
from typing import TYPE_CHECKING, Any, cast, override

from ..utils import _serialize_localizations, convert_snowflake, iso_to_datetime
from ._base import BaseModel, BaseModelWithSession
from .application import PartialApplication
from .enums import (
    ContentRatingAgency,
    ESRBContentDescriptor,
    ESRBContentRating,
    ExternalSKUStrategyType,
    GuildPowerupCategoryType,
    Locale,
    OperatingSystem,
    PEGIContentDescriptor,
    PEGIContentRating,
    PremiumType,
    SKUAccessType,
    SKUFeature,
    SKUGenre,
    SKUProductLine,
    SKUType,
    StoreListingIconType,
    SubscriptionInterval,
    SubscriptionPlanPurchaseType,
    to_enum,
)
from .flags import SKUFlags
from .user import PartialUser

if TYPE_CHECKING:
    from ..internals._types import store as store_types

__all__ = (
    "EULA",
    "SKU",
    "ContentRating",
    "CountryPrices",
    "ExternalSKUStrategy",
    "GameServerInstructions",
    "GameServerPowerupMetadata",
    "GameServerPowerupProductMetadata",
    "GuildMonetizationMetadata",
    "GuildMonetizationProductMetadata",
    "GuildPowerupMetadata",
    "GuildPremiumFeatures",
    "LocalizedString",
    "PartialGuildPowerupMetadata",
    "PremiumPrice",
    "Price",
    "ProductOption",
    "ProductSKU",
    "ProductSKUOption",
    "ProductSKUPlanFeature",
    "ProductSKUTenantMetadata",
    "ProductTenantMetadata",
    "SocialLayerMetadata",
    "StoreAsset",
    "StoreCarouselItem",
    "StoreListing",
    "StoreListingBenefit",
    "StoreListingIcon",
    "StoreNote",
    "Storefront",
    "StorefrontCollection",
    "StorefrontLeaderboard",
    "StorefrontPage",
    "StorefrontPageSection",
    "StorefrontProduct",
    "SubscriptionPlan",
    "SubscriptionPrices",
    "SystemRequirement",
    "SystemRequirements",
    "TenantMetadata",
    "UnitPrice",
)


def _iso_to_date(value: str | None) -> datetime.date | None:
    if not value:
        return None
    return datetime.date.fromisoformat(value)


def _parse_locale_map(data: Any) -> dict[Locale | str, str]:
    if not data:
        return {}

    parsed: dict[Locale | str, str] = {}
    for key, value in data.items():
        try:
            parsed[to_enum(Locale, key)] = value
        except ValueError:
            parsed[key] = value
    return parsed


def _serialize_locale_map(
    data: dict[Locale | str, str] | None,
) -> dict[str, str]:
    if not data:
        return {}

    if all(isinstance(key, Locale) for key in data):
        return _serialize_localizations(cast("dict[Locale, str]", data))

    serialized: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(key, Locale):
            serialized[key.value] = value
        else:
            serialized[str(key)] = value
    return serialized


def _localized_payload(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return {"default": value}
    return value


class LocalizedString(
    BaseModel["store_types.LocalizedString", "store_types.LocalizedString"]
):
    """Localized string payload used by Discord store resources.

    Attributes
    ----------
    default: :class:`str`
        The default string value.
    localizations: :class:`dict`
        Localized string overrides keyed by locale code.
    """

    __slots__ = ("default", "localizations")

    @override
    def _initialize(self, data: store_types.LocalizedString) -> None:
        self.default: str = data["default"]
        self.localizations: dict[Locale | str, str] = _parse_locale_map(
            data.get("localizations")
        )

    @override
    def _to_request(self) -> store_types.LocalizedString:
        payload: store_types.LocalizedString = {"default": self.default}
        if self.localizations:
            payload["localizations"] = cast(
                "Any", _serialize_locale_map(self.localizations)
            )
        return payload


class StoreAsset(BaseModel["store_types.StoreAssetResponse"]):
    """Image or video asset attached to a store resource.

    Attributes
    ----------
    id: :class:`int`
        The store asset snowflake.
    size: :class:`int`
        The asset size in bytes.
    mime_type: :class:`str`
        The media type of the asset.
    filename: :class:`str`
        The uploaded filename, if included by Discord.
    width: :class:`int`
        The asset width in pixels.
    height: :class:`int`
        The asset height in pixels.
    """

    __slots__ = ("filename", "height", "id", "mime_type", "size", "width")

    @override
    def _initialize(self, data: store_types.StoreAssetResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.size: int = data["size"]
        self.mime_type: str = data["mime_type"]
        self.filename: str | None = data.get("filename")
        self.width: int = data["width"]
        self.height: int = data["height"]


class StoreListingIcon(BaseModel["store_types.StoreListingIconResponse"]):
    """Icon metadata for a store listing benefit.

    Attributes
    ----------
    type: :class:`StoreListingIconType`
        The icon type.
    store_asset_id: :class:`int`
        The backing store asset snowflake, if the icon is a store asset.
    emoji: :class:`str`
        The unicode emoji for the icon, if the icon uses emoji.
    """

    __slots__ = ("emoji", "store_asset_id", "type")

    @override
    def _initialize(self, data: store_types.StoreListingIconResponse) -> None:
        self.type: StoreListingIconType = to_enum(StoreListingIconType, data["type"])
        self.store_asset_id: int | None = convert_snowflake(
            data, "store_asset_id", always_available=False
        )
        self.emoji: str | None = data.get("emoji")


class StoreListingBenefit(BaseModel["store_types.StoreListingBenefitResponse"]):
    """Benefit entry shown on a store listing.

    Attributes
    ----------
    id: :class:`int`
        The benefit snowflake.
    name: :class:`str`
        The benefit name.
    description: :class:`str`
        The benefit description.
    icon: :class:`StoreListingIcon`
        The icon associated with the benefit.
    """

    __slots__ = ("description", "icon", "id", "name")

    @override
    def _initialize(self, data: store_types.StoreListingBenefitResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.icon: StoreListingIcon = self._initialize_other(
            StoreListingIcon, data, possible_keys="icon"
        )


class StoreCarouselItem(
    BaseModel[
        "store_types.StoreCarouselItemResponse", "store_types.StoreCarouselItemResponse"
    ]
):
    """Carousel media item attached to a store listing.

    Attributes
    ----------
    youtube_video_id: :class:`str`
        The YouTube video identifier, if the item is a YouTube embed.
    asset_id: :class:`int`
        The store asset snowflake, if the item is a direct store asset.
    thumbnail_asset_id: :class:`int`
        The thumbnail store asset snowflake, if included.
    background_asset_id: :class:`int`
        The background store asset snowflake, if included.
    label: :class:`str`
        The display label for the item, if present.
    label_icon_asset_id: :class:`int`
        The label icon store asset snowflake, if included.
    """

    __slots__ = (
        "asset_id",
        "background_asset_id",
        "label",
        "label_icon_asset_id",
        "thumbnail_asset_id",
        "youtube_video_id",
    )

    @override
    def _initialize(self, data: store_types.StoreCarouselItemResponse) -> None:
        self.youtube_video_id: str | None = data.get("youtube_video_id")
        self.asset_id: int | None = convert_snowflake(
            data, "asset_id", always_available=False
        )
        self.thumbnail_asset_id: int | None = convert_snowflake(
            data, "thumbnail_asset_id", always_available=False
        )
        self.background_asset_id: int | None = convert_snowflake(
            data, "background_asset_id", always_available=False
        )
        self.label: str | None = data.get("label")
        self.label_icon_asset_id: int | None = convert_snowflake(
            data, "label_icon_asset_id", always_available=False
        )

    @override
    def _to_request(self) -> store_types.StoreCarouselItemResponse:  # pyright: ignore[reportIncompatibleMethodOverride]
        payload: store_types.StoreCarouselItemResponse = {}
        if self.youtube_video_id is not None:
            payload["youtube_video_id"] = self.youtube_video_id
        if self.asset_id is not None:
            payload["asset_id"] = str(self.asset_id)
        if self.thumbnail_asset_id is not None:
            payload["thumbnail_asset_id"] = str(self.thumbnail_asset_id)
        if self.background_asset_id is not None:
            payload["background_asset_id"] = str(self.background_asset_id)
        if self.label is not None:
            payload["label"] = self.label
        if self.label_icon_asset_id is not None:
            payload["label_icon_asset_id"] = str(self.label_icon_asset_id)
        return payload


class StoreNote(BaseModelWithSession["store_types.StoreNoteResponse"]):
    """Staff note attached to a store listing.

    Attributes
    ----------
    user: :class:`PartialUser`
        The user who created the note, if Discord included user data.
    content: :class:`str`
        The note content.
    """

    __slots__ = ("content", "user")

    @override
    def _initialize(self, data: store_types.StoreNoteResponse) -> None:
        self.user: PartialUser | None = self._initialize_other(
            PartialUser, data, possible_keys="user", optional=True
        )
        self.content: str = data["content"]


class GuildPremiumFeatures(BaseModel["store_types.GuildPremiumFeaturesResponse"]):
    """Guild premium feature values granted by a powerup.

    Attributes
    ----------
    features: list[:class:`str`]
        Guild premium feature names granted by the powerup.
    additional_emoji_slots: :class:`int`
        Additional emoji slots granted by the powerup.
    additional_sticker_slots: :class:`int`
        Additional sticker slots granted by the powerup.
    additional_sound_slots: :class:`int`
        Additional soundboard slots granted by the powerup.
    """

    __slots__ = (
        "additional_emoji_slots",
        "additional_sound_slots",
        "additional_sticker_slots",
        "features",
    )

    @override
    def _initialize(self, data: store_types.GuildPremiumFeaturesResponse) -> None:
        self.features: list[str] = data.get("features", [])
        self.additional_emoji_slots: int = data.get("additional_emoji_slots", 0)
        self.additional_sticker_slots: int = data.get("additional_sticker_slots", 0)
        self.additional_sound_slots: int = data.get("additional_sound_slots", 0)


class PartialGuildPowerupMetadata(BaseModel["store_types.PartialGuildPowerupMetadata"]):
    """Partial guild powerup metadata exposed on store listings.

    Attributes
    ----------
    category_type: :class:`GuildPowerupCategoryType` | :class:`str`
        The guild powerup category type.
    static_image_url: :class:`str`
        The static banner image URL.
    animated_image_url: :class:`str`
        The animated banner image URL.
    store_removal_date: :class:`datetime.datetime`
        When the powerup is scheduled to be removed from the store, if present.
    """

    __slots__ = (
        "animated_image_url",
        "category_type",
        "static_image_url",
        "store_removal_date",
    )

    @override
    def _initialize(self, data: store_types.PartialGuildPowerupMetadata) -> None:
        raw_category = data["category_type"]
        try:
            self.category_type: GuildPowerupCategoryType | str = to_enum(
                GuildPowerupCategoryType, raw_category
            )
        except ValueError:
            self.category_type = raw_category
        self.static_image_url: str = data["static_image_url"]
        self.animated_image_url: str = data["animated_image_url"]
        self.store_removal_date: datetime.datetime | None = iso_to_datetime(
            data.get("store_removal_date")
        )


class GuildPowerupMetadata(BaseModel["store_types.GuildPowerupMetadata"]):
    """Guild powerup metadata attached to a SKU.

    Attributes
    ----------
    boost_price: :class:`int`
        The number of boosts required to purchase the powerup.
    purchase_limit: :class:`int`
        The maximum number of entitlements a guild can hold for the powerup.
    guild_features: :class:`GuildPremiumFeatures`
        The guild premium features granted by the powerup.
    category_type: :class:`GuildPowerupCategoryType` | :class:`str`
        The guild powerup category type.
    static_image_url: :class:`str`
        The static banner image URL.
    animated_image_url: :class:`str`
        The animated banner image URL.
    store_removal_date: :class:`datetime.datetime`
        When the powerup will be removed from the store, if present.
    """

    __slots__ = (
        "animated_image_url",
        "boost_price",
        "category_type",
        "guild_features",
        "purchase_limit",
        "static_image_url",
        "store_removal_date",
    )

    @override
    def _initialize(self, data: store_types.GuildPowerupMetadata) -> None:
        self.boost_price: int = data["boost_price"]
        self.purchase_limit: int = data["purchase_limit"]
        self.guild_features: GuildPremiumFeatures = self._initialize_other(
            GuildPremiumFeatures, data, possible_keys="guild_features"
        )
        raw_category = data["category_type"]
        try:
            self.category_type: GuildPowerupCategoryType | str = to_enum(
                GuildPowerupCategoryType, raw_category
            )
        except ValueError:
            self.category_type = raw_category
        self.static_image_url: str = data["static_image_url"]
        self.animated_image_url: str = data["animated_image_url"]
        self.store_removal_date: datetime.datetime | None = iso_to_datetime(
            data.get("store_removal_date")
        )


class GameServerPowerupMetadata(BaseModel["store_types.GameServerPowerupMetadata"]):
    """Game server powerup metadata attached to a SKU.

    Attributes
    ----------
    boost_price: :class:`int`
        The number of boosts required to purchase the powerup.
    purchase_limit: :class:`int`
        The maximum number of entitlements a guild can hold for the powerup.
    guild_features: :class:`GuildPremiumFeatures`
        The guild premium features granted by the powerup.
    category_type: :class:`GuildPowerupCategoryType` | :class:`str`
        The guild powerup category type.
    available_providers: list[:class:`str`]
        The available game server providers.
    memory: :class:`int`
        The amount of RAM in megabytes.
    cpu: :class:`int`
        The number of CPU cores.
    storage: :class:`int`
        The amount of storage in gigabytes.
    max_slots: :class:`int`
        The maximum supported player slots.
    memory_string: :class:`str`
        Human-readable RAM size.
    player_string: :class:`str`
        Human-readable player capacity.
    """

    __slots__ = (
        "available_providers",
        "boost_price",
        "category_type",
        "cpu",
        "guild_features",
        "max_slots",
        "memory",
        "memory_string",
        "player_string",
        "purchase_limit",
        "storage",
    )

    @override
    def _initialize(self, data: store_types.GameServerPowerupMetadata) -> None:
        self.boost_price: int = data["boost_price"]
        self.purchase_limit: int = data["purchase_limit"]
        self.guild_features: GuildPremiumFeatures = self._initialize_other(
            GuildPremiumFeatures, data, possible_keys="guild_features"
        )
        raw_category = data["category_type"]
        try:
            self.category_type: GuildPowerupCategoryType | str = to_enum(
                GuildPowerupCategoryType, raw_category
            )
        except ValueError:
            self.category_type = raw_category
        self.available_providers: list[str] = data["available_providers"]
        self.memory: int = data["memory"]
        self.cpu: int = data["cpu"]
        self.storage: int = data["storage"]
        self.max_slots: int = data["max_slots"]
        self.memory_string: str = data["memory_string"]
        self.player_string: str = data["player_string"]


class GuildMonetizationMetadata(BaseModel["store_types.GuildMonetizationMetadata"]):
    """Guild monetization metadata for a store tenant.

    Attributes
    ----------
    powerup: :class:`GuildPowerupMetadata`
        Guild powerup metadata, if included.
    game_server: :class:`GameServerPowerupMetadata`
        Game server powerup metadata, if included.
    """

    __slots__ = ("game_server", "powerup")

    @override
    def _initialize(self, data: store_types.GuildMonetizationMetadata) -> None:
        self.powerup: GuildPowerupMetadata | None = self._initialize_other(
            GuildPowerupMetadata, data, possible_keys="powerup", optional=True
        )
        self.game_server: GameServerPowerupMetadata | None = self._initialize_other(
            GameServerPowerupMetadata,
            data,
            possible_keys="game_server",
            optional=True,
        )


class SocialLayerMetadata(BaseModel["store_types.SocialLayerMetadata"]):
    """Social layer marketplace metadata for a SKU.

    Attributes
    ----------
    carousel_items: list[:class:`StoreCarouselItem`]
        Carousel items shown for the social layer listing.
    label: :class:`str`
        The listing label.
    expires_at: :class:`datetime.datetime`
        When the listing expires, if present.
    card_image_asset_id: :class:`int`
        The card image store asset snowflake, if present.
    card_background_image_asset_id: :class:`int`
        The card background store asset snowflake, if present.
    price_tier: :class:`int`
        The base price tier, if present.
    """

    __slots__ = (
        "card_background_image_asset_id",
        "card_image_asset_id",
        "carousel_items",
        "expires_at",
        "label",
        "price_tier",
    )

    @override
    def _initialize(self, data: store_types.SocialLayerMetadata) -> None:
        self.carousel_items: list[StoreCarouselItem] = [
            self._initialize_other(StoreCarouselItem, item)
            for item in data["carousel_items"]
        ]
        self.label: str = data["label"]
        self.expires_at: datetime.datetime | None = iso_to_datetime(
            data.get("expires_at")
        )
        self.card_image_asset_id: int | None = convert_snowflake(
            data, "card_image_asset_id", always_available=False
        )
        self.card_background_image_asset_id: int | None = convert_snowflake(
            data, "card_background_image_asset_id", always_available=False
        )
        self.price_tier: int | None = data.get("price_tier")


class TenantMetadata(BaseModel["store_types.TenantMetadata"]):
    """Tenant metadata attached to a store SKU.

    Attributes
    ----------
    guild_monetization: :class:`GuildMonetizationMetadata`
        Guild monetization metadata, if present.
    social_layer: :class:`SocialLayerMetadata`
        Social layer metadata, if present.
    """

    __slots__ = ("guild_monetization", "social_layer")

    @override
    def _initialize(self, data: store_types.TenantMetadata) -> None:
        self.guild_monetization: GuildMonetizationMetadata | None = (
            self._initialize_other(
                GuildMonetizationMetadata,
                data,
                possible_keys="guild_monetization",
                optional=True,
            )
        )
        self.social_layer: SocialLayerMetadata | None = self._initialize_other(
            SocialLayerMetadata,
            data,
            possible_keys="social_layer",
            optional=True,
        )


class PremiumPrice(BaseModel["store_types.SKUPricePremiumResponse"]):
    """Premium-specific price override for a SKU.

    Attributes
    ----------
    amount: :class:`int`
        The price amount in the smallest currency unit.
    percentage: :class:`int`
        The discount percentage for premium users.
    """

    __slots__ = ("amount", "percentage")

    @override
    def _initialize(self, data: store_types.SKUPricePremiumResponse) -> None:
        self.amount: int = data["amount"]
        self.percentage: int = data["percentage"]


class Price(BaseModel["store_types.SKUPriceResponse"]):
    """Localized price payload for a SKU.

    Attributes
    ----------
    currency: :class:`str`
        The lower-cased ISO 4217 currency code.
    currency_exponent: :class:`int`
        The currency exponent used for display conversion.
    amount: :class:`int`
        The price amount in the smallest currency unit.
    sale_amount: :class:`int`
        The sale price amount in the smallest currency unit, if present.
    sale_percentage: :class:`int`
        The percentage discount of the sale price, if present.
    premium: :class:`dict`
        Premium-user prices keyed by premium type.
    """

    __slots__ = (
        "amount",
        "currency",
        "currency_exponent",
        "premium",
        "sale_amount",
        "sale_percentage",
    )

    @override
    def _initialize(self, data: store_types.SKUPriceResponse) -> None:
        self.currency: str = data["currency"]
        self.currency_exponent: int = data["currency_exponent"]
        self.amount: int = data["amount"]
        self.sale_amount: int | None = data.get("sale_amount")
        self.sale_percentage: int | None = data.get("sale_percentage")
        self.premium: dict[PremiumType | int, PremiumPrice] = {}
        for raw_key, raw_value in data.get("premium", {}).items():
            try:
                key: PremiumType | int = to_enum(PremiumType, int(raw_key))
            except ValueError:
                key = int(raw_key)
            self.premium[key] = self._initialize_other(PremiumPrice, raw_value)


class ContentRating(
    BaseModel["store_types.ContentRatingResponse", "store_types.ContentRatingResponse"]
):
    """Content rating for a SKU.

    Attributes
    ----------
    agency: :class:`ContentRatingAgency`
        The content rating agency, if known.
    rating: :class:`ESRBContentRating` | :class:`PEGIContentRating` | :class:`int`
        The rating value for the agency.
    descriptors: list[:class:`ESRBContentDescriptor` | :class:`PEGIContentDescriptor` | :class:`int`]
        Content descriptor values associated with the rating.
    """

    __slots__ = ("agency", "descriptors", "rating")

    @override
    def _initialize(self, data: store_types.ContentRatingResponse) -> None:
        self.agency: ContentRatingAgency | None = None
        self.rating: ESRBContentRating | PEGIContentRating | int = data["rating"]
        self.descriptors: list[ESRBContentDescriptor | PEGIContentDescriptor | int] = (
            data["descriptors"]
        )

    @classmethod
    def _from_response(
        cls,
        data: store_types.ContentRatingResponse,
        *,
        agency: ContentRatingAgency | int | None = None,
    ) -> "ContentRating":
        self = cls(data=data)
        parsed_agency = to_enum(ContentRatingAgency, agency)
        self.agency = parsed_agency

        if parsed_agency is not None:
            self.rating = to_enum(parsed_agency.content_rating_type, data["rating"])
            self.descriptors = [
                to_enum(parsed_agency.content_descriptor_type, descriptor)
                for descriptor in data["descriptors"]
            ]

        return self

    @override
    def _to_request(self) -> store_types.ContentRatingResponse:  # pyright: ignore[reportIncompatibleMethodOverride]
        return cast(
            "store_types.ContentRatingResponse",
            {
                "rating": int(self.rating),
                "descriptors": [int(descriptor) for descriptor in self.descriptors],
            },
        )


class SystemRequirement(
    BaseModel[
        "store_types.SystemRequirementResponse", "store_types.SystemRequirementResponse"
    ]
):
    """Minimum or recommended requirements for one operating system.

    Attributes
    ----------
    ram: :class:`int`
        Required RAM in megabytes, if present.
    disk: :class:`int`
        Required disk space in megabytes, if present.
    operating_system_version: :class:`LocalizedString`
        Required operating system version text, if present.
    cpu: :class:`LocalizedString`
        Required CPU text, if present.
    gpu: :class:`LocalizedString`
        Required GPU text, if present.
    sound_card: :class:`LocalizedString`
        Required sound card text, if present.
    directx: :class:`LocalizedString`
        Required DirectX version text, if present.
    network: :class:`LocalizedString`
        Required network connectivity text, if present.
    notes: :class:`LocalizedString`
        Additional notes, if present.
    """

    __slots__ = (
        "cpu",
        "directx",
        "disk",
        "gpu",
        "network",
        "notes",
        "operating_system_version",
        "ram",
        "sound_card",
    )

    @override
    def _initialize(self, data: store_types.SystemRequirementResponse) -> None:
        self.ram: int | None = data.get("ram")
        self.disk: int | None = data.get("disk")
        self.operating_system_version: LocalizedString | None = self._initialize_other(
            LocalizedString,
            data,
            possible_keys="operating_system_version",
            optional=True,
        )
        self.cpu: LocalizedString | None = self._initialize_other(
            LocalizedString, data, possible_keys="cpu", optional=True
        )
        self.gpu: LocalizedString | None = self._initialize_other(
            LocalizedString, data, possible_keys="gpu", optional=True
        )
        self.sound_card: LocalizedString | None = self._initialize_other(
            LocalizedString, data, possible_keys="sound_card", optional=True
        )
        self.directx: LocalizedString | None = self._initialize_other(
            LocalizedString, data, possible_keys="directx", optional=True
        )
        self.network: LocalizedString | None = self._initialize_other(
            LocalizedString, data, possible_keys="network", optional=True
        )
        self.notes: LocalizedString | None = self._initialize_other(
            LocalizedString, data, possible_keys="notes", optional=True
        )

    @override
    def _to_request(self) -> store_types.SystemRequirementResponse:  # pyright: ignore[reportIncompatibleMethodOverride]
        payload: store_types.SystemRequirementResponse = {}
        if self.ram is not None:
            payload["ram"] = self.ram
        if self.disk is not None:
            payload["disk"] = self.disk
        if self.operating_system_version is not None:
            payload["operating_system_version"] = (
                self.operating_system_version._to_request()
            )
        if self.cpu is not None:
            payload["cpu"] = self.cpu._to_request()
        if self.gpu is not None:
            payload["gpu"] = self.gpu._to_request()
        if self.sound_card is not None:
            payload["sound_card"] = self.sound_card._to_request()
        if self.directx is not None:
            payload["directx"] = self.directx._to_request()
        if self.network is not None:
            payload["network"] = self.network._to_request()
        if self.notes is not None:
            payload["notes"] = self.notes._to_request()
        return payload


class SystemRequirements(
    BaseModel[
        "store_types.SystemRequirementsResponse",
        "store_types.SystemRequirementsResponse",
    ]
):
    """System requirements grouping for one operating system.

    Attributes
    ----------
    minimum: :class:`SystemRequirement`
        Minimum system requirements, if present.
    recommended: :class:`SystemRequirement`
        Recommended system requirements, if present.
    """

    __slots__ = ("minimum", "recommended")

    @override
    def _initialize(self, data: store_types.SystemRequirementsResponse) -> None:
        self.minimum: SystemRequirement | None = self._initialize_other(
            SystemRequirement, data, possible_keys="minimum", optional=True
        )
        self.recommended: SystemRequirement | None = self._initialize_other(
            SystemRequirement, data, possible_keys="recommended", optional=True
        )

    @override
    def _to_request(self) -> store_types.SystemRequirementsResponse:  # pyright: ignore[reportIncompatibleMethodOverride]
        payload: store_types.SystemRequirementsResponse = {}
        if self.minimum is not None:
            payload["minimum"] = self.minimum._to_request()
        if self.recommended is not None:
            payload["recommended"] = self.recommended._to_request()
        return payload


class ExternalSKUStrategy(BaseModel["store_types.ExternalSKUStrategyResponse"]):
    """External purchase strategy metadata for a SKU.

    Attributes
    ----------
    type: :class:`ExternalSKUStrategyType`
        The external strategy type.
    metadata: :class:`dict`
        Additional string metadata for the strategy.
    """

    __slots__ = ("metadata", "type")

    @override
    def _initialize(self, data: store_types.ExternalSKUStrategyResponse) -> None:
        self.type: ExternalSKUStrategyType = to_enum(
            ExternalSKUStrategyType, data["type"]
        )
        self.metadata: dict[str, str] = data.get("metadata", {})


class UnitPrice(BaseModel["store_types.UnitPriceResponse"]):
    """Unit price value used in subscription pricing responses.

    Attributes
    ----------
    currency: :class:`str`
        The lower-cased ISO 4217 currency code.
    amount: :class:`int`
        The amount in the smallest currency unit.
    exponent: :class:`int`
        The currency exponent.
    """

    __slots__ = ("amount", "currency", "exponent")

    @override
    def _initialize(self, data: store_types.UnitPriceResponse) -> None:
        self.currency: str = data["currency"]
        self.amount: int = data["amount"]
        self.exponent: int = data["exponent"]


class CountryPrices(BaseModel["store_types.CountryPricesResponse"]):
    """Country-specific subscription pricing.

    Attributes
    ----------
    country_code: :class:`str`
        The ISO 3166-1 alpha-2 country code.
    prices: list[:class:`UnitPrice`]
        Unit prices returned for the country.
    """

    __slots__ = ("country_code", "prices")

    @override
    def _initialize(self, data: store_types.CountryPricesResponse) -> None:
        self.country_code: str = data["country_code"]
        self.prices: list[UnitPrice] = [
            self._initialize_other(UnitPrice, price) for price in data["prices"]
        ]


class SubscriptionPrices(BaseModel["store_types.SubscriptionPricesResponse"]):
    """Detailed pricing entry for a subscription plan purchase type.

    Attributes
    ----------
    country_prices: :class:`CountryPrices`
        Country pricing returned for the current request context.
    payment_source_prices: :class:`dict`
        Unit prices keyed by payment source snowflake.
    """

    __slots__ = ("country_prices", "payment_source_prices")

    @override
    def _initialize(self, data: store_types.SubscriptionPricesResponse) -> None:
        self.country_prices: CountryPrices = self._initialize_other(
            CountryPrices, data, possible_keys="country_prices"
        )
        self.payment_source_prices: dict[int, list[UnitPrice]] = {
            int(payment_source_id): [
                self._initialize_other(UnitPrice, price) for price in prices
            ]
            for payment_source_id, prices in data["payment_source_prices"].items()
        }


class SKU(BaseModelWithSession["store_types.SKU"]):
    """Purchasable Discord store item or bundle.

    Attributes
    ----------
    id: :class:`int`
        The SKU snowflake.
    type: :class:`SKUType` | :class:`int`
        The SKU type.
    application_id: :class:`int`
        The owning application snowflake.
    application: :class:`PartialApplication`
        The owning application payload, if included.
    product_line: :class:`SKUProductLine` | :class:`int`
        The SKU product line, if included.
    product_id: :class:`int`
        The storefront product snowflake, if included.
    flags: :class:`SKUFlags`
        SKU flags bitfield.
    name: :class:`LocalizedString`
        The SKU name.
    summary: :class:`LocalizedString`
        The SKU summary, if included.
    description: :class:`LocalizedString`
        The SKU description, if included.
    legal_notice: :class:`LocalizedString`
        The SKU legal notice, if included.
    slug: :class:`str`
        The URL slug.
    thumbnail_asset_id: :class:`int`
        The thumbnail store asset snowflake, if included.
    dependent_sku_id: :class:`int`
        The prerequisite SKU snowflake, if included.
    bundled_skus: list[:class:`SKU`]
        Included SKUs bundled with this SKU.
    bundled_sku_ids: list[:class:`int`]
        Snowflakes of bundled SKUs.
    access_type: :class:`SKUAccessType` | :class:`int`
        The access level for the SKU.
    manifest_labels: list[:class:`int`]
        Manifest label snowflakes associated with the SKU.
    features: list[:class:`SKUFeature` | :class:`int`]
        Declared SKU features.
    locales: list[:class:`str`]
        Locale codes where the SKU is available.
    genres: list[:class:`SKUGenre` | :class:`int`]
        Genre identifiers for the SKU.
    available_regions: list[:class:`str`]
        Country codes where the SKU is available.
    content_rating: :class:`ContentRating`
        Localized content rating, if included.
    content_rating_agency: :class:`ContentRatingAgency`
        Agency for the localized content rating, if included.
    content_ratings: :class:`dict`
        Content ratings keyed by agency.
    system_requirements: :class:`dict`
        System requirements keyed by operating system.
    price: :class:`Price` | :class:`dict`
        Localized price object or unlocalized per-currency price map.
    price_tier: :class:`int`
        Base price tier, if included.
    sale_price_tier: :class:`int`
        Sale price tier, if included.
    sale_price: :class:`dict`
        Localized sale pricing keyed by currency, if included.
    created_at: :class:`datetime.datetime`
        When the SKU was created.
    updated_at: :class:`datetime.datetime`
        When the SKU was last updated.
    release_date: :class:`datetime.date`
        The release date, if included.
    preorder_approximate_release_date: :class:`str`
        Developer-provided preorder release text, if included.
    preorder_released_at: :class:`datetime.datetime`
        When the SKU was released for preorder, if included.
    external_purchase_url: :class:`str`
        External purchase URL, if included.
    external_sku_strategies: :class:`dict`
        External SKU strategies keyed by strategy type.
    eligible_payment_gateways: list[:class:`int`]
        Supported payment gateway identifiers.
    premium: :class:`bool`
        Whether the SKU is a premium user perk.
    show_age_gate: :class:`bool`
        Whether Discord should show an age gate when purchasing.
    restricted: :class:`bool`
        Whether the SKU is restricted in the current region, if included.
    exclusive: :class:`bool`
        Whether the SKU is exclusive to Discord, if included.
    deleted: :class:`bool`
        Whether the SKU has been soft deleted, if included.
    tenant_metadata: :class:`TenantMetadata`
        Tenant metadata attached to the SKU, if included.
    powerup_metadata: :class:`GuildPowerupMetadata`
        Guild powerup metadata attached to the SKU, if included.
    orbs_reward: :class:`int`
        The amount of Orbs granted by the SKU, if included.
    """

    __slots__ = (
        "access_type",
        "application",
        "application_id",
        "available_regions",
        "bundled_sku_ids",
        "bundled_skus",
        "content_rating",
        "content_rating_agency",
        "content_ratings",
        "created_at",
        "deleted",
        "dependent_sku_id",
        "description",
        "eligible_payment_gateways",
        "exclusive",
        "external_purchase_url",
        "external_sku_strategies",
        "features",
        "flags",
        "genres",
        "id",
        "legal_notice",
        "locales",
        "manifest_labels",
        "name",
        "orbs_reward",
        "powerup_metadata",
        "premium",
        "preorder_approximate_release_date",
        "preorder_released_at",
        "price",
        "price_tier",
        "product_id",
        "product_line",
        "release_date",
        "restricted",
        "sale_price",
        "sale_price_tier",
        "show_age_gate",
        "slug",
        "summary",
        "system_requirements",
        "tenant_metadata",
        "thumbnail_asset_id",
        "type",
        "updated_at",
    )

    @override
    def _initialize(self, data: store_types.SKU) -> None:
        self.id: int = convert_snowflake(data, "id")
        raw_type = data["type"]
        try:
            self.type: SKUType | int = to_enum(SKUType, raw_type)
        except ValueError:
            self.type = raw_type

        self.application_id: int = convert_snowflake(data, "application_id")
        self.application: PartialApplication | None = self._initialize_other(
            PartialApplication, data, possible_keys="application", optional=True
        )

        raw_product_line = data.get("product_line")
        try:
            self.product_line: SKUProductLine | int | None = to_enum(
                SKUProductLine, raw_product_line
            )
        except ValueError:
            self.product_line = raw_product_line

        self.product_id: int | None = convert_snowflake(
            data, "product_id", always_available=False
        )
        self.flags: SKUFlags = SKUFlags(data["flags"])
        self.name: LocalizedString = self._initialize_other(
            LocalizedString, _localized_payload(data["name"])
        )
        self.summary: LocalizedString | None = self._initialize_other(
            LocalizedString, _localized_payload(data.get("summary")), optional=True
        )
        self.description: LocalizedString | None = self._initialize_other(
            LocalizedString,
            _localized_payload(data.get("description")),
            optional=True,
        )
        self.legal_notice: LocalizedString | None = self._initialize_other(
            LocalizedString,
            _localized_payload(data.get("legal_notice")),
            optional=True,
        )
        self.slug: str = data["slug"]
        self.thumbnail_asset_id: int | None = convert_snowflake(
            data, "thumbnail_asset_id", always_available=False
        )
        self.dependent_sku_id: int | None = convert_snowflake(
            data, "dependent_sku_id", always_available=False
        )
        self.bundled_skus: list[SKU] = [
            self._initialize_other(SKU, sku) for sku in data.get("bundled_skus", [])
        ]
        self.bundled_sku_ids: list[int] = [
            int(sku_id) for sku_id in data.get("bundled_sku_ids", [])
        ]

        raw_access_type = data["access_type"]
        try:
            self.access_type: SKUAccessType | int = to_enum(
                SKUAccessType, raw_access_type
            )
        except ValueError:
            self.access_type = raw_access_type

        manifest_labels = data.get("manifest_labels")
        self.manifest_labels: list[int] | None = (
            [int(label) for label in manifest_labels]
            if manifest_labels is not None
            else None
        )

        self.features: list[SKUFeature | int] = []
        for raw_feature in data["features"]:
            try:
                self.features.append(to_enum(SKUFeature, raw_feature))
            except ValueError:
                self.features.append(raw_feature)

        self.locales: list[str] = data.get("locales", [])
        self.genres: list[SKUGenre | int] = []
        for raw_genre in data.get("genres", []):
            try:
                self.genres.append(to_enum(SKUGenre, raw_genre))
            except ValueError:
                self.genres.append(raw_genre)

        self.available_regions: list[str] = data.get("available_regions", [])
        self.content_rating_agency: ContentRatingAgency | None = to_enum(
            ContentRatingAgency, data.get("content_rating_agency")
        )
        self.content_rating: ContentRating | None = (
            ContentRating._from_response(
                data["content_rating"],
                agency=self.content_rating_agency,
            )
            if "content_rating" in data
            else None
        )
        self.content_ratings: dict[ContentRatingAgency | int, ContentRating] = {}
        for raw_key, raw_value in data.get("content_ratings", {}).items():
            try:
                rating_key: ContentRatingAgency | int = to_enum(
                    ContentRatingAgency, int(raw_key)
                )
            except ValueError:
                rating_key = int(raw_key)
            self.content_ratings[rating_key] = ContentRating._from_response(
                raw_value,
                agency=int(raw_key),
            )

        self.system_requirements: dict[OperatingSystem | int, SystemRequirements] = {}
        for raw_key, raw_value in data.get("system_requirements", {}).items():
            try:
                os_key: OperatingSystem | int = to_enum(OperatingSystem, int(raw_key))
            except ValueError:
                os_key = int(raw_key)
            self.system_requirements[os_key] = self._initialize_other(
                SystemRequirements, raw_value
            )

        raw_price = data.get("price")
        self.price: Price | dict[str, int] | None
        if isinstance(raw_price, dict) and "currency" in raw_price:
            self.price = self._initialize_other(Price, raw_price)
        else:
            self.price = raw_price
        self.price_tier: int | None = data.get("price_tier")
        self.sale_price_tier: int | None = data.get("sale_price_tier")
        self.sale_price: dict[str, int] | None = data.get("sale_price")
        self.created_at: datetime.datetime = iso_to_datetime(data["created_at"])
        self.updated_at: datetime.datetime = iso_to_datetime(data["updated_at"])
        self.release_date: datetime.date | None = _iso_to_date(data.get("release_date"))
        self.preorder_approximate_release_date: str | None = data.get(
            "preorder_approximate_release_date"
        )
        self.preorder_released_at: datetime.datetime | None = iso_to_datetime(
            data.get("preorder_released_at")
        )
        self.external_purchase_url: str | None = data.get("external_purchase_url")
        self.external_sku_strategies: dict[
            ExternalSKUStrategyType | int, ExternalSKUStrategy
        ] = {}
        for raw_key, raw_value in data.get("external_sku_strategies", {}).items():
            try:
                key: ExternalSKUStrategyType | int = to_enum(
                    ExternalSKUStrategyType, int(raw_key)
                )
            except ValueError:
                key = int(raw_key)
            self.external_sku_strategies[key] = self._initialize_other(
                ExternalSKUStrategy, raw_value
            )
        self.eligible_payment_gateways: list[int] = data.get(
            "eligible_payment_gateways", []
        )
        self.premium: bool = data["premium"]
        self.show_age_gate: bool = data["show_age_gate"]
        self.restricted: bool | None = data.get("restricted")
        self.exclusive: bool | None = data.get("exclusive")
        self.deleted: bool | None = data.get("deleted")
        self.tenant_metadata: TenantMetadata | None = self._initialize_other(
            TenantMetadata, data, possible_keys="tenant_metadata", optional=True
        )
        self.powerup_metadata: GuildPowerupMetadata | None = self._initialize_other(
            GuildPowerupMetadata,
            data,
            possible_keys="powerup_metadata",
            optional=True,
        )
        self.orbs_reward: int | None = data.get("orbs_reward")


class StoreListing(BaseModelWithSession["store_types.StoreListingResponse"]):
    """Market listing associated with a single SKU.

    Attributes
    ----------
    id: :class:`int`
        The store listing snowflake.
    sku: :class:`SKU`
        The primary SKU for the listing.
    child_skus: list[:class:`SKU`]
        Child SKUs for category listings.
    alternative_skus: list[:class:`SKU`]
        Alternative SKUs associated with the listing.
    summary: :class:`LocalizedString`
        The listing summary.
    description: :class:`LocalizedString`
        The listing description, if included.
    tagline: :class:`LocalizedString`
        The listing tagline, if included.
    flavor_text: :class:`str`
        Flavor text for the listing, if included.
    benefits: list[:class:`StoreListingBenefit`]
        Benefits shown on the listing, if included.
    published: :class:`bool`
        Whether the listing is published, if included.
    carousel_items: list[:class:`StoreCarouselItem`]
        Carousel items for the listing, if included.
    staff_notes: :class:`StoreNote`
        Staff notes, if included.
    guild: :class:`dict`
        Public guild payload associated with the listing, if included.
    assets: list[:class:`StoreAsset`]
        Store assets attached to the listing.
    thumbnail: :class:`StoreAsset`
        Thumbnail asset, if included.
    preview_video: :class:`StoreAsset`
        Preview video asset, if included.
    header_background: :class:`StoreAsset`
        Header background asset, if included.
    header_logo_dark_theme: :class:`StoreAsset`
        Dark theme header logo asset, if included.
    header_logo_light_theme: :class:`StoreAsset`
        Light theme header logo asset, if included.
    box_art: :class:`StoreAsset`
        Box art asset, if included.
    hero_background: :class:`StoreAsset`
        Hero background asset, if included.
    hero_video: :class:`StoreAsset`
        Hero video asset, if included.
    entitlement_branch_id: :class:`int`
        Granted application branch snowflake, if included.
    published_at: :class:`datetime.datetime`
        When the listing was published, if included.
    unpublished_at: :class:`datetime.datetime`
        When the listing was unpublished, if included.
    powerup_metadata: :class:`PartialGuildPowerupMetadata`
        Partial guild powerup metadata, if included.
    """

    __slots__ = (
        "alternative_skus",
        "assets",
        "benefits",
        "box_art",
        "carousel_items",
        "child_skus",
        "description",
        "entitlement_branch_id",
        "flavor_text",
        "guild",
        "header_background",
        "header_logo_dark_theme",
        "header_logo_light_theme",
        "hero_background",
        "hero_video",
        "id",
        "powerup_metadata",
        "preview_video",
        "published",
        "published_at",
        "sku",
        "staff_notes",
        "summary",
        "tagline",
        "thumbnail",
        "unpublished_at",
    )

    @override
    def _initialize(self, data: store_types.StoreListingResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.sku: SKU = self._initialize_other(SKU, data, possible_keys="sku")
        self.child_skus: list[SKU] = [
            self._initialize_other(SKU, sku) for sku in data.get("child_skus", [])
        ]
        self.alternative_skus: list[SKU] = [
            self._initialize_other(SKU, sku) for sku in data.get("alternative_skus", [])
        ]
        self.summary: LocalizedString = self._initialize_other(
            LocalizedString, _localized_payload(data["summary"])
        )
        self.description: LocalizedString | None = self._initialize_other(
            LocalizedString,
            _localized_payload(data.get("description")),
            optional=True,
        )
        self.tagline: LocalizedString | None = self._initialize_other(
            LocalizedString, _localized_payload(data.get("tagline")), optional=True
        )
        self.flavor_text: str | None = data.get("flavor_text")
        benefits = data.get("benefits")
        self.benefits: list[StoreListingBenefit] | None = (
            [
                self._initialize_other(StoreListingBenefit, benefit)
                for benefit in benefits
            ]
            if benefits is not None
            else None
        )
        self.published: bool | None = data.get("published")
        carousel_items = data.get("carousel_items")
        self.carousel_items: list[StoreCarouselItem] | None = (
            [self._initialize_other(StoreCarouselItem, item) for item in carousel_items]
            if carousel_items is not None
            else None
        )
        self.staff_notes: StoreNote | None = self._initialize_other(
            StoreNote, data, possible_keys="staff_notes", optional=True
        )
        self.guild: dict[str, object] | None = data.get("guild")
        self.assets: list[StoreAsset] = [
            self._initialize_other(StoreAsset, asset)
            for asset in data.get("assets", [])
        ]
        self.thumbnail: StoreAsset | None = self._initialize_other(
            StoreAsset, data, possible_keys="thumbnail", optional=True
        )
        self.preview_video: StoreAsset | None = self._initialize_other(
            StoreAsset, data, possible_keys="preview_video", optional=True
        )
        self.header_background: StoreAsset | None = self._initialize_other(
            StoreAsset, data, possible_keys="header_background", optional=True
        )
        self.header_logo_dark_theme: StoreAsset | None = self._initialize_other(
            StoreAsset, data, possible_keys="header_logo_dark_theme", optional=True
        )
        self.header_logo_light_theme: StoreAsset | None = self._initialize_other(
            StoreAsset, data, possible_keys="header_logo_light_theme", optional=True
        )
        self.box_art: StoreAsset | None = self._initialize_other(
            StoreAsset, data, possible_keys="box_art", optional=True
        )
        self.hero_background: StoreAsset | None = self._initialize_other(
            StoreAsset, data, possible_keys="hero_background", optional=True
        )
        self.hero_video: StoreAsset | None = self._initialize_other(
            StoreAsset, data, possible_keys="hero_video", optional=True
        )
        self.entitlement_branch_id: int | None = convert_snowflake(
            data, "entitlement_branch_id", always_available=False
        )
        self.published_at: datetime.datetime | None = iso_to_datetime(
            data.get("published_at")
        )
        self.unpublished_at: datetime.datetime | None = iso_to_datetime(
            data.get("unpublished_at")
        )
        self.powerup_metadata: PartialGuildPowerupMetadata | None = (
            self._initialize_other(
                PartialGuildPowerupMetadata,
                data,
                possible_keys="powerup_metadata",
                optional=True,
            )
        )


class SubscriptionPlan(BaseModel["store_types.SubscriptionPlanResponse"]):
    """Recurring billing plan attached to a subscription SKU.

    Attributes
    ----------
    id: :class:`int`
        The subscription plan snowflake.
    name: :class:`str`
        The plan name.
    sku_id: :class:`int`
        The parent SKU snowflake.
    interval: :class:`SubscriptionInterval` | :class:`int`
        The billing interval.
    interval_count: :class:`int`
        Number of intervals per billing cycle.
    tax_inclusive: :class:`bool`
        Whether prices include tax.
    price: :class:`int` | :class:`dict`
        Deprecated integer price or currency-to-price mapping, if included.
    currency: :class:`str`
        Deprecated currency code, if included.
    prices: :class:`dict`
        Pricing data keyed by subscription plan purchase type.
    """

    __slots__ = (
        "currency",
        "id",
        "interval",
        "interval_count",
        "name",
        "price",
        "prices",
        "sku_id",
        "tax_inclusive",
    )

    @override
    def _initialize(self, data: store_types.SubscriptionPlanResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.sku_id: int = convert_snowflake(data, "sku_id")
        raw_interval = data["interval"]
        try:
            self.interval: SubscriptionInterval | int = to_enum(
                SubscriptionInterval, raw_interval
            )
        except ValueError:
            self.interval = raw_interval
        self.interval_count: int = data["interval_count"]
        self.tax_inclusive: bool = data["tax_inclusive"]
        self.price: int | dict[str, int] | None = data.get("price")
        self.currency: str | None = data.get("currency")
        self.prices: dict[SubscriptionPlanPurchaseType | int, SubscriptionPrices] = {}
        for raw_key, raw_value in data.get("prices", {}).items():
            try:
                key: SubscriptionPlanPurchaseType | int = to_enum(
                    SubscriptionPlanPurchaseType, int(raw_key)
                )
            except ValueError:
                key = int(raw_key)
            self.prices[key] = self._initialize_other(SubscriptionPrices, raw_value)


class EULA(BaseModel["store_types.EULAResponse"]):
    """End User License Agreement for an application.

    Attributes
    ----------
    id: :class:`int`
        The EULA snowflake.
    name: :class:`str`
        The EULA name.
    content: :class:`str`
        The EULA content.
    """

    __slots__ = ("content", "id", "name")

    @override
    def _initialize(self, data: store_types.EULAResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.content: str = data["content"]


class StorefrontLeaderboard(BaseModel["store_types.StorefrontLeaderboardResponse"]):
    """Leaderboard shown on a storefront page.

    Attributes
    ----------
    title: :class:`str`
        The leaderboard title, if present.
    description: :class:`str`
        The leaderboard description, if present.
    background_image_asset_id: :class:`int`
        The background image store asset snowflake, if present.
    """

    __slots__ = ("background_image_asset_id", "description", "title")

    @override
    def _initialize(self, data: store_types.StorefrontLeaderboardResponse) -> None:
        self.title: str | None = data.get("title")
        self.description: str | None = data.get("description")
        self.background_image_asset_id: int | None = convert_snowflake(
            data, "background_image_asset_id", always_available=False
        )


class StorefrontPageSection(BaseModel["store_types.StorefrontPageSectionResponse"]):
    """Section within a storefront page.

    Attributes
    ----------
    title: :class:`str`
        The section title, if present.
    sku_ids: list[:class:`int`]
        SKU snowflakes included in the section.
    """

    __slots__ = ("sku_ids", "title")

    @override
    def _initialize(self, data: store_types.StorefrontPageSectionResponse) -> None:
        self.title: str | None = data.get("title")
        self.sku_ids: list[int] = [int(sku_id) for sku_id in data["sku_ids"]]


class StorefrontPage(BaseModel["store_types.StorefrontPageResponse"]):
    """Page within a storefront.

    Attributes
    ----------
    title: :class:`str`
        The page title, if present.
    leaderboard: :class:`StorefrontLeaderboard`
        The leaderboard shown on the page, if present.
    sku_ids: list[:class:`int`]
        SKU snowflakes attached directly to the page.
    sections: list[:class:`StorefrontPageSection`]
        Sections contained in the page.
    """

    __slots__ = ("leaderboard", "sections", "sku_ids", "title")

    @override
    def _initialize(self, data: store_types.StorefrontPageResponse) -> None:
        self.title: str | None = data.get("title")
        self.leaderboard: StorefrontLeaderboard | None = self._initialize_other(
            StorefrontLeaderboard, data, possible_keys="leaderboard", optional=True
        )
        self.sku_ids: list[int] = [int(sku_id) for sku_id in data["sku_ids"]]
        self.sections: list[StorefrontPageSection] = [
            self._initialize_other(StorefrontPageSection, section)
            for section in data.get("sections", [])
        ]


class Storefront(BaseModelWithSession["store_types.StorefrontResponse"]):
    """Unified storefront for an application.

    Attributes
    ----------
    application_id: :class:`int`
        The owning application snowflake.
    application: :class:`PartialApplication`
        Partial application metadata, if included.
    title: :class:`str`
        The storefront title.
    logo_asset_id: :class:`int`
        The storefront logo asset snowflake, if present.
    light_theme_logo_asset_id: :class:`int`
        The light-theme logo asset snowflake, if present.
    pages: list[:class:`StorefrontPage`]
        Pages defined for the storefront.
    store_listings: list[:class:`StoreListing`]
        Store listings included in the storefront.
    assets: list[:class:`StoreAsset`]
        Store assets available to the storefront.
    """

    __slots__ = (
        "application",
        "application_id",
        "assets",
        "light_theme_logo_asset_id",
        "logo_asset_id",
        "pages",
        "store_listings",
        "title",
    )

    @override
    def _initialize(self, data: store_types.StorefrontResponse) -> None:
        self.application_id: int = convert_snowflake(data, "application_id")
        self.application: PartialApplication | None = self._initialize_other(
            PartialApplication, data, possible_keys="application", optional=True
        )
        self.title: str = data["title"]
        self.logo_asset_id: int | None = convert_snowflake(
            data, "logo_asset_id", always_available=False
        )
        self.light_theme_logo_asset_id: int | None = convert_snowflake(
            data, "light_theme_logo_asset_id", always_available=False
        )
        self.pages: list[StorefrontPage] = [
            self._initialize_other(StorefrontPage, page) for page in data["pages"]
        ]
        self.store_listings: list[StoreListing] = [
            self._initialize_other(StoreListing, listing)
            for listing in data["store_listings"]
        ]
        self.assets: list[StoreAsset] = [
            self._initialize_other(StoreAsset, asset) for asset in data["assets"]
        ]


class StorefrontCollection(BaseModel["store_types.StorefrontCollectionResponse"]):
    """Collection of storefront products.

    Attributes
    ----------
    id: :class:`int`
        The storefront collection snowflake.
    application_id: :class:`int`
        The owning application snowflake.
    name: :class:`str`
        The collection name.
    description: :class:`str`
        The collection description.
    product_ids: list[:class:`int`]
        Storefront product snowflakes in the collection.
    created_at: :class:`datetime.datetime`
        When the collection was created.
    updated_at: :class:`datetime.datetime`
        When the collection was last updated.
    tenant_metadata: :class:`dict`
        Raw tenant metadata returned for the collection.
    """

    __slots__ = (
        "application_id",
        "created_at",
        "description",
        "id",
        "name",
        "product_ids",
        "tenant_metadata",
        "updated_at",
    )

    @override
    def _initialize(self, data: store_types.StorefrontCollectionResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.application_id: int = convert_snowflake(data, "application_id")
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.product_ids: list[int] = [
            int(product_id) for product_id in data["product_ids"]
        ]
        self.created_at: datetime.datetime = iso_to_datetime(data["created_at"])
        self.updated_at: datetime.datetime = iso_to_datetime(data["updated_at"])
        self.tenant_metadata: dict[str, object] = data["tenant_metadata"]


class ProductOption(BaseModel["store_types.ProductOptionResponse"]):
    """Selectable product option for a storefront product.

    Attributes
    ----------
    name: :class:`str`
        The option name.
    option_values: list[:class:`str`]
        Allowed option values.
    """

    __slots__ = ("name", "option_values")

    @override
    def _initialize(self, data: store_types.ProductOptionResponse) -> None:
        self.name: str = data["name"]
        self.option_values: list[str] = data["option_values"]


class GameServerInstructions(BaseModel["store_types.GameServerInstructionsResponse"]):
    """Instructions for joining a game server product.

    Attributes
    ----------
    pc: list[:class:`str`]
        Instructions shown to PC players.
    """

    __slots__ = ("pc",)

    @override
    def _initialize(self, data: store_types.GameServerInstructionsResponse) -> None:
        self.pc: list[str] = data["pc"]


class GameServerPowerupProductMetadata(
    BaseModel["store_types.GameServerPowerupProductMetadataResponse"]
):
    """Game server product metadata for storefront products.

    Attributes
    ----------
    instructions: :class:`GameServerInstructions`
        Instructions for joining the server.
    deactivation_cooldown_period_days: :class:`int`
        Days before the server can be disabled.
    game_application_id: :class:`int`
        The backing game application snowflake.
    provider: :class:`str`
        The game server provider identifier.
    disabled: :class:`bool`
        Whether the product is disabled.
    early_access: :class:`bool`
        Whether the product is in early access.
    can_market: :class:`bool`
        Whether the product can be marketed.
    """

    __slots__ = (
        "can_market",
        "deactivation_cooldown_period_days",
        "disabled",
        "early_access",
        "game_application_id",
        "instructions",
        "provider",
    )

    @override
    def _initialize(
        self, data: store_types.GameServerPowerupProductMetadataResponse
    ) -> None:
        self.instructions: GameServerInstructions = self._initialize_other(
            GameServerInstructions, data, possible_keys="instructions"
        )
        self.deactivation_cooldown_period_days: int = data[
            "deactivation_cooldown_period_days"
        ]
        self.game_application_id: int = convert_snowflake(data, "game_application_id")
        self.provider: str = data["provider"]
        self.disabled: bool = data["disabled"]
        self.early_access: bool = data["early_access"]
        self.can_market: bool = data["can_market"]


class GuildMonetizationProductMetadata(
    BaseModel["store_types.GuildMonetizationProductMetadataResponse"]
):
    """Guild monetization metadata for a storefront product.

    Attributes
    ----------
    game_server: :class:`GameServerPowerupProductMetadata`
        Game server product metadata, if included.
    """

    __slots__ = ("game_server",)

    @override
    def _initialize(
        self, data: store_types.GuildMonetizationProductMetadataResponse
    ) -> None:
        self.game_server: GameServerPowerupProductMetadata | None = (
            self._initialize_other(
                GameServerPowerupProductMetadata,
                data,
                possible_keys="game_server",
                optional=True,
            )
        )


class ProductTenantMetadata(BaseModel["store_types.ProductTenantMetadataResponse"]):
    """Tenant metadata attached to a storefront product.

    Attributes
    ----------
    guild_monetization: :class:`GuildMonetizationProductMetadata`
        Guild monetization metadata, if included.
    """

    __slots__ = ("guild_monetization",)

    @override
    def _initialize(self, data: store_types.ProductTenantMetadataResponse) -> None:
        self.guild_monetization: GuildMonetizationProductMetadata | None = (
            self._initialize_other(
                GuildMonetizationProductMetadata,
                data,
                possible_keys="guild_monetization",
                optional=True,
            )
        )


class ProductSKUPlanFeature(BaseModel["store_types.ProductSKUPlanFeatureResponse"]):
    """Feature badge shown for a product SKU plan.

    Attributes
    ----------
    title: :class:`str`
        The feature title.
    description: :class:`str`
        The feature description.
    """

    __slots__ = ("description", "title")

    @override
    def _initialize(self, data: store_types.ProductSKUPlanFeatureResponse) -> None:
        self.title: str = data["title"]
        self.description: str = data["description"]


class ProductSKUTenantMetadata(
    BaseModel["store_types.ProductSKUTenantMetadataResponse"]
):
    """Tenant metadata attached to a storefront product SKU.

    Attributes
    ----------
    boost_price: :class:`int`
        The number of boosts required for the plan.
    purchase_limit: :class:`int`
        The maximum number of entitlements for the plan.
    category_type: :class:`GuildPowerupCategoryType` | :class:`str`
        The powerup category type.
    plan_features: list[:class:`ProductSKUPlanFeature`]
        Plan features shown for the SKU.
    """

    __slots__ = ("boost_price", "category_type", "plan_features", "purchase_limit")

    @override
    def _initialize(self, data: store_types.ProductSKUTenantMetadataResponse) -> None:
        self.boost_price: int = data["boost_price"]
        self.purchase_limit: int = data["purchase_limit"]
        raw_category = data["category_type"]
        try:
            self.category_type: GuildPowerupCategoryType | str = to_enum(
                GuildPowerupCategoryType, raw_category
            )
        except ValueError:
            self.category_type = raw_category
        self.plan_features: list[ProductSKUPlanFeature] = [
            self._initialize_other(ProductSKUPlanFeature, feature)
            for feature in data["plan_features"]
        ]


class ProductSKUOption(BaseModel["store_types.ProductSKUOptionResponse"]):
    """Selected option value for a product SKU.

    Attributes
    ----------
    option_name: :class:`str`
        The option name.
    option_value: :class:`str`
        The selected option value.
    """

    __slots__ = ("option_name", "option_value")

    @override
    def _initialize(self, data: store_types.ProductSKUOptionResponse) -> None:
        self.option_name: str = data["option_name"]
        self.option_value: str = data["option_value"]


class ProductSKU(BaseModel["store_types.ProductSKUResponse"]):
    """SKU variant attached to a storefront product.

    Attributes
    ----------
    id: :class:`int`
        The SKU snowflake.
    type: :class:`SKUType` | :class:`int`
        The SKU type.
    product_line: :class:`SKUProductLine` | :class:`int`
        The SKU product line.
    application_id: :class:`int`
        The owning application snowflake.
    name: :class:`str`
        The SKU name.
    thumbnail_asset_id: :class:`int`
        The thumbnail store asset snowflake, if present.
    slug: :class:`str`
        The URL slug.
    premium: :class:`bool`
        Whether the SKU is a premium user perk.
    selected_options: list[:class:`ProductSKUOption`]
        Selected option values for the SKU.
    product_id: :class:`int`
        The parent product snowflake.
    position: :class:`int`
        The ordering position of the SKU.
    tenant_metadata: :class:`ProductSKUTenantMetadata`
        Tenant metadata for the SKU.
    """

    __slots__ = (
        "application_id",
        "id",
        "name",
        "position",
        "premium",
        "product_id",
        "product_line",
        "selected_options",
        "slug",
        "tenant_metadata",
        "thumbnail_asset_id",
        "type",
    )

    @override
    def _initialize(self, data: store_types.ProductSKUResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        raw_type = data["type"]
        try:
            self.type: SKUType | int = to_enum(SKUType, raw_type)
        except ValueError:
            self.type = raw_type
        raw_product_line = data["product_line"]
        try:
            self.product_line: SKUProductLine | int = to_enum(
                SKUProductLine, raw_product_line
            )
        except ValueError:
            self.product_line = raw_product_line
        self.application_id: int = convert_snowflake(data, "application_id")
        self.name: str = data["name"]
        self.thumbnail_asset_id: int | None = convert_snowflake(
            data, "thumbnail_asset_id", always_available=False
        )
        self.slug: str = data["slug"]
        self.premium: bool = data["premium"]
        self.selected_options: list[ProductSKUOption] = [
            self._initialize_other(ProductSKUOption, option)
            for option in data["selected_options"]
        ]
        self.product_id: int = convert_snowflake(data, "product_id")
        self.position: int = data["position"]
        self.tenant_metadata: ProductSKUTenantMetadata = self._initialize_other(
            ProductSKUTenantMetadata, data, possible_keys="tenant_metadata"
        )


class StorefrontProduct(BaseModel["store_types.StorefrontProductResponse"]):
    """Modern storefront product abstraction for Discord marketplace items.

    Attributes
    ----------
    id: :class:`int`
        The storefront product snowflake.
    application_id: :class:`int`
        The owning application snowflake.
    sku_ids: list[:class:`int`]
        SKU snowflakes associated with the product.
    name: :class:`str`
        The product name.
    options: list[:class:`ProductOption`]
        Product options for the plan variants.
    created_at: :class:`datetime.datetime`
        When the product was created.
    updated_at: :class:`datetime.datetime`
        When the product was last updated.
    tenant_metadata: :class:`ProductTenantMetadata`
        Tenant metadata attached to the product.
    skus: list[:class:`ProductSKU`]
        SKU variants associated with the product.
    """

    __slots__ = (
        "application_id",
        "created_at",
        "id",
        "name",
        "options",
        "sku_ids",
        "skus",
        "tenant_metadata",
        "updated_at",
    )

    @override
    def _initialize(self, data: store_types.StorefrontProductResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.application_id: int = convert_snowflake(data, "application_id")
        self.sku_ids: list[int] = [int(sku_id) for sku_id in data["sku_ids"]]
        self.name: str = data["name"]
        self.options: list[ProductOption] = [
            self._initialize_other(ProductOption, option) for option in data["options"]
        ]
        self.created_at: datetime.datetime = iso_to_datetime(data["created_at"])
        self.updated_at: datetime.datetime = iso_to_datetime(data["updated_at"])
        self.tenant_metadata: ProductTenantMetadata = self._initialize_other(
            ProductTenantMetadata, data, possible_keys="tenant_metadata"
        )
        self.skus: list[ProductSKU] = [
            self._initialize_other(ProductSKU, sku) for sku in data["skus"]
        ]
