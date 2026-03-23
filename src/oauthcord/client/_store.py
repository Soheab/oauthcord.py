import datetime
from typing import TYPE_CHECKING

from .. import utils
from ..models.flags import SKUFlags
from ..models.store import (
    SKU,
    ContentRating,
    LocalizedString,
    StoreAsset,
    StoreCarouselItem,
    StoreListing,
    SubscriptionPlan,
    SystemRequirements,
)

if TYPE_CHECKING:
    from ..internals._types import store as store_types
    from ..models.file import File
    from ._base import _AuthorisedSessionProto


class StoreClient:
    async def get_application_skus(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        country_code: str = utils.NotSet,
        localize: bool = utils.NotSet,
        with_bundled_skus: bool = utils.NotSet,
    ) -> list[SKU]:
        """Fetch SKUs for an application.

        Current user must be the owner of the application or be a member
        of the owning team.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The application ID to fetch SKUs for.
        country_code: :class:`str` | ``None``
            ISO 3166-1 alpha-2 country code used for localization.
        localize: :class:`bool` | ``None``
            Whether to localize SKU strings and prices for the request context.
        with_bundled_skus: :class:`bool` | ``None``
            Whether bundled SKU objects should be included in each SKU payload.

        Returns
        -------
        list[:class:`SKU`]
            SKUs for the target application.
        """

        res = await self.client.http.get_application_skus(
            self.token,
            application_id=application_id,
            country_code=country_code,
            localize=localize,
            with_bundled_skus=with_bundled_skus,
        )
        return [utils._construct_model(SKU, data=sku, session=self) for sku in res]

    async def create_sku(
        self: _AuthorisedSessionProto,
        *,
        type: store_types.SKUType | int,
        application_id: int | str,
        name: store_types.LocalizedString | LocalizedString,
        flags: SKUFlags | int | None = None,
        legal_notice: store_types.LocalizedString | LocalizedString | None = None,
        dependent_sku_id: int | str | None = None,
        bundled_skus: list[int | str] | None = None,
        access_type: store_types.SKUAccessType | int | None = None,
        manifest_labels: list[int | str] | None = None,
        features: list[store_types.SKUFeature | int] | None = None,
        locales: list[str] | None = None,
        genres: list[store_types.SKUGenre | int] | None = None,
        content_ratings: (
            dict[
                store_types.ContentRatingAgency | int,
                store_types.ContentRatingResponse | ContentRating,
            ]
            | None
        ) = None,
        system_requirements: (
            dict[
                store_types.OperatingSystem | int,
                store_types.SystemRequirementsResponse | SystemRequirements,
            ]
            | None
        ) = None,
        price_tier: int | None = None,
        price: dict[str, int] | None = None,
        sale_price_tier: int | None = None,
        sale_price: dict[str, int] | None = None,
        release_date: datetime.date | str | None = None,
    ) -> SKU:
        """Create a new SKU.

        This requires an application with access to the store or monetization.
        The current user must be the owner of the application or be a member of
        the owning team.

        Parameters
        ----------
        type: :class:`store_types.SKUType` | :class:`int`
            The SKU type.
        application_id: :class:`int` | :class:`str`
            The application ID that owns the SKU.
        name: :class:`store_types.LocalizedString`
            Localized SKU name.
        flags: :class:`int` | ``None``
            SKU flag bitfield.
        legal_notice: :class:`store_types.LocalizedString` | ``None``
            Localized legal notice.
        dependent_sku_id: :class:`int` | :class:`str` | ``None``
            Prerequisite SKU ID required for purchase.
        bundled_skus: list[:class:`int` | :class:`str`] | ``None``
            Included SKU IDs for bundle purchases.
        access_type: :class:`store_types.SKUAccessType` | :class:`int` | ``None``
            Access type of the SKU.
        manifest_labels: list[:class:`int` | :class:`str`] | ``None``
            Manifest label IDs associated with the SKU.
        features: list[:class:`store_types.SKUFeature` | :class:`int`] | ``None``
            Feature identifiers for the SKU.
        locales: list[:class:`str`] | ``None``
            Locale codes where the SKU is available.
        genres: list[:class:`store_types.SKUGenre` | :class:`int`] | ``None``
            Genre identifiers for the SKU.
        content_ratings: :class:`dict` | ``None``
            Mapping of content-rating agency values (enum or int) to rating payloads.
        system_requirements: :class:`dict` | ``None``
            Mapping of operating-system values (enum or int) to system requirement payloads.
        price_tier: :class:`int` | ``None``
            Base price tier.
        price: dict[:class:`str`, :class:`int`] | ``None``
            Currency-to-price overrides.
        sale_price_tier: :class:`int` | ``None``
            Sale price tier.
        sale_price: dict[:class:`str`, :class:`int`] | ``None``
            Currency-to-sale-price overrides.
        release_date: :class:`datetime.date` | :class:`str` | ``None``
            Release date in ISO format.

        Returns
        -------
        :class:`SKU`
            The created SKU.
        """
        flags_ = flags.value if isinstance(flags, SKUFlags) else flags

        res = await self.client.http.create_sku(
            self.token,
            type=type,
            application_id=application_id,
            name=name,
            flags=flags_,
            legal_notice=legal_notice,
            dependent_sku_id=dependent_sku_id,
            bundled_skus=bundled_skus,
            access_type=access_type,
            manifest_labels=manifest_labels,
            features=features,
            locales=locales,
            genres=genres,
            content_ratings=content_ratings,
            system_requirements=system_requirements,
            price_tier=price_tier,
            price=price,
            sale_price_tier=sale_price_tier,
            sale_price=sale_price,
            release_date=release_date.isoformat()
            if isinstance(release_date, datetime.date)
            else release_date,
        )
        return utils._construct_model(SKU, data=res, session=self)

    async def get_sku(
        self: _AuthorisedSessionProto,
        *,
        sku_id: int | str,
        country_code: str | None = None,
        localize: bool | None = None,
    ) -> SKU:
        """Fetch a SKU.

        Parameters
        ----------
        sku_id: :class:`int` | :class:`str`
            The SKU ID.
        country_code: :class:`str` | ``None``
            ISO 3166-1 alpha-2 country code used for localization.
        localize: :class:`bool` | ``None``
            Whether to localize SKU strings and prices for the request context.

        Returns
        -------
        :class:`SKU`
            The fetched SKU.
        """

        res = await self.client.http.get_sku(
            self.token,
            sku_id=sku_id,
            country_code=country_code,
            localize=localize,
        )
        return utils._construct_model(SKU, data=res, session=self)

    async def modify_sku(
        self: _AuthorisedSessionProto,
        *,
        sku_id: int | str,
        name: store_types.LocalizedString | LocalizedString | None = None,
        flags: SKUFlags | int | None = None,
        legal_notice: store_types.LocalizedString | LocalizedString | None = None,
        dependent_sku_id: int | str | None = None,
        bundled_skus: list[int | str] | None = None,
        access_type: store_types.SKUAccessType | int | None = None,
        manifest_labels: list[int | str] | None = None,
        features: list[store_types.SKUFeature | int] | None = None,
        locales: list[str] | None = None,
        genres: list[store_types.SKUGenre | int] | None = None,
        content_ratings: (
            dict[
                store_types.ContentRatingAgency | int,
                store_types.ContentRatingResponse | ContentRating,
            ]
            | None
        ) = None,
        system_requirements: (
            dict[
                store_types.OperatingSystem | int,
                store_types.SystemRequirementsResponse | SystemRequirements,
            ]
            | None
        ) = None,
        price_tier: int | None = None,
        price: dict[str, int] | None = None,
        sale_price_tier: int | None = None,
        sale_price: dict[str, int] | None = None,
        release_date: datetime.date | str | None = None,
    ) -> SKU:
        """Modify an existing SKU.

        Parameters
        ----------
        sku_id: :class:`int` | :class:`str`
            The SKU ID.
        name: :class:`store_types.LocalizedString` | ``None``
            Localized SKU name.
        flags: :class:`int` | ``None``
            SKU flag bitfield.
        legal_notice: :class:`store_types.LocalizedString` | ``None``
            Localized legal notice.
        dependent_sku_id: :class:`int` | :class:`str` | ``None``
            Prerequisite SKU ID required for purchase.
        bundled_skus: list[:class:`int` | :class:`str`] | ``None``
            Included SKU IDs for bundle purchases.
        access_type: :class:`store_types.SKUAccessType` | :class:`int` | ``None``
            Access type of the SKU.
        manifest_labels: list[:class:`int` | :class:`str`] | ``None``
            Manifest label IDs associated with the SKU.
        features: list[:class:`store_types.SKUFeature` | :class:`int`] | ``None``
            Feature identifiers for the SKU.
        locales: list[:class:`str`] | ``None``
            Locale codes where the SKU is available.
        genres: list[:class:`store_types.SKUGenre` | :class:`int`] | ``None``
            Genre identifiers for the SKU.
        content_ratings: :class:`dict` | ``None``
            Mapping of content-rating agency values (enum or int) to rating payloads.
        system_requirements: :class:`dict` | ``None``
            Mapping of operating-system values (enum or int) to system requirement payloads.
        price_tier: :class:`int` | ``None``
            Base price tier.
        price: dict[:class:`str`, :class:`int`] | ``None``
            Currency-to-price overrides.
        sale_price_tier: :class:`int` | ``None``
            Sale price tier.
        sale_price: dict[:class:`str`, :class:`int`] | ``None``
            Currency-to-sale-price overrides.
        release_date: :class:`datetime.date` | :class:`str` | ``None``
            Release date in ISO format.

        Returns
        -------
        :class:`SKU`
            The modified SKU.
        """
        flags_ = flags.value if isinstance(flags, SKUFlags) else flags

        res = await self.client.http.modify_sku(
            self.token,
            sku_id=sku_id,
            name=name,
            flags=flags_,
            legal_notice=legal_notice,
            dependent_sku_id=dependent_sku_id,
            bundled_skus=bundled_skus,
            access_type=access_type,
            manifest_labels=manifest_labels,
            features=features,
            locales=locales,
            genres=genres,
            content_ratings=content_ratings,
            system_requirements=system_requirements,
            price_tier=price_tier,
            price=price,
            sale_price_tier=sale_price_tier,
            sale_price=sale_price,
            release_date=release_date.isoformat()
            if isinstance(release_date, datetime.date)
            else release_date,
        )
        return utils._construct_model(SKU, data=res, session=self)

    async def get_sku_store_listings(
        self: _AuthorisedSessionProto,
        *,
        sku_id: int | str,
        country_code: str | None = None,
        localize: bool | None = None,
    ) -> list[StoreListing]:
        """Fetch store listings for a SKU.

        Parameters
        ----------
        sku_id: :class:`int` | :class:`str`
            The SKU ID.
        country_code: :class:`str` | ``None``
            ISO 3166-1 alpha-2 country code used for localization.
        localize: :class:`bool` | ``None``
            Whether to localize listing strings and prices for the request context.

        Returns
        -------
        list[:class:`StoreListing`]
            Store listings associated with the SKU.
        """

        res = await self.client.http.get_sku_store_listings(
            self.token,
            sku_id=sku_id,
            country_code=country_code,
            localize=localize,
        )
        return [
            utils._construct_model(StoreListing, data=listing, session=self)
            for listing in res
        ]

    async def create_store_listing(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        sku_id: int | str,
        summary: store_types.LocalizedString | LocalizedString,
        description: store_types.LocalizedString | LocalizedString,
        child_sku_ids: list[int | str] | None = None,
        tagline: store_types.LocalizedString | LocalizedString | None = None,
        published: bool | None = None,
        carousel_items: list[store_types.StoreCarouselItemResponse | StoreCarouselItem]
        | None = None,
        guild_id: int | str | None = None,
        thumbnail_asset_id: int | str | None = None,
        preview_video_asset_id: int | str | None = None,
        header_background_asset_id: int | str | None = None,
        header_logo_dark_theme_asset_id: int | str | None = None,
        header_logo_light_theme_asset_id: int | str | None = None,
        box_art_asset_id: int | str | None = None,
        hero_background_asset_id: int | str | None = None,
        hero_video_asset_id: int | str | None = None,
    ) -> StoreListing:
        """Create a store listing.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The application ID that owns the listing.
        sku_id: :class:`int` | :class:`str`
            The parent SKU ID for the listing.
        summary: :class:`store_types.LocalizedString`
            Localized listing summary.
        description: :class:`store_types.LocalizedString`
            Localized listing description.
        child_sku_ids: list[:class:`int` | :class:`str`] | ``None``
            Child SKU IDs for category listings.
        tagline: :class:`store_types.LocalizedString` | ``None``
            Localized listing tagline.
        published: :class:`bool` | ``None``
            Whether the listing is published.
        carousel_items: list[:class:`store_types.StoreCarouselItemResponse`] | ``None``
            Carousel media items.
        guild_id: :class:`int` | :class:`str` | ``None``
            Public guild ID associated with the listing.
        thumbnail_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for thumbnail.
        preview_video_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for preview video.
        header_background_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for header background.
        header_logo_dark_theme_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for dark-theme header logo.
        header_logo_light_theme_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for light-theme header logo.
        box_art_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for box art.
        hero_background_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for hero background.
        hero_video_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for hero video.

        Returns
        -------
        :class:`StoreListing`
            The created store listing.
        """

        res = await self.client.http.create_store_listing(
            self.token,
            application_id=application_id,
            sku_id=sku_id,
            summary=summary,
            description=description,
            child_sku_ids=child_sku_ids,
            tagline=tagline,
            published=published,
            carousel_items=carousel_items,
            guild_id=guild_id,
            thumbnail_asset_id=thumbnail_asset_id,
            preview_video_asset_id=preview_video_asset_id,
            header_background_asset_id=header_background_asset_id,
            header_logo_dark_theme_asset_id=header_logo_dark_theme_asset_id,
            header_logo_light_theme_asset_id=header_logo_light_theme_asset_id,
            box_art_asset_id=box_art_asset_id,
            hero_background_asset_id=hero_background_asset_id,
            hero_video_asset_id=hero_video_asset_id,
        )
        return utils._construct_model(StoreListing, data=res, session=self)

    async def get_store_listing(
        self: _AuthorisedSessionProto,
        *,
        listing_id: int | str,
        country_code: str | None = None,
        localize: bool | None = None,
    ) -> StoreListing:
        """Fetch a store listing.

        Parameters
        ----------
        listing_id: :class:`int` | :class:`str`
            The store listing ID.
        country_code: :class:`str` | ``None``
            ISO 3166-1 alpha-2 country code used for localization.
        localize: :class:`bool` | ``None``
            Whether to localize listing strings and prices for the request context.

        Returns
        -------
        :class:`StoreListing`
            The fetched store listing.
        """

        res = await self.client.http.get_store_listing(
            self.token,
            listing_id=listing_id,
            country_code=country_code,
            localize=localize,
        )
        return utils._construct_model(StoreListing, data=res, session=self)

    async def modify_store_listing(
        self: _AuthorisedSessionProto,
        *,
        listing_id: int | str,
        child_sku_ids: list[int | str] | None = None,
        summary: store_types.LocalizedString | LocalizedString | None = None,
        description: store_types.LocalizedString | LocalizedString | None = None,
        tagline: store_types.LocalizedString | LocalizedString | None = None,
        published: bool | None = None,
        carousel_items: list[store_types.StoreCarouselItemResponse | StoreCarouselItem]
        | None = None,
        guild_id: int | str | None = None,
        thumbnail_asset_id: int | str | None = None,
        preview_video_asset_id: int | str | None = None,
        header_background_asset_id: int | str | None = None,
        header_logo_dark_theme_asset_id: int | str | None = None,
        header_logo_light_theme_asset_id: int | str | None = None,
        box_art_asset_id: int | str | None = None,
        hero_background_asset_id: int | str | None = None,
        hero_video_asset_id: int | str | None = None,
    ) -> StoreListing:
        """Modify a store listing.

        Parameters
        ----------
        listing_id: :class:`int` | :class:`str`
            The store listing ID.
        child_sku_ids: list[:class:`int` | :class:`str`] | ``None``
            Child SKU IDs for category listings.
        summary: :class:`store_types.LocalizedString` | ``None``
            Localized listing summary.
        description: :class:`store_types.LocalizedString` | ``None``
            Localized listing description.
        tagline: :class:`store_types.LocalizedString` | ``None``
            Localized listing tagline.
        published: :class:`bool` | ``None``
            Whether the listing is published.
        carousel_items: list[:class:`store_types.StoreCarouselItemResponse`] | ``None``
            Carousel media items.
        guild_id: :class:`int` | :class:`str` | ``None``
            Public guild ID associated with the listing.
        thumbnail_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for thumbnail.
        preview_video_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for preview video.
        header_background_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for header background.
        header_logo_dark_theme_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for dark-theme header logo.
        header_logo_light_theme_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for light-theme header logo.
        box_art_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for box art.
        hero_background_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for hero background.
        hero_video_asset_id: :class:`int` | :class:`str` | ``None``
            Store asset ID for hero video.

        Returns
        -------
        :class:`StoreListing`
            The modified store listing.
        """

        res = await self.client.http.modify_store_listing(
            self.token,
            listing_id=listing_id,
            child_sku_ids=child_sku_ids,
            summary=summary,
            description=description,
            tagline=tagline,
            published=published,
            carousel_items=carousel_items,
            guild_id=guild_id,
            thumbnail_asset_id=thumbnail_asset_id,
            preview_video_asset_id=preview_video_asset_id,
            header_background_asset_id=header_background_asset_id,
            header_logo_dark_theme_asset_id=header_logo_dark_theme_asset_id,
            header_logo_light_theme_asset_id=header_logo_light_theme_asset_id,
            box_art_asset_id=box_art_asset_id,
            hero_background_asset_id=hero_background_asset_id,
            hero_video_asset_id=hero_video_asset_id,
        )
        return utils._construct_model(StoreListing, data=res, session=self)

    async def delete_store_listing(
        self: _AuthorisedSessionProto,
        *,
        listing_id: int | str,
    ) -> None:
        """Delete a store listing.

        Parameters
        ----------
        listing_id: :class:`int` | :class:`str`
            The store listing ID.
        """

        await self.client.http.delete_store_listing(
            self.token,
            listing_id=listing_id,
        )

    async def get_subscription_plans(
        self: _AuthorisedSessionProto,
        *,
        sku_id: int | str,
    ) -> list[SubscriptionPlan]:
        """Fetch subscription plans for a SKU.

        Parameters
        ----------
        sku_id: :class:`int` | :class:`str`
            The SKU ID.

        Returns
        -------
        list[:class:`SubscriptionPlan`]
            Subscription plans for the SKU.
        """

        res = await self.client.http.get_subscription_plans(self.token, sku_id=sku_id)
        return [utils._construct_model(SubscriptionPlan, data=plan) for plan in res]

    async def get_application_store_assets(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
    ) -> list[StoreAsset]:
        """Fetch store assets for an application.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The application ID.

        Returns
        -------
        list[:class:`StoreAsset`]
            Store assets for the application.
        """

        res = await self.client.http.get_application_store_assets(
            self.token,
            application_id=application_id,
        )
        return [utils._construct_model(StoreAsset, data=asset) for asset in res]

    async def create_application_store_asset(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        file: File,
    ) -> StoreAsset:
        """Upload a store asset for an application.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The application ID.
        file: :class:`File`
            The file to upload.

        Returns
        -------
        :class:`StoreAsset`
            The uploaded store asset.
        """

        res = await self.client.http.create_application_store_asset(
            self.token,
            application_id=application_id,
            file=file,
        )
        return utils._construct_model(StoreAsset, data=res)

    async def delete_application_store_asset(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        asset_id: int | str,
    ) -> None:
        """Delete a store asset for an application.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The application ID.
        asset_id: :class:`int` | :class:`str`
            The store asset ID.
        """

        await self.client.http.delete_application_store_asset(
            self.token,
            application_id=application_id,
            asset_id=asset_id,
        )
