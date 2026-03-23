import datetime
from typing import TYPE_CHECKING, Any, override

from ..utils import convert_snowflake, iso_to_datetime, maybe_available
from ._base import BaseModel, BaseModelWithHTTP, BaseModelWithSession
from .asset import Asset
from .enums import (
    CollectibleNameplatePalette,
    DisplayNameEffect,
    DisplayNameFont,
    Locale,
    PremiumType,
    to_enum,
)
from .flags import UserFlags

if TYPE_CHECKING:
    from .channel import DMChannel
    from ..internals._types.user import (
        AvatarDecorationDataResponse,
        CollectablesResponse,
        CurrentUserResponse,
        DisplayNameStyleResponse,
        GuildMemberWithUserResponse,
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


__all__ = (
    "AvatarDecorationData",
    "BaseCollectable",
    "Collectible",
    "CollectibleNameplate",
    "CurrentUser",
    "DisplayNameStyle",
    "GuildMemberWithUser",
    "Harvest",
    "HarvestMetadata",
    "PartialUser",
    "PrimaryGuild",
)


class BaseCollectable[D: Any = BaseCollectibleResponse](BaseModelWithHTTP[D]):
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


class Collectible(BaseModelWithHTTP["CollectablesResponse"]):
    """Represents Discord API data for `Collectible`."""

    __slots__ = ("nameplate",)

    @override
    def _initialize(self, data: CollectablesResponse) -> None:
        self.nameplate: CollectibleNameplate | None = self._initialize_other(
            CollectibleNameplate,
            data,
            possible_keys="nameplate",
        )


class PrimaryGuild(BaseModelWithHTTP["PrimaryGuildResponse"]):
    """Represents Discord API data for `PrimaryGuild`."""

    __slots__ = ("badge", "identity_enabled", "identity_guild_id", "tag")

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


class AvatarDecorationData(BaseModelWithHTTP["AvatarDecorationDataResponse"]):
    """Represents Discord API data for `AvatarDecorationData`."""

    __slots__ = ("asset", "sku_id")

    @override
    def _initialize(self, data: AvatarDecorationDataResponse) -> None:
        self.asset: Asset = self.get_asset(Asset._from_avatar_decoration, data["asset"])
        self.sku_id: int = convert_snowflake(data, "sku_id")


class DisplayNameStyle(BaseModel["DisplayNameStyleResponse"]):
    """Represents Discord API data for `DisplayNameStyle`."""

    __slots__ = ("colors", "effect", "font")

    @override
    def _initialize(self, data: DisplayNameStyleResponse) -> None:
        self.font: DisplayNameFont = DisplayNameFont(data["font_id"])
        self.effect: DisplayNameEffect = DisplayNameEffect(data["effect_id"])
        self.colors: list[int] = data["colors"]


class PartialUser[D = PartialUserResponse](BaseModelWithSession[D]):
    """Represents a partial Discord user payload."""

    __slots__ = (
        "avatar",
        "discriminator",
        "global_name",
        "id",
        "public_flags",
        "username",
    )

    @override
    def _initialize(self, data: D) -> None:  # type: ignore
        data_: PartialUserResponse = data  # pyright: ignore[reportAssignmentType]

        self.id: int = convert_snowflake(data, "id")
        self.username: str = data_["username"]
        avatar: str | None = data_["avatar"]
        if avatar:
            self.avatar = self.get_asset(Asset._from_avatar, self.id, avatar)
        else:
            self.avatar = self.get_asset(
                Asset._from_default_avatar, (self.id >> 22) % 6
            )

        self.discriminator: str = data_["discriminator"]
        self.public_flags: int = data_["public_flags"]
        self.global_name: str | None = data_["global_name"]

    async def dm_channel(self) -> DMChannel:
        """Get a DM channel with this user."""
        return await self._session.dm_channel(user_id=self.id)


class GuildMemberWithUser[D = GuildMemberWithUserResponse](PartialUser[D]):
    __slots__ = (
        "accent_color",
        "avatar_decoration_data",
        "banner",
        "banner_color",
        "collectibles",
        "display_name_styles",
        "flags",
        "primary_guild",
    )

    @override
    def _initialize(self, data: D) -> None:  # type: ignore
        super()._initialize(data)

        data_: GuildMemberWithUserResponse = data  # pyright: ignore[reportAssignmentType]

        self.flags: UserFlags = UserFlags(data_["flags"])
        self.banner: Asset | None = (
            self.get_asset(Asset._from_user_banner, self.id, data_["banner"])
            if data_["banner"]
            else None
        )
        self.accent_color: int | None = data_["accent_color"]
        self.banner_color: str | None = data_["banner_color"]

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


class CurrentUser(GuildMemberWithUser["CurrentUserResponse"]):
    """Represents the currently authorized Discord user."""

    __slots__ = ("_email", "locale", "mfa_enabled", "premium_type")

    @override
    def _initialize(self, data: CurrentUserResponse) -> None:
        super()._initialize(data)
        self._email: str | None = data.get("email")
        self.mfa_enabled: bool = data["mfa_enabled"]
        self.locale: Locale = to_enum(Locale, data["locale"])
        self.premium_type: PremiumType = to_enum(PremiumType, data["premium_type"])

    @property
    def email(self) -> str:
        if not self._email:
            raise ValueError(
                "Email is not available. Have you requested the `email` scope?"
            )
        return self._email


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
