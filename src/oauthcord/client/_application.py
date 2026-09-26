from __future__ import annotations

from typing import TYPE_CHECKING

from .. import utils
from ..enums import (
    ApplicationCommandHandlerType,
    IntegrationInstallType,
    InteractionContextType,
)
from ..models.application import (
    ActivityLink,
    ApplicationRoleConnection,
    PartialApplication,
    PartialApplicationIdentity,
)
from ..models.attachment import Attachment
from ..models.builders.commands import (
    ChatInputGroupCommandBuilder,
    _coerce_enum,
    _coerce_permissions,
)
from ..models.commands import Command, GuildApplicationCommandPermissions
from ..models.entitlement import Entitlement

if TYPE_CHECKING:
    from ..enums import Locale
    from ..internals._types import commands as command_types
    from ..models.builders.commands import (
        ApplicationCommandBuilder,
        ApplicationCommandPermissionBuilder,
        ChatInputSubCommandBuilder,
        OptionBuilder,
    )
    from ..models.file import File
    from ..models.flags import Permissions
    from ._proto import _AuthorisedSessionProto


class ApplicationClientMixin:
    async def create_application_attachment(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        file: File,
    ) -> Attachment:
        """Upload an ephemeral attachment for an application.

        This requires the :attr:`oauthcord.ApplicationFlags.embedded` flag.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The ID of the application.
        file: :class:`File`
            The file to upload.

            This must be one of the following types: ``png``, ``jpeg``, ``gif``.
        """
        res = await self.client.http.create_application_attachment(
            self.token,
            application_id=application_id,
            file=file,
        )
        return utils._construct_model(
            Attachment, data=res["attachment"], state=self._state
        )

    async def get_partial_application(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        with_guild: bool | None = None,
    ) -> PartialApplication:
        """Fetch a partial application with
        all the publicly available information about it.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The ID of the application.
        with_guild: :class:`bool`
            Whether to include the guild object in the response if the guild is discoverable.

            Defaults to `False`.

        Returns
        -------
        :class:`PartialApplication`
            Object representing the partial application.
        """
        res = await self.client.http.get_partial_application(
            self.token,
            application_id=application_id,
            with_guild=with_guild,
        )
        return utils._construct_model(PartialApplication, data=res, state=self._state)

    async def get_user_application_role_connection(
        self: _AuthorisedSessionProto,
    ) -> ApplicationRoleConnection:
        """Fetch the role connection for the current user and application.

        .. scope:: role_connections.write

        Returns
        -------
        :class:`ApplicationRoleConnection`
            Object representing the user's role connection for the application.
        """
        current_auth = self.current_authorization_information
        if current_auth is None:
            raise ValueError(
                "current_authorization_information is not available for this session"
            )

        application_id = current_auth.application.id
        res = await self.client.http.get_user_application_role_connection(
            self.token,
            application_id=application_id,
        )
        return utils._construct_model(
            ApplicationRoleConnection, data=res, state=self._state
        )

    async def edit_user_application_role_connection(
        self: _AuthorisedSessionProto,
        *,
        platform_name: str | None = utils.NotSet,
        platform_username: str | None = utils.NotSet,
        metadata: dict[str, str] | None = utils.NotSet,
    ) -> ApplicationRoleConnection:
        """Replace the role connection for the current user and application.

        All parameters are optional. Omitting or setting a parameter to :data:`None`
        will set that field to default.

        .. scope:: role_connections.write

        Parameters
        ----------
        platform_name: :class:`str`
            The vanity name of the platform a bot has connected. Max 50 characters.
        platform_username: :class:`str`
            The username of the platform a bot has connected. Max 100 characters.
        metadata: dict[str, str] | None
            Object mapping application role connection metadata keys to their
            stringified values for the user on the platform a bot has connected.
            Each value must be at most 100 characters.

        Returns
        -------
        :class:`ApplicationRoleConnection`
            Object representing the user's updated role connection for the application.
        """
        current_auth = self.current_authorization_information
        if current_auth is None:
            raise ValueError(
                "current_authorization_information is not available for this session"
            )

        application_id = current_auth.application.id
        res = await self.client.http.edit_user_application_role_connection(
            self.token,
            application_id=application_id,
            platform_name=platform_name,
            platform_username=platform_username,
            metadata=metadata,
        )
        return utils._construct_model(
            ApplicationRoleConnection, data=res, state=self._state
        )

    async def create_application_quick_link(
        self: _AuthorisedSessionProto,
        *,
        title: str,
        description: str,
        image: File,
        custom_id: str | None = None,
    ) -> ActivityLink:
        """Create a new activity quick link for the current application.

        Parameters
        ----------
        title: :class:`str`
            The title of the activity link.
            Can be between 1 and 32 characters.
        description: :class:`str`
            The description of the activity link.
            Can be between 1 and 64 characters.
        image: :class:`File`
            The activity link asset.
        custom_id: :class:`str`
            A custom id for the activity link.
            Can be between 1 and 256 characters.

        Returns
        -------
        :class:`ActivityLink`
            Object representing the created quick link.
        """
        current_auth = self.current_authorization_information
        if current_auth is None:
            raise ValueError(
                "current_authorization_information is not available for this session"
            )

        res = await self.client.http.create_application_quick_link(
            self.token,
            application_id=current_auth.application.id,
            title=title,
            description=description,
            image=image,
            custom_id=custom_id,
        )
        return utils._construct_model(ActivityLink, data=res, state=self._state)

    async def get_bulk_application_identities(
        self: _AuthorisedSessionProto,
        *,
        user_ids: list[int | str],
    ) -> list[PartialApplicationIdentity]:
        """Fetch a list of partial application identities for the current application.

        Parameters
        ----------
        user_ids: list[:class:`int` | :class:`str`]
            A list of user IDs to retrieve application identities for.
            Can only contain between 1 and 100 IDs. Invalid IDs are ignored.

        Returns
        -------
        list[:class:`PartialApplicationIdentity`]
            A list of objects representing the fetched partial application identities.
        """
        res = await self.client.http.get_bulk_application_identities(
            self.token,
            user_ids=user_ids,
        )
        return [
            utils._construct_model(
                PartialApplicationIdentity,
                data=app_data,
                state=self._state,
            )
            for app_data in res
        ]

    async def get_application_entitlements(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        user_id: int | str | None = None,
        sku_ids: list[int | str] | None = None,
        guild_id: int | str | None = None,
        exclude_ended: bool | None = None,
        exclude_deleted: bool | None = None,
        before: int | str | None = None,
        after: int | str | None = None,
        limit: int | None = None,
    ) -> list[Entitlement]:
        """Fetch a list of entitlements for an application.

        This includes active and expired entitlements.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The ID of the application.
        user_id: :class:`int` | :class:`str`
            The ID of the user to look up entitlements for.
        sku_ids: list[:class:`int` | :class:`str`]
            The IDs of the SKUs to look up entitlements for.
        guild_id: :class:`int` | :class:`str`
            The ID of the guild to look up entitlements for.
        exclude_ended: :class:`bool`
            Whether ended entitlements should be omitted. Defaults to ``False``.
        exclude_deleted: :class:`bool`
            Whether deleted entitlements should be omitted. Defaults to ``True``.
        before: :class:`int` | :class:`str`
            Get entitlements before this entitlement ID.
        after: :class:`int` | :class:`str`
            Get entitlements after this entitlement ID.
        limit: :class:`int`
            Max number of entitlements to return. Must be between 1 and 100. Defaults to 100.

        Returns
        -------
        list[:class:`Entitlement`]
            A list of objects representing the fetched entitlements.
        """
        res = await self.client.http.get_application_entitlements(
            self.token,
            application_id=application_id,
            user_id=user_id,
            sku_ids=sku_ids,
            guild_id=guild_id,
            exclude_ended=exclude_ended,
            exclude_deleted=exclude_deleted,
            before=before,
            after=after,
            limit=limit,
        )
        return [
            utils._construct_model(Entitlement, data=entitlement, state=self._state)
            for entitlement in res
        ]

    async def get_application_entitlement(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> Entitlement:
        """Fetch an entitlement for an application.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The ID of the application.
        entitlement_id: :class:`int` | :class:`str`
            The ID of the entitlement.

        Returns
        -------
        :class:`Entitlement`
            Object representing the fetched entitlement.
        """
        res = await self.client.http.get_application_entitlement(
            self.token,
            application_id=application_id,
            entitlement_id=entitlement_id,
        )
        return utils._construct_model(Entitlement, data=res, state=self._state)

    async def consume_application_entitlement(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> None:
        """Consume an entitlement for an application.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The ID of the application.
        entitlement_id: :class:`int` | :class:`str`
            The ID of the entitlement to consume.
        """
        await self.client.http.consume_application_entitlement(
            self.token,
            application_id=application_id,
            entitlement_id=entitlement_id,
        )

    async def delete_application_entitlement(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> None:
        """Delete an entitlement for an application.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The ID of the application.
        entitlement_id: :class:`int` | :class:`str`
            The ID of the entitlement to delete.
        """
        await self.client.http.delete_application_entitlement(
            self.token,
            application_id=application_id,
            entitlement_id=entitlement_id,
        )

    async def get_global_application_commands(
        self: _AuthorisedSessionProto,
        *,
        with_localizations: bool | None = None,
    ) -> list[Command]:
        """Fetch the global commands for the current application.

        Parameters
        ----------
        with_localizations: :class:`bool`
            Whether to include the full localization dictionaries.

            Defaults to ``False``.

        Returns
        -------
        list[:class:`Command`]
            The application's global commands.
        """
        res = await self.client.http.get_global_application_commands(
            self.token,
            application_id=self.client.id,
            with_localizations=with_localizations,
        )
        return [
            utils._construct_model(Command, data=command, state=self._state)
            for command in res
        ]

    async def get_global_application_command(
        self: _AuthorisedSessionProto,
        *,
        command: Command | int | str,
    ) -> Command:
        """Fetch a global command for the current application.

        Parameters
        ----------
        command: :class:`Command` | :class:`int` | :class:`str`
            The command or command ID.

        Returns
        -------
        :class:`Command`
            The fetched command.
        """
        res = await self.client.http.get_global_application_command(
            self.token,
            application_id=self.client.id,
            command_id=command.id if isinstance(command, Command) else command,
        )
        return utils._construct_model(Command, data=res, state=self._state)

    async def create_global_application_command(
        self: _AuthorisedSessionProto,
        *,
        command: ApplicationCommandBuilder,
    ) -> Command:
        """Create a global command for the current application.

        Creating a command with the same name as an existing command
        of the same type overwrites it.

        .. scope:: applications.commands.update

        Parameters
        ----------
        command: :class:`ApplicationCommandBuilder`
            The command to create.

        Returns
        -------
        :class:`Command`
            The created command.
        """
        res = await self.client.http.create_global_application_command(
            self.token,
            application_id=self.client.id,
            data=ApplicationClientMixin._command_to_request(command),
        )
        return utils._construct_model(Command, data=res, state=self._state)

    async def edit_global_application_command(
        self: _AuthorisedSessionProto,
        *,
        command: Command | int | str,
        name: str = utils.NotSet,
        name_localizations: dict[Locale | str, str] | None = utils.NotSet,
        description: str = utils.NotSet,
        description_localizations: dict[Locale | str, str] | None = utils.NotSet,
        options: list[
            OptionBuilder | ChatInputSubCommandBuilder | ChatInputGroupCommandBuilder
        ] = utils.NotSet,
        default_member_permissions: Permissions | int | None = utils.NotSet,
        integration_types: list[IntegrationInstallType | int] = utils.NotSet,
        contexts: list[InteractionContextType | int] = utils.NotSet,
        nsfw: bool = utils.NotSet,
        handler: ApplicationCommandHandlerType | int = utils.NotSet,
    ) -> Command:
        """Edit a global command for the current application.

        Only the provided fields are updated. Each provided field
        entirely replaces its existing value.

        .. scope:: applications.commands.update

        Parameters
        ----------
        command: :class:`Command` | :class:`int` | :class:`str`
            The command or command ID to edit.
        name: :class:`str`
            The new name of the command. Must be between 1 and 32 characters.
        name_localizations: dict[:class:`Locale` | :class:`str`, :class:`str`] | :data:`None`
            The new localizations for the name.
        description: :class:`str`
            The new description of the command. Must be between 1 and 100 characters.
        description_localizations: dict[:class:`Locale` | :class:`str`, :class:`str`] | :data:`None`
            The new localizations for the description.
        options: list[:class:`OptionBuilder` | :class:`ChatInputSubCommandBuilder` | :class:`ChatInputGroupCommandBuilder`]
            The new options of the command. Only for chat input commands. Max 25.
        default_member_permissions: :class:`Permissions` | :class:`int` | :data:`None`
            The permissions required to use the command by default.
        integration_types: list[:class:`IntegrationInstallType` | :class:`int`]
            The installation contexts where the command is available.
        contexts: list[:class:`InteractionContextType` | :class:`int`]
            The interaction contexts where the command can be used.
        nsfw: :class:`bool`
            Whether the command is age-restricted.
        handler: :class:`ApplicationCommandHandlerType` | :class:`int`
            How interactions are handled. Only for primary entry point commands.

        Returns
        -------
        :class:`Command`
            The edited command.
        """  # noqa: E501
        res = await self.client.http.edit_global_application_command(
            self.token,
            application_id=self.client.id,
            command_id=command.id if isinstance(command, Command) else command,
            data=ApplicationClientMixin._edit_command_payload(
                name=name,
                name_localizations=name_localizations,
                description=description,
                description_localizations=description_localizations,
                options=options,
                default_member_permissions=default_member_permissions,
                nsfw=nsfw,
                integration_types=integration_types,
                contexts=contexts,
                handler=handler,
            ),
        )
        return utils._construct_model(Command, data=res, state=self._state)

    async def delete_global_application_command(
        self: _AuthorisedSessionProto,
        *,
        command: Command | int | str,
    ) -> None:
        """Delete a global command for the current application.

        .. scope:: applications.commands.update

        Parameters
        ----------
        command: :class:`Command` | :class:`int` | :class:`str`
            The command or command ID to delete.
        """
        await self.client.http.delete_global_application_command(
            self.token,
            application_id=self.client.id,
            command_id=command.id if isinstance(command, Command) else command,
        )

    async def bulk_overwrite_global_application_commands(
        self: _AuthorisedSessionProto,
        *,
        commands: list[ApplicationCommandBuilder],
    ) -> list[Command]:
        """Overwrite all global commands for the current application.

        Commands not in ``commands`` are deleted.

        .. scope:: applications.commands.update

        Parameters
        ----------
        commands: list[:class:`ApplicationCommandBuilder`]
            The commands that should exist after the overwrite.

        Returns
        -------
        list[:class:`Command`]
            The application's global commands after the overwrite.
        """
        res = await self.client.http.bulk_overwrite_global_application_commands(
            self.token,
            application_id=self.client.id,
            data=[
                ApplicationClientMixin._command_to_request(command)
                for command in commands
            ],
        )
        return [
            utils._construct_model(Command, data=command, state=self._state)
            for command in res
        ]

    async def get_guild_application_commands(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
        with_localizations: bool | None = None,
    ) -> list[Command]:
        """Fetch the commands for the current application in a guild.

        This does not include global commands.

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        with_localizations: :class:`bool`
            Whether to include the full localization dictionaries.

            Defaults to ``False``.

        Returns
        -------
        list[:class:`Command`]
            The application's commands in the guild.
        """
        res = await self.client.http.get_guild_application_commands(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
            with_localizations=with_localizations,
        )
        return [
            utils._construct_model(Command, data=command, state=self._state)
            for command in res
        ]

    async def get_guild_application_command(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
        command: Command | int | str,
    ) -> Command:
        """Fetch a command for the current application in a guild.

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        command: :class:`Command` | :class:`int` | :class:`str`
            The command or command ID.

        Returns
        -------
        :class:`Command`
            The fetched command.
        """
        res = await self.client.http.get_guild_application_command(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
            command_id=command.id if isinstance(command, Command) else command,
        )
        return utils._construct_model(Command, data=res, state=self._state)

    async def create_guild_application_command(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
        command: ApplicationCommandBuilder,
    ) -> Command:
        """Create a command for the current application in a guild.

        Creating a command with the same name as an existing command
        of the same type overwrites it.

        .. scope:: applications.commands.update

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        command: :class:`ApplicationCommandBuilder`
            The command to create.

        Returns
        -------
        :class:`Command`
            The created command.
        """
        res = await self.client.http.create_guild_application_command(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
            data=ApplicationClientMixin._command_to_request(command),
        )
        return utils._construct_model(Command, data=res, state=self._state)

    async def edit_guild_application_command(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
        command: Command | int | str,
        name: str = utils.NotSet,
        name_localizations: dict[Locale | str, str] | None = utils.NotSet,
        description: str = utils.NotSet,
        description_localizations: dict[Locale | str, str] | None = utils.NotSet,
        options: list[
            OptionBuilder | ChatInputSubCommandBuilder | ChatInputGroupCommandBuilder
        ] = utils.NotSet,
        default_member_permissions: Permissions | int | None = utils.NotSet,
        nsfw: bool = utils.NotSet,
    ) -> Command:
        """Edit a command for the current application in a guild.

        Only the provided fields are updated. Each provided field
        entirely replaces its existing value.

        .. scope:: applications.commands.update

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        command: :class:`Command` | :class:`int` | :class:`str`
            The command or command ID to edit.
        name: :class:`str`
            The new name of the command. Must be between 1 and 32 characters.
        name_localizations: dict[:class:`Locale` | :class:`str`, :class:`str`] | :data:`None`
            The new localizations for the name.
        description: :class:`str`
            The new description of the command. Must be between 1 and 100 characters.
        description_localizations: dict[:class:`Locale` | :class:`str`, :class:`str`] | :data:`None`
            The new localizations for the description.
        options: list[:class:`OptionBuilder` | :class:`ChatInputSubCommandBuilder` | :class:`ChatInputGroupCommandBuilder`]
            The new options of the command. Only for chat input commands. Max 25.
        default_member_permissions: :class:`Permissions` | :class:`int` | :data:`None`
            The permissions required to use the command by default.
        nsfw: :class:`bool`
            Whether the command is age-restricted.

        Returns
        -------
        :class:`Command`
            The edited command.
        """  # noqa: E501
        res = await self.client.http.edit_guild_application_command(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
            command_id=command.id if isinstance(command, Command) else command,
            data=ApplicationClientMixin._edit_command_payload(
                name=name,
                name_localizations=name_localizations,
                description=description,
                description_localizations=description_localizations,
                options=options,
                default_member_permissions=default_member_permissions,
                nsfw=nsfw,
            ),
        )
        return utils._construct_model(Command, data=res, state=self._state)

    async def delete_guild_application_command(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
        command: Command | int | str,
    ) -> None:
        """Delete a command for the current application in a guild.

        .. scope:: applications.commands.update

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        command: :class:`Command` | :class:`int` | :class:`str`
            The command or command ID to delete.
        """
        await self.client.http.delete_guild_application_command(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
            command_id=command.id if isinstance(command, Command) else command,
        )

    async def bulk_overwrite_guild_application_commands(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
        commands: list[ApplicationCommandBuilder],
    ) -> list[Command]:
        """Overwrite all commands for the current application in a guild.

        Commands not in ``commands`` are deleted.

        .. scope:: applications.commands.update

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        commands: list[:class:`ApplicationCommandBuilder`]
            The commands that should exist after the overwrite.

        Returns
        -------
        list[:class:`Command`]
            The application's commands in the guild after the overwrite.
        """
        res = await self.client.http.bulk_overwrite_guild_application_commands(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
            data=[
                ApplicationClientMixin._command_to_request(command)
                for command in commands
            ],
        )
        return [
            utils._construct_model(Command, data=command, state=self._state)
            for command in res
        ]

    async def get_guild_application_command_permissions(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
    ) -> list[GuildApplicationCommandPermissions]:
        """Fetch the permissions for all commands of the current application in a guild.

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.

        Returns
        -------
        list[:class:`GuildApplicationCommandPermissions`]
            The command permissions in the guild.
        """
        res = await self.client.http.get_guild_application_command_permissions(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
        )
        return [
            utils._construct_model(
                GuildApplicationCommandPermissions, data=perms, state=self._state
            )
            for perms in res
        ]

    async def get_application_command_permissions(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
        command: Command | int | str,
    ) -> GuildApplicationCommandPermissions:
        """Fetch the permissions for a command of the current application in a guild.

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        command: :class:`Command` | :class:`int` | :class:`str`
            The command or command ID.

        Returns
        -------
        :class:`GuildApplicationCommandPermissions`
            The command's permissions in the guild.
        """
        res = await self.client.http.get_application_command_permissions(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
            command_id=command.id if isinstance(command, Command) else command,
        )
        return utils._construct_model(
            GuildApplicationCommandPermissions, data=res, state=self._state
        )

    async def edit_application_command_permissions(
        self: _AuthorisedSessionProto,
        *,
        guild_id: int | str,
        command: Command | int | str,
        permissions: list[ApplicationCommandPermissionBuilder],
    ) -> GuildApplicationCommandPermissions:
        """Overwrite the permissions for a command of the current application in a guild.

        The authorising user must be able to manage the guild and its roles.

        .. scope:: applications.commands.permissions.update

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        command: :class:`Command` | :class:`int` | :class:`str`
            The command or command ID.

            Use the application ID to target all commands of the application.
        permissions: list[:class:`ApplicationCommandPermissionBuilder`]
            The permission overwrites for the command. Max 100.

        Returns
        -------
        :class:`GuildApplicationCommandPermissions`
            The command's updated permissions in the guild.
        """
        res = await self.client.http.edit_application_command_permissions(
            self.token,
            application_id=self.client.id,
            guild_id=guild_id,
            command_id=command.id if isinstance(command, Command) else command,
            data={"permissions": [perm.to_request() for perm in permissions]},
        )
        return utils._construct_model(
            GuildApplicationCommandPermissions, data=res, state=self._state
        )

    @staticmethod
    def _command_to_request(
        command: ApplicationCommandBuilder,
    ) -> command_types.ApplicationCommandRequest:
        if isinstance(command, ChatInputGroupCommandBuilder):
            return command._to_command_request()
        return command.to_request()

    @staticmethod
    def _edit_command_payload(
        *,
        name: str,
        name_localizations: dict[Locale | str, str] | None,
        description: str,
        description_localizations: dict[Locale | str, str] | None,
        options: list[
            OptionBuilder | ChatInputSubCommandBuilder | ChatInputGroupCommandBuilder
        ],
        default_member_permissions: Permissions | int | None,
        nsfw: bool,
        integration_types: list[IntegrationInstallType | int] = utils.NotSet,
        contexts: list[InteractionContextType | int] = utils.NotSet,
        handler: ApplicationCommandHandlerType | int = utils.NotSet,
    ) -> command_types.EditApplicationCommandRequest:
        payload: command_types.EditApplicationCommandRequest = {}
        if name is not utils.NotSet:
            payload["name"] = name
        if name_localizations is not utils.NotSet:
            payload["name_localizations"] = (
                {str(locale): value for locale, value in name_localizations.items()}
                if name_localizations is not None
                else None
            )
        if description is not utils.NotSet:
            payload["description"] = description
        if description_localizations is not utils.NotSet:
            payload["description_localizations"] = (
                {
                    str(locale): value
                    for locale, value in description_localizations.items()
                }
                if description_localizations is not None
                else None
            )
        if options is not utils.NotSet:
            payload["options"] = [
                option._to_option_request()
                if isinstance(option, ChatInputGroupCommandBuilder)
                else option.to_request()
                for option in options
            ]
        if default_member_permissions is not utils.NotSet:
            payload["default_member_permissions"] = (
                str(permissions.value)
                if (permissions := _coerce_permissions(default_member_permissions))
                is not None
                else None
            )
        if nsfw is not utils.NotSet:
            payload["nsfw"] = nsfw
        if integration_types is not utils.NotSet:
            payload["integration_types"] = [
                _coerce_enum(IntegrationInstallType, it).value
                for it in integration_types
            ]
        if contexts is not utils.NotSet:
            payload["contexts"] = [
                _coerce_enum(InteractionContextType, context).value
                for context in contexts
            ]
        if handler is not utils.NotSet:
            payload["handler"] = _coerce_enum(
                ApplicationCommandHandlerType, handler
            ).value
        return payload
