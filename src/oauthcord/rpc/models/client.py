from __future__ import annotations

from typing import TYPE_CHECKING, override

from ...models._base import BaseModel

if TYPE_CHECKING:
    from ...internals._types.rpc import client

__all__ = ("Image", "LocaleSettings")


class Image(BaseModel["client.GetImageResponse"]):
    __slots__ = ("data_url",)

    @override
    def _initialize(self, data: client.GetImageResponse) -> None:
        self.data_url: str = data["data_url"]


class LocaleSettings(BaseModel["client.UserSettingsGetLocaleResponse"]):
    __slots__ = ("locale",)

    @override
    def _initialize(self, data: client.UserSettingsGetLocaleResponse) -> None:
        self.locale: str = data["locale"]
