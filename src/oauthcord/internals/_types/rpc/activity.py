from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from .. import components as component_types
from ..base import Snowflake
from ..presence import ActivityPartyRequest as _ActivityPartyRequest
from ..presence import ActivityRequest as _ActivityRequest
from ..presence import ActivityResponse as _ActivityResponse
from .user import RPCActivityParticipantResponse

# ActivityType values Discord's RPC SET_ACTIVITY accepts: PLAYING, LISTENING,
# WATCHING, COMPETING. STREAMING, CUSTOM, and HANGING are rejected over RPC.
RPCActivityType = Literal[0, 2, 3, 5]


ActivityPartyPrivacy = Literal[
    0,  # PRIVATE
    1,  # PUBLIC
]


class ActivityPartyRequest(_ActivityPartyRequest):
    """The general party object plus RPC's ``privacy`` field."""

    privacy: NotRequired[ActivityPartyPrivacy]  # default PRIVATE


class ActivityPartyResponse(_ActivityPartyRequest):
    """The general party object plus RPC's ``privacy`` field, as received."""

    privacy: NotRequired[ActivityPartyPrivacy]


class ActivityRequest(_ActivityRequest):
    """The activity payload accepted by the ``SET_ACTIVITY`` command.

    Structurally the general activity object; RPC only narrows ``type`` (see
    ``RPCActivityType``) and extends ``party`` with ``privacy``.
    """

    party: NotRequired[ActivityPartyRequest]  # pyright: ignore[reportIncompatibleVariableOverride]
    type: NotRequired[RPCActivityType]  # pyright: ignore[reportIncompatibleVariableOverride]


ActivityResponse = _ActivityResponse
"""``SET_ACTIVITY`` echoes back the general activity object (with ``id``,
``created_at``, and label-only ``buttons``), not the request shape it was sent."""


class SetActivityRequest(TypedDict):
    pid: NotRequired[int]
    activity: NotRequired[ActivityRequest]


SetActivityResponse = ActivityResponse


# -- Commands ----------------------------------------------------------------

# Only JOIN is accepted over RPC.
ActivityActionType = Literal[1]


class SendActivityJoinInviteRequest(TypedDict):
    user_id: Snowflake
    pid: int


SendActivityJoinInviteResponse = None


class CloseActivityJoinRequestRequest(TypedDict):
    user_id: Snowflake


CloseActivityJoinRequestResponse = None


class ActivityInviteUserRequest(TypedDict):
    user_id: Snowflake
    type: ActivityActionType
    content: NotRequired[str]  # max 1024 characters
    pid: int


ActivityInviteUserResponse = None


class AcceptActivityInviteRequest(TypedDict):
    type: ActivityActionType
    user_id: Snowflake
    session_id: str
    channel_id: Snowflake
    message_id: Snowflake
    application_id: NotRequired[Snowflake]


AcceptActivityInviteResponse = None
OpenInviteDialogResponse = None


class OpenShareMomentDialogRequest(TypedDict):
    mediaUrl: str  # max 1024 characters


OpenShareMomentDialogResponse = None


class InteractionOptionRequest(TypedDict):
    name: str
    value: str


class InteractionResponsePreviewImageRequest(TypedDict):
    height: int
    url: str
    width: int


class ShareInteractionRequest(TypedDict):
    command: str
    options: NotRequired[list[InteractionOptionRequest]]
    content: NotRequired[str]  # max 2000 characters
    require_launch_channel: NotRequired[bool]
    preview_image: NotRequired[InteractionResponsePreviewImageRequest]
    components: NotRequired[list[component_types.ActionRowRequest]]
    pid: NotRequired[int]


class ShareInteractionResponse(TypedDict):
    success: bool


class InitiateImageUploadResponse(TypedDict):
    image_url: str


class ShareLinkRequest(TypedDict):
    custom_id: NotRequired[str]  # max 64 characters
    message: str  # max 1000 characters
    link_id: NotRequired[str]  # max 64 characters


class ShareLinkResponse(TypedDict):
    success: bool
    didCopyLink: bool
    didSendMessage: bool


class GetActivityInstanceConnectedParticipantsResponse(TypedDict):
    participants: list[RPCActivityParticipantResponse]
