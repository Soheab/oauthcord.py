from __future__ import annotations

from typing import TYPE_CHECKING, override

from ...enums import PremiumType
from ...models._base import BaseModel
from ...models.user import AvatarDecorationData
from ...utils import to_enum

if TYPE_CHECKING:
    from ...internals._types.rpc.user import (
        RPCActivityParticipantResponse,
        RPCUserResponse,
    )
__all__ = (
    "RPCActivityParticipant",
    "RPCUser",
)


class RPCUser[D = RPCUserResponse](BaseModel[D, D]):
    __slots__ = (
        "avatar",
        "avatar_decoration_data",
        "bot",
        "discriminator",
        "flags",
        "global_name",
        "id",
        "premium_type",
        "username",
    )

    @override
    def _initialize(self, data: D) -> None:
        data_: RPCUserResponse = data  # type: ignore

        self.id: int = int(data_["id"])
        self.username: str = data_["username"]
        self.discriminator: str = data_["discriminator"]
        self.global_name: str | None = data_.get("global_name")
        self.avatar: str | None = data_.get("avatar")
        self.avatar_decoration_data: AvatarDecorationData | None = (
            self._initialize_other(
                AvatarDecorationData, data_["avatar_decoration_data"], optional=True
            )
        )
        self.bot: bool = data_["bot"]
        self.flags: int = data_["flags"]
        self.premium_type: PremiumType = to_enum(PremiumType, data_["premium_type"])


class RPCActivityParticipant(RPCUser["RPCActivityParticipantResponse"]):
    __slots__ = (
        *RPCUser.__slots__,
        "nickname",
    )

    @override
    def _initialize(self, data: RPCActivityParticipantResponse) -> None:
        super()._initialize(data)
        self.nickname: str | None = data.get("nickname")
