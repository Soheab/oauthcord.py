from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

import aiohttp

from ... import utils
from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from ...models.file import File
    from ...models.store import (
        ContentRating,
        LocalizedString,
        StoreCarouselItem,
        SystemRequirements,
    )
    from .._types import store as store_types
    from .base import ValidToken


def _coerce_store_literal(value: int | object) -> int:
    return int(value)  # type: ignore[arg-type]


class StoreHTTPClientMixin(BaseHTTPClient):
    async def get_application_skus(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        country_code: str = utils.NotSet,
        localize: bool = utils.NotSet,
        with_bundled_skus: bool = utils.NotSet,
    ) -> list[store_types.SKU]:
        params: store_types.GetApplicationSKUsRequest = {}
        if country_code is not utils.NotSet:
            params["country_code"] = country_code
        if localize is not utils.NotSet:
            params["localize"] = localize
        if with_bundled_skus is not utils.NotSet:
            params["with_bundled_skus"] = with_bundled_skus

        return await self.request(
            Route("GET", f"/applications/{application_id}/skus"),
            token=token,
            params=params,
        )

    async def create_sku(
        self,
        token: ValidToken,
        *,
        type: store_types.SKUType | int,
        application_id: int | str,
        name: store_types.LocalizedString | LocalizedString,
        flags: int | None = None,
        legal_notice: store_types.LocalizedString | LocalizedString | None = None,
        dependent_sku_id: int | str | None = None,
        bundled_skus: list[int | str] | None = None,
        access_type: store_types.SKUAccessType | int | None = None,
        manifest_labels: list[int | str] | None = None,
        features: list[store_types.SKUFeature | int] | None = None,
        locales: list[str] | None = None,
        genres: list[store_types.SKUGenre | int] | None = None,
        content_ratings: (
            Mapping[
                store_types.ContentRatingAgency | int,
                store_types.ContentRatingResponse | ContentRating,
            ]
            | None
        ) = None,
        system_requirements: (
            Mapping[
                store_types.OperatingSystem | int,
                store_types.SystemRequirementsResponse | SystemRequirements,
            ]
            | None
        ) = None,
        price_tier: int | None = None,
        price: dict[str, int] | None = None,
        sale_price_tier: int | None = None,
        sale_price: dict[str, int] | None = None,
        release_date: str | None = None,
    ) -> store_types.SKU:
        data: store_types.CreateSKURequest = {
            "type": int(type),  # type: ignore
            "application_id": application_id,
            "name": cast(
                "store_types.LocalizedString",
                cast(Any, name)._to_request() if hasattr(name, "_to_request") else name,
            ),
        }
        if flags is not None:
            data["flags"] = flags
        if legal_notice is not None:
            data["legal_notice"] = cast(
                "store_types.LocalizedString",
                cast(Any, legal_notice)._to_request()
                if hasattr(legal_notice, "_to_request")
                else legal_notice,
            )
        if dependent_sku_id is not None:
            data["dependent_sku_id"] = dependent_sku_id
        if bundled_skus is not None:
            data["bundled_skus"] = bundled_skus
        if access_type is not None:
            data["access_type"] = int(access_type)  # pyright: ignore[reportGeneralTypeIssues]
        if manifest_labels is not None:
            data["manifest_labels"] = manifest_labels
        if features is not None:
            data["features"] = [int(feature) for feature in features]  # pyright: ignore[reportGeneralTypeIssues]
        if locales is not None:
            data["locales"] = locales
        if genres is not None:
            data["genres"] = [
                cast("store_types.SKUGenre", int(genre)) for genre in genres
            ]
        if content_ratings is not None:
            data["content_ratings"] = {  # pyright: ignore[reportGeneralTypeIssues]
                int(agency): cast(
                    "store_types.ContentRatingResponse",
                    cast(Any, rating)._to_request()
                    if hasattr(rating, "_to_request")
                    else rating,
                )
                for agency, rating in content_ratings.items()
            }
        if system_requirements is not None:
            data["system_requirements"] = {  # pyright: ignore[reportGeneralTypeIssues]
                int(os): cast(
                    "store_types.SystemRequirementsResponse",
                    cast(Any, req)._to_request()
                    if hasattr(req, "_to_request")
                    else req,
                )
                for os, req in system_requirements.items()
            }
        if price_tier is not None:
            data["price_tier"] = price_tier
        if price is not None:
            data["price"] = price
        if sale_price_tier is not None:
            data["sale_price_tier"] = sale_price_tier
        if sale_price is not None:
            data["sale_price"] = sale_price
        if release_date is not None:
            data["release_date"] = release_date

        return await self.request(
            Route("POST", "/store/skus"),
            token=token,
            json=data,
        )

    async def get_sku(
        self,
        token: ValidToken,
        *,
        sku_id: int | str,
        country_code: str | None = None,
        localize: bool | None = None,
    ) -> store_types.SKU:
        params: store_types.GetSKURequest = {}
        if country_code is not None:
            params["country_code"] = country_code
        if localize is not None:
            params["localize"] = localize

        return await self.request(
            Route("GET", f"/store/skus/{sku_id}"),
            token=token,
            params=params,
        )

    async def modify_sku(
        self,
        token: ValidToken,
        *,
        sku_id: int | str,
        name: store_types.LocalizedString | LocalizedString | None = None,
        flags: int | None = None,
        legal_notice: store_types.LocalizedString | LocalizedString | None = None,
        dependent_sku_id: int | str | None = None,
        bundled_skus: list[int | str] | None = None,
        access_type: store_types.SKUAccessType | int | None = None,
        manifest_labels: list[int | str] | None = None,
        features: list[store_types.SKUFeature | int] | None = None,
        locales: list[str] | None = None,
        genres: list[store_types.SKUGenre | int] | None = None,
        content_ratings: (
            Mapping[
                store_types.ContentRatingAgency | int,
                store_types.ContentRatingResponse | ContentRating,
            ]
            | None
        ) = None,
        system_requirements: (
            Mapping[
                store_types.OperatingSystem | int,
                store_types.SystemRequirementsResponse | SystemRequirements,
            ]
            | None
        ) = None,
        price_tier: int | None = None,
        price: dict[str, int] | None = None,
        sale_price_tier: int | None = None,
        sale_price: dict[str, int] | None = None,
        release_date: str | None = None,
    ) -> store_types.SKU:
        data: store_types.ModifySKURequest = {}
        if name is not None:
            data["name"] = cast(
                "store_types.LocalizedString",
                cast(Any, name)._to_request() if hasattr(name, "_to_request") else name,
            )
        if flags is not None:
            data["flags"] = flags
        if legal_notice is not None:
            data["legal_notice"] = cast(
                "store_types.LocalizedString",
                cast(Any, legal_notice)._to_request()
                if hasattr(legal_notice, "_to_request")
                else legal_notice,
            )
        if dependent_sku_id is not None:
            data["dependent_sku_id"] = dependent_sku_id
        if bundled_skus is not None:
            data["bundled_skus"] = bundled_skus
        if access_type is not None:
            data["access_type"] = int(access_type)  # pyright: ignore[reportGeneralTypeIssues]
        if manifest_labels is not None:
            data["manifest_labels"] = manifest_labels
        if features is not None:
            data["features"] = [
                cast("store_types.SKUFeature", _coerce_store_literal(feature))
                for feature in features
            ]
        if locales is not None:
            data["locales"] = locales
        if genres is not None:
            data["genres"] = [
                cast("store_types.SKUGenre", _coerce_store_literal(genre))
                for genre in genres
            ]
        if content_ratings is not None:
            data["content_ratings"] = {
                cast(
                    "store_types.ContentRatingAgency",
                    _coerce_store_literal(agency),
                ): cast(
                    "store_types.ContentRatingResponse",
                    cast(Any, rating)._to_request()
                    if hasattr(rating, "_to_request")
                    else rating,
                )
                for agency, rating in content_ratings.items()
            }
        if system_requirements is not None:
            data["system_requirements"] = {
                cast("store_types.OperatingSystem", _coerce_store_literal(os)): cast(
                    "store_types.SystemRequirementsResponse",
                    cast(Any, req)._to_request()
                    if hasattr(req, "_to_request")
                    else req,
                )
                for os, req in system_requirements.items()
            }
        if price_tier is not None:
            data["price_tier"] = price_tier
        if price is not None:
            data["price"] = price
        if sale_price_tier is not None:
            data["sale_price_tier"] = sale_price_tier
        if sale_price is not None:
            data["sale_price"] = sale_price
        if release_date is not None:
            data["release_date"] = release_date

        return await self.request(
            Route("PATCH", f"/store/skus/{sku_id}"),
            token=token,
            json=data,
        )

    async def get_sku_store_listings(
        self,
        token: ValidToken,
        *,
        sku_id: int | str,
        country_code: str | None = None,
        localize: bool | None = None,
    ) -> list[store_types.StoreListingResponse]:
        params: store_types.GetSKUStoreListingsRequest = {}
        if country_code is not None:
            params["country_code"] = country_code
        if localize is not None:
            params["localize"] = localize

        return await self.request(
            Route("GET", f"/store/skus/{sku_id}/listings"),
            token=token,
            params=params,
        )

    async def create_store_listing(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        sku_id: int | str,
        summary: store_types.LocalizedString | LocalizedString,
        description: store_types.LocalizedString | LocalizedString,
        child_sku_ids: list[int | str] | None = None,
        tagline: store_types.LocalizedString | LocalizedString | None = None,
        published: bool | None = None,
        carousel_items: Sequence[
            store_types.StoreCarouselItemResponse | StoreCarouselItem
        ]
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
    ) -> store_types.StoreListingResponse:
        data: store_types.CreateStoreListingRequest = {
            "application_id": application_id,
            "sku_id": sku_id,
            "summary": cast(
                "store_types.LocalizedString",
                cast(Any, summary)._to_request()
                if hasattr(summary, "_to_request")
                else summary,
            ),
            "description": cast(
                "store_types.LocalizedString",
                cast(Any, description)._to_request()
                if hasattr(description, "_to_request")
                else description,
            ),
        }
        if child_sku_ids is not None:
            data["child_sku_ids"] = child_sku_ids
        if tagline is not None:
            data["tagline"] = cast(
                "store_types.LocalizedString",
                cast(Any, tagline)._to_request()
                if hasattr(tagline, "_to_request")
                else tagline,
            )
        if published is not None:
            data["published"] = published
        if carousel_items is not None:
            data["carousel_items"] = [
                cast(
                    "store_types.StoreCarouselItemResponse",
                    cast(Any, item)._to_request()
                    if hasattr(item, "_to_request")
                    else item,
                )
                for item in carousel_items
            ]
        if guild_id is not None:
            data["guild_id"] = guild_id
        if thumbnail_asset_id is not None:
            data["thumbnail_asset_id"] = thumbnail_asset_id
        if preview_video_asset_id is not None:
            data["preview_video_asset_id"] = preview_video_asset_id
        if header_background_asset_id is not None:
            data["header_background_asset_id"] = header_background_asset_id
        if header_logo_dark_theme_asset_id is not None:
            data["header_logo_dark_theme_asset_id"] = header_logo_dark_theme_asset_id
        if header_logo_light_theme_asset_id is not None:
            data["header_logo_light_theme_asset_id"] = header_logo_light_theme_asset_id
        if box_art_asset_id is not None:
            data["box_art_asset_id"] = box_art_asset_id
        if hero_background_asset_id is not None:
            data["hero_background_asset_id"] = hero_background_asset_id
        if hero_video_asset_id is not None:
            data["hero_video_asset_id"] = hero_video_asset_id

        return await self.request(
            Route("POST", "/store/listings"),
            token=token,
            json=data,
        )

    async def get_store_listing(
        self,
        token: ValidToken,
        *,
        listing_id: int | str,
        country_code: str | None = None,
        localize: bool | None = None,
    ) -> store_types.StoreListingResponse:
        params: store_types.GetStoreListingRequest = {}
        if country_code is not None:
            params["country_code"] = country_code
        if localize is not None:
            params["localize"] = localize

        return await self.request(
            Route("GET", f"/store/listings/{listing_id}"),
            token=token,
            params=params,
        )

    async def modify_store_listing(
        self,
        token: ValidToken,
        *,
        listing_id: int | str,
        child_sku_ids: list[int | str] | None = None,
        summary: store_types.LocalizedString | LocalizedString | None = None,
        description: store_types.LocalizedString | LocalizedString | None = None,
        tagline: store_types.LocalizedString | LocalizedString | None = None,
        published: bool | None = None,
        carousel_items: Sequence[
            store_types.StoreCarouselItemResponse | StoreCarouselItem
        ]
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
    ) -> store_types.StoreListingResponse:
        data: store_types.ModifyStoreListingRequest = {}
        if child_sku_ids is not None:
            data["child_sku_ids"] = child_sku_ids
        if summary is not None:
            data["summary"] = cast(
                "store_types.LocalizedString",
                cast(Any, summary)._to_request()
                if hasattr(summary, "_to_request")
                else summary,
            )
        if description is not None:
            data["description"] = cast(
                "store_types.LocalizedString",
                cast(Any, description)._to_request()
                if hasattr(description, "_to_request")
                else description,
            )
        if tagline is not None:
            data["tagline"] = cast(
                "store_types.LocalizedString",
                cast(Any, tagline)._to_request()
                if hasattr(tagline, "_to_request")
                else tagline,
            )
        if published is not None:
            data["published"] = published
        if carousel_items is not None:
            data["carousel_items"] = [
                cast(
                    "store_types.StoreCarouselItemResponse",
                    cast(Any, item)._to_request()
                    if hasattr(item, "_to_request")
                    else item,
                )
                for item in carousel_items
            ]
        if guild_id is not None:
            data["guild_id"] = guild_id
        if thumbnail_asset_id is not None:
            data["thumbnail_asset_id"] = thumbnail_asset_id
        if preview_video_asset_id is not None:
            data["preview_video_asset_id"] = preview_video_asset_id
        if header_background_asset_id is not None:
            data["header_background_asset_id"] = header_background_asset_id
        if header_logo_dark_theme_asset_id is not None:
            data["header_logo_dark_theme_asset_id"] = header_logo_dark_theme_asset_id
        if header_logo_light_theme_asset_id is not None:
            data["header_logo_light_theme_asset_id"] = header_logo_light_theme_asset_id
        if box_art_asset_id is not None:
            data["box_art_asset_id"] = box_art_asset_id
        if hero_background_asset_id is not None:
            data["hero_background_asset_id"] = hero_background_asset_id
        if hero_video_asset_id is not None:
            data["hero_video_asset_id"] = hero_video_asset_id

        return await self.request(
            Route("PATCH", f"/store/listings/{listing_id}"),
            token=token,
            json=data,
        )

    async def delete_store_listing(
        self,
        token: ValidToken,
        *,
        listing_id: int | str,
    ) -> None:
        await self.request(
            Route("DELETE", f"/store/listings/{listing_id}"),
            token=token,
        )

    async def get_subscription_plans(
        self,
        token: ValidToken,
        *,
        sku_id: int | str,
    ) -> list[store_types.SubscriptionPlanResponse]:
        return await self.request(
            Route("GET", f"/store/skus/{sku_id}/plans"),
            token=token,
        )

    async def get_application_store_assets(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
    ) -> list[store_types.StoreAssetResponse]:
        return await self.request(
            Route("GET", f"/store/applications/{application_id}/assets"),
            token=token,
        )

    async def create_application_store_asset(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        file: File,
    ) -> store_types.StoreAssetResponse:
        form = aiohttp.FormData()
        content, filename = file.read()
        form.add_field(
            "files",
            content,
            filename=filename,
            content_type=file.content_type or "application/octet-stream",
        )
        return await self.request(
            Route("POST", f"/store/applications/{application_id}/assets"),
            token=token,
            data=form,
        )

    async def delete_application_store_asset(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        asset_id: int | str,
    ) -> None:
        await self.request(
            Route("DELETE", f"/store/applications/{application_id}/assets/{asset_id}"),
            token=token,
        )
