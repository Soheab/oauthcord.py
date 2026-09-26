from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, override

from ..enums import Scope
from ..utils import NotSet, convert_snowflake
from ._base import BaseModel
from .application import PartialApplication
from .commands import Command, GuildApplicationCommandPermissions
from .user import PartialUser

if TYPE_CHECKING:
    from ..enums import (
        ApplicationCommandHandlerType,
        IntegrationInstallType,
        InteractionContextType,
        Locale,
        UnknownEnum,
    )
    from ..internals._types.current_auth_info import (
        CurrentAuthApplicationResponse as CurrentAuthorizationInformationApplicationResponsePayload,
    )
    from ..internals._types.current_auth_info import (
        CurrentAuthResponse as CurrentAuthorizationInformationResponsePayload,
    )
    from .builders.commands import (
        ApplicationCommandBuilder,
        ApplicationCommandPermissionBuilder,
        ChatInputGroupCommandBuilder,
        ChatInputSubCommandBuilder,
        OptionBuilder,
    )
    from .flags import Permissions


__all__ = (
    "CurrentApplication",
    "CurrentInformation",
)


class CurrentApplication(
    BaseModel["CurrentAuthorizationInformationApplicationResponsePayload"]
):
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

    async def get_global_application_commands(
        self, *, with_localizations: bool | None = None
    ) -> list[Command]:
        """Fetch the global commands for this application.

        See :meth:`AuthorisedSession.get_global_application_commands`.
        """
        return await self._session.get_global_application_commands(
            with_localizations=with_localizations
        )

    async def get_global_application_command(
        self, command: Command | int | str
    ) -> Command:
        """Fetch a global command for this application.

        See :meth:`AuthorisedSession.get_global_application_command`.
        """
        return await self._session.get_global_application_command(command=command)

    async def create_global_application_command(
        self, command: ApplicationCommandBuilder
    ) -> Command:
        """Create a global command for this application.

        See :meth:`AuthorisedSession.create_global_application_command`.
        """
        return await self._session.create_global_application_command(command=command)

    async def edit_global_application_command(
        self,
        command: Command | int | str,
        *,
        name: str = NotSet,
        name_localizations: dict[Locale | str, str] | None = NotSet,
        description: str = NotSet,
        description_localizations: dict[Locale | str, str] | None = NotSet,
        options: list[
            OptionBuilder | ChatInputSubCommandBuilder | ChatInputGroupCommandBuilder
        ] = NotSet,
        default_member_permissions: Permissions | int | None = NotSet,
        integration_types: list[IntegrationInstallType | int] = NotSet,
        contexts: list[InteractionContextType | int] = NotSet,
        nsfw: bool = NotSet,
        handler: ApplicationCommandHandlerType | int = NotSet,
    ) -> Command:
        """Edit a global command for this application.

        See :meth:`AuthorisedSession.edit_global_application_command`.
        """
        return await self._session.edit_global_application_command(
            command=command,
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            integration_types=integration_types,
            contexts=contexts,
            nsfw=nsfw,
            handler=handler,
        )

    async def delete_global_application_command(
        self, command: Command | int | str
    ) -> None:
        """Delete a global command for this application.

        See :meth:`AuthorisedSession.delete_global_application_command`.
        """
        await self._session.delete_global_application_command(command=command)

    async def bulk_overwrite_global_application_commands(
        self, commands: list[ApplicationCommandBuilder]
    ) -> list[Command]:
        """Overwrite all global commands for this application.

        See :meth:`AuthorisedSession.bulk_overwrite_global_application_commands`.
        """
        return await self._session.bulk_overwrite_global_application_commands(
            commands=commands
        )

    async def get_guild_application_commands(
        self, guild_id: int | str, *, with_localizations: bool | None = None
    ) -> list[Command]:
        """Fetch the commands for this application in a guild.

        See :meth:`AuthorisedSession.get_guild_application_commands`.
        """
        return await self._session.get_guild_application_commands(
            guild_id=guild_id,
            with_localizations=with_localizations,
        )

    async def get_guild_application_command(
        self, guild_id: int | str, command: Command | int | str
    ) -> Command:
        """Fetch a command for this application in a guild.

        See :meth:`AuthorisedSession.get_guild_application_command`.
        """
        return await self._session.get_guild_application_command(
            guild_id=guild_id, command=command
        )

    async def create_guild_application_command(
        self, guild_id: int | str, command: ApplicationCommandBuilder
    ) -> Command:
        """Create a command for this application in a guild.

        See :meth:`AuthorisedSession.create_guild_application_command`.
        """
        return await self._session.create_guild_application_command(
            guild_id=guild_id, command=command
        )

    async def edit_guild_application_command(
        self,
        guild_id: int | str,
        command: Command | int | str,
        *,
        name: str = NotSet,
        name_localizations: dict[Locale | str, str] | None = NotSet,
        description: str = NotSet,
        description_localizations: dict[Locale | str, str] | None = NotSet,
        options: list[
            OptionBuilder | ChatInputSubCommandBuilder | ChatInputGroupCommandBuilder
        ] = NotSet,
        default_member_permissions: Permissions | int | None = NotSet,
        nsfw: bool = NotSet,
    ) -> Command:
        """Edit a command for this application in a guild.

        See :meth:`AuthorisedSession.edit_guild_application_command`.
        """
        return await self._session.edit_guild_application_command(
            guild_id=guild_id,
            command=command,
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            nsfw=nsfw,
        )

    async def delete_guild_application_command(
        self, guild_id: int | str, command: Command | int | str
    ) -> None:
        """Delete a command for this application in a guild.

        See :meth:`AuthorisedSession.delete_guild_application_command`.
        """
        await self._session.delete_guild_application_command(
            guild_id=guild_id, command=command
        )

    async def bulk_overwrite_guild_application_commands(
        self, guild_id: int | str, commands: list[ApplicationCommandBuilder]
    ) -> list[Command]:
        """Overwrite all commands for this application in a guild.

        See :meth:`AuthorisedSession.bulk_overwrite_guild_application_commands`.
        """
        return await self._session.bulk_overwrite_guild_application_commands(
            guild_id=guild_id, commands=commands
        )

    async def get_guild_application_command_permissions(
        self, guild_id: int | str
    ) -> list[GuildApplicationCommandPermissions]:
        """Fetch the permissions for all commands of this application in a guild.

        See :meth:`AuthorisedSession.get_guild_application_command_permissions`.
        """
        return await self._session.get_guild_application_command_permissions(
            guild_id=guild_id
        )

    async def get_application_command_permissions(
        self, guild_id: int | str, command: Command | int | str
    ) -> GuildApplicationCommandPermissions:
        """Fetch the permissions for a command of this application in a guild.

        See :meth:`AuthorisedSession.get_application_command_permissions`.
        """
        return await self._session.get_application_command_permissions(
            guild_id=guild_id, command=command
        )

    async def edit_application_command_permissions(
        self,
        guild_id: int | str,
        command: Command | int | str,
        permissions: list[ApplicationCommandPermissionBuilder],
    ) -> GuildApplicationCommandPermissions:
        """Overwrite the permissions for a command of this application in a guild.

        See :meth:`AuthorisedSession.edit_application_command_permissions`.
        """
        return await self._session.edit_application_command_permissions(
            guild_id=guild_id,
            command=command,
            permissions=permissions,
        )

    async def get_partial(
        self,
        with_guild: bool | None = None,
    ) -> PartialApplication:
        return await self._session.get_partial_application(
            application_id=self.id, with_guild=with_guild
        )


class CurrentInformation(BaseModel["CurrentAuthorizationInformationResponsePayload"]):
    """Represents Discord API data for `CurrentInformation`."""

    __slots__ = (
        "_expires",
        "application",
        "scopes",
        "user",
    )

    def _initialize(self, data: CurrentAuthorizationInformationResponsePayload) -> None:
        self._expires: datetime.datetime = datetime.datetime.fromisoformat(
            data["expires"]
        )

        self.scopes: list[Scope | UnknownEnum] = Scope.from_list(data["scopes"])
        self.application = self._initialize_other(
            CurrentApplication, data, possible_keys="application"
        )
        self.user: PartialUser | None = self._initialize_other(
            PartialUser, data, possible_keys="user"
        )

    @property
    def expires_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The time at which the current access token will expire."""
        return self._expires
