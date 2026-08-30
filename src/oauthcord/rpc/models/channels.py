from __future__ import annotations

from typing import TYPE_CHECKING, override

from ...enums import ChannelType
from ...internals._types.rpc.channels import (
    GetChannelPermissionsResponse,
    PartialRPCChannelResponse,
    RPCChannelResponse,
    RPCChannelWithMessagesResponse,
)
from ...models._base import BaseModel
from ...models.flags import Permissions
from ...utils import to_enum
from .message import RPCMessage

__all__ = (
    "ChannelPermissions",
    "RPCChannel",
    "RPCPartialChannel",
)

if TYPE_CHECKING:
    from ...internals._types.rpc.voice import RPCVoiceStateResponse


class ChannelPermissions(BaseModel["GetChannelPermissionsResponse"]):
    __slots__ = ("permissions",)

    @override
    def _initialize(self, data: GetChannelPermissionsResponse) -> None:
        self.permissions: Permissions = Permissions(int(data["permissions"]))


class RPCPartialChannel[D = PartialRPCChannelResponse](BaseModel[D, D]):
    __slots__ = (
        "id",
        "name",
        "type",
    )

    @override
    def _initialize(self, data: D) -> None:
        data_: PartialRPCChannelResponse = data  # type: ignore
        self.id: int = int(data_["id"])
        self.type: ChannelType = to_enum(ChannelType, data_["type"])
        self.name: str | None = data_.get("name")


class RPCChannel(RPCPartialChannel[RPCChannelResponse]):
    __slots__ = (
        *RPCPartialChannel.__slots__,
        "topic",
        "bitrate",
        "user_limit",
        "guild_id",
        "position",
        "voice_states",
        "messages",
    )

    @override
    def _initialize(self, data: RPCChannelResponse) -> None:
        super()._initialize(data)
        self.topic: str | None = data.get("topic") or None
        self.bitrate: int | None = data.get("bitrate")
        self.user_limit: int = data["user_limit"]
        self.guild_id: int = int(data["guild_id"])
        self.position: int = data["position"]
        self.voice_states: RPCVoiceStateResponse | None = data.get("voice_states")

        data_: RPCChannelWithMessagesResponse = data  # type: ignore
        self.messages: list[RPCMessage] = [
            self._initialize_other(RPCMessage, message)
            for message in data_.get("messages", [])
        ]
