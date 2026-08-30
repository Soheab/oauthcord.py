from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

from ...models._base import BaseModel
from ...utils import convert_snowflake, to_enum
from ..enums import ShortcutKeyComboType, VoiceSettingsModeType
from .user import RPCUser

if TYPE_CHECKING:
    from ...internals._types.rpc import voice as voice_types

__all__ = (
    "AvailableDevice",
    "Pan",
    "RPCVoiceState",
    "RemoteVoiceState",
    "ShortcutKeyCombo",
    "UserVoiceSettings",
    "VoiceIOSettings",
    "VoiceInputMode",
    "VoiceSettings",
    "VoiceSettingsMode",
)


class Pan(BaseModel["voice_types.RPCPan", "voice_types.RPCPan"]):
    """A user's stereo pan position, as sent to and received from
    ``SET_USER_VOICE_SETTINGS``."""

    __slots__ = ("left", "right")

    def __init__(self, *, left: float = 1.0, right: float = 1.0) -> None:
        self.left: float = left
        self.right: float = right
        super().__init__(data=self.to_dict())

    @override
    def to_dict(self) -> voice_types.RPCPan:
        return {"left": self.left, "right": self.right}

    @classmethod
    @override
    def from_dict(cls, data: voice_types.RPCPan) -> Self:
        return cls(left=data["left"], right=data["right"])


class VoiceInputMode(
    BaseModel[
        "voice_types.RPCVoiceInputModeRequest", "voice_types.RPCVoiceInputModeRequest"
    ]
):
    """The ``input_mode`` sent to ``SET_VOICE_SETTINGS_2``.

    Unlike :class:`VoiceSettingsMode`, ``shortcut`` here is a single pre-encoded
    shortcut string rather than a list of :class:`ShortcutKeyCombo`.
    """

    __slots__ = ("shortcut", "type")

    def __init__(
        self,
        type: VoiceSettingsModeType | voice_types.RPCVoiceSettingsModeType,
        shortcut: str,
    ) -> None:
        self.type: VoiceSettingsModeType = to_enum(VoiceSettingsModeType, type)
        self.shortcut: str = shortcut
        super().__init__(data=self.to_dict())

    @override
    def to_dict(self) -> voice_types.RPCVoiceInputModeRequest:
        return {"type": self.type.value, "shortcut": self.shortcut}

    @classmethod
    @override
    def from_dict(cls, data: voice_types.RPCVoiceInputModeRequest) -> Self:
        return cls(type=data["type"], shortcut=data["shortcut"])


class RemoteVoiceState(BaseModel["voice_types.RPCRemoteVoiceStateResponse"]):
    """Represents Discord API data for `RPCRemoteVoiceState`."""

    __slots__ = (
        "deaf",
        "mute",
        "self_deaf",
        "self_mute",
        "suppress",
    )

    @override
    def _initialize(self, data: voice_types.RPCRemoteVoiceStateResponse) -> None:
        self.mute: bool = data["mute"]
        self.deaf: bool = data["deaf"]
        self.self_mute: bool = data["self_mute"]
        self.self_deaf: bool = data["self_deaf"]
        self.suppress: bool = data["suppress"]


class RPCVoiceState(BaseModel["voice_types.RPCVoiceStateResponse"]):
    """Represents Discord API data for `RPCVoiceState`."""

    __slots__ = (
        "mute",
        "nick",
        "pan",
        "user",
        "voice_state",
        "volume",
    )

    @override
    def _initialize(self, data: voice_types.RPCVoiceStateResponse) -> None:
        self.nick: str = data["nick"]
        self.mute: bool = data["mute"]
        self.volume: float = data["volume"]
        self.pan: Pan = Pan.from_dict(data["pan"])
        self.voice_state: RemoteVoiceState = self._initialize_other(
            RemoteVoiceState, data["voice_state"]
        )
        self.user: RPCUser = self._initialize_other(RPCUser, data["user"])


class AvailableDevice(BaseModel["voice_types.AvailableDeviceResponse"]):
    """Represents Discord API data for `AvailableDevice`."""

    __slots__ = ("id", "name")

    @override
    def _initialize(self, data: voice_types.AvailableDeviceResponse) -> None:
        self.id: str = data["id"]
        self.name: str = data["name"]


class ShortcutKeyCombo(
    BaseModel[
        "voice_types.ShortcutKeyComboResponse", "voice_types.ShortcutKeyComboRequest"
    ]
):
    """Represents Discord API data for `ShortcutKeyCombo`."""

    __slots__ = ("code", "name", "type")

    @override
    def _initialize(self, data: voice_types.ShortcutKeyComboResponse) -> None:
        self.type: ShortcutKeyComboType = to_enum(ShortcutKeyComboType, data["type"])
        self.code: int = data["code"]
        self.name: str = data["name"]

    @override
    def to_dict(self) -> voice_types.ShortcutKeyComboRequest:
        return {"type": self.type.value, "code": self.code, "name": self.name}


class VoiceIOSettings(
    BaseModel[
        "voice_types.RPCVoiceIOSettingsResponse",
        "voice_types.RPCVoiceIOSettingsRequest",
    ]
):
    """Represents Discord API data for `RPCVoiceIOSettings`."""

    __slots__ = ("available_devices", "device_id", "volume")

    @override
    def _initialize(self, data: voice_types.RPCVoiceIOSettingsResponse) -> None:
        self.device_id: str = data["device_id"]
        self.volume: float = data["volume"]
        self.available_devices: list[AvailableDevice] = [
            self._initialize_other(AvailableDevice, device)
            for device in data["available_devices"]
        ]

    @override
    def to_dict(self) -> voice_types.RPCVoiceIOSettingsRequest:
        return {"device_id": self.device_id, "volume": self.volume}


class VoiceSettingsMode(
    BaseModel[
        "voice_types.RPCVoiceSettingsModeResponse",
        "voice_types.PartialRPCVoiceSettingsModeRequest",
    ]
):
    """Represents Discord API data for `RPCVoiceSettingsMode`."""

    __slots__ = (
        "auto_threshold",
        "delay",
        "shortcut",
        "threshold",
        "type",
    )

    @override
    def _initialize(self, data: voice_types.RPCVoiceSettingsModeResponse) -> None:
        self.type: VoiceSettingsModeType = to_enum(VoiceSettingsModeType, data["type"])
        self.auto_threshold: bool = data["auto_threshold"]
        self.threshold: int = data["threshold"]
        self.shortcut: list[ShortcutKeyCombo] = [
            self._initialize_other(ShortcutKeyCombo, combo)
            for combo in data["shortcut"]
        ]
        self.delay: int = data["delay"]

    @override
    def to_dict(self) -> voice_types.PartialRPCVoiceSettingsModeRequest:
        return {
            "type": self.type.value,
            "auto_threshold": self.auto_threshold,
            "threshold": self.threshold,
            "shortcut": [combo.to_dict() for combo in self.shortcut],
            "delay": self.delay,
        }


class VoiceSettings(
    BaseModel[
        "voice_types.RPCVoiceSettingsResponse", "voice_types.SetVoiceSettingsRequest"
    ]
):
    """Represents Discord API data for `RPCVoiceSettings`."""

    __slots__ = (
        "automatic_gain_control",
        "deaf",
        "echo_cancellation",
        "input",
        "mode",
        "mute",
        "noise_suppression",
        "output",
        "qos",
        "silence_warning",
    )

    @override
    def _initialize(self, data: voice_types.RPCVoiceSettingsResponse) -> None:
        self.input: VoiceIOSettings = self._initialize_other(
            VoiceIOSettings, data["input"]
        )
        self.output: VoiceIOSettings = self._initialize_other(
            VoiceIOSettings, data["output"]
        )
        self.mode: VoiceSettingsMode = self._initialize_other(
            VoiceSettingsMode, data["mode"]
        )
        self.automatic_gain_control: bool = data["automatic_gain_control"]
        self.echo_cancellation: bool = data["echo_cancellation"]
        self.noise_suppression: bool = data["noise_suppression"]
        self.qos: bool = data["qos"]
        self.silence_warning: bool = data["silence_warning"]
        self.deaf: bool = data["deaf"]
        self.mute: bool = data["mute"]

    @override
    def to_dict(self) -> voice_types.SetVoiceSettingsRequest:
        """Serialize this object into a ``SET_VOICE_SETTINGS`` request payload."""
        return {
            "input": self.input.to_dict(),
            "output": self.output.to_dict(),
            "mode": self.mode.to_dict(),
            "automatic_gain_control": self.automatic_gain_control,
            "echo_cancellation": self.echo_cancellation,
            "noise_suppression": self.noise_suppression,
            "qos": self.qos,
            "silence_warning": self.silence_warning,
            "deaf": self.deaf,
            "mute": self.mute,
        }


class UserVoiceSettings(
    BaseModel[
        "voice_types.SetUserVoiceSettingsResponse",
        "voice_types.SetUserVoiceSettingsRequest",
    ]
):
    """Per-user local voice settings, as resolved by the client in response to
    ``SET_USER_VOICE_SETTINGS``."""

    __slots__ = ("mute", "pan", "user_id", "volume")

    @override
    def _initialize(self, data: voice_types.SetUserVoiceSettingsResponse) -> None:
        self.user_id: int = convert_snowflake(data, "user_id")
        self.pan: Pan = Pan.from_dict(data["pan"])
        self.volume: int = data["volume"]
        self.mute: bool = data["mute"]

    @override
    def to_dict(self) -> voice_types.SetUserVoiceSettingsRequest:
        """Serialize this object into a ``SET_USER_VOICE_SETTINGS`` request payload."""
        return {
            "user_id": self.user_id,
            "pan": self.pan.to_dict(),
            "volume": self.volume,
            "mute": self.mute,
        }
