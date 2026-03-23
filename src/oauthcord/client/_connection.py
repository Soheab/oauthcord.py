from typing import TYPE_CHECKING

from .. import utils
from ..models.connection import Connection

if TYPE_CHECKING:
    from ._base import _AuthorisedSessionProto


class ConnectionClient:
    async def get_current_user_connections(
        self: _AuthorisedSessionProto,
    ) -> list[Connection]:
        """Get a list of the user's connections.

        Returns
        -------
        list[:class:`Connection`]
            A list of the user's connections.
        """
        res = await self.client.http.get_current_user_connections(self.token)
        return [
            utils._construct_model(Connection, data=conn, http=self.client.http)
            for conn in res
        ]

    async def get_current_user_linked_connections(
        self: _AuthorisedSessionProto,
    ) -> list[Connection]:
        """Get a list of the user's linked connections.

        .. scope:: connections

        Returns
        -------
        list[:class:`Connection`]
            A list of the user's linked connections that have a two-way
            link with the current application.
        """
        res = await self.client.http.get_user_linked_connections(self.token)
        return [
            utils._construct_model(Connection, data=conn, http=self.client.http)
            for conn in res
        ]
