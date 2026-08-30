from __future__ import annotations

from typing import TYPE_CHECKING, override

from ...models._base import BaseModel

if TYPE_CHECKING:
    from ...internals._types.rpc import connection

__all__ = ("ProviderAccessToken",)


class ProviderAccessToken(BaseModel["connection.GetProviderAccessTokenResponse"]):
    __slots__ = ("access_token",)

    @override
    def _initialize(self, data: connection.GetProviderAccessTokenResponse) -> None:
        self.access_token: str = data["access_token"]
