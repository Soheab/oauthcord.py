from typing import TYPE_CHECKING

from .. import utils
from ..models.user import CurrentUser, PartialUser

if TYPE_CHECKING:
    from ._base import _AuthorisedSessionProto


class UserClient:
    async def get_current_user(
        self: _AuthorisedSessionProto,
    ) -> CurrentUser:
        """Get the current user.

        Returns
        -------
        :class:`CurrentUser`
            The current user.
        """
        data = await self.client.http.get_current_user(self.token)
        return utils._construct_model(CurrentUser, data=data, session=self)

    async def edit_current_user_account(
        self: _AuthorisedSessionProto,
        *,
        global_name: str | None = utils.NotSet,
    ) -> PartialUser:
        """Edit the current user's account settings.

        .. scope:: account.global_name.update

        Parameters
        ----------
        global_name: Optional[:class:`str`]
            The new global name for the current user. Must be between 2 and 32 characters.

        Returns
        -------
        :class:`PartialUser`
            The updated current user.
        """
        data = await self.client.http.modify_current_user_account(
            self.token,
            global_name=global_name,
        )
        return utils._construct_model(PartialUser, data=data, session=self)
