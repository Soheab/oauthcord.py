from typing import TYPE_CHECKING, Self, override

from ._base import StatelessBaseModel

if TYPE_CHECKING:
    from .internals._types import message as message_types

__all__ = (
    "Embed",
    "EmbedAuthor",
    "EmbedField",
    "EmbedFooter",
    "EmbedMedia",
)


@StatelessBaseModel.add_slots("text", "icon_url", "proxy_icon_url")
class EmbedFooter(
    StatelessBaseModel[
        "message_types.EmbedFooterResponse", "message_types.EmbedFooterRequest"
    ]
):
    def __init__(
        self,
        text: str,
        *,
        icon_url: str | None = None,
        proxy_icon_url: str | None = None,
    ) -> None:
        super().__init__(
            data={
                "text": text,
            }
        )
        self.text: str = text
        self.icon_url: str | None = icon_url
        self.proxy_icon_url: str | None = proxy_icon_url

    @override
    def _to_request(self) -> message_types.EmbedFooterRequest:
        payload: message_types.EmbedFooterRequest = {"text": self.text}
        if self.icon_url is not None:
            payload["icon_url"] = self.icon_url
        return payload

    @override
    @classmethod
    def _from_response(cls, data: message_types.EmbedFooterResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            data["text"],
            icon_url=data.get("icon_url"),
            proxy_icon_url=data.get("proxy_icon_url"),
        )


@StatelessBaseModel.add_slots(
    "url",
    "proxy_url",
    "height",
    "width",
    "flags",
    "description",
    "content_type",
    "content_scan_metadata",
    "placeholder_version",
    "placeholder",
)
class EmbedMedia(
    StatelessBaseModel[
        "message_types.EmbedMediaResponse", "message_types.EmbedMediaRequest"
    ]
):
    """Builder and serializer for Discord embed payload data."""

    def __init__(
        self,
        url: str,
        *,
        description: str | None = None,
        proxy_url: str | None = None,
        height: int | None = None,
        width: int | None = None,
        flags: int | None = None,
        content_type: str | None = None,
        content_scan_metadata: dict[str, object] | None = None,
        placeholder_version: int | None = None,
        placeholder: str | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(data={"url": url})
        self.url: str = url
        self.description: str | None = description
        self.proxy_url: str | None = proxy_url
        self.height: int | None = height
        self.width: int | None = width
        self.flags: int | None = flags
        self.content_type: str | None = content_type
        self.content_scan_metadata: dict[str, object] | None = content_scan_metadata
        self.placeholder_version: int | None = placeholder_version
        self.placeholder: str | None = placeholder

    @override
    def _to_request(self) -> message_types.EmbedMediaRequest:
        payload: message_types.EmbedMediaRequest = {"url": self.url}
        if self.description is not None:
            payload["description"] = self.description
        return payload

    @classmethod
    @override
    def _from_response(cls, data: message_types.EmbedMediaResponse) -> Self:
        return cls(
            data["url"],
            proxy_url=data.get("proxy_url"),
            height=data.get("height"),
            width=data.get("width"),
            flags=data.get("flags"),
            description=data.get("description"),
            content_type=data.get("content_type"),
            content_scan_metadata=data.get("content_scan_metadata"),
            placeholder_version=data.get("placeholder_version"),
            placeholder=data.get("placeholder"),
        )


@StatelessBaseModel.add_slots("name", "url", "icon_url", "proxy_icon_url")
class EmbedAuthor(
    StatelessBaseModel[
        "message_types.EmbedAuthorResponse", "message_types.EmbedAuthorRequest"
    ]
):
    def __init__(
        self,
        name: str,
        *,
        url: str | None = None,
        icon_url: str | None = None,
        proxy_icon_url: str | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.name = name
        self.url = url
        self.icon_url = icon_url
        self.proxy_icon_url = proxy_icon_url

    @override
    def _to_request(self) -> message_types.EmbedAuthorRequest:
        """Serialize this object into a Discord API request payload."""
        payload: message_types.EmbedAuthorRequest = {"name": self.name}
        if self.url is not None:
            payload["url"] = self.url
        if self.icon_url is not None:
            payload["icon_url"] = self.icon_url
        return payload

    @classmethod
    @override
    def _from_response(cls, data: message_types.EmbedAuthorResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            data["name"],
            url=data.get("url"),
            icon_url=data.get("icon_url"),
            proxy_icon_url=data.get("proxy_icon_url"),
        )


@StatelessBaseModel.add_slots("name", "value", "inline")
class EmbedField(
    StatelessBaseModel[
        "message_types.EmbedFieldResponse", "message_types.EmbedFieldRequest"
    ]
):
    """Builder and serializer for Discord embed payload data."""

    def __init__(self, name: str, value: str, *, inline: bool | None = None) -> None:
        super().__init__(data={"name": name, "value": value})
        self.name = name
        self.value = value
        self.inline = inline

    @override
    def _to_request(self) -> message_types.EmbedFieldRequest:
        """Serialize this object into a Discord API request payload."""
        payload: message_types.EmbedFieldRequest = {
            "name": self.name,
            "value": self.value,
        }
        if self.inline is not None:
            payload["inline"] = self.inline
        return payload

    @classmethod
    @override
    def _from_response(cls, data: message_types.EmbedFieldResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(data["name"], data["value"], inline=data.get("inline"))


@StatelessBaseModel.add_slots(
    "title",
    "type",
    "description",
    "url",
    "timestamp",
    "color",
    "footer",
    "image",
    "thumbnail",
    "video",
    "provider",
    "author",
    "fields",
    "reference_id",
    "content_scan_version",
    "flags",
)
class Embed(
    StatelessBaseModel["message_types.EmbedResponse", "message_types.EmbedRequest"]
):
    def __init__(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        timestamp: str | None = None,
        color: int | None = None,
        footer: EmbedFooter | None = None,
        image: EmbedMedia | None = None,
        thumbnail: EmbedMedia | None = None,
        author: EmbedAuthor | None = None,
        fields: list[EmbedField] | None = None,
        type: str | None = None,
        video: EmbedMedia | None = None,
        provider: dict[str, object] | None = None,
        reference_id: int | str | None = None,
        content_scan_version: int | None = None,
        flags: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.title = title
        self.type = type
        self.description = description
        self.url = url
        self.timestamp = timestamp
        self.color = color
        self.footer = footer
        self.image = image
        self.thumbnail = thumbnail
        self.video = video
        self.provider = provider
        self.author = author
        self.fields = fields or []
        self.reference_id = reference_id
        self.content_scan_version = content_scan_version
        self.flags = flags

    @override
    def _to_request(self) -> message_types.EmbedRequest:
        """Serialize this object into a Discord API request payload."""
        payload: message_types.EmbedRequest = {}
        if self.title is not None:
            payload["title"] = self.title
        if self.description is not None:
            payload["description"] = self.description
        if self.url is not None:
            payload["url"] = self.url
        if self.timestamp is not None:
            payload["timestamp"] = self.timestamp
        if self.color is not None:
            payload["color"] = self.color
        if self.footer is not None:
            payload["footer"] = self.footer._to_request()
        if self.image is not None:
            payload["image"] = self.image._to_request()
        if self.thumbnail is not None:
            payload["thumbnail"] = self.thumbnail._to_request()
        if self.author is not None:
            payload["author"] = self.author._to_request()
        if self.fields:
            payload["fields"] = [field._to_request() for field in self.fields]
        return payload

    @classmethod
    @override
    def _from_response(cls, data: message_types.EmbedResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            title=data.get("title"),
            type=data.get("type"),
            description=data.get("description"),
            url=data.get("url"),
            timestamp=data.get("timestamp"),
            color=data.get("color"),
            footer=(
                EmbedFooter._from_response(fdata)
                if (fdata := data.get("footer"))
                else None
            ),
            image=(
                EmbedMedia._from_response(idata)
                if (idata := data.get("image"))
                else None
            ),
            thumbnail=(
                EmbedMedia._from_response(tdata)
                if (tdata := data.get("thumbnail"))
                else None
            ),
            video=(
                EmbedMedia._from_response(vdata)
                if (vdata := data.get("video"))
                else None
            ),
            provider=data.get("provider"),  # type: ignore
            author=(
                EmbedAuthor._from_response(adata)
                if (adata := data.get("author"))
                else None
            ),
            fields=[
                EmbedField._from_response(field) for field in data.get("fields", [])
            ],
            reference_id=data.get("reference_id"),
            content_scan_version=data.get("content_scan_version"),
            flags=data.get("flags"),
        )
