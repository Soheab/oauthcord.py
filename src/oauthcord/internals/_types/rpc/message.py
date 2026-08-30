from __future__ import annotations

from typing import NotRequired, TypedDict

from ..attachment import Attachment
from ..base import Snowflake
from ..message import EmbedResponse, MessageType
from .user import RPCUserResponse


class RPCMessageResponse(TypedDict):
    id: str
    blocked: NotRequired[bool]
    bot: NotRequired[bool]
    content: str
    content_parsed: NotRequired[list[object]]
    nicked: NotRequired[bool]
    author_color: NotRequired[str]
    edited_timestamp: str | None  # iso
    timestamp: str  # iso
    tts: bool
    mentions: list[RPCUserResponse]
    mention_everyone: bool
    mention_roles: list[Snowflake]
    embeds: list[EmbedResponse]
    attachments: list[Attachment]
    author: NotRequired[RPCUserResponse | None]
    pinned: bool
    type: MessageType


# -- Commands ----------------------------------------------------------------


class OpenMessageRequest(TypedDict):
    guild_id: NotRequired[Snowflake | None]
    channel_id: Snowflake
    message_id: Snowflake
    pid: int


OpenMessageResponse = None
