from typing import TYPE_CHECKING

from .. import utils
from ..models.channel import (
    CallEligibility,
    DMChannel,
    GuildChannel,
    LinkedAccount,
    _from_data,
)

if TYPE_CHECKING:
    from ._base import _AuthorisedSessionProto


class ChannelClient:
    async def get_dm_channel(
        self: _AuthorisedSessionProto,
        *,
        user_id: int | str,
    ) -> DMChannel:
        """Get an existing DM channel with an user.

        Parameters
        ----------
        user_id: :class:`int` | :class:`str`
            The ID of the other user.

        Returns
        -------
        :class:`DMChannel`
            Object representing the DM channel.
        """
        res = await self.client.http.get_dm_channel(
            self.token,
            user_id=user_id,
        )
        return utils._construct_model(DMChannel, data=res, session=self)

    async def create_private_channel(
        self: _AuthorisedSessionProto,
        *,
        recipients: list[int | str] | None = None,
        nicks: dict[str | int, str] | None = None,
    ) -> DMChannel:
        """Create a new private channel with one or more users.

        .. warning::
            Don't spam this.

        Parameters
        ----------
        recipients: list[:class:`int` | :class:`str`]
            A list of user IDs to include in the private channel.

            The client's user ID can be included in this to
            create a group DM with only one user.
        nicks: dict[:class:`int` | :class:`str`, :class:`str`]
            A mapping of user IDs to nicknames to use for those users in the private channel.

        Returns
        -------
        :class:`DMChannel`
            Object representing the created private channel.
        """
        res = await self.client.http.create_private_channel(
            self.token,
            recipients=recipients,
            nicks=nicks,
        )
        return utils._construct_model(DMChannel, data=res, session=self)

    async def get_guild_channels(
        self: _AuthorisedSessionProto,
        *,
        guild_id: str | int,
        permissions: bool = False,
        with_can_link_lobby: bool = False,
    ) -> list[GuildChannel]:
        """Get a list of channels in a guild.

        Parameters
        ----------
        guild_id: :class:`int` | :class:`str`
            The ID of the guild.
        permissions: :class:`bool`
            Whether to include calculated permissions for the user
            in each channel. Defaults to ``False``.
        with_can_link_lobby: :class:`bool`
            Whether to include ``is_linkable`` and
            ``is_viewable_and_writeable_by_all_members``
            for each channel. Defaults to ``False``.

        Returns
        -------
        list[:class:`GuildChannel`]
            A list of objects representing the channels in the guild.
        """
        res = await self.client.http.get_guild_channels(
            self.token,
            guild_id=guild_id,
            permissions=permissions,
            with_can_link_lobby=with_can_link_lobby,
        )
        return [_from_data(session=self, data=channel) for channel in res]  # type: ignore

    async def get_call_eligibility(
        self: _AuthorisedSessionProto, *, channel_id: int | str
    ) -> CallEligibility:
        """Check if the user can start a call in the DM channel.

        Parameters
        ----------
        channel_id: :class:`int` | :class:`str`
            The ID of the channel.

        Returns
        -------
        :class:`CallEligibility`
            Object representing the call eligibility of the user in the channel.
        """
        res = await self.client.http.get_call_eligibility(
            self.token,
            channel_id=channel_id,
        )
        return utils._construct_model(CallEligibility, data=res)

    async def ring_channel_recipients(
        self: _AuthorisedSessionProto,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        """Ring one or more recipients in a DM channel.

        .. note::
            This requires an active call in the channel.

        Parameters
        ----------
        channel_id: :class:`int` | :class:`str`
            The ID of the channel.
        recipients: list[:class:`int` | :class:`str`]
            A list of user IDs to ring. If not provided, all users will be rung.
        """
        await self.client.http.ring_channel_recipients(
            self.token,
            channel_id=channel_id,
            recipients=recipients,
        )

    async def stop_ringing_channel_recipients(
        self: _AuthorisedSessionProto,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        """Stop ringing one or more recipients in a DM channel.

        Parameters
        ----------
        channel_id: :class:`int` | :class:`str`
            The ID of the channel.
        recipients: list[:class:`int` | :class:`str`]
            A list of user IDs to stop ringing. Defaults to the current user.
        """
        await self.client.http.stop_ringing_channel_recipients(
            self.token,
            channel_id=channel_id,
            recipients=recipients,
        )

    async def get_channel_linked_accounts(
        self: _AuthorisedSessionProto,
        *,
        channel_id: int | str,
        user_ids: list[int | str] | None = None,
    ) -> dict[int, list[LinkedAccount]]:
        """Get the linked accounts of one or more users in a DM channel.

        Parameters
        ----------
        channel_id: :class:`int` | :class:`str`
            The ID of the channel.
        user_ids: list[:class:`int` | :class:`str`]
            A list of user IDs to get linked accounts for.

        Returns
        -------
        dict[:class:`int`, list[:class:`LinkedAccount`]]
            A mapping of user IDs to lists of linked accounts for those users in the channel.
        """
        res = await self.client.http.get_channel_linked_accounts(
            self.token,
            channel_id=channel_id,
            user_ids=user_ids,
        )
        return {
            int(user_id): [
                utils._construct_model(LinkedAccount, data=account)
                for account in accounts
            ]
            for user_id, accounts in res["linked_accounts"].items()
        }
