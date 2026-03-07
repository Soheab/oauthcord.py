from typing import NotRequired, TypedDict

from .base import Snowflake


class PartialEmojiResponse(TypedDict):
    id: Snowflake | None
    name: str | None
    animated: NotRequired[bool]


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
    components: list["ComponentRequest"]


class ActionRowResponse(TypedDict):
    type: int
    id: NotRequired[int]
    components: list["ComponentResponse"]


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


class ButtonResponse(ButtonRequest):
    pass


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


class StringSelectResponse(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    options: list[SelectOptionResponse]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: NotRequired[bool]
    disabled: NotRequired[bool]


class AutoPopulatedSelectRequest(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    placeholder: NotRequired[str]
    default_values: NotRequired[list[SelectDefaultValueRequest]]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: NotRequired[bool]
    disabled: NotRequired[bool]


class AutoPopulatedSelectResponse(TypedDict):
    type: int
    id: NotRequired[int]
    custom_id: str
    placeholder: NotRequired[str]
    default_values: NotRequired[list[SelectDefaultValueResponse]]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: NotRequired[bool]
    disabled: NotRequired[bool]


class UserSelectRequest(AutoPopulatedSelectRequest):
    pass


class UserSelectResponse(AutoPopulatedSelectResponse):
    pass


class RoleSelectRequest(AutoPopulatedSelectRequest):
    pass


class RoleSelectResponse(AutoPopulatedSelectResponse):
    pass


class MentionableSelectRequest(AutoPopulatedSelectRequest):
    pass


class MentionableSelectResponse(AutoPopulatedSelectResponse):
    pass


class ChannelSelectRequest(AutoPopulatedSelectRequest):
    channel_types: NotRequired[list[int]]


class ChannelSelectResponse(AutoPopulatedSelectResponse):
    channel_types: NotRequired[list[int]]


class TextDisplayRequest(TypedDict):
    type: int
    id: NotRequired[int]
    content: str


class TextDisplayResponse(TextDisplayRequest):
    pass


class ThumbnailRequest(TypedDict):
    type: int
    id: NotRequired[int]
    media: UnfurledMediaItemRequest
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class ThumbnailResponse(TypedDict):
    type: int
    id: NotRequired[int]
    media: UnfurledMediaItemResponse
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class SectionRequest(TypedDict):
    type: int
    id: NotRequired[int]
    components: list[TextDisplayRequest]
    accessory: "ThumbnailRequest | ButtonRequest"


class SectionResponse(TypedDict):
    type: int
    id: NotRequired[int]
    components: list[TextDisplayResponse]
    accessory: "ThumbnailResponse | ButtonResponse"


class MediaGalleryItemRequest(TypedDict):
    media: UnfurledMediaItemRequest
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGalleryItemResponse(TypedDict):
    media: UnfurledMediaItemResponse
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGalleryRequest(TypedDict):
    type: int
    id: NotRequired[int]
    items: list[MediaGalleryItemRequest]


class MediaGalleryResponse(TypedDict):
    type: int
    id: NotRequired[int]
    items: list[MediaGalleryItemResponse]


class FileComponentRequest(TypedDict):
    type: int
    id: NotRequired[int]
    file: UnfurledMediaItemRequest
    spoiler: NotRequired[bool]


class FileComponentResponse(TypedDict):
    type: int
    id: NotRequired[int]
    file: UnfurledMediaItemResponse
    spoiler: NotRequired[bool]
    name: NotRequired[str]
    size: NotRequired[int]


class SeparatorRequest(TypedDict):
    type: int
    id: NotRequired[int]
    divider: NotRequired[bool]
    spacing: NotRequired[int]


class SeparatorResponse(SeparatorRequest):
    pass


class ContentInventoryEntryDataResponse(TypedDict):
    id: str
    author_id: Snowflake
    author_type: int
    content_type: int
    traits: list[dict[str, object]]
    extra: dict[str, object]
    participants: NotRequired[list[Snowflake]]
    expires_at: NotRequired[str]
    ended_at: NotRequired[str]
    started_at: NotRequired[str]
    original_id: NotRequired[Snowflake]
    guild_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake]
    session_id: NotRequired[Snowflake]
    signature: dict[str, object]


class ContentInventoryEntryComponentResponse(TypedDict):
    type: int
    id: NotRequired[int]
    content_inventory_entry: ContentInventoryEntryDataResponse


class ContainerRequest(TypedDict):
    type: int
    id: NotRequired[int]
    components: list["ComponentRequest"]
    accent_color: NotRequired[int | None]
    spoiler: NotRequired[bool]


class ContainerResponse(TypedDict):
    type: int
    id: NotRequired[int]
    components: list["ComponentResponse"]
    accent_color: NotRequired[int | None]
    spoiler: NotRequired[bool]


class CheckpointDataResponse(TypedDict):
    version: int
    card_id: int
    power_level: float
    power_level_percentile: float
    num_messages_sent: int
    total_voice_minutes: float
    num_emojis_sent: int
    top_guild: NotRequired[dict[str, object]]
    top_emoji: NotRequired[dict[str, object]]
    top_game: NotRequired[dict[str, object]]


class CheckpointCardResponse(TypedDict):
    type: int
    id: NotRequired[int]
    checkpoint_data: CheckpointDataResponse


ComponentRequest = (
    ActionRowRequest
    | ButtonRequest
    | StringSelectRequest
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
)


ComponentResponse = (
    ActionRowResponse
    | ButtonResponse
    | StringSelectResponse
    | UserSelectResponse
    | RoleSelectResponse
    | MentionableSelectResponse
    | ChannelSelectResponse
    | SectionResponse
    | TextDisplayResponse
    | ThumbnailResponse
    | MediaGalleryResponse
    | FileComponentResponse
    | SeparatorResponse
    | ContentInventoryEntryComponentResponse
    | ContainerResponse
    | CheckpointCardResponse
)
