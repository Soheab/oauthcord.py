from __future__ import annotations

from typing import TYPE_CHECKING, override

from ...models._base import BaseModel
from ...models.emoji import Emoji
from ...utils import convert_snowflake

if TYPE_CHECKING:
    from ...internals._types.rpc import soundboard

__all__ = ("SoundboardSound",)


class SoundboardSound(BaseModel["soundboard.SoundboardSoundResponse"]):
    __slots__ = (
        "_emoji_id",
        "_emoji_name",
        "available",
        "guild_id",
        "name",
        "sound_id",
        "user",
        "user_id",
        "volume",
    )

    @override
    def _initialize(self, data: soundboard.SoundboardSoundResponse) -> None:
        self.sound_id: int = convert_snowflake(data, "sound_id")
        self.name: str = data["name"]
        self.volume: float = data["volume"]

        self._emoji_id: int | None = convert_snowflake(
            data, "emoji_id", always_available=False
        )
        self._emoji_name: str | None = data["emoji_name"]

        self.guild_id: int | None = convert_snowflake(
            data, "guild_id", always_available=False
        )
        self.available: bool = data["available"]

    @property
    def emoji(self) -> Emoji | None:
        if self._emoji_id is None and self._emoji_name is None:
            return None
        return Emoji(name=self._emoji_name or "", id=self._emoji_id)
