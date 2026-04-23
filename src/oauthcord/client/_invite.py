from __future__ import annotations

from typing import TYPE_CHECKING

from .. import utils
from ..models.invite import Invite

if TYPE_CHECKING:
    from ._proto import _AuthorisedSessionProto


class InviteClientMixin:
    async def accept_invite(
        self: _AuthorisedSessionProto,
        invite: str,
        *,
        session_id: str | None = None,
    ) -> Invite:
        """Accept an invite to a guild.

        The bot that belongs to the current application must be a member of the guild that
        the invite originates from.

        This cannot be used to accept invites of guilds with the "HUB" feature.

        .. warning::
            Don't use this to join many guilds in a short period of time.

        Parameters
        ----------
        invite: :class:`str`
            The invite code or URL of the invite to accept.
        session_id: :class:`str` | :data:`None`
            The session ID that is accepting the invite. This is only required for guest invites.

        Returns
        -------
        :class:`Invite`
             Object representing the accepted invite.
        """
        code = utils.parse_invite(invite) or invite
        res = await self.client.http.accept_invite(
            self.token, code=code, session_id=session_id
        )
        return utils._construct_model(Invite, data=res, session=self)
