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
        "mentions",
        "nicked",
        "pinned",
        "timestamp",
        "tts",
        "type",
    )

    @override
    def _initialize(self, data: RPCMessageResponse) -> None:
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
        self.mentions: list[RPCUser] = [
            self._initialize_other(RPCUser, mention)
            for mention in data.get("mentions", [])
        ]
        self.mention_everyone: bool = data["mention_everyone"]
        self.mention_roles: list[int] = [
            int(role_id) for role_id in data.get("mention_roles", [])
        ]
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
