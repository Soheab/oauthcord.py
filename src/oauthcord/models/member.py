from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake, iso_to_datetime
from ._base import BaseModel
from .asset import Asset
from .flags import MemberFlags, Permissions
from .user import (
    AvatarDecorationData,
    Collectible,
    DisplayNameStyle,
    PartialUser,
)

if TYPE_CHECKING:
    from ..internals._types.channels import ThreadMemberResponse
    from ..internals._types.member import GuildMemberResponse
    from ..internals.state import State


__all__ = (
    "GuildMember",
    "ThreadMember",
)


class GuildMember(BaseModel["GuildMemberResponse"]):
    """Represents a guild member payload for the authorized user."""

    __slots__ = (
        "avatar",
        "avatar_decoration_data",
        "banner",
        "bio",
        "collectibles",
        "communication_disabled_until",
        "deaf",
        "display_name_styles",
        "flags",
        "guild_id",
        "joined_at",
        "mute",
        "nick",
        "pending",
        "permissions",
        "premium_since",
        "role_ids",
        "unusual_dm_activity_until",
        "user",
    )

    @override
    def __init__(
        self,
        *,
        state: State | None = None,
        data: GuildMemberResponse,
        guild_id: int | None = None,
    ) -> None:
        self.guild_id: int | None = guild_id
        super().__init__(state=state, data=data)

    @override
    def _initialize(self, data: GuildMemberResponse) -> None:
        self.user: PartialUser = self._initialize_other(
            PartialUser, data, possible_keys="user"
        )

        avatar_hash = data.get("avatar")
        self.avatar: Asset | None = (
            self.get_asset(
                Asset._from_guild_avatar, self.guild_id, self.user.id, avatar_hash
            )
            if avatar_hash and self.guild_id is not None
            else None
        )

        banner_hash = data.get("banner")
        self.banner: Asset | None = (
            self.get_asset(
                Asset._from_guild_member_banner,
                self.guild_id,
                self.user.id,
                banner_hash,
            )
            if banner_hash and self.guild_id is not None
            else None
        )

        self.communication_disabled_until: datetime.datetime | None = iso_to_datetime(
            data.get("communication_disabled_until")
        )
        self.flags: MemberFlags = MemberFlags(data.get("flags", 0))
        self.joined_at: datetime.datetime | None = iso_to_datetime(
            data.get("joined_at")
        )
        self.nick: str | None = data.get("nick")
        self.pending: bool = data.get("pending", False)
        self.premium_since: datetime.datetime | None = iso_to_datetime(
            data.get("premium_since")
        )
        self.role_ids: list[int] = [int(role_id) for role_id in data.get("roles", [])]
        self.unusual_dm_activity_until: datetime.datetime | None = iso_to_datetime(
            data.get("unusual_dm_activity_until")
        )
        self.display_name_styles: DisplayNameStyle | None = self._initialize_other(
            DisplayNameStyle, data, possible_keys="display_name_styles", optional=True
        )
        self.mute: bool = data.get("mute", False)
        self.deaf: bool = data.get("deaf", False)
        self.bio: str | None = data.get("bio")

        raw_permissions = data.get("permissions")
        self.permissions: Permissions = (
            Permissions(int(raw_permissions))
            if raw_permissions is not None
            else Permissions(0)
        )
        self.avatar_decoration_data: AvatarDecorationData | None = (
            self._initialize_other(
                AvatarDecorationData,
                data,
                possible_keys="avatar_decoration_data",
                optional=True,
            )
        )

        self.collectibles: Collectible | None = self._initialize_other(
            Collectible, data, possible_keys="collectibles", optional=True
        )


class ThreadMember(BaseModel["ThreadMemberResponse"]):
    """Represents a thread member payload."""

    __slots__ = (
        "flags",
        "guild_id",
        "id",
        "join_timestamp",
        "member",
        "mute_config",
        "muted",
        "user_id",
    )

    @override
    def __init__(
        self,
        *,
        state: State | None = None,
        data: ThreadMemberResponse,
        guild_id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.guild_id: int | None = guild_id
        super().__init__(state=state, data=data)

    @override
    def _initialize(self, data: ThreadMemberResponse) -> None:
        self.id: int | None = convert_snowflake(data, "id", always_available=False)
        self.user_id: int | None = convert_snowflake(
            data, "user_id", always_available=False
        )
        self.join_timestamp: datetime.datetime = iso_to_datetime(data["join_timestamp"])
        self.flags: int = data["flags"]
        self.muted: bool | None = data.get("muted")
        self.mute_config: dict[str, object] | None = data.get("mute_config")
        member_data = data.get("member")
        self.member: GuildMember | None = (
            GuildMember(state=self._state, data=member_data, guild_id=self.guild_id)
            if member_data
            else None
        )
