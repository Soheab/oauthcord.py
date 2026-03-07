import datetime
from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake, iso_to_datetime
from ._base import BaseModel
from .application import PartialApplication
from .asset import Asset
from .channel import PartialChannel
from .enums import InviteTargetType, InviteType, to_enum
from .user import PartialUser

if TYPE_CHECKING:
    from .internals._types.invite import (
        InviteGuildResponse,
        InviteResponse,
    )


__all__ = (
    "Invite",
    "InviteGuild",
)


class InviteGuild(BaseModel["InviteGuildResponse"]):
    """Represents Discord API data for `InviteGuild`."""

    __slots__ = (
        "banner",
        "description",
        "features",
        "icon",
        "id",
        "name",
        "nsfw",
        "nsfw_level",
        "premium_subscription_count",
        "premium_tier",
        "splash",
        "vanity_url_code",
        "verification_level",
    )

    @override
    def _initialize(self, data: InviteGuildResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.icon: Asset | None = (
            self.get_asset(Asset._from_guild_icon, self.id, data["icon"])
            if data["icon"]
            else None
        )
        self.description: str | None = data["description"]
        self.banner: str | None = data["banner"]
        self.splash: str | None = data["splash"]
        self.verification_level: int = data["verification_level"]
        self.features: list[str] = data["features"]
        self.vanity_url_code: str | None = data["vanity_url_code"]
        self.premium_subscription_count: int | None = data.get(
            "premium_subscription_count"
        )
        self.premium_tier: int = data["premium_tier"]
        self.nsfw: bool = data["nsfw"]
        self.nsfw_level: int = data["nsfw_level"]


class Invite(BaseModel["InviteResponse"]):
    """Represents a Discord invite."""

    __slots__ = (
        "approximate_member_count",
        "approximate_presence_count",
        "channel",
        "code",
        "expires_at",
        "flags",
        "guild",
        "guild_id",
        "guild_join_request",
        "guild_scheduled_event",
        "inviter",
        "new_member",
        "profile",
        "roles",
        "show_verification_form",
        "stage_instance",
        "target_application",
        "target_type",
        "target_user",
        "type",
    )

    @override
    def _initialize(self, data: InviteResponse) -> None:
        self.code: str = data["code"]
        self.type: InviteType = to_enum(InviteType, data["type"])
        self.guild_id: int | None = convert_snowflake(
            data, "guild_id", always_available=False
        )
        self.guild: InviteGuild | None = self._maybe_subclass_with_http(
            InviteGuild, data, "guild"
        )
        self.channel: PartialChannel | None = self._maybe_subclass_with_http(
            PartialChannel, data, "channel"
        )
        self.profile: dict[str, object] | None = data.get("profile")
        self.inviter: PartialUser | None = self._maybe_subclass_with_http(
            PartialUser, data, "inviter"
        )
        self.target_type: InviteTargetType | None = to_enum(
            InviteTargetType, data.get("target_type")
        )
        self.target_user: PartialUser | None = self._maybe_subclass_with_http(
            PartialUser, data, "target_user"
        )
        self.target_application: PartialApplication | None = (
            self._maybe_subclass_with_http(
                PartialApplication, data, "target_application"
            )
        )
        self.roles: list[dict[str, object]] = data.get("roles", [])
        self.approximate_presence_count: int | None = data.get(
            "approximate_presence_count"
        )
        self.approximate_member_count: int | None = data.get("approximate_member_count")
        self.expires_at: datetime.datetime | None = iso_to_datetime(
            data.get("expires_at")
        )
        self.flags: int = data.get("flags", 0)
        self.new_member: bool = data.get("new_member", False)
        self.show_verification_form: bool = data.get("show_verification_form", False)
        self.stage_instance: dict[str, object] | None = data.get("stage_instance")
        self.guild_scheduled_event: dict[str, object] | None = data.get(
            "guild_scheduled_event"
        )
        self.guild_join_request: dict[str, object] | None = data.get(
            "guild_join_request"
        )
