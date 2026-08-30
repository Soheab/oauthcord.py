"""Command types for the ``TOGGLE_VIDEO`` and ``TOGGLE_SCREENSHARE`` RPC commands.

See https://docs.discord.food/topics/rpc#toggle-video.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict

ToggleVideoResponse = None


class ToggleScreenshareRequest(TypedDict):
    pid: NotRequired[int]  # omit to present the screenshare modal


ToggleScreenshareResponse = None
