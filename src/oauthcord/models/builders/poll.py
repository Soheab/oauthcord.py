import datetime
from typing import TYPE_CHECKING

from .._base import BaseModel
from ..emoji import Emoji
from ..enums import PollLayoutType

if TYPE_CHECKING:
    from ...internals._types.message import (
        PollAnswerRequest,
        PollCreateRequest,
    )

__all__ = (
    "PollAnswerBuilder",
    "PollBuilder",
)


class PollBuilder(BaseModel[None, "PollCreateRequest"]):
    def __init__(
        self,
        *,
        question: str,
        answers: list[PollAnswerBuilder],
        duration: int | float | datetime.timedelta | datetime.datetime,
        allow_multiselect: bool = False,
        layout: PollLayoutType | int = PollLayoutType.DEFAULT,
    ) -> None:
        self.question = question
        self.answers: list[PollAnswerBuilder] = answers
        self.duration: int | float | datetime.timedelta | datetime.datetime = duration
        self.allow_multiselect: bool = allow_multiselect
        self.layout: PollLayoutType | int = layout

    def add_answer(
        self,
        *,
        text: str,
        emoji: str | Emoji | None = None,
    ) -> PollAnswerBuilder:
        answer = PollAnswerBuilder(text=text, emoji=emoji)
        self.answers.append(answer)
        return answer

    def _to_request(self) -> PollCreateRequest:
        duration_seconds: int = 0
        if isinstance(self.duration, datetime.timedelta):
            duration_seconds = int(self.duration.total_seconds())
        elif isinstance(self.duration, datetime.datetime):
            now = datetime.datetime.now(datetime.timezone.utc)
            if self.duration.tzinfo is None:
                # Assume it's in UTC if it's naive
                target_time = self.duration.replace(tzinfo=datetime.timezone.utc)
            else:
                target_time = self.duration

            duration_seconds = int((target_time - now).total_seconds())
        elif isinstance(self.duration, (int, float)):
            duration_seconds = int(self.duration)

        return {
            "question": {
                "text": self.question,
            },
            "answers": [answer._to_request() for answer in self.answers],
            "duration": duration_seconds,
            "allow_multiselect": self.allow_multiselect,
            "layout_type": self.layout.value
            if isinstance(self.layout, PollLayoutType)
            else self.layout,  # type: ignore
        }


class PollAnswerBuilder(BaseModel[None, "PollAnswerRequest"]):
    def __init__(
        self,
        *,
        text: str,
        emoji: str | Emoji | None = None,
    ):
        self.text: str = text
        self.emoji: str | Emoji | None = emoji

    def _to_request(self) -> PollAnswerRequest:
        base = {
            "text": self.text,
        }
        if self.emoji is not None:
            base["emoji"] = (  # type: ignore
                self.emoji._to_request()
                if isinstance(self.emoji, Emoji)
                else self.emoji
            )
        return {"poll_media": base}  # type: ignore
