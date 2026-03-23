from typing import Literal, NotRequired, TypedDict

from .base import Snowflake
from .user import PartialUserResponse

RelationshipType = Literal[0, 1, 2, 3, 4, 5]


class _RelationshipBase(TypedDict):
    id: str
    type: RelationshipType
    user: PartialUserResponse
    since: str  # iso 8601 timestamp


class RelationshipResponse(_RelationshipBase):
    nickname: str | None
    is_spam_request: NotRequired[bool]
    stranger_request: NotRequired[bool]
    user_ignored: bool
    origin_application_id: NotRequired[Snowflake | None]
    has_played_game: NotRequired[bool]


class GameRelationshipResponse(_RelationshipBase):
    application_id: Snowflake
    dm_access_type: int
    user_id: Snowflake


class CreateRelationshipRequest(TypedDict):
    type: NotRequired[
        RelationshipType | Literal[-1]
    ]  # -1 = accept an existing or create
    from_friend_suggestion: NotRequired[bool]  # default false
    confirm_stranger_request: NotRequired[bool]  # default false


class CreateGameRelationshipRequest(TypedDict):
    type: NotRequired[
        RelationshipType | Literal[-1]
    ]  # -1 = accept an existing or create


class SendFriendRequestRequest(TypedDict):
    username: str


SendFriendRequestResponse = None
