"""Command types for the quest RPC commands.

See https://docs.discord.food/topics/rpc#get-quest-enrollment-status.
"""

from __future__ import annotations

from typing import TypedDict

from ..base import Snowflake


class GetQuestEnrollmentStatusRequest(TypedDict):
    quest_id: Snowflake


class GetQuestEnrollmentStatusResponse(TypedDict):
    quest_id: Snowflake
    is_enrolled: bool
    enrolled_at: str | None  # iso


class QuestStartTimerRequest(TypedDict):
    quest_id: Snowflake


class QuestStartTimerResponse(TypedDict):
    success: bool
