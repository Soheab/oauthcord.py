from typing import NotRequired, TypedDict

from .base import Snowflake
from .user import PartialUserResponse


class QuestRewardsMetadataResponse(TypedDict):
    tag: int
    reward_code: NotRequired[dict[str, object]]


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
    sku: NotRequired[dict[str, object]]
    subscription_plan: NotRequired[dict[str, object]]


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
