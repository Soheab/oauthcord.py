"""Command types for the soundboard RPC commands.

See https://docs.discord.food/topics/rpc#get-soundboard-sounds.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict

from ..base import Snowflake
from ..user import PartialUserResponse


class SoundboardSoundResponse(TypedDict):
    """See https://docs.discord.food/resources/soundboard#soundboard-sound-object."""

    sound_id: Snowflake
    name: str
    volume: float  # 0-1
    emoji_id: Snowflake | None
    emoji_name: str | None
    guild_id: NotRequired[Snowflake]  # default sounds may have this set to 0
    available: bool
    user: NotRequired[
        PartialUserResponse
    ]  # Only included from List Guild Soundboard Sounds or Get Guild Soundboard Sound
    user_id: NotRequired[Snowflake]  # only from gateway


GetSoundboardSoundsResponse = list[SoundboardSoundResponse]


class PlaySoundboardSoundRequest(TypedDict):
    guild_id: NotRequired[Snowflake]
    sound_id: NotRequired[Snowflake]


PlaySoundboardSoundResponse = None
