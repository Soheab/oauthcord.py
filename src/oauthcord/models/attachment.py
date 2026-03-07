from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake
from ._base import BaseModel
from .flags import AttachmentFlags

if TYPE_CHECKING:
    from .internals._types.attachment import Attachment as AttachmentPayload
    from .internals._types.message import PartialAttachmentRequest

__all__ = ("Attachment",)


class Attachment(BaseModel["AttachmentPayload", "PartialAttachmentRequest"]):
    """Represents a Discord message attachment.

    Attributes
    ----------
    id: :class:`int`
        The attachment snowflake identifier.
    filename: :class:`str`
        The attachment filename.
    size: :class:`int`
        The attachment size in bytes.
    url: :class:`str`
        The attachment URL.
    proxy_url: :class:`str`
        The proxied attachment URL.
    title: :class:`str`
        The attachment title, if available.
    description: :class:`str`
        The attachment description, if available.
    content_type: :class:`str`
        The attachment content type, if available.
    height: :class:`int`
        The attachment height, if available.
    width: :class:`int`
        The attachment width, if available.
    content_scan_version: :class:`int`
        The content scan version, if available.
    placeholder_version: :class:`int`
        The placeholder version, if available.
    placeholder: :class:`str`
        The placeholder hash, if available.
    ephemeral: :class:`bool`
        Whether the attachment is ephemeral.
    duration_secs: :class:`float`
        The audio or video duration in seconds, if available.
    waveform: :class:`str`
        The audio waveform, if available.
    flags: :class:`AttachmentFlags`
        Attachment flags.
    """

    __slots__ = (
        "content_scan_version",
        "content_type",
        "description",
        "duration_secs",
        "ephemeral",
        "filename",
        "flags",
        "height",
        "id",
        "placeholder",
        "placeholder_version",
        "proxy_url",
        "size",
        "title",
        "url",
        "waveform",
        "width",
    )

    @override
    def _initialize(self, data: AttachmentPayload) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.filename: str = data["filename"]
        self.size: int = data["size"]
        self.url: str = data["url"]
        self.proxy_url: str = data["proxy_url"]
        self.title: str | None = data.get("title")
        self.description: str | None = data.get("description")
        self.content_type: str | None = data.get("content_type")
        self.height: int | None = data.get("height")
        self.width: int | None = data.get("width")
        self.content_scan_version: int | None = data.get("content_scan_version")
        self.placeholder_version: int | None = data.get("placeholder_version")
        self.placeholder: str | None = data.get("placeholder")
        self.ephemeral: bool = data.get("ephemeral", False)
        self.duration_secs: float | None = data.get("duration_secs")
        self.waveform: str | None = data.get("waveform")
        self.flags: AttachmentFlags = AttachmentFlags(data.get("flags", 0))

    @override
    def _to_request(
        self, *, uploaded_filename: str | None = None
    ) -> PartialAttachmentRequest:
        payload: PartialAttachmentRequest = {"id": self.id}
        if self.filename:
            payload["filename"] = self.filename
        if self.description:
            payload["description"] = self.description
        if uploaded_filename:
            payload["uploaded_filename"] = uploaded_filename
        return payload
