from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, override

from ...models._base import BaseModel
from ...utils import convert_snowflake, iso_to_datetime

if TYPE_CHECKING:
    from ...internals._types.rpc import quest

__all__ = ("QuestEnrollmentStatus", "TimerResult")


class QuestEnrollmentStatus(BaseModel["quest.GetQuestEnrollmentStatusResponse"]):
    __slots__ = ("enrolled_at", "is_enrolled", "quest_id")

    @override
    def _initialize(self, data: quest.GetQuestEnrollmentStatusResponse) -> None:
        self.quest_id: int = convert_snowflake(data, "quest_id")
        self.is_enrolled: bool = data["is_enrolled"]
        self.enrolled_at: datetime.datetime | None = iso_to_datetime(
            data["enrolled_at"]
        )


class TimerResult(BaseModel["quest.QuestStartTimerResponse"]):
    __slots__ = ("success",)

    @override
    def _initialize(self, data: quest.QuestStartTimerResponse) -> None:
        self.success: bool = data["success"]
