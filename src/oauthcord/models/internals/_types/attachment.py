from typing import NotRequired, TypedDict

from .base import Snowflake


class Attachment(TypedDict):
    id: Snowflake
    filename: str
    size: int
    url: str
    proxy_url: str
    title: NotRequired[str]
    description: NotRequired[str]
    content_type: NotRequired[str]
    height: NotRequired[int | None]
    width: NotRequired[int | None]
    content_scan_version: NotRequired[int]
    placeholder_version: NotRequired[int]
    placeholder: NotRequired[str]
    ephemeral: NotRequired[bool]
    duration_secs: NotRequired[float]
    waveform: NotRequired[str]
    flags: NotRequired[int]
