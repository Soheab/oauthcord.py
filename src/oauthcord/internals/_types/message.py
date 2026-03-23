from typing import Literal, NotRequired, TypedDict

from . import components as component_types
from .base import Snowflake
from .channels import GuildChannelResponse, PartialChannelResponse
from .user import PartialUserResponse

EmbedType = Literal[
    "rich",
    "image",
    "video",
    "gifv",
    "article",
    "link",
    "auto_moderation_message",
    "auto_moderation_notification",
    "gift",
    "poll_result",
    "post_preview",
    "age_verification_system_notification",
    "safety_policy_notice",
    "safety_system_notification",
]


class PartialEmojiResponse(TypedDict):
    id: Snowflake | None
    name: str | None
    animated: NotRequired[bool]


class AllowedMentionsRequest(TypedDict):
    parse: NotRequired[list[str]]
    roles: NotRequired[list[Snowflake]]
    users: NotRequired[list[Snowflake]]
    replied_user: NotRequired[bool]


class PartialAttachmentRequest(TypedDict):
    id: Snowflake
    filename: NotRequired[str]
    description: NotRequired[str]
    uploaded_filename: NotRequired[str]


class EmbedFooterRequest(TypedDict):
    text: str
    icon_url: NotRequired[str]


class EmbedMediaRequest(TypedDict):
    url: str
    description: NotRequired[str]


class EmbedAuthorRequest(TypedDict):
    name: str
    url: NotRequired[str]
    icon_url: NotRequired[str]


class EmbedFieldRequest(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


class EmbedRequest(TypedDict):
    title: NotRequired[str]
    description: NotRequired[str]
    url: NotRequired[str]
    timestamp: NotRequired[str]
    color: NotRequired[int]
    footer: NotRequired[EmbedFooterRequest]
    image: NotRequired[EmbedMediaRequest]
    thumbnail: NotRequired[EmbedMediaRequest]
    author: NotRequired[EmbedAuthorRequest]
    fields: NotRequired[list[EmbedFieldRequest]]


class UnfurledMediaItemRequest(TypedDict):
    url: str


class UnfurledMediaItemResponse(TypedDict):
    id: NotRequired[Snowflake]
    url: str
    proxy_url: NotRequired[str]
    height: NotRequired[int | None]
    width: NotRequired[int | None]
    flags: NotRequired[int]
    content_type: NotRequired[str]
    content_scan_metadata: NotRequired[dict[str, object]]
    placeholder_version: NotRequired[int]
    placeholder: NotRequired[str]
    loading_state: NotRequired[int]
    attachment_id: NotRequired[Snowflake]


class SelectOptionRequest(TypedDict):
    label: str
    value: str
    description: NotRequired[str]
    emoji: NotRequired[PartialEmojiResponse]
    default: NotRequired[bool]


class SelectOptionResponse(SelectOptionRequest):
    pass


class SelectDefaultValueRequest(TypedDict):
    id: Snowflake
    type: str


class SelectDefaultValueResponse(SelectDefaultValueRequest):
    pass


class ActionRowRequest(TypedDict):
    type: int
    id: NotRequired[int]
    components: list[ComponentRequest]


class ButtonRequest(TypedDict):
    type: int
    id: NotRequired[int]
    style: int
    label: NotRequired[str]
    emoji: NotRequired[PartialEmojiResponse]
    custom_id: NotRequired[str]
    sku_id: NotRequired[Snowflake]
    url: NotRequired[str]
    disabled: NotRequired[bool]


class StringSelectRequest(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    options: list[SelectOptionRequest]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: NotRequired[bool]
    disabled: NotRequired[bool]


class TextInputRequest(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    style: int
    label: NotRequired[str]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    value: NotRequired[str]
    placeholder: NotRequired[str]


class UserSelectRequest(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    placeholder: NotRequired[str]
    default_values: NotRequired[list[SelectDefaultValueRequest]]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: NotRequired[bool]
    disabled: NotRequired[bool]


class RoleSelectRequest(UserSelectRequest):
    pass


class MentionableSelectRequest(UserSelectRequest):
    pass


class ChannelSelectRequest(UserSelectRequest):
    channel_types: NotRequired[list[int]]


class SectionRequest(TypedDict):
    type: int
    id: NotRequired[int]
    components: list[TextDisplayRequest]
    accessory: ThumbnailRequest | ButtonRequest


class TextDisplayRequest(TypedDict):
    type: int
    id: NotRequired[int]
    content: str


class ThumbnailRequest(TypedDict):
    type: int
    id: NotRequired[int]
    media: UnfurledMediaItemRequest
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGalleryItemRequest(TypedDict):
    media: UnfurledMediaItemRequest
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGalleryRequest(TypedDict):
    type: int
    id: NotRequired[int]
    items: list[MediaGalleryItemRequest]


class FileComponentRequest(TypedDict):
    type: int
    id: NotRequired[int]
    file: UnfurledMediaItemRequest
    spoiler: NotRequired[bool]


class SeparatorRequest(TypedDict):
    type: int
    id: NotRequired[int]
    divider: NotRequired[bool]
    spacing: NotRequired[int]


class ContainerRequest(TypedDict):
    type: int
    id: NotRequired[int]
    components: list[ComponentRequest]
    accent_color: NotRequired[int | None]
    spoiler: NotRequired[bool]


class LabelRequest(TypedDict):
    type: int
    id: NotRequired[int]
    label: str
    description: NotRequired[str]
    component: ComponentRequest


class FileUploadRequest(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: NotRequired[bool]


class RadioGroupOptionRequest(TypedDict):
    value: str
    label: str
    description: NotRequired[str]
    default: NotRequired[bool]


class RadioGroupRequest(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    options: list[RadioGroupOptionRequest]
    required: NotRequired[bool]


class CheckboxGroupOptionRequest(TypedDict):
    value: str
    label: str
    description: NotRequired[str]
    default: NotRequired[bool]


class CheckboxGroupRequest(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    options: list[CheckboxGroupOptionRequest]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: NotRequired[bool]


class CheckboxRequest(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    default: NotRequired[bool]


ComponentRequest = (
    ActionRowRequest
    | ButtonRequest
    | StringSelectRequest
    | TextInputRequest
    | UserSelectRequest
    | RoleSelectRequest
    | MentionableSelectRequest
    | ChannelSelectRequest
    | SectionRequest
    | TextDisplayRequest
    | ThumbnailRequest
    | MediaGalleryRequest
    | FileComponentRequest
    | SeparatorRequest
    | ContainerRequest
    | LabelRequest
    | FileUploadRequest
    | RadioGroupRequest
    | CheckboxGroupRequest
    | CheckboxRequest
)


class ReactionCountDetailsResponse(TypedDict):
    burst: int
    normal: int


class ReactionResponse(TypedDict):
    count: int
    count_details: NotRequired[ReactionCountDetailsResponse]
    me: bool
    me_burst: bool
    emoji: PartialEmojiResponse
    burst_colors: NotRequired[list[str]]


class AttachmentResponse(TypedDict):
    id: Snowflake
    filename: str
    size: int
    url: str
    proxy_url: str
    title: NotRequired[str]
    uploaded_filename: NotRequired[str]
    description: NotRequired[str]
    content_type: NotRequired[str]
    height: NotRequired[int | None]
    width: NotRequired[int | None]
    content_scan_version: NotRequired[int]
    placeholder_version: NotRequired[int]
    placeholder: NotRequired[str]
    ephemeral: NotRequired[bool]
    duration_secs: NotRequired[float]
    waveform: NotRequired[str]
    flags: NotRequired[int]
    is_clip: NotRequired[bool]
    is_thumbnail: NotRequired[bool]
    is_remix: NotRequired[bool]
    is_spoiler: NotRequired[bool]
    clip_created_at: NotRequired[str]
    clip_participant_ids: NotRequired[list[Snowflake]]
    clip_participants: NotRequired[list[PartialUserResponse]]
    application_id: NotRequired[Snowflake]
    application: NotRequired[dict[str, object] | None]


class EmbedFooterResponse(TypedDict):
    text: str
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedMediaResponse(TypedDict):
    url: str
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]
    flags: NotRequired[int]
    description: NotRequired[str]
    content_type: NotRequired[str]
    content_scan_metadata: NotRequired[dict[str, object]]
    placeholder_version: NotRequired[int]
    placeholder: NotRequired[str]


class EmbedProviderResponse(TypedDict):
    name: NotRequired[str]
    url: NotRequired[str]


class EmbedAuthorResponse(TypedDict):
    name: str
    url: NotRequired[str]
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedFieldResponse(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


class EmbedResponse(TypedDict):
    title: NotRequired[str]
    type: NotRequired[EmbedType]
    description: NotRequired[str]
    url: NotRequired[str]
    timestamp: NotRequired[str]
    color: NotRequired[int]
    footer: NotRequired[EmbedFooterResponse]
    image: NotRequired[EmbedMediaResponse]
    thumbnail: NotRequired[EmbedMediaResponse]
    video: NotRequired[EmbedMediaResponse]
    provider: NotRequired[EmbedProviderResponse]
    author: NotRequired[EmbedAuthorResponse]
    fields: NotRequired[list[EmbedFieldResponse]]
    reference_id: NotRequired[Snowflake]
    content_scan_version: NotRequired[int]
    flags: NotRequired[int]


class MessageReferenceRequest(TypedDict):
    type: NotRequired[int]
    message_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake]
    guild_id: NotRequired[Snowflake]
    fail_if_not_exists: NotRequired[bool]
    forward_only: NotRequired[dict[str, object]]


class MessageReferenceResponse(TypedDict):
    type: NotRequired[int]
    message_id: NotRequired[Snowflake]
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    fail_if_not_exists: NotRequired[bool]
    forward_only: NotRequired[dict[str, object]]


class MessageCallResponse(TypedDict):
    participants: list[Snowflake]
    ended_timestamp: NotRequired[str | None]


class MessageActivityRequest(TypedDict):
    type: int
    session_id: str
    party_id: NotRequired[str]
    name_override: NotRequired[str]
    icon_override: NotRequired[str]


class MessageInteractionResponse(TypedDict):
    id: Snowflake
    type: int
    name: NotRequired[str]
    command_type: NotRequired[int]
    ephemerality_reason: NotRequired[int]
    user: PartialUserResponse
    authorizing_integration_owners: NotRequired[dict[int, Snowflake]]
    original_response_message_id: NotRequired[Snowflake]
    interacted_message_id: NotRequired[Snowflake]
    triggering_interaction_metadata: NotRequired[dict[str, object]]
    target_user: NotRequired[PartialUserResponse]
    target_message_id: NotRequired[Snowflake]


class MessageRoleSubscriptionResponse(TypedDict):
    role_subscription_listing_id: Snowflake
    tier_name: str
    total_months_subscribed: int
    is_renewal: bool


class MessagePurchaseNotificationResponse(TypedDict):
    type: int
    guild_product_purchase: NotRequired[dict[str, object] | None]


class MessageGiftInfoResponse(TypedDict):
    emoji: NotRequired[PartialEmojiResponse]
    sound: NotRequired[dict[str, object]]


BaseThemeType = Literal[1, 2, 3, 4]


class SharedClientThemeRequest(TypedDict):
    colors: list[str]
    gradient_angle: int
    base_mix: int
    base_theme: NotRequired[BaseThemeType | None]


class SharedClientThemeResponse(TypedDict):
    colors: list[str]
    gradient_angle: int
    base_mix: int
    base_theme: NotRequired[BaseThemeType | None]


class MessageSnapshotResponse(TypedDict):
    message: dict[str, object]


class PartialMessageResponse(TypedDict):
    id: Snowflake
    lobby_id: NotRequired[Snowflake]
    channel_id: Snowflake
    type: NotRequired[int]
    content: str
    author: PartialUserResponse
    flags: NotRequired[int]
    application_id: NotRequired[Snowflake]
    parent_application_id: NotRequired[Snowflake]
    channel: NotRequired[GuildChannelResponse]
    recipient_id: NotRequired[Snowflake]


PollLayoutType = Literal[1]


class PollQuestion(TypedDict):
    text: str


class PollAnswerPollMedia(TypedDict):
    text: str
    emoji: NotRequired[PartialEmojiResponse]


class PollAnswerRequest(TypedDict):
    poll_media: PollAnswerPollMedia


class PollAnswerResponse(PollAnswerRequest):
    answer_id: int


class PollCreateRequest(TypedDict):
    question: PollQuestion
    answers: list[PollAnswerRequest]
    duration: int
    allow_multiselect: NotRequired[bool]
    layout_type: NotRequired[PollLayoutType]


class PollAnswerCountResponse(TypedDict):
    id: int
    count: int
    me_voted: bool


class PollResultResponse(TypedDict):
    is_finalized: bool
    answers_counts: list[PollAnswerCountResponse]


class PollResponse(TypedDict):
    question: PollQuestion
    answers: list[PollAnswerResponse]
    expiry: str | None  # iso 8601 timestamp
    allow_multiselect: bool
    layout_type: PollLayoutType
    results: NotRequired[PollResultResponse]


class MessageResponse(TypedDict):
    id: Snowflake
    channel_id: Snowflake
    lobby_id: NotRequired[Snowflake]
    author: PartialUserResponse
    content: str
    timestamp: str
    edited_timestamp: str | None
    tts: bool
    mention_everyone: bool
    mentions: list[PartialUserResponse]
    mention_roles: list[Snowflake]
    mention_channels: NotRequired[list[PartialChannelResponse]]
    attachments: list[AttachmentResponse]
    embeds: list[EmbedResponse]
    reactions: NotRequired[list[ReactionResponse]]
    nonce: NotRequired[int | str]
    pinned: bool
    webhook_id: NotRequired[Snowflake]
    type: int
    activity: NotRequired[dict[str, object]]
    application: NotRequired[dict[str, object]]
    application_id: NotRequired[Snowflake]
    flags: int
    message_reference: NotRequired[MessageReferenceResponse]
    referenced_message: NotRequired[dict[str, object] | None]
    message_snapshots: NotRequired[list[MessageSnapshotResponse]]
    call: NotRequired[MessageCallResponse]
    interaction: NotRequired[dict[str, object]]
    interaction_metadata: NotRequired[MessageInteractionResponse]
    resolved: NotRequired[dict[str, object]]
    thread: NotRequired[GuildChannelResponse]
    role_subscription_data: NotRequired[MessageRoleSubscriptionResponse]
    purchase_notification: NotRequired[MessagePurchaseNotificationResponse]
    gift_info: NotRequired[MessageGiftInfoResponse]
    components: list[component_types.ComponentResponse]
    sticker_items: NotRequired[list[dict[str, object]]]
    stickers: NotRequired[list[dict[str, object]]]
    poll: NotRequired[PollResponse]
    changelog_id: NotRequired[Snowflake]
    soundboard_sounds: NotRequired[list[dict[str, object]]]
    potions: NotRequired[list[dict[str, object]]]
    shared_client_theme: NotRequired[SharedClientThemeResponse]


class GetDMMessagesRequest(TypedDict):
    limit: NotRequired[int]


class CreateDMMessageRequest(TypedDict):
    content: NotRequired[str]
    tts: NotRequired[bool]
    nonce: NotRequired[int | str]
    embeds: NotRequired[list[EmbedRequest]]
    allowed_mentions: NotRequired[AllowedMentionsRequest]
    message_reference: NotRequired[MessageReferenceRequest]
    components: NotRequired[list[component_types.ComponentRequest]]
    sticker_ids: NotRequired[list[Snowflake]]
    attachments: NotRequired[list[PartialAttachmentRequest]]
    flags: NotRequired[int]
    metadata: NotRequired[dict[str, object]]


class EditDMMessageRequest(TypedDict):
    content: NotRequired[str | None]


class CreateMessageRequest(TypedDict):
    content: NotRequired[str]
    tts: NotRequired[bool]
    embeds: NotRequired[list[EmbedRequest]]
    nonce: NotRequired[int | str]
    allowed_mentions: NotRequired[AllowedMentionsRequest]
    message_reference: NotRequired[MessageReferenceRequest]
    components: NotRequired[list[component_types.ComponentRequest]]
    sticker_ids: NotRequired[list[Snowflake]]
    activity: NotRequired[MessageActivityRequest]
    flags: NotRequired[int]
    attachments: NotRequired[list[PartialAttachmentRequest]]
    poll: NotRequired[PollCreateRequest]
    shared_client_theme: NotRequired[SharedClientThemeRequest]
    with_checkpoint: NotRequired[bool]


GetDMMessagesResponse = list[PartialMessageResponse]
CreateDMMessageResponse = MessageResponse
EditDMMessageResponse = MessageResponse
DeleteDMMessageResponse = None
CreateMessageResponse = MessageResponse
