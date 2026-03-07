from typing import Any, override

from ._base import StatelessBaseModel

__all__ = ("Emoji",)


class Emoji(StatelessBaseModel[Any, Any]):
    """Represents an emoji payload used in Discord request and response models."""

    __slots__ = ("animated", "id", "name")

    def __init__(
        self,
        *,
        name: str,
        id: int | None = None,
        animated: bool = False,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.name: str = name
        self.id: int | None = id
        self.animated: bool = animated

    def __str__(self) -> str:
        if not self.id:
            return self.name

        animated_key = "a" if self.animated else ""
        return f"<{animated_key}:{self.name}:{self.id}>"

    @override
    def _to_request(
        self,
        *,
        name_key: str | None = "name",
        id_key: str | None = "id",
        animated_key: str | None = "animated",
    ) -> dict[str, Any]:
        """Serialize this object into a Discord API request payload."""
        base: dict[str, Any] = {}
        if name_key:
            base[name_key] = self.name
        if id_key:
            base[id_key] = self.id
        if animated_key:
            base[animated_key] = self.animated
        return base

    @classmethod
    def from_forum_emoji(
        cls, *, emoji_name: str | None = None, emoji_id: int | str | None = None
    ) -> Emoji:
        """Create this object from a serialized payload."""
        return cls(
            name=emoji_name or "", id=int(emoji_id) if emoji_id is not None else None
        )
