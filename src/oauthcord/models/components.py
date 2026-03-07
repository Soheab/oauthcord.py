from collections.abc import Iterable
from typing import TYPE_CHECKING, Self

from .emoji import Emoji

if TYPE_CHECKING:
    from .internals._types import components as component_types


__all__ = (
    "ActionRow",
    "BaseComponent",
    "Button",
    "ChannelSelect",
    "CheckpointCard",
    "Container",
    "ContentInventoryEntryComponent",
    "FileComponent",
    "MediaGallery",
    "MediaGalleryItem",
    "MentionableSelect",
    "RoleSelect",
    "Section",
    "SelectDefaultValue",
    "SelectOption",
    "Separator",
    "StringSelect",
    "TextDisplay",
    "Thumbnail",
    "UnfurledMediaItem",
    "UserSelect",
)


def _emoji_from_partial(
    data: component_types.PartialEmojiResponse | None,
) -> Emoji | None:
    if data is None:
        return None
    emoji_id = data.get("id")
    return Emoji(
        name=data.get("name") or "",
        id=int(emoji_id) if emoji_id is not None else None,
        animated=data.get("animated", False),
    )


class UnfurledMediaItem:
    """Builder and serializer for Discord component payload data."""

    __slots__ = (
        "attachment_id",
        "content_scan_metadata",
        "content_type",
        "flags",
        "height",
        "id",
        "loading_state",
        "placeholder",
        "placeholder_version",
        "proxy_url",
        "url",
        "width",
    )

    def __init__(
        self,
        url: str,
        *,
        id: int | str | None = None,
        proxy_url: str | None = None,
        height: int | None = None,
        width: int | None = None,
        flags: int | None = None,
        content_type: str | None = None,
        content_scan_metadata: dict[str, object] | None = None,
        placeholder_version: int | None = None,
        placeholder: str | None = None,
        loading_state: int | None = None,
        attachment_id: int | str | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.url = url
        self.id = id
        self.proxy_url = proxy_url
        self.height = height
        self.width = width
        self.flags = flags
        self.content_type = content_type
        self.content_scan_metadata = content_scan_metadata
        self.placeholder_version = placeholder_version
        self.placeholder = placeholder
        self.loading_state = loading_state
        self.attachment_id = attachment_id

    def _to_request(self) -> component_types.UnfurledMediaItemRequest:
        """Serialize this object into a Discord API request payload."""
        return {"url": self.url}

    @classmethod
    def _from_response(cls, data: component_types.UnfurledMediaItemResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            url=data["url"],
            id=data.get("id"),
            proxy_url=data.get("proxy_url"),
            height=data.get("height"),
            width=data.get("width"),
            flags=data.get("flags"),
            content_type=data.get("content_type"),
            content_scan_metadata=data.get("content_scan_metadata"),
            placeholder_version=data.get("placeholder_version"),
            placeholder=data.get("placeholder"),
            loading_state=data.get("loading_state"),
            attachment_id=data.get("attachment_id"),
        )


class SelectOption:
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        label: str,
        value: str,
        description: str | None = None,
        emoji: Emoji | None = None,
        default: bool | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

    def _to_request(self) -> component_types.SelectOptionRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.SelectOptionRequest = {
            "label": self.label,
            "value": self.value,
        }
        if self.description is not None:
            payload["description"] = self.description
        if self.emoji is not None:
            payload["emoji"] = self.emoji._to_request()  # type: ignore[assignment]
        if self.default is not None:
            payload["default"] = self.default
        return payload

    @classmethod
    def _from_response(cls, data: component_types.SelectOptionResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description"),
            emoji=_emoji_from_partial(data.get("emoji")),
            default=data.get("default"),
        )


class SelectDefaultValue:
    """Builder and serializer for Discord component payload data."""

    def __init__(self, *, id: int | str, type: str) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.id = id
        self.type = type

    def _to_request(self) -> component_types.SelectDefaultValueRequest:
        """Serialize this object into a Discord API request payload."""
        return {"id": self.id, "type": self.type}

    @classmethod
    def _from_response(cls, data: component_types.SelectDefaultValueResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(id=data["id"], type=data["type"])


class BaseComponent:
    """Builder and serializer for Discord component payload data."""

    def __init__(self, *, type: int, id: int | None = None) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.type = type
        self.id = id

    def _to_request(self) -> component_types.ComponentRequest:
        """Serialize this object into a Discord API request payload."""
        return {
            "type": self.type,
            **({"id": self.id} if self.id is not None else {}),
        }  # pyright: ignore[reportReturnType]


class ActionRow(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        components: Iterable[BaseComponent],
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=1, id=id)
        self.components = list(components)

    def _to_request(self) -> component_types.ActionRowRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.ActionRowRequest = {
            "type": 1,
            "components": [component._to_request() for component in self.components],
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload

    @classmethod
    def _from_response(cls, data: component_types.ActionRowResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            components=[
                component_from_response(component) for component in data["components"]
            ],
        )


class Button(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        style: int,
        label: str | None = None,
        emoji: Emoji | None = None,
        custom_id: str | None = None,
        sku_id: int | str | None = None,
        url: str | None = None,
        disabled: bool | None = None,
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=2, id=id)
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.sku_id = sku_id
        self.url = url
        self.disabled = disabled

    def _to_request(self) -> component_types.ButtonRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.ButtonRequest = {"type": 2, "style": self.style}
        if self.id is not None:
            payload["id"] = self.id
        if self.label is not None:
            payload["label"] = self.label
        if self.emoji is not None:
            payload["emoji"] = self.emoji._to_request()  # type: ignore[assignment]
        if self.custom_id is not None:
            payload["custom_id"] = self.custom_id
        if self.sku_id is not None:
            payload["sku_id"] = self.sku_id
        if self.url is not None:
            payload["url"] = self.url
        if self.disabled is not None:
            payload["disabled"] = self.disabled
        return payload

    @classmethod
    def _from_response(cls, data: component_types.ButtonResponse) -> Button:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            style=data["style"],
            label=data.get("label"),
            emoji=_emoji_from_partial(data.get("emoji")),
            custom_id=data.get("custom_id"),
            sku_id=data.get("sku_id"),
            url=data.get("url"),
            disabled=data.get("disabled"),
        )


class StringSelect(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        custom_id: str,
        options: Iterable[SelectOption],
        placeholder: str | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool | None = None,
        disabled: bool | None = None,
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=3, id=id)
        self.custom_id = custom_id
        self.options = list(options)
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.required = required
        self.disabled = disabled

    def _to_request(self) -> component_types.StringSelectRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.StringSelectRequest = {
            "type": 3,
            "custom_id": self.custom_id,
            "options": [opt._to_request() for opt in self.options],
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder
        if self.min_values is not None:
            payload["min_values"] = self.min_values
        if self.max_values is not None:
            payload["max_values"] = self.max_values
        if self.required is not None:
            payload["required"] = self.required
        if self.disabled is not None:
            payload["disabled"] = self.disabled
        return payload

    @classmethod
    def _from_response(cls, data: component_types.StringSelectResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            custom_id=data["custom_id"],
            options=[SelectOption._from_response(opt) for opt in data["options"]],
            placeholder=data.get("placeholder"),
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
            required=data.get("required"),
            disabled=data.get("disabled"),
        )


class _AutoPopulatedSelect(BaseComponent):
    component_type: int = 0

    def __init__(
        self,
        *,
        custom_id: str,
        placeholder: str | None = None,
        default_values: Iterable[SelectDefaultValue] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool | None = None,
        disabled: bool | None = None,
        id: int | None = None,
    ) -> None:
        super().__init__(type=self.component_type, id=id)
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.default_values = list(default_values or [])
        self.min_values = min_values
        self.max_values = max_values
        self.required = required
        self.disabled = disabled

    def _base_select_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "type": self.component_type,
            "custom_id": self.custom_id,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder
        if self.default_values:
            payload["default_values"] = [v._to_request() for v in self.default_values]
        if self.min_values is not None:
            payload["min_values"] = self.min_values
        if self.max_values is not None:
            payload["max_values"] = self.max_values
        if self.required is not None:
            payload["required"] = self.required
        if self.disabled is not None:
            payload["disabled"] = self.disabled
        return payload


class UserSelect(_AutoPopulatedSelect):
    """Builder and serializer for Discord component payload data."""

    component_type = 5

    def _to_request(self) -> component_types.UserSelectRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.UserSelectRequest = {  # pyright: ignore[reportAssignmentType]
            "type": 5,
            "custom_id": self.custom_id,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder
        if self.default_values:
            payload["default_values"] = [v._to_request() for v in self.default_values]
        if self.min_values is not None:
            payload["min_values"] = self.min_values
        if self.max_values is not None:
            payload["max_values"] = self.max_values
        if self.required is not None:
            payload["required"] = self.required
        if self.disabled is not None:
            payload["disabled"] = self.disabled
        return payload

    @classmethod
    def _from_response(cls, data: component_types.UserSelectResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            custom_id=data["custom_id"],
            placeholder=data.get("placeholder"),
            default_values=[
                SelectDefaultValue._from_response(value)
                for value in data.get("default_values", [])
            ],
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
            required=data.get("required"),
            disabled=data.get("disabled"),
        )


class RoleSelect(_AutoPopulatedSelect):
    """Builder and serializer for Discord component payload data."""

    component_type = 6

    def _to_request(self) -> component_types.RoleSelectRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.RoleSelectRequest = {  # pyright: ignore[reportAssignmentType]
            "type": 6,
            "custom_id": self.custom_id,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder
        if self.default_values:
            payload["default_values"] = [v._to_request() for v in self.default_values]
        if self.min_values is not None:
            payload["min_values"] = self.min_values
        if self.max_values is not None:
            payload["max_values"] = self.max_values
        if self.required is not None:
            payload["required"] = self.required
        if self.disabled is not None:
            payload["disabled"] = self.disabled
        return payload

    @classmethod
    def _from_response(cls, data: component_types.RoleSelectResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            custom_id=data["custom_id"],
            placeholder=data.get("placeholder"),
            default_values=[
                SelectDefaultValue._from_response(value)
                for value in data.get("default_values", [])
            ],
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
            required=data.get("required"),
            disabled=data.get("disabled"),
        )


class MentionableSelect(_AutoPopulatedSelect):
    """Builder and serializer for Discord component payload data."""

    component_type = 7

    def _to_request(self) -> component_types.MentionableSelectRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.MentionableSelectRequest = {  # pyright: ignore[reportAssignmentType]
            "type": 7,
            "custom_id": self.custom_id,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder
        if self.default_values:
            payload["default_values"] = [v._to_request() for v in self.default_values]
        if self.min_values is not None:
            payload["min_values"] = self.min_values
        if self.max_values is not None:
            payload["max_values"] = self.max_values
        if self.required is not None:
            payload["required"] = self.required
        if self.disabled is not None:
            payload["disabled"] = self.disabled
        return payload

    @classmethod
    def _from_response(cls, data: component_types.MentionableSelectResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            custom_id=data["custom_id"],
            placeholder=data.get("placeholder"),
            default_values=[
                SelectDefaultValue._from_response(value)
                for value in data.get("default_values", [])
            ],
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
            required=data.get("required"),
            disabled=data.get("disabled"),
        )


class ChannelSelect(_AutoPopulatedSelect):
    """Builder and serializer for Discord component payload data."""

    component_type = 8

    def __init__(
        self,
        *,
        custom_id: str,
        channel_types: Iterable[int] | None = None,
        placeholder: str | None = None,
        default_values: Iterable[SelectDefaultValue] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool | None = None,
        disabled: bool | None = None,
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(
            id=id,
            custom_id=custom_id,
            placeholder=placeholder,
            default_values=default_values,
            min_values=min_values,
            max_values=max_values,
            required=required,
            disabled=disabled,
        )
        self.channel_types = list(channel_types or [])

    def _to_request(self) -> component_types.ChannelSelectRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.ChannelSelectRequest = {  # pyright: ignore[reportAssignmentType]
            "type": 8,
            "custom_id": self.custom_id,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder
        if self.default_values:
            payload["default_values"] = [v._to_request() for v in self.default_values]
        if self.min_values is not None:
            payload["min_values"] = self.min_values
        if self.max_values is not None:
            payload["max_values"] = self.max_values
        if self.required is not None:
            payload["required"] = self.required
        if self.disabled is not None:
            payload["disabled"] = self.disabled
        if self.channel_types:
            payload["channel_types"] = self.channel_types
        return payload

    @classmethod
    def _from_response(cls, data: component_types.ChannelSelectResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            custom_id=data["custom_id"],
            channel_types=data.get("channel_types", []),
            placeholder=data.get("placeholder"),
            default_values=[
                SelectDefaultValue._from_response(value)
                for value in data.get("default_values", [])
            ],
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
            required=data.get("required"),
            disabled=data.get("disabled"),
        )


class TextDisplay(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(self, *, content: str, id: int | None = None) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=10, id=id)
        self.content = content

    def _to_request(self) -> component_types.TextDisplayRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.TextDisplayRequest = {
            "type": 10,
            "content": self.content,
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload

    @classmethod
    def _from_response(cls, data: component_types.TextDisplayResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(id=data.get("id"), content=data["content"])


class Thumbnail(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        media: UnfurledMediaItem,
        description: str | None = None,
        spoiler: bool | None = None,
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=11, id=id)
        self.media = media
        self.description = description
        self.spoiler = spoiler

    def _to_request(self) -> component_types.ThumbnailRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.ThumbnailRequest = {
            "type": 11,
            "media": self.media._to_request(),
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.description is not None:
            payload["description"] = self.description
        if self.spoiler is not None:
            payload["spoiler"] = self.spoiler
        return payload

    @classmethod
    def _from_response(cls, data: component_types.ThumbnailResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            media=UnfurledMediaItem._from_response(data["media"]),
            description=data.get("description"),
            spoiler=data.get("spoiler"),
        )


class MediaGalleryItem:
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        media: UnfurledMediaItem,
        description: str | None = None,
        spoiler: bool | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self.media = media
        self.description = description
        self.spoiler = spoiler

    def _to_request(self) -> component_types.MediaGalleryItemRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.MediaGalleryItemRequest = {
            "media": self.media._to_request()
        }
        if self.description is not None:
            payload["description"] = self.description
        if self.spoiler is not None:
            payload["spoiler"] = self.spoiler
        return payload

    @classmethod
    def _from_response(cls, data: component_types.MediaGalleryItemResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            media=UnfurledMediaItem._from_response(data["media"]),
            description=data.get("description"),
            spoiler=data.get("spoiler"),
        )


class MediaGallery(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self, *, items: Iterable[MediaGalleryItem], id: int | None = None
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=12, id=id)
        self.items = list(items)

    def _to_request(self) -> component_types.MediaGalleryRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.MediaGalleryRequest = {
            "type": 12,
            "items": [item._to_request() for item in self.items],
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload

    @classmethod
    def _from_response(cls, data: component_types.MediaGalleryResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            items=[MediaGalleryItem._from_response(item) for item in data["items"]],
        )


class FileComponent(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        file: UnfurledMediaItem,
        spoiler: bool | None = None,
        name: str | None = None,
        size: int | None = None,
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=13, id=id)
        self.file = file
        self.spoiler = spoiler
        self.name = name
        self.size = size

    def _to_request(self) -> component_types.FileComponentRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.FileComponentRequest = {
            "type": 13,
            "file": self.file._to_request(),
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.spoiler is not None:
            payload["spoiler"] = self.spoiler
        return payload

    @classmethod
    def _from_response(cls, data: component_types.FileComponentResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            file=UnfurledMediaItem._from_response(data["file"]),
            spoiler=data.get("spoiler"),
            name=data.get("name"),
            size=data.get("size"),
        )


class Separator(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        divider: bool | None = None,
        spacing: int | None = None,
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=14, id=id)
        self.divider = divider
        self.spacing = spacing

    def _to_request(self) -> component_types.SeparatorRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.SeparatorRequest = {"type": 14}
        if self.id is not None:
            payload["id"] = self.id
        if self.divider is not None:
            payload["divider"] = self.divider
        if self.spacing is not None:
            payload["spacing"] = self.spacing
        return payload

    @classmethod
    def _from_response(cls, data: component_types.SeparatorResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            divider=data.get("divider"),
            spacing=data.get("spacing"),
        )


class Section(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        components: Iterable[TextDisplay],
        accessory: Thumbnail | Button,
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=9, id=id)
        self.components = list(components)
        self.accessory = accessory

    def _to_request(self) -> component_types.SectionRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.SectionRequest = {
            "type": 9,
            "components": [component._to_request() for component in self.components],
            "accessory": self.accessory._to_request(),  # pyright: ignore[reportAssignmentType]
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload

    @classmethod
    def _from_response(cls, data: component_types.SectionResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        accessory_data = data["accessory"]
        accessory_type = accessory_data["type"]
        accessory: Thumbnail | Button
        if accessory_type == 11:
            accessory = Thumbnail._from_response(
                accessory_data  # pyright: ignore[reportArgumentType]
            )
        elif accessory_type == 2:
            accessory = Button._from_response(accessory_data)  # pyright: ignore[reportArgumentType]
        else:
            raise ValueError(
                f"Unsupported section accessory component type: {accessory_type}"
            )

        return cls(
            id=data.get("id"),
            components=[
                TextDisplay._from_response(component)
                for component in data["components"]
            ],
            accessory=accessory,
        )


class Container(BaseComponent):
    """Builder and serializer for Discord component payload data."""

    def __init__(
        self,
        *,
        components: Iterable[BaseComponent],
        accent_color: int | None = None,
        spoiler: bool | None = None,
        id: int | None = None,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        super().__init__(type=17, id=id)
        self.components = list(components)
        self.accent_color = accent_color
        self.spoiler = spoiler

    def _to_request(self) -> component_types.ContainerRequest:
        """Serialize this object into a Discord API request payload."""
        payload: component_types.ContainerRequest = {
            "type": 17,
            "components": [component._to_request() for component in self.components],
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.accent_color is not None:
            payload["accent_color"] = self.accent_color
        if self.spoiler is not None:
            payload["spoiler"] = self.spoiler
        return payload

    @classmethod
    def _from_response(cls, data: component_types.ContainerResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            id=data.get("id"),
            components=[
                component_from_response(component) for component in data["components"]
            ],
            accent_color=data.get("accent_color"),
            spoiler=data.get("spoiler"),
        )


class ContentInventoryEntryComponent(BaseComponent):
    def __init__(
        self,
        *,
        content_inventory_entry: component_types.ContentInventoryEntryDataResponse,
        id: int | None = None,
    ) -> None:
        super().__init__(type=16, id=id)
        self.content_inventory_entry = content_inventory_entry

    @classmethod
    def _from_response(
        cls, data: component_types.ContentInventoryEntryComponentResponse
    ) -> Self:
        return cls(
            id=data.get("id"),
            content_inventory_entry=data["content_inventory_entry"],
        )


class CheckpointCard(BaseComponent):
    def __init__(
        self,
        *,
        checkpoint_data: component_types.CheckpointDataResponse,
        id: int | None = None,
    ) -> None:
        super().__init__(type=20, id=id)
        self.checkpoint_data = checkpoint_data

    @classmethod
    def _from_response(cls, data: component_types.CheckpointCardResponse) -> Self:
        return cls(id=data.get("id"), checkpoint_data=data["checkpoint_data"])


def component_from_response(data: component_types.ComponentResponse) -> BaseComponent:
    component_type = data["type"]
    if component_type == 1:
        return ActionRow._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 2:
        return Button._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 3:
        return StringSelect._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 5:
        return UserSelect._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 6:
        return RoleSelect._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 7:
        return MentionableSelect._from_response(
            data  # pyright: ignore[reportArgumentType]
        )
    if component_type == 8:
        return ChannelSelect._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 9:
        return Section._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 10:
        return TextDisplay._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 11:
        return Thumbnail._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 12:
        return MediaGallery._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 13:
        return FileComponent._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 14:
        return Separator._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 16:
        return ContentInventoryEntryComponent._from_response(
            data  # pyright: ignore[reportArgumentType]
        )
    if component_type == 17:
        return Container._from_response(data)  # pyright: ignore[reportArgumentType]
    if component_type == 20:
        return CheckpointCard._from_response(data)  # pyright: ignore[reportArgumentType]
    return BaseComponent(type=component_type, id=data.get("id"))
