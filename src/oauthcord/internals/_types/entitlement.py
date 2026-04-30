from typing import Literal, NotRequired, TypedDict

from .base import Snowflake
from .user import PartialUserResponse
from .store import SKU, SubscriptionPlanResponse

QuestPlatformType = Literal[
    0,  # CROSS_PLATFORM
    1,  # XBOX
    2,  # PLAYSTATION
    3,  # SWITCH
    4,  # PC
]


class QuestRewardCodeResponse(TypedDict):
    quest_id: Snowflake
    code: str
    platform: QuestPlatformType
    user_id: int
    claimed_at: str  # iso
    tier: int | None


class QuestRewardsMetadataResponse(TypedDict):
    tag: int
    reward_code: NotRequired[QuestRewardCodeResponse]


class TenantMetadataResponse(TypedDict):
    quest_rewards: NotRequired[QuestRewardsMetadataResponse]


class EntitlementResponse(TypedDict):
    id: Snowflake
    type: int
    sku_id: Snowflake
    application_id: Snowflake
    user_id: Snowflake
    deleted: bool
    starts_at: str | None
    ends_at: str | None
    promotion_id: Snowflake | None
    gift_code_flags: int
    user: NotRequired[PartialUserResponse]
    guild_id: NotRequired[Snowflake]
    parent_id: NotRequired[Snowflake]
    consumed: NotRequired[bool]
    branches: NotRequired[list[Snowflake]]
    subscription_id: NotRequired[Snowflake]
    gift_code_batch_id: NotRequired[Snowflake]
    gifter_user_id: NotRequired[Snowflake]
    gift_style: NotRequired[int]
    fulfillment_status: NotRequired[int]
    fulfilled_at: NotRequired[str]
    source_type: NotRequired[int]
    tenant_metadata: NotRequired[TenantMetadataResponse]
    sku: NotRequired[SKU]
    subscription_plan: NotRequired[SubscriptionPlanResponse]


class GetApplicationEntitlementsRequest(TypedDict):
    user_id: NotRequired[Snowflake]
    sku_ids: NotRequired[list[Snowflake]]
    guild_id: NotRequired[Snowflake]
    exclude_ended: NotRequired[bool]
    exclude_deleted: NotRequired[bool]
    before: NotRequired[Snowflake]
    after: NotRequired[Snowflake]
    limit: NotRequired[int]


GetApplicationEntitlementsResponse = list[EntitlementResponse]
