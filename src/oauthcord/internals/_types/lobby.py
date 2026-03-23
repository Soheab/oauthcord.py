from typing import NotRequired, TypedDict

from .base import Snowflake
from .channels import GuildChannelResponse
from .message import (
    AllowedMentionsRequest,
    ComponentRequest,
    EmbedRequest,
    MessageActivityRequest,
    MessageReferenceRequest,
    PartialAttachmentRequest,
    PartialMessageResponse,
)


class LobbyMemberResponse(TypedDict):
    id: Snowflake
    metadata: NotRequired[dict[str, str] | None]
    flags: NotRequired[int]


class LobbyResponse(TypedDict):
    id: Snowflake
    application_id: Snowflake
    metadata: NotRequired[dict[str, str] | None]
    members: list[LobbyMemberResponse]
    flags: NotRequired[int]
    linked_channel: NotRequired[GuildChannelResponse | None]


class JoinOrCreateLobbyRequest(TypedDict):
    secret: str
    lobby_metadata: NotRequired[dict[str, str] | None]
    member_metadata: NotRequired[dict[str, str] | None]
    idle_timeout_seconds: NotRequired[int]
    flags: NotRequired[int]


class CreateLobbyRequest(TypedDict):
    metadata: NotRequired[dict[str, str] | None]
    members: NotRequired[list[LobbyMemberResponse]]
    idle_timeout_seconds: NotRequired[int]
    flags: NotRequired[int]


class CreateLobbyInviteForCurrentUserResponse(TypedDict):
    code: str


class ModifyLobbyLinkedChannelRequest(TypedDict):
    channel_id: NotRequired[Snowflake | None]


class GetLobbyMessagesRequest(TypedDict):
    limit: NotRequired[int]


class CreateLobbyMessageRequest(TypedDict):
    content: NotRequired[str]
    tts: NotRequired[bool]
    nonce: NotRequired[int | str]
    embeds: NotRequired[list[EmbedRequest]]
    allowed_mentions: NotRequired[AllowedMentionsRequest]
    message_reference: NotRequired[MessageReferenceRequest]
    components: NotRequired[list[ComponentRequest]]
    sticker_ids: NotRequired[list[Snowflake]]
    activity: NotRequired[MessageActivityRequest]
    application_id: NotRequired[Snowflake]
    flags: NotRequired[int]
    attachments: NotRequired[list[PartialAttachmentRequest]]
    poll: NotRequired[dict[str, object]]
    shared_client_theme: NotRequired[dict[str, object]]
    metadata: NotRequired[dict[str, object]]


JoinOrCreateLobbyResponse = LobbyResponse
LeaveLobbyResponse = None
ModifyLobbyLinkedChannelResponse = LobbyResponse
GetLobbyMessagesResponse = list[PartialMessageResponse]
CreateLobbyMessageResponse = PartialMessageResponse
