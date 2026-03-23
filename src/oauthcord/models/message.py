import datetime
from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake, iso_to_datetime
from ._base import BaseModelWithSession
from .attachment import Attachment
from .channel import BaseChannel, PartialChannel, _from_data
from .components import BaseComponent, component_from_response
from .embeds import Embed
from .user import PartialUser

if TYPE_CHECKING:
    from ..internals._types.message import (
        MessageResponse as MessagePayload,
    )
    from ..internals._types.message import (
        PartialMessageResponse as PartialMessagePayload,
    )
    from ..internals._types.message import (
        ReactionResponse as ReactionPayload,
    )


__all__ = (
    "Message",
    "PartialMessage",
)


class PartialMessage(BaseModelWithSession["PartialMessagePayload"]):
    """Represents a partial Discord message payload."""

    __slots__ = (
        "application_id",
        "author",
        "channel",
        "channel_id",
        "content",
        "flags",
        "id",
        "lobby_id",
        "parent_application_id",
        "recipient_id",
        "type",
    )

    @override
    def _initialize(self, data: PartialMessagePayload) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.lobby_id: int | None = convert_snowflake(
            data, "lobby_id", always_available=False
        )
        self.channel_id: int = convert_snowflake(data, "channel_id")
        self.type: int | None = data.get("type")
        self.content: str = data.get("content", "")
        self.author: PartialUser = self._initialize_other(
            PartialUser, data, possible_keys="author"
        )
        self.flags: int | None = data.get("flags")
        self.application_id: int | None = convert_snowflake(
            data, "application_id", always_available=False
        )
        self.parent_application_id: int | None = convert_snowflake(
            data, "parent_application_id", always_available=False
        )

        channel_data = data.get("channel")
        self.channel: BaseChannel | PartialChannel | None = (
            _from_data(self._http, channel_data) if channel_data else None
        )
        self.recipient_id: int | None = convert_snowflake(
            data, "recipient_id", always_available=False
        )


class Message(BaseModelWithSession["MessagePayload"]):
    """Represents a full Discord message."""

    __slots__ = (
        "attachments",
        "author",
        "channel_id",
        "components",
        "content",
        "edited_timestamp",
        "embeds",
        "flags",
        "id",
        "lobby_id",
        "mention_channels",
        "mention_everyone",
        "mention_roles",
        "mentions",
        "nonce",
        "pinned",
        "reactions",
        "thread",
        "timestamp",
        "tts",
        "type",
        "webhook_id",
    )

    @override
    def _initialize(self, data: MessagePayload) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.channel_id: int = convert_snowflake(data, "channel_id")
        self.lobby_id: int | None = convert_snowflake(
            data, "lobby_id", always_available=False
        )
        self.author: PartialUser = self._initialize_other(
            PartialUser, data, possible_keys="author"
        )
        self.content: str = data.get("content", "")
        self.timestamp: datetime.datetime = iso_to_datetime(data["timestamp"])
        self.edited_timestamp: datetime.datetime | None = iso_to_datetime(
            data.get("edited_timestamp")
        )
        self.tts: bool = data.get("tts", False)
        self.mention_everyone: bool = data.get("mention_everyone", False)
        self.mentions: list[PartialUser] = [
            self._initialize_other(PartialUser, mention)
            for mention in data.get("mentions", [])
        ]
        self.mention_roles: list[int] = [
            int(role_id) for role_id in data.get("mention_roles", [])
        ]
        self.mention_channels: list[PartialChannel] = [
            self._initialize_other(PartialChannel, channel)
            for channel in data.get("mention_channels", [])
        ]
        self.attachments: list[Attachment] = [
            self._initialize_other(Attachment, attachment)
            for attachment in data.get("attachments", [])
        ]
        self.embeds: list[Embed] = [
            Embed._from_response(embed) for embed in data.get("embeds", [])
        ]
        self.reactions: list[ReactionPayload] = data.get("reactions", [])
        self.nonce: int | str | None = data.get("nonce")
        self.pinned: bool = data.get("pinned", False)
        self.webhook_id: int | None = convert_snowflake(
            data, "webhook_id", always_available=False
        )
        self.type: int = data.get("type", 0)
        self.flags: int = data.get("flags", 0)
        self.components: list[BaseComponent] = [
            component_from_response(component)
            for component in data.get("components", [])
        ]

        thread_data = data.get("thread")
        self.thread: BaseChannel | PartialChannel | None = (
            _from_data(self._http, thread_data) if thread_data else None
        )
