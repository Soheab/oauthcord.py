import datetime
from typing import TYPE_CHECKING, Any, override

from ..utils import convert_snowflake
from ._base import BaseModel
from .enums import Scope
from .user import PartialUser

if TYPE_CHECKING:
    from .internals._types.current_auth_info import (
        CurrentAuthApplicationResponse as CurrentAuthorizationInformationApplicationResponsePayload,
    )
    from .internals._types.current_auth_info import (
        CurrentAuthResponse as CurrentAuthorizationInformationResponsePayload,
    )


__all__ = (
    "CurrentApplication",
    "CurrentInformation",
)


class CurrentApplication(
    BaseModel["CurrentAuthorizationInformationApplicationResponsePayload"]
):
    """Represents Discord API data for `CurrentApplication`."""

    __slots__ = (
        "bot_public",
        "bot_require_code_grant",
        "description",
        "hook",
        "icon",
        "id",
        "name",
        "verify_key",
    )

    @override
    def _initialize(
        self, data: CurrentAuthorizationInformationApplicationResponsePayload
    ) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.icon: str | None = data.get("icon")
        self.description: str = data["description"]
        self.hook: bool = data["hook"]
        self.bot_public: bool = data["bot_public"]
        self.bot_require_code_grant: bool = data["bot_require_code_grant"]
        self.verify_key: str = data["verify_key"]

    async def get_global_application_commands(self):
        pass

    async def get_global_application_command(self, command_id: int):
        pass

    async def edit_global_application_command(self, command_id: int, data: Any) -> None:
        pass

    async def delete_global_application_command(self, command_id: int):
        pass

    async def bulk_overwrite_global_application_commands(self, data: Any) -> None:
        pass

    async def get_guild_application_commands(self, guild_id: int):
        pass

    async def create_global_application_command(self, data: Any) -> None:
        pass

    async def get_guild_application_command(self, guild_id: int, command_id: int):
        pass

    async def edit_guild_application_command(
        self, guild_id: int, command_id: int, data: Any
    ) -> None:
        pass

    async def delete_guild_application_command(self, guild_id: int, command_id: int):
        pass

    async def bulk_overwrite_guild_application_commands(
        self, guild_id: int, data: Any
    ) -> None:
        pass

    async def get_guild_application_command_permissions(self, guild_id: int):
        pass

    async def get_application_command_permissions(self, guild_id: int, command_id: int):
        pass

    async def edit_application_command_permissions(
        self, guild_id: int, command_id: int, data: Any
    ) -> None:
        pass


class CurrentInformation(BaseModel["CurrentAuthorizationInformationResponsePayload"]):
    """Represents Discord API data for `CurrentInformation`."""

    __slots__ = ("_expires", "application", "scopes", "user")

    def _initialize(self, data: CurrentAuthorizationInformationResponsePayload) -> None:
        self._expires: datetime.datetime = datetime.datetime.fromisoformat(
            data["expires"]
        )

        self.scopes: list[Scope] = Scope.from_list(data["scopes"])
        self.application = self._initialize_subclass_with_http(
            CurrentApplication, data, "application"
        )
        self.user: PartialUser | None = self._maybe_subclass_with_http(
            PartialUser, data, "user"
        )

    @property
    def expires_at(self) -> datetime.datetime:
        """Return the calculated expiration timestamp."""
        return self._expires
