from __future__ import annotations

from typing import override

from ...internals._types.rpc.guild import RPCGetGuildResponse, RPCGuildResponse
from ...models._base import BaseModel

__all__ = ("RPCGuild",)


class RPCGuild(
    BaseModel[
        RPCGuildResponse | RPCGetGuildResponse,
        RPCGuildResponse | RPCGetGuildResponse,
    ]
):
    @override
    def _initialize(self, data: RPCGuildResponse | RPCGetGuildResponse) -> None:
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.icon_url: str | None = data["icon_url"]
        self.vanity_url_code: str | None = data.get("vanity_url_code")
