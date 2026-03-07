from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake
from ._base import BaseModel
from .channel import GuildChannel, _from_data
from .flags import LobbyFlags, LobbyMemberFlags

if TYPE_CHECKING:
    from .internals._types.lobby import LobbyMemberResponse, LobbyResponse


__all__ = (
    "Lobby",
    "LobbyMember",
)


class LobbyMember(BaseModel["LobbyMemberResponse"]):
    """Represents a Discord lobby member payload."""

    __slots__ = ("flags", "id", "metadata")

    @override
    def _initialize(self, data: LobbyMemberResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.metadata: dict[str, str] | None = data.get("metadata")
        self.flags: LobbyMemberFlags | None = (
            LobbyMemberFlags(raw_flags)
            if (raw_flags := data.get("flags")) is not None
            else None
        )


class Lobby(BaseModel["LobbyResponse"]):
    """Represents a Discord lobby payload."""

    __slots__ = (
        "application_id",
        "flags",
        "id",
        "linked_channel",
        "members",
        "metadata",
    )

    @override
    def _initialize(self, data: LobbyResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.application_id: int = convert_snowflake(data, "application_id")
        self.metadata: dict[str, str] | None = data.get("metadata")
        self.members: list[LobbyMember] = [
            self._initialize_subclass_with_http(LobbyMember, member)
            for member in data.get("members", [])
        ]
        self.flags: LobbyFlags | None = (
            LobbyFlags(raw_flags)
            if (raw_flags := data.get("flags")) is not None
            else None
        )

        linked_channel_data = data.get("linked_channel")
        parsed = (
            _from_data(self._http, linked_channel_data) if linked_channel_data else None
        )
        self.linked_channel: GuildChannel | None = parsed  # type: ignore
