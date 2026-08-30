from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, override

from ..enums import (
    CollectibleNameplatePalette,
    DisplayNameEffect,
    DisplayNameFont,
    Locale,
    PremiumType,
)
from ..utils import convert_snowflake, iso_to_datetime, maybe_available, to_enum
from ._base import BaseModel
from .asset import Asset
from .flags import UserFlags

if TYPE_CHECKING:
    from ..internals._types.user import (
        AvatarDecorationDataResponse,
        CollectablesResponse,
        CurrentUserResponse,
        DisplayNameStyleResponse,
        HarvestMetadataResponse,
        HarvestResponse,
        PartialUserResponse,
        PrimaryGuildResponse,
    )
    from ..internals._types.user import (
        _CollectibleNameplateResponse as CollectibleNameplateResponse,
    )
    from ..internals._types.user import (
        _CollectibleResponse as BaseCollectibleResponse,
    )
    from .channel import DMChannel


__all__ = (
    "AvatarDecorationData",
    "BaseCollectable",
    "Collectible",
    "CollectibleNameplate",
    "CurrentUser",
    "DisplayNameStyle",
    "Harvest",
    "HarvestMetadata",
    "PartialUser",
    "PrimaryGuild",
)


class BaseCollectable[D: Any = BaseCollectibleResponse](BaseModel[D]):
    __slots__ = ("asset", "label", "sku_id")

    @override
    def _initialize(self, data: D) -> None:
        self.sku_id: int = convert_snowflake(data, "sku_id")
        self.asset: Asset = self.get_asset(Asset._from_user_collectible, data["asset"])
        self.label: str = data.get("label")


class CollectibleNameplate(BaseCollectable["CollectibleNameplateResponse"]):
    __slots__ = ("palette",)

    @override
    def _initialize(self, data: CollectibleNameplateResponse) -> None:
        super()._initialize(data)
        self.palette: CollectibleNameplatePalette = to_enum(
            CollectibleNameplatePalette, data["palette"]
        )


class Collectible(BaseModel["CollectablesResponse"]):
    """Represents Discord API data for `Collectible`."""

    __slots__ = ("nameplate",)

    @override
    def _initialize(self, data: CollectablesResponse) -> None:
        self.nameplate: CollectibleNameplate | None = self._initialize_other(
            CollectibleNameplate,
            data,
            possible_keys="nameplate",
        )


class PrimaryGuild(BaseModel["PrimaryGuildResponse"]):
    """Represents Discord API data for `PrimaryGuild`."""

    __slots__ = (
        "badge",
        "identity_enabled",
        "identity_guild_id",
        "tag",
    )

    @override
    def _initialize(self, data: PrimaryGuildResponse) -> None:
        self.identity_guild_id: int | None = convert_snowflake(
            data, "identity_guild_id", always_available=False
        )
        self.identity_enabled: bool = maybe_available(
            data, "identity_enabled", bool, False
        )
        self.tag: str | None = data.get("tag")
        badge: str | None = data.get("badge")
        if badge and self.identity_guild_id:
            self.badge = self.get_asset(
                Asset._from_primary_guild, self.identity_guild_id, badge
            )
        else:
            self.badge = None


class AvatarDecorationData(BaseModel["AvatarDecorationDataResponse"]):
    """Represents Discord API data for `AvatarDecorationData`."""

    __slots__ = ("asset", "sku_id")

    @override
    def _initialize(self, data: AvatarDecorationDataResponse) -> None:
        self.asset: Asset = self.get_asset(Asset._from_avatar_decoration, data["asset"])
        # The REST API sends `sku_id`, but RPC sends the same field as `skuId`.
        if "sku_id" not in data and "skuId" in data:
            data["sku_id"] = data.pop("skuId")
        self.sku_id: int = convert_snowflake(data, "sku_id")


class DisplayNameStyle(BaseModel["DisplayNameStyleResponse"]):
    """Represents Discord API data for `DisplayNameStyle`."""

    __slots__ = ("colors", "effect", "font")

    @override
    def _initialize(self, data: DisplayNameStyleResponse) -> None:
        self.font: DisplayNameFont = DisplayNameFont(data["font_id"])
        self.effect: DisplayNameEffect = DisplayNameEffect(data["effect_id"])
        self.colors: list[int] = data["colors"]


class PartialUser[D = PartialUserResponse](BaseModel[D]):
    """Represents a partial Discord user payload."""

    __slots__ = (
        "accent_color",
        "avatar",
        "avatar_decoration_data",
        "banner",
        "bot",
        "collectibles",
        "discriminator",
        "display_name_styles",
        "global_name",
        "id",
        "primary_guild",
        "public_flags",
        "system",
        "username",
    )

    @override
    def _initialize(self, data: D) -> None:
        data_: PartialUserResponse = data  # pyright: ignore[reportAssignmentType]

        self.id: int = convert_snowflake(data, "id")
        self.username: str = data_["username"]
        self.discriminator: str = data_["discriminator"]
        self.global_name: str | None = data_.get("global_name")

        avatar: str | None = data_["avatar"]
        if avatar:
            self.avatar = self.get_asset(Asset._from_avatar, self.id, avatar)
        else:
            self.avatar = self.get_asset(
                Asset._from_default_avatar, (self.id >> 22) % 6
            )

        self.avatar_decoration_data: AvatarDecorationData | None = (
            self._initialize_other(
                AvatarDecorationData,
                data_,
                possible_keys="avatar_decoration_data",
                optional=True,
            )
        )
        self.collectibles: Collectible | None = self._initialize_other(
            Collectible, data_, possible_keys="collectibles", optional=True
        )
        self.display_name_styles: DisplayNameStyle | None = self._initialize_other(
            DisplayNameStyle, data_, possible_keys="display_name_styles", optional=True
        )
        self.primary_guild: PrimaryGuild | None = self._initialize_other(
            PrimaryGuild, data_, possible_keys="primary_guild", optional=True
        )
        self.bot: bool = data_.get("bot", False)
        self.system: bool = data_.get("system", False)
        self.banner: Asset | None = (
            self.get_asset(Asset._from_user_banner, self.id, banner)
            if (banner := data_.get("banner"))
            else None
        )
        self.accent_color: int | None = data_.get("accent_color")

        self.public_flags: UserFlags = UserFlags(data_.get("public_flags", 0))

    async def dm_channel(self) -> DMChannel:
        """Get a DM channel with this user."""
        return await self._session.get_dm_channel(user_id=self.id)


class CurrentUser(PartialUser["CurrentUserResponse"]):
    """Represents the currently authorized Discord user."""

    __slots__ = (
        "_email",
        "_premium_type",
        "locale",
        "mfa_enabled",
    )

    @override
    def _initialize(self, data: CurrentUserResponse) -> None:
        super()._initialize(data)
        self._email: str | None = data.get("email")
        self.mfa_enabled: bool = data["mfa_enabled"]
        self.locale: Locale = to_enum(Locale, data["locale"])
        self._premium_type: PremiumType = to_enum(PremiumType, data["premium_type"])

    @property
    def email(self) -> str | None:
        """Get the user's email.

        .. scope:: email

        Returns
        -------
        :class:`str` | :data:`None`
            The user's email.
        """
        return self._email

    @property
    def premium_type(self) -> PremiumType:
        """Get the user's premium type.

        .. scope:: identity.premium

        Returns
        -------
        :class:`PremiumType`
            The user's premium type.
        """
        return self._premium_type


class HarvestMetadata(BaseModel["HarvestMetadataResponse"]):
    """Represents Discord API data for `HarvestMetadata`."""

    __slots__ = (
        "backend_attempts",
        "bypass_cooldown",
        "is_provisional",
        "sla_email_sent",
        "user_is_staff",
    )

    @override
    def _initialize(self, data: HarvestMetadataResponse) -> None:
        self.user_is_staff: bool = data["user_is_staff"]
        self.sla_email_sent: bool = data["sla_email_sent"]
        self.bypass_cooldown: bool = data["bypass_cooldown"]
        self.is_provisional: bool | None = data.get("is_provisional")
        self.backend_attempts: dict[str, int] = data.get("backend_attempts", {})


class Harvest(BaseModel["HarvestResponse"]):
    """Represents Discord API data for `Harvest`."""

    __slots__ = (
        "backends",
        "completed_at",
        "created_at",
        "email",
        "harvest_id",
        "harvest_metadata",
        "polled_at",
        "shadow_run",
        "state",
        "status",
        "updated_at",
        "user_id",
    )

    @override
    def _initialize(self, data: HarvestResponse) -> None:
        self.harvest_id: int = convert_snowflake(data, "harvest_id")
        self.user_id: int = convert_snowflake(data, "user_id")
        self.email: str = data["email"]
        self.state: str = data["state"]
        self.status: int = data["status"]
        self.created_at: datetime.datetime = iso_to_datetime(data["created_at"])
        self.completed_at: datetime.datetime | None = iso_to_datetime(
            data["completed_at"]
        )
        self.polled_at: datetime.datetime | None = iso_to_datetime(data["polled_at"])
        self.backends: dict[str, str] = data["backends"]
        self.updated_at: datetime.datetime = iso_to_datetime(data["updated_at"])
        self.shadow_run: bool = data["shadow_run"]
        self.harvest_metadata: HarvestMetadata = self._initialize_other(
            HarvestMetadata,
            data,
            possible_keys="harvest_metadata",
        )
