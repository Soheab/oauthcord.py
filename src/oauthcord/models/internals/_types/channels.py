from typing import Literal, NotRequired, TypedDict

from .base import Snowflake
from .member import GuildMemberResponse
from .user import PartialUserResponse

ChannelType = Literal[
    # Documented channel types
    0,  # GUILD_TEXT
    1,  # DM
    2,  # GUILD_VOICE
    3,  # GROUP_DM
    4,  # GUILD_CATEGORY
    5,  # GUILD_ANNOUNCEMENT
    10,  # ANNOUNCEMENT_THREAD
    11,  # PUBLIC_THREAD
    12,  # PRIVATE_THREAD
    13,  # GUILD_STAGE_VOICE
    14,  # GUILD_DIRECTORY
    15,  # GUILD_FORUM
    16,  # GUILD_MEDIA
    # Undocumented / internal channel types
    6,  # GUILD_STORE
    7,  # GUILD_LFG
    8,  # LFG_GROUP_DM
    9,  # THREAD_ALPHA
    17,  # LOBBY
    18,  # EPHEMERAL_DM
]


class ChannelNickResponse(TypedDict):
    id: Snowflake
    nick: str


class SafetyWarningResponse(TypedDict):
    id: str
    type: int
    expiry: str  # ISO8601
    dismiss_timestamp: str | None  # ISO8601


class PermissionOverwriteResponse(TypedDict):
    id: Snowflake
    type: int  # 0 (role) or 1 (member)
    allow: NotRequired[str]
    deny: NotRequired[str]


class ThreadMetadataResponse(TypedDict):
    archived: bool
    auto_archive_duration: int
    archive_timestamp: str  # ISO8601
    locked: bool
    invitable: NotRequired[bool]
    create_timestamp: NotRequired[str | None]  # ISO8601


class ThreadMemberResponse(TypedDict):
    id: NotRequired[Snowflake]
    user_id: NotRequired[Snowflake]
    join_timestamp: str  # ISO8601
    flags: int
    # Undocumented
    muted: NotRequired[bool]
    mute_config: NotRequired[dict[str, object] | None]
    member: NotRequired[GuildMemberResponse]


class DefaultReactionResponse(TypedDict):
    emoji_id: Snowflake | None
    emoji_name: str | None


class IconEmojiResponse(TypedDict):
    """Undocumented."""

    id: Snowflake | None
    name: str | None


class ForumTagResponse(TypedDict):
    id: Snowflake
    name: str
    moderated: bool
    emoji_id: Snowflake | None
    emoji_name: str | None


class LinkedLobbyResponse(TypedDict):
    """Undocumented."""

    application_id: Snowflake
    lobby_id: Snowflake
    linked_by: Snowflake
    linked_at: str  # ISO8601
    require_application_authorization: bool


class FollowedChannelResponse(TypedDict):
    channel_id: Snowflake
    webhook_id: Snowflake


# -- Base channel payload --
# Fields common to all channel types


class _BaseChannelResponse(TypedDict):
    id: Snowflake
    type: ChannelType
    flags: NotRequired[int]
    last_message_id: NotRequired[Snowflake | None]


# -- Guild channel shared fields --


class _GuildChannelResponse(_BaseChannelResponse):
    guild_id: NotRequired[Snowflake]
    position: NotRequired[int]
    permission_overwrites: NotRequired[list[PermissionOverwriteResponse]]
    name: NotRequired[str | None]
    parent_id: NotRequired[Snowflake | None]
    permissions: NotRequired[
        str
    ]  # computed permissions, only in resolved interaction data
    # Undocumented
    icon_emoji: NotRequired[IconEmojiResponse | None]
    theme_color: NotRequired[int | None]


# -- Text-based guild channel fields --


class _TextChannelResponse(_GuildChannelResponse):
    topic: NotRequired[str | None]
    nsfw: NotRequired[bool]
    last_pin_timestamp: NotRequired[str | None]  # ISO8601
    rate_limit_per_user: NotRequired[int]
    default_auto_archive_duration: NotRequired[int]
    default_thread_rate_limit_per_user: NotRequired[int]


# -- Voice-based guild channel fields --


class _VoiceChannelResponse(_GuildChannelResponse):
    bitrate: NotRequired[int]
    user_limit: NotRequired[int]
    rtc_region: NotRequired[str | None]
    video_quality_mode: NotRequired[int]
    topic: NotRequired[str | None]
    nsfw: NotRequired[bool]
    rate_limit_per_user: NotRequired[int]
    last_pin_timestamp: NotRequired[str | None]  # ISO8601
    # Undocumented
    status: NotRequired[str | None]
    hd_streaming_until: NotRequired[str | None]  # ISO8601
    hd_streaming_buyer_id: NotRequired[Snowflake | None]
    linked_lobby: NotRequired[LinkedLobbyResponse | None]


# -- Forum / Media channel fields --


class _ForumChannelResponse(_GuildChannelResponse):
    topic: NotRequired[str | None]
    nsfw: NotRequired[bool]
    rate_limit_per_user: NotRequired[int]
    last_pin_timestamp: NotRequired[str | None]  # ISO8601
    default_auto_archive_duration: NotRequired[int]
    default_thread_rate_limit_per_user: NotRequired[int]
    available_tags: NotRequired[list[ForumTagResponse]]
    default_reaction_emoji: NotRequired[DefaultReactionResponse | None]
    default_sort_order: NotRequired[int | None]
    default_forum_layout: NotRequired[int]
    # Undocumented
    default_tag_setting: NotRequired[str]


# -- Thread channel fields --


class _ThreadChannelResponse(_BaseChannelResponse):
    guild_id: NotRequired[Snowflake]
    parent_id: NotRequired[Snowflake | None]
    name: NotRequired[str | None]
    owner_id: NotRequired[Snowflake]
    owner: NotRequired[GuildMemberResponse | None]
    rate_limit_per_user: NotRequired[int]
    message_count: NotRequired[int]
    member_count: NotRequired[int]
    total_message_sent: NotRequired[int]
    thread_metadata: NotRequired[ThreadMetadataResponse]
    member: NotRequired[ThreadMemberResponse]
    applied_tags: NotRequired[list[Snowflake]]
    permissions: NotRequired[str]
    # Undocumented
    member_ids_preview: NotRequired[list[Snowflake]]


GuildChannelResponse = (
    _TextChannelResponse
    | _VoiceChannelResponse
    | _ForumChannelResponse
    | _ThreadChannelResponse
    | _GuildChannelResponse
)


# -- DM channel types --


class DMChannelResponse(_BaseChannelResponse):
    recipients: NotRequired[list[PartialUserResponse]]
    # Undocumented
    recipient_flags: NotRequired[int]
    is_message_request: NotRequired[bool]
    is_message_request_timestamp: NotRequired[str | None]  # ISO8601
    is_spam: NotRequired[bool]
    safety_warnings: NotRequired[list[SafetyWarningResponse]]


class GroupDMChannelResponse(_BaseChannelResponse):
    name: NotRequired[str | None]
    icon: NotRequired[str | None]
    recipients: NotRequired[list[PartialUserResponse]]
    owner_id: NotRequired[Snowflake]
    application_id: NotRequired[Snowflake]
    managed: NotRequired[bool]
    # Undocumented
    recipient_flags: NotRequired[int]
    nicks: NotRequired[list[ChannelNickResponse]]
    blocked_user_warning_dismissed: NotRequired[bool]
    is_message_request: NotRequired[bool]
    is_message_request_timestamp: NotRequired[str | None]  # ISO8601
    is_spam: NotRequired[bool]
    safety_warnings: NotRequired[list[SafetyWarningResponse]]


class EphemeralDMChannelResponse(_BaseChannelResponse):
    """Undocumented channel type."""

    recipients: NotRequired[list[PartialUserResponse]]


PrivateChannelResponse = (
    DMChannelResponse | GroupDMChannelResponse | EphemeralDMChannelResponse
)


class PartialChannelResponse(TypedDict):
    id: Snowflake
    type: ChannelType
    name: str | None
    recipients: NotRequired[list[PartialUserResponse]]
    icon: NotRequired[str | None]
    guild_id: NotRequired[Snowflake | None]


class CreatePrivateChannelRequest(TypedDict):
    recipients: NotRequired[list[Snowflake]]
    access_tokens: NotRequired[list[str]]
    nicks: NotRequired[dict[Snowflake, str]]


class CallEligibilityResponse(TypedDict):
    ringable: bool


class RingChannelRecipientsRequest(TypedDict):
    recipients: NotRequired[list[Snowflake]]


class GetChannelLinkedAccountsRequest(TypedDict):
    user_ids: NotRequired[list[Snowflake]]


class LinkedAccountResponse(TypedDict):
    id: str
    name: str


class GetChannelLinkedAccountsResponse(TypedDict):
    linked_accounts: dict[Snowflake, list[LinkedAccountResponse]]
