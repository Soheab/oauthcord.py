from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, override

from ...models._base import BaseModel
from ...models.attachment import Attachment
from ...models.embeds import Embed
from ...utils import iso_to_datetime
from .user import RPCUser

if TYPE_CHECKING:
    from ...internals._types.rpc.message import RPCMessageResponse

__all__ = ("RPCMessage",)


class RPCMessage(BaseModel["RPCMessageResponse"]):
    __slots__ = (
        "attachments",
        "author",
        "author_color",
        "blocked",
        "bot",
        "content",
        "edited_timestamp",
        "embeds",
        "id",
        "mention_everyone",
        "mention_roles",
        "mentioned_ids",
        "mentions",
        "nicked",
        "pinned",
        "timestamp",
        "tts",
        "type",
    )

    @override
    def _initialize(self, data: RPCMessageResponse) -> None:
        self._handle_mentions(data)

        self.id: int = int(data["id"])
        self.blocked: bool = data.get("blocked", False)
        self.bot: bool = data.get("bot", False)
        self.content: str = data["content"]
        self.nicked: bool = data.get("nicked", False)
        self.author_color: str | None = data.get("author_color")
        self.edited_timestamp: datetime.datetime | None = iso_to_datetime(
            data["edited_timestamp"]
        )
        self.timestamp: datetime.datetime = iso_to_datetime(data["timestamp"])
        self.tts: bool = data["tts"]

        self.embeds: list[Embed] = [
            Embed.from_dict(embed) for embed in data.get("embeds", [])
        ]
        self.attachments: list[Attachment] = [
            self._initialize_other(Attachment, attachment)
            for attachment in data.get("attachments", [])
        ]
        self.author: RPCUser | None = self._initialize_other(
            RPCUser, data.get("author"), optional=True
        )
        self.pinned: bool = data["pinned"]
        self.type: int = data["type"]

    def _handle_mentions(self, data: RPCMessageResponse) -> None:
        mentions: list[RPCUser] = []
        role_mentions: list[int] = []
        raw_mentions: list[int] = []

        for mention in data.get("mentions", []):
            if isinstance(mention, dict):
                mentions.append(self._initialize_other(RPCUser, mention))
            else:
                try:
                    mention_id = int(mention)
                except (ValueError, TypeError):
                    continue
                else:
                    raw_mentions.append(mention_id)

        for role_id in data.get("mention_roles", []):
            try:
                role_mentions.append(int(role_id))
            except (ValueError, TypeError):
                continue

        self.mentions = mentions
        self.mentioned_ids = raw_mentions
        self.mention_roles = role_mentions
        self.mention_everyone = data.get("mention_everyone", False)
