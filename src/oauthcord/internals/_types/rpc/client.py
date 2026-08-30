"""Command types for the client-level RPC commands.

Covers ``SET_CERTIFIED_DEVICES``, ``GET_IMAGE``, ``OPEN_EXTERNAL_LINK`` and
``USER_SETTINGS_GET_LOCALE``.

See https://docs.discord.food/topics/rpc#set-certified-devices.
"""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from ..base import Locale, Snowflake

CertifiedDeviceType = Literal["audioinput", "audiooutput", "videoinput"]


class CertifiedDeviceVendorRequest(TypedDict):
    id: str
    name: str


class CertifiedDeviceModelRequest(TypedDict):
    id: str
    name: str


class CertifiedDeviceRequest(TypedDict):
    type: CertifiedDeviceType
    id: str
    vendor: CertifiedDeviceVendorRequest
    model: CertifiedDeviceModelRequest
    related: NotRequired[list[str]]
    # the settings below only apply to audioinput devices
    echo_cancellation: NotRequired[bool]
    noise_suppression: NotRequired[bool]
    automatic_gain_control: NotRequired[bool]
    hardware_mute: NotRequired[bool]


class SetCertifiedDevicesRequest(TypedDict):
    devices: list[CertifiedDeviceRequest]


SetCertifiedDevicesResponse = None

ImageType = Literal["user"]
ImageFormat = Literal["png", "webp", "jpg"]


class GetImageRequest(TypedDict):
    type: ImageType
    id: Snowflake
    format: ImageFormat
    size: int  # power of two between 16 and 1024


class GetImageResponse(TypedDict):
    data_url: str


class OpenExternalLinkRequest(TypedDict):
    url: str


OpenExternalLinkResponse = None


class UserSettingsGetLocaleResponse(TypedDict):
    locale: Locale
