from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake
from ._base import BaseModel
from .asset import Asset
from .enums import IntegrationType, Service, Visibility
from .user import to_enum

if TYPE_CHECKING:
    from .internals._types.connections import (
        ConnectionResponse as ConnectionPayload,
    )
    from .internals._types.connections import (
        IntegrationAccountResponse as IntegrationAccountResponsePayload,
    )
    from .internals._types.connections import (
        IntegrationGuildResponse as IntegrationGuildResponsePayload,
    )
    from .internals._types.connections import (
        IntegrationResponse as IntegrationResponsePayload,
    )


__all__ = (
    "Connection",
    "Integration",
    "IntegrationAccount",
    "IntegrationGuild",
)


class Connection(BaseModel["ConnectionPayload"]):
    """Represents a Discord user connection."""

    __slots__ = (
        "friend_sync",
        "id",
        "integrations",
        "metadata_visibility",
        "name",
        "revoked",
        "show_activity",
        "two_way_link",
        "type",
        "verified",
        "visibility",
    )

    @override
    def _initialize(self, data: ConnectionPayload) -> None:
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.type: Service = to_enum(Service, data["type"])
        self.revoked: bool = data.get("revoked", False)

        self.integrations: list[Integration] = [
            self._initialize_subclass_with_http(Integration, integration_data)
            for integration_data in data.get("integrations", [])
        ]
        self.verified: bool = data["verified"]
        self.friend_sync: bool = data["friend_sync"]
        self.metadata_visibility: int = data["metadata_visibility"]
        self.show_activity: bool = data["show_activity"]
        self.two_way_link: bool = data["two_way_link"]
        self.visibility: Visibility = to_enum(Visibility, data["visibility"])


class Integration(BaseModel["IntegrationResponsePayload"]):
    __slots__ = ("account", "guild", "id", "type")

    @override
    def _initialize(self, data: IntegrationResponsePayload) -> None:
        self.id: str = str(data["id"])
        self.type: IntegrationType = to_enum(IntegrationType, data["type"])
        self.account: IntegrationAccount = self._initialize_subclass_with_http(
            IntegrationAccount, data, "account"
        )
        self.guild: IntegrationGuild = self._initialize_subclass_with_http(
            IntegrationGuild, data, "guild"
        )


class IntegrationAccount(BaseModel["IntegrationAccountResponsePayload"]):
    __slots__ = ("id", "name")

    @override
    def _initialize(self, data: IntegrationAccountResponsePayload) -> None:
        self.id: str = str(data["id"])
        self.name: str = data["name"]


class IntegrationGuild(BaseModel["IntegrationGuildResponsePayload"]):
    __slots__ = ("icon", "id", "name")

    @override
    def _initialize(self, data: IntegrationGuildResponsePayload) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.icon: Asset | None = (
            self.get_asset(Asset._from_guild_icon, self.id, data["icon"])
            if data["icon"]
            else None
        )
