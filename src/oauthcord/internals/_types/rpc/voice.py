from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from ..base import Snowflake
from .user import RPCUserResponse


class RPCVoiceStateResponse(TypedDict):
    nick: str
    mute: bool
    volume: float
    pan: RPCPan
    voice_state: RPCRemoteVoiceStateResponse
    user: RPCUserResponse


class RPCPan(TypedDict):
    left: float
    right: float


class RPCRemoteVoiceStateResponse(TypedDict):
    mute: bool
    deaf: bool
    self_mute: bool
    self_deaf: bool
    suppress: bool


RPCVoiceSettingsModeType = Literal["PUSH_TO_TALK", "VOICE_ACTIVITY"]
ShortcutKeyComboType = Literal[
    0,  # KEYBOARD_KEY
    1,  # MOUSE_BUTTON
    2,  # KEYBOARD_MODIFIER_KEY
    3,  # GAMEPAD_BUTTON
]


class ShortcutKeyComboRequest(TypedDict):
    type: ShortcutKeyComboType
    code: int
    name: NotRequired[str]


class ShortcutKeyComboResponse(TypedDict):
    type: ShortcutKeyComboType
    code: int
    name: str  # always present when received


class AvailableDeviceResponse(TypedDict):
    id: str
    name: str


class RPCVoiceIOSettingsRequest(TypedDict):
    device_id: NotRequired[str]
    volume: NotRequired[float]


class RPCVoiceIOSettingsResponse(TypedDict):
    available_devices: list[AvailableDeviceResponse]
    device_id: str
    volume: float


class PartialRPCVoiceSettingsModeRequest(TypedDict):
    type: NotRequired[RPCVoiceSettingsModeType]
    auto_threshold: NotRequired[bool]
    threshold: NotRequired[int]  # -100-0
    shortcut: NotRequired[list[ShortcutKeyComboRequest]]
    delay: NotRequired[int]  # max 2000


class RPCVoiceSettingsModeResponse(TypedDict):
    type: RPCVoiceSettingsModeType
    auto_threshold: bool
    threshold: int
    shortcut: list[ShortcutKeyComboResponse]
    delay: int


class RPCVoiceSettingsResponse(TypedDict):
    input: RPCVoiceIOSettingsResponse
    output: RPCVoiceIOSettingsResponse
    mode: RPCVoiceSettingsModeResponse
    automatic_gain_control: bool
    echo_cancellation: bool
    noise_suppression: bool
    qos: bool
    silence_warning: bool
    deaf: bool
    mute: bool


class RPCVoiceInputModeRequest(TypedDict):
    type: RPCVoiceSettingsModeType
    shortcut: str


# -- Commands ----------------------------------------------------------------


class SetUserVoiceSettingsRequest(TypedDict):
    user_id: Snowflake
    pan: NotRequired[RPCPan]
    volume: NotRequired[int]  # 0-200
    mute: NotRequired[bool]


class SetUserVoiceSettingsResponse(TypedDict):
    """The settings as resolved by the client."""

    user_id: Snowflake
    pan: RPCPan
    volume: int
    mute: bool


class SetUserVoiceSettings2Request(TypedDict):
    user_id: Snowflake
    volume: NotRequired[int]  # 0-200
    mute: NotRequired[bool]


SetUserVoiceSettings2Response = None


class PushToTalkRequest(TypedDict):
    active: bool


PushToTalkResponse = None

GetVoiceSettingsResponse = RPCVoiceSettingsResponse


class SetVoiceSettingsRequest(TypedDict):
    input: NotRequired[RPCVoiceIOSettingsRequest]
    output: NotRequired[RPCVoiceIOSettingsRequest]
    mode: NotRequired[PartialRPCVoiceSettingsModeRequest]
    automatic_gain_control: NotRequired[bool]
    echo_cancellation: NotRequired[bool]
    noise_suppression: NotRequired[bool]
    qos: NotRequired[bool]
    silence_warning: NotRequired[bool]
    deaf: NotRequired[bool]
    mute: NotRequired[bool]


SetVoiceSettingsResponse = RPCVoiceSettingsResponse


class SetVoiceSettings2Request(TypedDict):
    input_mode: NotRequired[RPCVoiceInputModeRequest]
    self_mute: NotRequired[bool]
    self_deaf: NotRequired[bool]


SetVoiceSettings2Response = None
