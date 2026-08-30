from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from ...models._base import BaseModel
from ...utils import convert_snowflake
from .activity import Activity
from .guild import RPCGuild
from .message import RPCMessage
from .user import RPCActivityParticipant, RPCUser
from .voice import VoiceInputMode

if TYPE_CHECKING:
    from ...internals._types.rpc import events as event_types

__all__ = (
    "ActivityInstanceParticipantsUpdate",
    "ActivityInvite",
    "ActivityJoin",
    "ActivityJoinRequest",
    "ActivityLayoutModeUpdate",
    "ActivityPipModeUpdate",
    "ActivitySpectate",
    "ClientEnvironmentConfig",
    "GuildStatus",
    "MessageDelete",
    "MessageEvent",
    "OrientationUpdate",
    "OverlayUpdate",
    "PartialRPCMessage",
    "QuestEnrollmentStatusUpdate",
    "RPCErrorEvent",
    "ReadyEvent",
    "ScreenshareApplication",
    "ScreenshareStateUpdate",
    "SpeakingStartData",
    "SpeakingStopData",
    "ThermalStateUpdate",
    "VideoStateUpdate",
    "VoiceChannelSelect",
    "VoiceConnectionPing",
    "VoiceConnectionStatus",
    "VoiceSettingsUpdate2",
)


class RPCErrorEvent(BaseModel["event_types.ErrorEventData"]):
    __slots__ = ("code", "message")

    @override
    def _initialize(self, data: event_types.ErrorEventData) -> None:
        self.code: int = data["code"]
        self.message: str = data["message"]


class VoiceChannelSelect(BaseModel["event_types.VoiceChannelSelectEventData"]):
    __slots__ = ("channel_id", "guild_id")

    @override
    def _initialize(self, data: event_types.VoiceChannelSelectEventData) -> None:
        self.channel_id: int | None = convert_snowflake(data, "channel_id", False)
        self.guild_id: int | None = convert_snowflake(data, "guild_id", False)


class VoiceSettingsUpdate2(BaseModel["event_types.VoiceSettingsUpdate2EventData"]):
    __slots__ = (
        "input_mode",
        "local_mutes",
        "local_volumes",
        "self_deaf",
        "self_mute",
    )

    @override
    def _initialize(self, data: event_types.VoiceSettingsUpdate2EventData) -> None:
        self.input_mode: VoiceInputMode = VoiceInputMode.from_dict(data["input_mode"])
        self.local_mutes: list[int] = [int(mute) for mute in data["local_mutes"]]
        self.local_volumes: dict[int, float] = {
            int(user_id): volume for user_id, volume in data["local_volumes"].items()
        }
        self.self_mute: bool = data["self_mute"]
        self.self_deaf: bool = data["self_deaf"]


class VoiceConnectionPing(BaseModel["event_types.VoiceConnectionPingResponse"]):
    __slots__ = ("time", "value")

    @override
    def _initialize(self, data: event_types.VoiceConnectionPingResponse) -> None:
        self.time: int = data["time"]
        self.value: int = data["value"]


class VoiceConnectionStatus(BaseModel["event_types.VoiceConnectionStatusEventData"]):
    __slots__ = (
        "average_ping",
        "hostname",
        "last_ping",
        "pings",
        "state",
    )

    @override
    def _initialize(self, data: event_types.VoiceConnectionStatusEventData) -> None:
        self.state: event_types.VoiceConnectionState = data["state"]
        self.hostname: str = data["hostname"]
        self.pings: list[VoiceConnectionPing] = [
            self._initialize_other(VoiceConnectionPing, ping) for ping in data["pings"]
        ]
        self.average_ping: int | None = data.get("average_ping")
        self.last_ping: int | None = data.get("last_ping")


class SpeakingStartData(BaseModel["event_types.SpeakingStartEventData"]):
    __slots__ = ("channel_id", "user_id")

    @override
    def _initialize(self, data: event_types.SpeakingStartEventData) -> None:
        self.channel_id: int = convert_snowflake(data, "channel_id")
        self.user_id: int = convert_snowflake(data, "user_id")


class SpeakingStopData(BaseModel["event_types.SpeakingStopEventData"]):
    __slots__ = ("channel_id", "user_id")

    @override
    def _initialize(self, data: event_types.SpeakingStopEventData) -> None:
        self.channel_id: int = convert_snowflake(data, "channel_id")
        self.user_id: int = convert_snowflake(data, "user_id")


class ActivityJoin(BaseModel["event_types.ActivityJoinEventData"]):
    __slots__ = ("intent", "secret")

    @override
    def _initialize(self, data: event_types.ActivityJoinEventData) -> None:
        self.secret: str = data["secret"]
        self.intent: event_types.JoinIntent | None = data.get("intent")


class ActivitySpectate(BaseModel["event_types.ActivitySpectateEventData"]):
    __slots__ = ("secret",)

    @override
    def _initialize(self, data: event_types.ActivitySpectateEventData) -> None:
        self.secret: str = data["secret"]


class ActivityPipModeUpdate(BaseModel["event_types.ActivityPipModeUpdateEventData"]):
    __slots__ = ("is_pip_mode",)

    @override
    def _initialize(self, data: event_types.ActivityPipModeUpdateEventData) -> None:
        self.is_pip_mode: bool = data["is_pip_mode"]


class ActivityLayoutModeUpdate(
    BaseModel["event_types.ActivityLayoutModeUpdateEventData"]
):
    __slots__ = ("layout_mode",)

    @override
    def _initialize(self, data: event_types.ActivityLayoutModeUpdateEventData) -> None:
        self.layout_mode: event_types.LayoutMode = data["layout_mode"]


class ThermalStateUpdate(BaseModel["event_types.ThermalStateUpdateEventData"]):
    __slots__ = ("thermal_state",)

    @override
    def _initialize(self, data: event_types.ThermalStateUpdateEventData) -> None:
        self.thermal_state: event_types.ThermalState = data["thermal_state"]


class OrientationUpdate(BaseModel["event_types.OrientationUpdateEventData"]):
    __slots__ = ("screen_orientation",)

    @override
    def _initialize(self, data: event_types.OrientationUpdateEventData) -> None:
        self.screen_orientation: int = data["screen_orientation"]


class PartialRPCMessage(BaseModel["event_types.PartialRPCMessageResponse"]):
    __slots__ = ("id",)

    @override
    def _initialize(self, data: event_types.PartialRPCMessageResponse) -> None:
        self.id: int = convert_snowflake(data, "id")


class OverlayUpdate(BaseModel["event_types.OverlayUpdateEventData"]):
    __slots__ = ("enabled", "locked")

    @override
    def _initialize(self, data: event_types.OverlayUpdateEventData) -> None:
        self.enabled: bool = data["enabled"]
        self.locked: bool = data["locked"]


class ScreenshareApplication(BaseModel["event_types.ScreenshareApplicationResponse"]):
    __slots__ = ("name",)

    @override
    def _initialize(self, data: event_types.ScreenshareApplicationResponse) -> None:
        self.name: str = data["name"]


class ScreenshareStateUpdate(BaseModel["event_types.ScreenshareStateUpdateEventData"]):
    __slots__ = ("active", "application", "pid")

    @override
    def _initialize(self, data: event_types.ScreenshareStateUpdateEventData) -> None:
        self.active: bool = data["active"]
        self.pid: int | None = data["pid"]
        self.application: ScreenshareApplication | None = self._initialize_other(
            ScreenshareApplication, data["application"], optional=True
        )


class VideoStateUpdate(BaseModel["event_types.VideoStateUpdateEventData"]):
    __slots__ = ("active",)

    @override
    def _initialize(self, data: event_types.VideoStateUpdateEventData) -> None:
        self.active: bool = data["active"]


class QuestEnrollmentStatusUpdate(
    BaseModel["event_types.QuestEnrollmentStatusUpdateEventData"]
):
    __slots__ = ("is_enrolled", "quest_id")

    @override
    def _initialize(
        self, data: event_types.QuestEnrollmentStatusUpdateEventData
    ) -> None:
        self.quest_id: int = convert_snowflake(data, "quest_id")
        self.is_enrolled: bool = data["is_enrolled"]


class ClientEnvironmentConfig(BaseModel["event_types.ClientEnvironmentConfigResponse"]):
    __slots__ = ("api_endpoint", "cdn_host", "environment")

    @override
    def _initialize(self, data: event_types.ClientEnvironmentConfigResponse) -> None:
        self.cdn_host: str | None = data.get("cdn_host")
        self.api_endpoint: str = data["api_endpoint"]
        self.environment: str = data["environment"]


class ReadyEvent(BaseModel["event_types.ReadyEventData"]):
    __slots__ = ("config", "user", "version")

    @override
    def _initialize(self, data: event_types.ReadyEventData) -> None:
        self.version: int = data["v"]
        self.config: ClientEnvironmentConfig = self._initialize_other(
            ClientEnvironmentConfig, data["config"]
        )
        # Only present in the IPC transport.
        self.user: RPCUser | None = self._initialize_other(
            RPCUser, data.get("user"), optional=True
        )


class GuildStatus(BaseModel["event_types.GuildStatusEventData"]):
    __slots__ = ("guild",)

    @override
    def _initialize(self, data: event_types.GuildStatusEventData) -> None:
        self.guild: RPCGuild = self._initialize_other(RPCGuild, data["guild"])


class MessageEvent(BaseModel["event_types.MessageCreateEventData"]):
    """Payload shared by ``NOTIFICATION_CREATE``, ``MESSAGE_CREATE``, and ``MESSAGE_UPDATE``."""

    __slots__ = ("channel_id", "message")

    @override
    def _initialize(self, data: event_types.MessageCreateEventData) -> None:
        self.channel_id: int = convert_snowflake(data, "channel_id")
        self.message: RPCMessage = self._initialize_other(RPCMessage, data["message"])


class MessageDelete(BaseModel["event_types.MessageDeleteEventData"]):
    __slots__ = ("channel_id", "message")

    @override
    def _initialize(self, data: event_types.MessageDeleteEventData) -> None:
        self.channel_id: int = convert_snowflake(data, "channel_id")
        self.message: PartialRPCMessage = self._initialize_other(
            PartialRPCMessage, data["message"]
        )


class _BaseActivityJoinRequestOrInvite[D: Any](BaseModel[D]):
    """Fields shared by ``ACTIVITY_JOIN_REQUEST`` and ``ACTIVITY_INVITE``.

    The two events carry the same payload apart from their ``type``
    discriminator; each has its own model so they can diverge independently.
    """

    __slots__ = (
        "activity",
        "channel_id",
        "message_id",
        "user",
    )

    @override
    def _initialize(self, data: D) -> None:
        data_: (
            event_types.ActivityJoinRequestEventData
            | event_types.ActivityInviteEventData
        ) = data
        self.user: RPCUser = self._initialize_other(RPCUser, data_["user"])
        self.activity: Activity = Activity.from_dict(data_["activity"])
        self.channel_id: int = convert_snowflake(data_, "channel_id")
        self.message_id: int = convert_snowflake(data_, "message_id")


class ActivityJoinRequest(
    _BaseActivityJoinRequestOrInvite["event_types.ActivityJoinRequestEventData"]
):
    """Payload of the ``ACTIVITY_JOIN_REQUEST`` event."""

    __slots__ = ()


class ActivityInvite(
    _BaseActivityJoinRequestOrInvite["event_types.ActivityInviteEventData"]
):
    """Payload of the ``ACTIVITY_INVITE`` event."""

    __slots__ = ()


class ActivityInstanceParticipantsUpdate(
    BaseModel["event_types.ActivityInstanceParticipantsUpdateEventData"]
):
    __slots__ = ("participants",)

    @override
    def _initialize(
        self, data: event_types.ActivityInstanceParticipantsUpdateEventData
    ) -> None:
        self.participants: list[RPCActivityParticipant] = [
            self._initialize_other(RPCActivityParticipant, participant)
            for participant in data.get("participants", [])
        ]
