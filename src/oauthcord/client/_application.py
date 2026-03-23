from typing import TYPE_CHECKING

from .. import utils
from ..models.application import (
    ActivityLink,
    ApplicationRoleConnection,
    PartialApplication,
    PartialApplicationIdentity,
)
from ..models.attachment import Attachment
from ..models.entitlement import Entitlement

if TYPE_CHECKING:
    from ..models.file import File
    from ._base import _AuthorisedSessionProto


class ApplicationClient:
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
        return utils._construct_model(Attachment, data=res["attachment"])

    async def get_partial_application(
        self: _AuthorisedSessionProto,
        *,
        application_id: int | str,
    ) -> PartialApplication:
        """Fetch a partial application with
        all the publicly available information about it.

        Parameters
        ----------
        application_id: :class:`int` | :class:`str`
            The ID of the application.

        Returns
        -------
        :class:`PartialApplication`
            Object representing the partial application.
        """
        res = await self.client.http.get_partial_application(
            self.token,
            application_id=application_id,
        )
        return utils._construct_model(PartialApplication, data=res, session=self)

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
        application_id = self.current_authorization_information.application.id
        res = await self.client.http.get_user_application_role_connection(
            self.token,
            application_id=application_id,
        )
        return utils._construct_model(ApplicationRoleConnection, data=res, session=self)

    async def edit_user_application_role_connection(
        self: _AuthorisedSessionProto,
        *,
        platform_name: str | None = utils.NotSet,
        platform_username: str | None = utils.NotSet,
        metadata: dict[str, str] | None = utils.NotSet,
    ) -> ApplicationRoleConnection:
        """Replace the role connection for the current user and application.

        All parameters are optional. Omitting or setting a parameter to ``None``
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
        application_id = self.current_authorization_information.application.id
        res = await self.client.http.edit_user_application_role_connection(
            self.token,
            application_id=application_id,
            platform_name=platform_name,
            platform_username=platform_username,
            metadata=metadata,
        )
        return utils._construct_model(ApplicationRoleConnection, data=res, session=self)

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
        res = await self.client.http.create_application_quick_link(
            self.token,
            application_id=self.current_authorization_information.application.id,
            title=title,
            description=description,
            image=image,
            custom_id=custom_id,
        )
        return utils._construct_model(ActivityLink, data=res)

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
            utils._construct_model(Entitlement, data=entitlement, session=self)
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
        return utils._construct_model(Entitlement, data=res, session=self)

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
