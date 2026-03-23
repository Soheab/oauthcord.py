from typing import TYPE_CHECKING

from .. import utils
from ..models.guild import Guild
from ..models.member import GuildMember

if TYPE_CHECKING:
    from ._base import _AuthorisedSessionProto


class GuildClient:
    async def get_current_user_guilds(
        self: _AuthorisedSessionProto,
    ) -> list[Guild]:
        """Get a list of the current user's guilds.

        .. scope:: guilds.members.read

        Returns
        -------
        list[:class:`Guild`]
            List of objects representing the guilds the user is a member of.
        """
        res = await self.client.http.get_current_user_guilds(self.token)
        return [
            utils._construct_model(Guild, data=guild, session=self) for guild in res
        ]

    async def get_current_guild_member(
        self: _AuthorisedSessionProto,
        guild_id: int,
    ) -> GuildMember:
        """Get the current user's private member object for a specific guild.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the guild to get the member object for.

        Returns
        -------
        :class:`GuildMember`
            Object representing the user's member object in the guild.
        """

        res = await self.client.http.get_current_guild_member(
            self.token, guild_id=guild_id
        )
        return utils._construct_model(GuildMember, data=res, session=self)

    async def add_current_user_to_guild(
        self: _AuthorisedSessionProto,
        guild_id: int,
        *,
        bot_token: str,
        user_id: int | str = utils.NotSet,
        nick: str = utils.NotSet,
        roles: list[int | str] = utils.NotSet,
        mute: bool = utils.NotSet,
        deaf: bool = utils.NotSet,
        bypass_verification: bool = utils.NotSet,
    ) -> GuildMember | None:
        """Add the current user to a guild.

        .. scope:: guilds.join

        This endpoint requires bot authorization for the same application.
        For guilds with membership screening enabled, the member will have to
        complete the process before they become full members of the guild. Until then,
          they will have a ``pending`` status.

        The bot must be a member of the guild and have the ``CREATE_INSTANT_INVITE`` permission too.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the guild to add the user to.
        bot_token: :class:`str`
            Bot token for the application.
        nick: :class:`str` | ``None``
            A nickname to assign to the user upon joining.

            This requires the bot to have the ``MANAGE_NICKNAMES`` permission.

            Must be between 1 and 32 characters in length.
        roles: list[:class:`int` | :class:`str`] | ``None``
            A list of role IDs to assign to the user upon joining.

            This requires the bot to have the ``MANAGE_ROLES`` permission.
        mute: :class:`bool`
            Whether the user should be muted in voice channels upon joining.

            This requires the bot to have the ``MUTE_MEMBERS`` permission.
        deaf: :class:`bool`
            Whether the user should be deafened in voice channels upon joining.

            This requires the bot to have the ``DEAFEN_MEMBERS`` permission.
        bypass_verification: :class:`bool`
            Whether the user should bypass the guild's membership screening process.

            This sets the :attr:`MemberFlags.bypasses_verification` flag on the member.

            This requires the bot to have the ``MANAGE_GUILD`` permission OR all of
            the following permissions: ``MODERATE_MEMBERS``, ``KICK_MEMBERS``, ``BAN_MEMBERS``.
        user_id: :class:`int` | :class:`str`
            The ID of the user to add to the guild. This is only required if the current session
            was not autohorized with the ``identify`` scope. Therfore, it cannot use
            :attr:`AuthorisedSession.current_authorization_information.user.id` to get the user's ID.

        Returns
        -------
        :class:`GuildMember` | ``None``
            Object representing the joined member, if the user was successfully added to the guild.
              If the user is already a member of the guild, ``None`` is returned instead.
        """
        try:
            user_id = user_id or self.current_authorization_information.user.id  # pyright: ignore[reportOptionalMemberAccess]
        except AttributeError:
            raise ValueError(
                "user_id is required if the session is not authorized with the 'identify' scope"
            )

        res = await self.client.http.add_user_to_guild(
            self.token,
            guild_id=guild_id,
            bot_token=bot_token,
            nick=nick,
            roles=roles,
            user_id=user_id,
            deaf=deaf,
            mute=mute,
            bypass_verification=bypass_verification,
        )
        if res:
            return utils._construct_model(GuildMember, data=res, session=self)
