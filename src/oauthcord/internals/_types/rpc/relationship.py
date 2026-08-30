from __future__ import annotations

from typing import TypedDict

from ..presence import ActivityResponse
from ..relationship import RelationshipType
from .member import Status
from .user import RPCUserResponse


class RPCRelationshipPresenceResponse(TypedDict):
    status: Status
    activity: ActivityResponse | None


class RPCRelationshipResponse(TypedDict):
    type: RelationshipType
    user: RPCUserResponse
    presence: RPCRelationshipPresenceResponse


# -- Commands ----------------------------------------------------------------


class GetRelationshipsResponse(TypedDict):
    relationships: list[RPCRelationshipResponse]
