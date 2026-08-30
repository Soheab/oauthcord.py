from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

from ...models._base import BaseModel
from ...utils import to_enum
from ..enums import ActivityType, StatusDisplayType

if TYPE_CHECKING:
    from ...internals._types import presence as presence_types
    from ...internals._types.rpc import activity as activity_types

__all__ = (
    "Activity",
    "ActivityAssets",
    "ActivityButton",
    "ActivityParty",
    "ActivitySecrets",
    "ActivityTimestamps",
    "ImageUpload",
    "ShareInteractionResult",
    "ShareLinkResult",
)


class ActivityTimestamps(
    BaseModel[
        "presence_types.ActivityTimestampsResponse",
        "presence_types.ActivityTimestampsRequest",
    ]
):
    __slots__ = ("end", "start")

    def __init__(self, *, start: int | None = None, end: int | None = None) -> None:
        self.start: int | None = start
        self.end: int | None = end
        super().__init__(data=self.to_dict())

    @override
    def to_dict(self) -> presence_types.ActivityTimestampsRequest:
        payload: presence_types.ActivityTimestampsRequest = {}
        if self.start is not None:
            payload["start"] = self.start
        if self.end is not None:
            payload["end"] = self.end
        return payload

    @classmethod
    @override
    def from_dict(cls, data: presence_types.ActivityTimestampsResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(start=data.get("start"), end=data.get("end"))


class ActivityParty(
    BaseModel[
        "presence_types.ActivityPartyResponse", "activity_types.ActivityPartyRequest"
    ]
):
    __slots__ = ("current_size", "id", "max_size")

    def __init__(
        self,
        *,
        id: str | None = None,
        current_size: int | None = None,
        max_size: int | None = None,
    ) -> None:
        self.id: str | None = id
        self.current_size: int | None = current_size
        self.max_size: int | None = max_size
        super().__init__(data=self.to_dict())

    @override
    def to_dict(self) -> activity_types.ActivityPartyRequest:
        payload: activity_types.ActivityPartyRequest = {}
        if self.id is not None:
            payload["id"] = self.id
        if self.current_size is not None and self.max_size is not None:
            payload["size"] = [self.current_size, self.max_size]
        return payload

    @classmethod
    @override
    def from_dict(cls, data: presence_types.ActivityPartyResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        size = data.get("size") or []
        return cls(
            id=data.get("id"),
            current_size=size[0] if len(size) > 0 else None,
            max_size=size[1] if len(size) > 1 else None,
        )


class ActivityAssets(
    BaseModel[
        "presence_types.ActivityAssetsResponse", "presence_types.ActivityAssetsRequest"
    ]
):
    __slots__ = (
        "invite_cover_image",
        "large_image",
        "large_text",
        "large_url",
        "small_image",
        "small_text",
        "small_url",
    )

    def __init__(
        self,
        *,
        large_image: str | None = None,
        large_text: str | None = None,
        large_url: str | None = None,
        small_image: str | None = None,
        small_text: str | None = None,
        small_url: str | None = None,
        invite_cover_image: str | None = None,
    ) -> None:
        self.large_image: str | None = large_image
        self.large_text: str | None = large_text
        self.large_url: str | None = large_url
        self.small_image: str | None = small_image
        self.small_text: str | None = small_text
        self.small_url: str | None = small_url
        self.invite_cover_image: str | None = invite_cover_image
        super().__init__(data=self.to_dict())

    @override
    def to_dict(self) -> presence_types.ActivityAssetsRequest:
        payload: presence_types.ActivityAssetsRequest = {}
        if self.large_image is not None:
            payload["large_image"] = self.large_image
        if self.large_text is not None:
            payload["large_text"] = self.large_text
        if self.large_url is not None:
            payload["large_url"] = self.large_url
        if self.small_image is not None:
            payload["small_image"] = self.small_image
        if self.small_text is not None:
            payload["small_text"] = self.small_text
        if self.small_url is not None:
            payload["small_url"] = self.small_url
        if self.invite_cover_image is not None:
            payload["invite_cover_image"] = self.invite_cover_image
        return payload

    @classmethod
    @override
    def from_dict(cls, data: presence_types.ActivityAssetsResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            large_image=data.get("large_image"),
            large_text=data.get("large_text"),
            large_url=data.get("large_url"),
            small_image=data.get("small_image"),
            small_text=data.get("small_text"),
            small_url=data.get("small_url"),
            invite_cover_image=data.get("invite_cover_image"),
        )


class ActivitySecrets(
    BaseModel[
        "presence_types.ActivitySecretsResponse",
        "presence_types.ActivitySecretsRequest",
    ]
):
    __slots__ = ("join", "match", "spectate")

    def __init__(
        self,
        *,
        join: str | None = None,
        spectate: str | None = None,
        match: str | None = None,
    ) -> None:
        self.join: str | None = join
        self.spectate: str | None = spectate
        self.match: str | None = match
        super().__init__(data=self.to_dict())

    @override
    def to_dict(self) -> presence_types.ActivitySecretsRequest:
        payload: presence_types.ActivitySecretsRequest = {}
        if self.join is not None:
            payload["join"] = self.join
        if self.spectate is not None:
            payload["spectate"] = self.spectate
        if self.match is not None:
            payload["match"] = self.match
        return payload

    @classmethod
    @override
    def from_dict(cls, data: presence_types.ActivitySecretsResponse) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(
            join=data.get("join"),
            spectate=data.get("spectate"),
            match=data.get("match"),
        )


class ActivityButton(
    BaseModel[
        "presence_types.ActivityButtonRequest", "presence_types.ActivityButtonRequest"
    ]
):
    __slots__ = ("label", "url")

    def __init__(self, label: str, url: str | None = None) -> None:
        self.label: str = label
        self.url: str | None = url
        super().__init__(data=self.to_dict())

    @override
    def to_dict(self) -> presence_types.ActivityButtonRequest:
        return {"label": self.label, "url": self.url or ""}

    @classmethod
    def from_label(cls, label: str) -> Self:
        return cls(label)

    @classmethod
    @override
    def from_dict(cls, data: presence_types.ActivityButtonRequest) -> Self:
        """Construct this object from a Discord API response payload."""
        return cls(label=data["label"], url=data["url"])


class Activity(
    BaseModel["presence_types.ActivityResponse", "activity_types.ActivityRequest"]
):
    """A rich presence activity, as sent to or received from RPC's ``SET_ACTIVITY``.

    This models the restricted RPC-specific activity shape, not Discord's general
    activity object. :attr:`type` cannot be
    :attr:`~oauthcord.enums.ActivityType.STREAMING`, :attr:`~oauthcord.enums.ActivityType.CUSTOM`,
    or :attr:`~oauthcord.enums.ActivityType.HANGING`.
    """

    __slots__ = (
        "assets",
        "buttons",
        "details",
        "details_url",
        "instance",
        "name",
        "party",
        "secrets",
        "state",
        "state_url",
        "status_display_type",
        "supported_platforms",
        "timestamps",
        "type",
    )

    def __init__(
        self,
        name: str,
        *,
        type: ActivityType | activity_types.RPCActivityType,
        state: str | None = None,
        state_url: str | None = None,
        details: str | None = None,
        details_url: str | None = None,
        timestamps: ActivityTimestamps
        | presence_types.ActivityTimestampsRequest
        | None = None,
        assets: ActivityAssets | presence_types.ActivityAssetsRequest | None = None,
        party: ActivityParty | activity_types.ActivityPartyRequest | None = None,
        secrets: ActivitySecrets | presence_types.ActivitySecretsRequest | None = None,
        buttons: list[ActivityButton | presence_types.ActivityButtonRequest]
        | None = None,
        instance: bool | None = None,
        supported_platforms: list[str] | None = None,
        status_display_type: StatusDisplayType | int | None = None,
    ) -> None:
        self.name: str = name
        self.type: ActivityType | None = to_enum(ActivityType, type)
        self.state: str | None = state
        self.state_url: str | None = state_url
        self.details: str | None = details
        self.details_url: str | None = details_url
        self.timestamps: ActivityTimestamps | None = (
            ActivityTimestamps.from_dict(timestamps)
            if isinstance(timestamps, dict)
            else timestamps
        )
        self.assets: ActivityAssets | None = (
            ActivityAssets.from_dict(assets) if isinstance(assets, dict) else assets
        )
        self.party: ActivityParty | None = (
            ActivityParty.from_dict(party) if isinstance(party, dict) else party
        )
        self.secrets: ActivitySecrets | None = (
            ActivitySecrets.from_dict(secrets) if isinstance(secrets, dict) else secrets
        )
        self.buttons: list[ActivityButton] = []

        if (
            buttons
            and not isinstance(buttons, list)
            and not all(
                isinstance(button, (ActivityButton, dict)) for button in buttons
            )
        ):
            raise TypeError(
                f"`buttons`: Expected list of ActivityButton or dict, got {buttons!r} instead."
            )

        for button in buttons or []:
            if isinstance(button, dict):
                self.buttons.append(ActivityButton.from_dict(button))
            else:
                self.buttons.append(button)

        self.instance: bool | None = instance
        self.supported_platforms: list[str] = supported_platforms or []
        self.status_display_type: StatusDisplayType | None = to_enum(
            StatusDisplayType, status_display_type
        )
        # A directly-constructed Activity has only the request shape to store; the
        # received-only fields (``id``, ``created_at``) are absent by definition.
        super().__init__(data=self.to_dict())  # pyright: ignore[reportArgumentType]

    @override
    def to_dict(self) -> activity_types.ActivityRequest:
        """Serialize this object into an RPC ``SET_ACTIVITY`` request payload."""
        payload: activity_types.ActivityRequest = {"name": self.name}
        if self.type is not None:
            payload["type"] = int(self.type)  # type: ignore
        if self.state is not None:
            payload["state"] = self.state
        if self.state_url is not None:
            payload["state_url"] = self.state_url
        if self.details is not None:
            payload["details"] = self.details
        if self.details_url is not None:
            payload["details_url"] = self.details_url
        if self.timestamps is not None:
            payload["timestamps"] = self.timestamps.to_dict()
        if self.assets is not None:
            payload["assets"] = self.assets.to_dict()
        if self.party is not None:
            payload["party"] = self.party.to_dict()
        if self.secrets is not None:
            payload["secrets"] = self.secrets.to_dict()
        if self.buttons:
            payload["buttons"] = [button.to_dict() for button in self.buttons]
        if self.instance is not None:
            payload["instance"] = self.instance
        if self.supported_platforms:
            payload["supported_platforms"] = self.supported_platforms
        if self.status_display_type is not None:
            payload["status_display_type"] = int(self.status_display_type)
        return payload

    @classmethod
    @override
    def from_dict(cls, data: presence_types.ActivityResponse) -> Self:
        """Construct this object from a received activity object.

        Accepts Discord's general activity shape, which is what RPC events carry and
        what ``SET_ACTIVITY`` echoes back. Received ``buttons`` are labels, not
        objects (see :class:`ActivityButton`).
        """
        return cls(
            data["name"],
            type=data.get("type"),  # type: ignore
            state=data.get("state"),
            state_url=data.get("state_url"),
            details=data.get("details"),
            details_url=data.get("details_url"),
            timestamps=(
                ActivityTimestamps.from_dict(ts)
                if (ts := data.get("timestamps"))
                else None
            ),
            assets=(
                ActivityAssets.from_dict(assets_data)
                if (assets_data := data.get("assets"))
                else None
            ),
            party=(
                ActivityParty.from_dict(party_data)
                if (party_data := data.get("party"))
                else None
            ),
            secrets=(
                ActivitySecrets.from_dict(secrets_data)
                if (secrets_data := data.get("secrets"))
                else None
            ),
            buttons=[
                ActivityButton.from_label(button)
                for button in data.get("buttons") or []
            ],
            instance=data.get("instance"),
            supported_platforms=list(data.get("supported_platforms") or []),
            status_display_type=data.get("status_display_type"),
        )


class ShareInteractionResult(BaseModel["activity_types.ShareInteractionResponse"]):
    __slots__ = ("success",)

    @override
    def _initialize(self, data: activity_types.ShareInteractionResponse) -> None:
        self.success: bool = data["success"]


class ImageUpload(BaseModel["activity_types.InitiateImageUploadResponse"]):
    __slots__ = ("image_url",)

    @override
    def _initialize(self, data: activity_types.InitiateImageUploadResponse) -> None:
        self.image_url: str = data["image_url"]


class ShareLinkResult(BaseModel["activity_types.ShareLinkResponse"]):
    __slots__ = ("did_copy_link", "did_send_message", "success")

    @override
    def _initialize(self, data: activity_types.ShareLinkResponse) -> None:
        self.success: bool = data["success"]
        self.did_copy_link: bool = data["didCopyLink"]
        self.did_send_message: bool = data["didSendMessage"]
