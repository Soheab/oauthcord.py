"""Command types for the overlay RPC commands.

Covers ``SET_OVERLAY_LOCKED`` and the ``OPEN_OVERLAY_*`` dialogs, all of which
require the ``rpc.local`` scope.

See https://docs.discord.food/topics/rpc#set-overlay-locked.
"""

from __future__ import annotations

from typing import TypedDict

from .activity import ActivityActionType


class SetOverlayLockedRequest(TypedDict):
    locked: bool
    pid: int


SetOverlayLockedResponse = None


class OpenOverlayActivityInviteRequest(TypedDict):
    type: ActivityActionType
    pid: int


OpenOverlayActivityInviteResponse = None


class OpenOverlayGuildInviteRequest(TypedDict):
    code: str
    pid: int


OpenOverlayGuildInviteResponse = None


class OpenOverlayVoiceSettingsRequest(TypedDict):
    pid: int


OpenOverlayVoiceSettingsResponse = None
