from __future__ import annotations

from typing import TYPE_CHECKING, override

from ...enums import RelationshipType
from ...models._base import BaseModel
from ...utils import to_enum
from .activity import Activity
from .user import RPCUser

if TYPE_CHECKING:
    from ...internals._types.rpc import relationship

__all__ = ("RPCRelationship", "RPCRelationshipPresence")


class RPCRelationshipPresence(
    BaseModel["relationship.RPCRelationshipPresenceResponse"]
):
    __slots__ = ("activity", "status")

    @override
    def _initialize(self, data: relationship.RPCRelationshipPresenceResponse) -> None:
        self.status: str = data["status"]
        self.activity: Activity | None = (
            Activity.from_dict(activity) if (activity := data["activity"]) else None
        )


class RPCRelationship(BaseModel["relationship.RPCRelationshipResponse"]):
    __slots__ = ("presence", "type", "user")

    @override
    def _initialize(self, data: relationship.RPCRelationshipResponse) -> None:
        self.type: RelationshipType = to_enum(RelationshipType, data["type"])
        self.user: RPCUser = self._initialize_other(RPCUser, data["user"])
        self.presence: RPCRelationshipPresence = self._initialize_other(
            RPCRelationshipPresence, data["presence"]
        )
