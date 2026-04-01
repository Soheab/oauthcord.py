from typing import TYPE_CHECKING

from .. import utils
from ..models.current_auth import CurrentInformation

if TYPE_CHECKING:
    from ._base import _AuthorisedSessionProto


class Oauth2Client:
    async def get_current_authorization_information(
        self: _AuthorisedSessionProto,
    ) -> CurrentInformation:
        """Returns info abotu the current authorization, including the authorized user, the application, and the scopes.

        :attr:`CurrentInformation.user` requires the ``identify`` scope.

        Returns
        -------
        :class:`CurrentInformation`
            An object containing the information.
        """
        res = await self.client.http.get_current_authorization_information(self.token)
        info = utils._construct_model(CurrentInformation, data=res, session=self)
        self.current_authorization_information = info
        return info
