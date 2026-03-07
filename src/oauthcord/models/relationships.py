from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake
from ._base import BaseModel
from .enums import RelationshipType
from .user import PartialUser, to_enum

if TYPE_CHECKING:
    from .internals._types.relationship import (
        GameRelationshipResponse as GameRelationshipPayload,
    )
    from .internals._types.relationship import (
        RelationshipResponse as RelationshipPayload,
    )
    from .internals._types.relationship import (
        _RelationshipBase as _RelationshipBasePayload,
    )


__all__ = (
    "GameRelationship",
    "Relationship",
)


@BaseModel.add_slots("id", "type", "user", "since")
class _RelationshipBase[D: _RelationshipBasePayload](BaseModel[D]):
    @override
    def _initialize(self, data: D) -> None:
        self.id: str = data["id"]
        self.type: RelationshipType = to_enum(RelationshipType, data["type"])
        self.user: PartialUser = self._initialize_subclass_with_http(
            PartialUser, data, "user"
        )
        self.since: str = data["since"]


@BaseModel.add_slots(
    "nickname",
    "is_spam_request",
    "stranger_request",
    "user_ignored",
    "origin_application_id",
    "has_played_game",
)
class Relationship(_RelationshipBase["RelationshipPayload"]):
    """Represents Discord API data for `Relationship`."""

    @override
    def _initialize(self, data: RelationshipPayload) -> None:
        super()._initialize(data)
        self.nickname: str | None = data["nickname"]
        self.is_spam_request: bool = data.get("is_spam_request", False)
        self.stranger_request: bool = data.get("stranger_request", False)
        self.user_ignored: bool = data["user_ignored"]
        self.origin_application_id: int | None = convert_snowflake(
            data, "origin_application_id", always_available=False
        )
        self.has_played_game: bool = data.get("has_played_game", False)


@BaseModel.add_slots("application_id", "dm_access_type", "user_id")
class GameRelationship(_RelationshipBase["GameRelationshipPayload"]):
    """Represents Discord API data for `GameRelationship`."""

    @override
    def _initialize(self, data: GameRelationshipPayload) -> None:
        super()._initialize(data)
        self.application_id: int = convert_snowflake(data, "application_id")
        self.dm_access_type: int = data.get("dm_access_type", 0)
        self.user_id: int = convert_snowflake(data, "user_id")
