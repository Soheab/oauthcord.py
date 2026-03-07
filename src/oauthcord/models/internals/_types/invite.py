from typing import NotRequired, TypedDict

from .application import PartialApplicationResponse
from .base import Snowflake
from .channels import PartialChannelResponse
from .user import PartialUserResponse


class AcceptInviteRequest(TypedDict):
    session_id: NotRequired[str]


class InviteGuildResponse(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
    description: str | None
    banner: str | None
    splash: str | None
    verification_level: int
    features: list[str]
    vanity_url_code: str | None
    premium_tier: int
    nsfw: bool
    nsfw_level: int
    premium_subscription_count: NotRequired[int]


class InviteResponse(TypedDict):
    code: str
    type: int
    channel: PartialChannelResponse | None
    expires_at: str | None
    guild_id: NotRequired[Snowflake]
    guild: NotRequired[InviteGuildResponse]
    profile: NotRequired[dict[str, object]]
    inviter: NotRequired[PartialUserResponse]
    target_type: NotRequired[int | None]
    target_user: NotRequired[PartialUserResponse | None]
    target_application: NotRequired[PartialApplicationResponse | None]
    roles: NotRequired[list[dict[str, object]]]
    approximate_presence_count: NotRequired[int]
    approximate_member_count: NotRequired[int]
    flags: NotRequired[int]
    new_member: NotRequired[bool]
    show_verification_form: NotRequired[bool]
    stage_instance: NotRequired[dict[str, object]]
    guild_scheduled_event: NotRequired[dict[str, object]]
    guild_join_request: NotRequired[dict[str, object]]
