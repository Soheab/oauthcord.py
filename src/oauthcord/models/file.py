import base64
import os
from typing import IO

__all__ = ("File",)


class File:
    """Represents a file that can be uploaded in multipart Discord API requests."""

    __slots__ = ("content_type", "data", "description", "filename")

    def __init__(
        self,
        data: bytes | bytearray | memoryview | IO[bytes] | os.PathLike[str] | str,
        *,
        filename: str | None = None,
        content_type: str | None = None,
        description: str | None = None,
    ) -> None:
        self.data = data
        self.filename = filename
        self.content_type = content_type
        self.description = description

    def read(self) -> tuple[bytes, str]:
        """Read file bytes and return them with the upload filename."""
        if isinstance(self.data, (str, os.PathLike)):
            path = os.fspath(self.data)
            with open(path, "rb") as handle:
                content = handle.read()
            filename = self.filename or os.path.basename(path)
            return content, filename

        if isinstance(self.data, (bytes, bytearray, memoryview)):
            content = bytes(self.data)
            filename = self.filename or "file"
            return content, filename

        content = self.data.read()
        filename = self.filename or "file"
        return content, filename

    def to_data_uri(self) -> str:
        """Encode the file as a data URI string."""
        content, _ = self.read()
        content_type = self.content_type or "application/octet-stream"
        encoded = base64.b64encode(content).decode("ascii")
        return f"data:{content_type};base64,{encoded}"
