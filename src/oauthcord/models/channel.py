import datetime
from typing import TYPE_CHECKING, Any, override

from ..utils import convert_snowflake, iso_to_datetime
from ._base import BaseModel
from .asset import Asset
from .emoji import Emoji
from .enums import (
    ChannelType,
    ForumLayoutType,
    PermissionOverwriteType,
    SafetyWarningType,
    SortOrderType,
    VideoQualityMode,
    to_enum,
)
from .flags import ChannelFlags, Permissions, RecipientFlags
from .member import GuildMember, ThreadMember
from .user import PartialUser

if TYPE_CHECKING:
    from .internals._types.channels import (
        CallEligibilityResponse,
        ChannelNickResponse,
        DefaultReactionResponse,
        DMChannelResponse,
        FollowedChannelResponse,
        ForumTagResponse,
        GetChannelLinkedAccountsResponse,
        GroupDMChannelResponse,
        IconEmojiResponse,
        LinkedAccountResponse,
        LinkedLobbyResponse,
        PartialChannelResponse,
        PermissionOverwriteResponse,
        PrivateChannelResponse,
        SafetyWarningResponse,
        ThreadMetadataResponse,
        _BaseChannelResponse,
        _ForumChannelResponse,
        _GuildChannelResponse,
        _TextChannelResponse,
        _ThreadChannelResponse,
        _VoiceChannelResponse,
    )
    from .internals.http import OAuth2HTTPClient, ValidToken

    type EmojiPayload = DefaultReactionResponse | IconEmojiResponse
else:
    type EmojiPayload = dict[str, object]


__all__ = (
    "BaseChannel",
    "CallEligibility",
    "ChannelLinkedAccounts",
    "ChannelNick",
    "DMChannel",
    "EphemeralDMChannel",
    "FollowedChannel",
    "ForumChannel",
    "ForumTag",
    "GroupDMChannel",
    "GuildChannel",
    "LinkedAccount",
    "LinkedLobby",
    "PartialChannel",
    "PermissionOverwrite",
    "PrivateChannel",
    "SafetyWarning",
    "TextChannel",
    "ThreadChannel",
    "ThreadMetadata",
    "VoiceChannel",
)


class PermissionOverwrite(BaseModel["PermissionOverwriteResponse"]):
    """Represents Discord API data for `PermissionOverwrite`."""

    __slots__ = ("allow", "deny", "id", "type")

    @override
    def _initialize(self, data: PermissionOverwriteResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.type: PermissionOverwriteType = to_enum(
            PermissionOverwriteType, data["type"]
        )
        self.allow: Permissions = Permissions(int(data.get("allow", 0)))
        self.deny: Permissions = Permissions(int(data.get("deny", 0)))


class ThreadMetadata(BaseModel["ThreadMetadataResponse"]):
    """Represents Discord API data for `ThreadMetadata`."""

    __slots__ = (
        "archive_timestamp",
        "archived",
        "auto_archive_duration",
        "create_timestamp",
        "invitable",
        "locked",
    )

    @override
    def _initialize(self, data: ThreadMetadataResponse) -> None:
        self.archived: bool = data["archived"]
        self.auto_archive_duration: int = data["auto_archive_duration"]
        self.archive_timestamp: datetime.datetime = iso_to_datetime(
            data["archive_timestamp"]
        )
        self.locked: bool = data["locked"]
        self.invitable: bool | None = data.get("invitable")
        self.create_timestamp: datetime.datetime | None = iso_to_datetime(
            data.get("create_timestamp")
        )


class ForumTag(BaseModel["ForumTagResponse"]):
    """Represents Discord API data for `ForumTag`."""

    __slots__ = ("emoji", "id", "moderated", "name")

    @override
    def _initialize(self, data: ForumTagResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.moderated: bool = data["moderated"]

        self.emoji: Emoji | None = Emoji.from_forum_emoji(
            emoji_name=data.get("emoji_name"), emoji_id=data.get("emoji_id")
        )


class LinkedLobby(BaseModel["LinkedLobbyResponse"]):
    """Represents Discord API data for `LinkedLobby`."""

    __slots__ = (
        "application_id",
        "linked_at",
        "linked_by",
        "lobby_id",
        "require_application_authorization",
    )

    @override
    def _initialize(self, data: LinkedLobbyResponse) -> None:
        self.application_id: int = convert_snowflake(data, "application_id")
        self.lobby_id: int = convert_snowflake(data, "lobby_id")
        self.linked_by: int = convert_snowflake(data, "linked_by")
        self.linked_at: datetime.datetime = iso_to_datetime(data["linked_at"])
        self.require_application_authorization: bool = data[
            "require_application_authorization"
        ]


class FollowedChannel(BaseModel["FollowedChannelResponse"]):
    """Represents Discord API data for `FollowedChannel`."""

    __slots__ = ("channel_id", "webhook_id")

    @override
    def _initialize(self, data: FollowedChannelResponse) -> None:
        self.channel_id: int = convert_snowflake(data, "channel_id")
        self.webhook_id: int = convert_snowflake(data, "webhook_id")


class LinkedAccount(BaseModel["LinkedAccountResponse"]):
    """Represents Discord API data for `LinkedAccount`."""

    __slots__ = ("id", "name")

    @override
    def _initialize(self, data: LinkedAccountResponse) -> None:
        self.id: str = data["id"]
        self.name: str = data["name"]


class ChannelLinkedAccounts(BaseModel["GetChannelLinkedAccountsResponse"]):
    """Represents Discord API data for `ChannelLinkedAccounts`."""

    __slots__ = ("linked_accounts",)

    @override
    def _initialize(self, data: GetChannelLinkedAccountsResponse) -> None:
        self.linked_accounts: dict[int, list[LinkedAccount]] = {
            int(user_id): [
                LinkedAccount(http=self._http, data=linked_account)
                for linked_account in linked_accounts
            ]
            for user_id, linked_accounts in data["linked_accounts"].items()
        }


class ChannelNick(BaseModel["ChannelNickResponse"]):
    """Represents Discord API data for `ChannelNick`."""

    __slots__ = ("id", "nick")

    @override
    def _initialize(self, data: ChannelNickResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.nick: str = data["nick"]


class SafetyWarning(BaseModel["SafetyWarningResponse"]):
    """Represents Discord API data for `SafetyWarning`."""

    __slots__ = ("dismiss_timestamp", "expiry", "id", "type")

    @override
    def _initialize(self, data: SafetyWarningResponse) -> None:
        self.id: str = data["id"]
        self.type: SafetyWarningType = to_enum(SafetyWarningType, data["type"])
        self.expiry: datetime.datetime = iso_to_datetime(data["expiry"])
        self.dismiss_timestamp: datetime.datetime | None = iso_to_datetime(
            data.get("dismiss_timestamp")
        )


class BaseChannel[D: Any = "_BaseChannelResponse"](BaseModel[D], check_slots=False):
    """Represents Discord API data for `BaseChannel`."""

    __slots__ = ("flags", "id", "last_message_id", "type")

    @override
    def _initialize(self, data: D) -> None:  # type: ignore
        _data: _BaseChannelResponse = data  # pyright: ignore[reportAssignmentType]

        self.id: int = convert_snowflake(_data, "id")
        self.type: ChannelType = to_enum(ChannelType, _data["type"])
        self.flags: ChannelFlags = ChannelFlags(_data.get("flags", 0))
        self.last_message_id: int | None = convert_snowflake(
            _data, "last_message_id", always_available=False
        )


class GuildChannel[D: Any = _GuildChannelResponse](BaseChannel[D]):
    """Represents Discord API data for `GuildChannel`."""

    __slots__ = (
        "guild_id",
        "icon_emoji",
        "name",
        "parent_id",
        "permission_overwrites",
        "permissions",
        "position",
        "theme_color",
    )

    @override
    def _initialize(self, data: D) -> None:
        super()._initialize(data)
        _data: _GuildChannelResponse = data  # type: ignore
        self.guild_id: int | None = convert_snowflake(
            _data, "guild_id", always_available=False
        )
        self.position: int | None = _data.get("position")
        self.permission_overwrites: list[PermissionOverwrite] = [
            self._initialize_subclass_with_http(PermissionOverwrite, overwrite)
            for overwrite in _data.get("permission_overwrites", [])
        ]
        self.name: str | None = _data.get("name")
        self.parent_id: int | None = convert_snowflake(
            _data, "parent_id", always_available=False
        )
        raw_permissions = _data.get("permissions")
        self.permissions: Permissions | None = (
            Permissions(int(raw_permissions)) if raw_permissions is not None else None
        )
        self.icon_emoji: Emoji | None = (
            Emoji(**ie) if (ie := _data.get("icon_emoji")) else None
        )
        self.theme_color: int | None = _data.get("theme_color")


class TextChannel(GuildChannel["_TextChannelResponse"]):
    """Represents Discord API data for `TextChannel`."""

    __slots__ = (
        "default_auto_archive_duration",
        "default_thread_rate_limit_per_user",
        "last_pin_timestamp",
        "nsfw",
        "rate_limit_per_user",
        "topic",
    )

    @override
    def _initialize(self, data: _TextChannelResponse) -> None:
        super()._initialize(data)
        self.topic: str | None = data.get("topic")
        self.nsfw: bool | None = data.get("nsfw")
        self.last_pin_timestamp: datetime.datetime | None = iso_to_datetime(
            data.get("last_pin_timestamp")
        )
        self.rate_limit_per_user: int | None = data.get("rate_limit_per_user")
        self.default_auto_archive_duration: int | None = data.get(
            "default_auto_archive_duration"
        )
        self.default_thread_rate_limit_per_user: int | None = data.get(
            "default_thread_rate_limit_per_user"
        )


class VoiceChannel(GuildChannel["_VoiceChannelResponse"]):
    """Represents Discord API data for `VoiceChannel`."""

    __slots__ = (
        "bitrate",
        "hd_streaming_buyer_id",
        "hd_streaming_until",
        "last_pin_timestamp",
        "linked_lobby",
        "nsfw",
        "rate_limit_per_user",
        "rtc_region",
        "status",
        "topic",
        "user_limit",
        "video_quality_mode",
    )

    @override
    def _initialize(self, data: _VoiceChannelResponse) -> None:
        super()._initialize(data)
        self.bitrate: int | None = data.get("bitrate")
        self.user_limit: int | None = data.get("user_limit")
        self.rtc_region: str | None = data.get("rtc_region")
        video_quality_mode = data.get("video_quality_mode")
        self.video_quality_mode: VideoQualityMode | None = (
            to_enum(VideoQualityMode, video_quality_mode)
            if video_quality_mode is not None
            else None
        )
        self.topic: str | None = data.get("topic")
        self.nsfw: bool | None = data.get("nsfw")
        self.rate_limit_per_user: int | None = data.get("rate_limit_per_user")
        self.last_pin_timestamp: datetime.datetime | None = iso_to_datetime(
            data.get("last_pin_timestamp")
        )
        self.status: str | None = data.get("status")
        self.hd_streaming_until: datetime.datetime | None = iso_to_datetime(
            data.get("hd_streaming_until")
        )
        self.hd_streaming_buyer_id: int | None = convert_snowflake(
            data, "hd_streaming_buyer_id", always_available=False
        )
        self.linked_lobby: LinkedLobby | None = self._maybe_subclass_with_http(
            LinkedLobby, data, "linked_lobby"
        )


class ForumChannel(GuildChannel["_ForumChannelResponse"]):
    """Represents Discord API data for `ForumChannel`."""

    __slots__ = (
        "available_tags",
        "default_auto_archive_duration",
        "default_forum_layout",
        "default_reaction_emoji",
        "default_sort_order",
        "default_tag_setting",
        "default_thread_rate_limit_per_user",
        "last_pin_timestamp",
        "nsfw",
        "rate_limit_per_user",
        "topic",
    )

    @override
    def _initialize(self, data: _ForumChannelResponse) -> None:
        super()._initialize(data)
        self.topic: str | None = data.get("topic")
        self.nsfw: bool | None = data.get("nsfw")
        self.rate_limit_per_user: int | None = data.get("rate_limit_per_user")
        self.last_pin_timestamp: datetime.datetime | None = iso_to_datetime(
            data.get("last_pin_timestamp")
        )
        self.default_auto_archive_duration: int | None = data.get(
            "default_auto_archive_duration"
        )
        self.default_thread_rate_limit_per_user: int | None = data.get(
            "default_thread_rate_limit_per_user"
        )
        self.available_tags: list[ForumTag] = [
            self._initialize_subclass_with_http(ForumTag, tag)
            for tag in data.get("available_tags", [])
        ]
        self.default_reaction_emoji: Emoji | None = (
            Emoji.from_forum_emoji(**dre)
            if (dre := data.get("default_reaction_emoji"))
            else None
        )
        default_sort_order = data.get("default_sort_order")
        self.default_sort_order: SortOrderType | None = (
            to_enum(SortOrderType, default_sort_order)
            if default_sort_order is not None
            else None
        )
        default_forum_layout = data.get("default_forum_layout")
        self.default_forum_layout: ForumLayoutType | None = (
            to_enum(ForumLayoutType, default_forum_layout)
            if default_forum_layout is not None
            else None
        )
        self.default_tag_setting: str | None = data.get("default_tag_setting")


class ThreadChannel(BaseChannel["_ThreadChannelResponse"]):
    """Represents Discord API data for `ThreadChannel`."""

    __slots__ = (
        "applied_tags",
        "guild_id",
        "member",
        "member_count",
        "member_ids_preview",
        "message_count",
        "name",
        "owner",
        "owner_id",
        "parent_id",
        "permissions",
        "rate_limit_per_user",
        "thread_metadata",
        "total_message_sent",
    )

    @override
    def _initialize(self, data: _ThreadChannelResponse) -> None:
        super()._initialize(data)
        self.guild_id: int | None = convert_snowflake(
            data, "guild_id", always_available=False
        )
        self.parent_id: int | None = convert_snowflake(
            data, "parent_id", always_available=False
        )
        self.name: str | None = data.get("name")
        self.owner_id: int | None = convert_snowflake(
            data, "owner_id", always_available=False
        )
        owner_data = data.get("owner")
        self.owner: GuildMember | None = (
            GuildMember(http=self._http, data=owner_data, guild_id=self.guild_id)
            if owner_data
            else None
        )
        self.rate_limit_per_user: int | None = data.get("rate_limit_per_user")
        self.message_count: int | None = data.get("message_count")
        self.member_count: int | None = data.get("member_count")
        self.total_message_sent: int | None = data.get("total_message_sent")
        self.thread_metadata: ThreadMetadata | None = self._maybe_subclass_with_http(
            ThreadMetadata, data, "thread_metadata"
        )
        member_data = data.get("member")
        self.member: ThreadMember | None = (
            ThreadMember(http=self._http, data=member_data, guild_id=self.guild_id)
            if member_data
            else None
        )
        self.applied_tags: list[int] = [
            int(tag_id) for tag_id in data.get("applied_tags", [])
        ]
        raw_permissions = data.get("permissions")
        self.permissions: Permissions | None = (
            Permissions(int(raw_permissions)) if raw_permissions is not None else None
        )
        self.member_ids_preview: list[int] = [
            int(member_id) for member_id in data.get("member_ids_preview", [])
        ]


class PrivateChannel[D = PrivateChannelResponse](BaseChannel[D]):
    __slots__ = ("recipients",)

    @override
    def _initialize(self, data: D) -> None:
        super()._initialize(data)
        _data: PrivateChannelResponse = data  # type: ignore
        self.recipients: list[PartialUser] = [
            self._initialize_subclass_with_http(PartialUser, user)
            for user in _data.get("recipients", [])
        ]

    async def ring(
        self, token: ValidToken, *, recipients: list[int | str] | None = None
    ) -> None:
        """Ring the recipients of this DM channel."""
        await self._http.__get_client().ring_channel_recipients(
            token=token, channel_id=self.id, recipients=recipients
        )

    async def stop_ringing(
        self, token: ValidToken, *, recipients: list[int | str] | None = None
    ) -> None:
        """Stop ringing the recipients of this DM channel."""
        await self._http.__get_client().stop_ringing_channel_recipients(
            token=token, channel_id=self.id, recipients=recipients
        )


class DMChannel(PrivateChannel["DMChannelResponse"]):
    """Represents Discord API data for `DMChannel`."""

    __slots__ = (
        "is_message_request",
        "is_message_request_timestamp",
        "is_spam",
        "recipient_flags",
        "safety_warnings",
    )

    @override
    def _initialize(self, data: DMChannelResponse) -> None:
        super()._initialize(data)
        self.recipient_flags: RecipientFlags = RecipientFlags(
            data.get("recipient_flags", 0)
        )
        self.is_message_request: bool = data.get("is_message_request", False)
        self.is_message_request_timestamp: datetime.datetime | None = iso_to_datetime(
            data.get("is_message_request_timestamp")
        )
        self.is_spam: bool = data.get("is_spam", False)
        self.safety_warnings: list[SafetyWarning] = [
            self._initialize_subclass_with_http(SafetyWarning, warning)
            for warning in data.get("safety_warnings", [])
        ]

    async def get_call_eligibility(self, token: ValidToken) -> CallEligibility:
        """Get the call eligibility for this DM channel."""
        return await self._http.__get_client().call_eligibility(
            token=token, channel_id=self.id
        )


class GroupDMChannel(PrivateChannel["GroupDMChannelResponse"]):
    """Represents Discord API data for `GroupDMChannel`."""

    __slots__ = (
        "application_id",
        "blocked_user_warning_dismissed",
        "icon",
        "is_message_request",
        "is_message_request_timestamp",
        "is_spam",
        "managed",
        "name",
        "nicks",
        "owner_id",
        "recipient_flags",
        "safety_warnings",
    )

    @override
    def _initialize(self, data: GroupDMChannelResponse) -> None:
        super()._initialize(data)
        self.name: str | None = data.get("name")

        icon = data.get("icon")
        self.icon: Asset | None = (
            self.get_asset(Asset._from_icon, self.id, icon, "channel-icons")
            if icon
            else None
        )

        self.owner_id: int | None = convert_snowflake(
            data, "owner_id", always_available=False
        )
        self.application_id: int | None = convert_snowflake(
            data, "application_id", always_available=False
        )
        self.managed: bool = data.get("managed", False)
        self.recipient_flags: RecipientFlags = RecipientFlags(
            data.get("recipient_flags", 0)
        )
        self.nicks: list[ChannelNick] = [
            self._initialize_subclass_with_http(ChannelNick, nick)
            for nick in data.get("nicks", [])
        ]
        self.blocked_user_warning_dismissed: bool = data.get(
            "blocked_user_warning_dismissed", False
        )
        self.is_message_request: bool = data.get("is_message_request", False)
        self.is_message_request_timestamp: datetime.datetime | None = iso_to_datetime(
            data.get("is_message_request_timestamp")
        )
        self.is_spam: bool = data.get("is_spam", False)
        self.safety_warnings: list[SafetyWarning] = [
            self._initialize_subclass_with_http(SafetyWarning, warning)
            for warning in data.get("safety_warnings", [])
        ]

    async def get_linked_accounts(
        self, token: ValidToken, *, user_ids: list[int | str]
    ) -> ChannelLinkedAccounts:
        """Get the linked accounts for this group DM channel."""
        return await self._http.__get_client().channel_linked_accounts(
            token=token, channel_id=self.id, user_ids=user_ids
        )


class EphemeralDMChannel(PrivateChannel["EphemeralDMChannelResponse"]):
    """Represents Discord API data for `EphemeralDMChannel`."""


class PartialChannel(BaseModel["PartialChannelResponse"]):
    """Represents Discord API data for `PartialChannel`."""

    __slots__ = ("guild_id", "icon", "id", "name", "recipients", "type")

    @override
    def _initialize(self, data: PartialChannelResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.type: ChannelType = to_enum(ChannelType, data["type"])
        self.name: str | None = data["name"]
        self.recipients: list[PartialUser] = [
            self._initialize_subclass_with_http(PartialUser, user)
            for user in data.get("recipients", [])
        ]

        self.icon: Asset | None = (
            self.get_asset(Asset._from_icon, self.id, icon, "channel-icons")
            if (icon := data.get("icon"))
            else None
        )

        self.guild_id: int | None = convert_snowflake(
            data, "guild_id", always_available=False
        )


class CallEligibility(BaseModel["CallEligibilityResponse"]):
    """Represents Discord API data for `CallEligibility`."""

    __slots__ = ("ringable",)

    @override
    def _initialize(self, data: CallEligibilityResponse) -> None:
        self.ringable: bool = data["ringable"]


def _from_data(  # type: ignore
    http: OAuth2HTTPClient, data: _BaseChannelResponse | PartialChannelResponse
) -> BaseChannel | PartialChannel:
    match to_enum(ChannelType, data["type"]):
        case ChannelType.DM:
            return DMChannel(http=http, data=data)  # type: ignore
        case ChannelType.GROUP_DM | ChannelType.LFG_GROUP_DM:
            return GroupDMChannel(http=http, data=data)  # type: ignore
        case ChannelType.EPHEMERAL_DM:
            return EphemeralDMChannel(http=http, data=data)  # type: ignore
        case (
            ChannelType.GUILD_TEXT
            | ChannelType.GUILD_ANNOUNCEMENT
            | ChannelType.GUILD_STORE
            | ChannelType.GUILD_LFG
            | ChannelType.GUILD_DIRECTORY
        ):
            return TextChannel(http=http, data=data)  # type: ignore
        case ChannelType.GUILD_CATEGORY | ChannelType.LOBBY:
            return GuildChannel(http=http, data=data)  # type: ignore
        case ChannelType.GUILD_VOICE | ChannelType.GUILD_STAGE_VOICE:
            return VoiceChannel(http=http, data=data)  # type: ignore
        case ChannelType.GUILD_FORUM | ChannelType.GUILD_MEDIA:
            return ForumChannel(http=http, data=data)  # type: ignore
        case (
            ChannelType.ANNOUNCEMENT_THREAD
            | ChannelType.PUBLIC_THREAD
            | ChannelType.PRIVATE_THREAD
            | ChannelType.THREAD_ALPHA
        ):
            return ThreadChannel(http=http, data=data)  # type: ignore
        case _:
            return PartialChannel(http=http, data=data)  # type: ignore
