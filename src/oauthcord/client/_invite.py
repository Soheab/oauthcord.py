from typing import TYPE_CHECKING

from .. import utils
from ..models.invite import Invite

if TYPE_CHECKING:
    from ._base import _AuthorisedSessionProto


class InviteClient:
    async def accept_invite(
        self: _AuthorisedSessionProto,
        invite_code: str,
        *,
        session_id: str | None = None,
    ) -> Invite:
        """Accept an invite to a guild.

        The bot must be a member of the guild that the invite originates from.

        This cannot be used to accept invites of guilds with the "HUB" feature.

        .. warning::
            Don't use this to join many guilds in a short period of time.

        Parameters
        ----------
        invite_code: :class:`str`
            The invite code of the invite to accept. This is the part after ``discord.gg/`` in the invite URL.
        session_id: :class:`str` | ``None``
            The session ID that is accepting the invite. This is only required for guest invites.

        Returns
        -------
        :class:`Invite`
             Object representing the accepted invite.
        """
        res = await self.client.http.accept_invite(
            self.token, code=invite_code, session_id=session_id
        )
        return utils._construct_model(Invite, data=res, session=self)
