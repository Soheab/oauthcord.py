import datetime
from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake, iso_to_datetime
from ._base import BaseModel, BaseModelWithSession
from .enums import (
    EntitlementFulfillmentStatus,
    EntitlementSourceType,
    EntitlementType,
    GiftStyle,
    to_enum,
)
from .user import PartialUser

if TYPE_CHECKING:
    from ..internals._types.entitlement import (
        EntitlementResponse,
        QuestRewardsMetadataResponse,
        TenantMetadataResponse,
    )


__all__ = (
    "Entitlement",
    "QuestRewardsMetadata",
    "TenantMetadata",
)


class QuestRewardsMetadata(BaseModel["QuestRewardsMetadataResponse"]):
    """Represents Discord API data for `QuestRewardsMetadata`."""

    __slots__ = ("reward_code", "tag")

    @override
    def _initialize(self, data: QuestRewardsMetadataResponse) -> None:
        self.tag: int = data["tag"]
        self.reward_code: dict[str, object] | None = data.get("reward_code")


class TenantMetadata(BaseModel["TenantMetadataResponse"]):
    """Represents Discord API data for `TenantMetadata`."""

    __slots__ = ("quest_rewards",)

    @override
    def _initialize(self, data: TenantMetadataResponse) -> None:
        self.quest_rewards: QuestRewardsMetadata | None = self._initialize_other(
            QuestRewardsMetadata, data, possible_keys="quest_rewards"
        )


class Entitlement(BaseModelWithSession["EntitlementResponse"]):
    """Represents a Discord application entitlement."""

    __slots__ = (
        "application_id",
        "branches",
        "consumed",
        "deleted",
        "ends_at",
        "fulfilled_at",
        "fulfillment_status",
        "gift_code_batch_id",
        "gift_code_flags",
        "gift_style",
        "gifter_user_id",
        "guild_id",
        "id",
        "parent_id",
        "promotion_id",
        "sku",
        "sku_id",
        "source_type",
        "starts_at",
        "subscription_id",
        "subscription_plan",
        "tenant_metadata",
        "type",
        "user",
        "user_id",
    )

    @override
    def _initialize(self, data: EntitlementResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.type: EntitlementType = to_enum(EntitlementType, data["type"])
        self.sku_id: int = convert_snowflake(data, "sku_id")
        self.application_id: int = convert_snowflake(data, "application_id")
        self.user_id: int = convert_snowflake(data, "user_id")
        self.user: PartialUser | None = self._initialize_other(
            PartialUser, data, possible_keys="user"
        )
        self.guild_id: int | None = convert_snowflake(
            data, "guild_id", always_available=False
        )
        self.parent_id: int | None = convert_snowflake(
            data, "parent_id", always_available=False
        )
        self.deleted: bool = data["deleted"]
        self.consumed: bool | None = data.get("consumed")
        self.branches: list[int] = [int(branch) for branch in data.get("branches", [])]
        self.starts_at: datetime.datetime | None = iso_to_datetime(data["starts_at"])
        self.ends_at: datetime.datetime | None = iso_to_datetime(data["ends_at"])
        self.promotion_id: int | None = convert_snowflake(
            data, "promotion_id", always_available=False
        )
        self.subscription_id: int | None = convert_snowflake(
            data, "subscription_id", always_available=False
        )
        self.gift_code_flags: int = data["gift_code_flags"]
        self.gift_code_batch_id: int | None = convert_snowflake(
            data, "gift_code_batch_id", always_available=False
        )
        self.gifter_user_id: int | None = convert_snowflake(
            data, "gifter_user_id", always_available=False
        )
        self.gift_style: GiftStyle | None = to_enum(GiftStyle, data.get("gift_style"))
        self.fulfillment_status: EntitlementFulfillmentStatus | None = to_enum(
            EntitlementFulfillmentStatus, data.get("fulfillment_status")
        )
        self.fulfilled_at: datetime.datetime | None = iso_to_datetime(
            data.get("fulfilled_at")
        )
        self.source_type: EntitlementSourceType | None = to_enum(
            EntitlementSourceType, data.get("source_type")
        )
        self.tenant_metadata: TenantMetadata | None = self._initialize_other(
            TenantMetadata, data, possible_keys="tenant_metadata"
        )
        self.sku: dict[str, object] | None = data.get("sku")
        self.subscription_plan: dict[str, object] | None = data.get("subscription_plan")
