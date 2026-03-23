from typing import TYPE_CHECKING

from .. import utils
from ..models.flags import LobbyFlags, MessageFlags
from ..models.lobby import Lobby
from ..models.message import PartialMessage

if TYPE_CHECKING:
    from ..internals._types import components as component_types
    from ..internals._types import message as message_types
    from ..models.file import File
    from ._base import _AuthorisedSessionProto


class LobbyClient:
    async def join_or_create_lobby(
        self: _AuthorisedSessionProto,
        *,
        secret: str,
        lobby_metadata: dict[str, str] | None = None,
        member_metadata: dict[str, str] | None = None,
        idle_timeout_seconds: int = utils.NotSet,
        flags: LobbyFlags | int = utils.NotSet,
    ) -> Lobby:
        """Join or create a lobby.

        If a lobby with the given secret already exists, the current user
        attempts to join it. Otherwise, a new lobby is created with the given
        secret and the current user is added as a member.


        Parameters
        ----------
        secret: :class:`str`
            The lobby secret. Maximum 250 characters.
        lobby_metadata: :class:`dict`\\[:class:`str`, :class:`str`] | ``None``
            The lobby metadata.

            Supports up to 25 keys, with up to 1024 characters per key and
            value.
        member_metadata: :class:`dict`\\[:class:`str`, :class:`str`] | ``None``
            The member metadata for the lobby.

            Supports up to 25 keys, with up to 1024 characters per key and
            value.
        idle_timeout_seconds: :class:`int`
            The number of seconds to wait before shutting down an idle lobby.

            Must be between 5 and 604800 seconds (7 days).
        flags: :class:`LobbyFlags` | :class:`int`
            The lobby's flags. Either a :class:`LobbyFlags` object or an integer
            representing the bitwise flags.

        Returns
        -------
        :class:`Lobby`
            The joined or created lobby.
        """
        if flags is not utils.NotSet:
            flags_value = flags.value if isinstance(flags, LobbyFlags) else flags
        else:
            flags_value = utils.NotSet

        res = await self.client.http.join_or_create_lobby(
            self.token,
            secret=secret,
            lobby_metadata=lobby_metadata,
            member_metadata=member_metadata,
            idle_timeout_seconds=idle_timeout_seconds,
            flags=flags_value,
        )
        return utils._construct_model(Lobby, data=res, session=self)

    async def leave_lobby(
        self: _AuthorisedSessionProto,
        lobby_id: int | str,
        user_id: int | str,
    ) -> None:
        """Removes the current user from the lobby.

        .. scope:: lobbies.write

        Parameters
        ----------
        lobby_id: :class:`int` | :class:`str`
            The ID of the lobby to leave.
        user_id: :class:`int` | :class:`str`
            The ID of the user to remove as a member.
        """
        await self.client.http.leave_lobby(
            self.token,
            lobby_id=lobby_id,
            user_id=user_id,
        )

    async def create_lobby_invite_for_current_user(
        self: _AuthorisedSessionProto,
        lobby_id: int | str,
    ) -> str:
        """Creates an invite for the current user to a lobby.

        .. scope:: lobbies.write

        Parameters
        ----------
        lobby_id: :class:`int` | :class:`str`
            The ID of the lobby to create an invite for.

        Returns
        -------
        :class:`str`
            The invite code.
        """
        res = await self.client.http.create_lobby_invite_for_current_user(
            self.token,
            lobby_id=lobby_id,
        )
        return res["code"]

    async def edit_lobby_linked_channel(
        self: _AuthorisedSessionProto,
        lobby_id: int | str,
        *,
        channel_id: int | str | None = utils.NotSet,
    ) -> Lobby:
        """Edits the linked channel of a lobby.

        The application must be the creator of the lobby or the member must
        have the ``CAN_LINK_LOBBY`` flag. Requires the ``MANAGE_CHANNELS``
        permission in the target channel.

        .. scope:: lobbies.write

        Parameters
        ----------
        lobby_id: :class:`int` | :class:`str`
            The ID of the lobby to edit the linked channel of.
        channel_id: :class:`int` | :class:`str` | ``None``
            The ID of the channel to link to the lobby, or ``None`` to unlink any linked channel.

        Returns
        -------
        :class:`Lobby`
            The edited lobby.
        """
        res = await self.client.http.edit_lobby_linked_channel(
            self.token,
            lobby_id=lobby_id,
            channel_id=channel_id,
        )
        return utils._construct_model(Lobby, data=res, session=self)

    async def get_lobby_messages(
        self: _AuthorisedSessionProto, lobby_id: int | str, limit: int = 50
    ) -> list[PartialMessage]:
        """Gets messages from a lobby.

        The current user must be a member of the lobby to get its messages.

        .. scope:: lobbies.write

        Parameters
        ----------
        lobby_id: :class:`int` | :class:`str`
            The ID of the lobby to get messages from.
        limit: :class:`int`
            The maximum number of messages to return. Must be between 1 and 100.

        Returns
        -------
        :class:`list`\\[:class:`PartialMessage`]
            The messages from the lobby.
        """
        res = await self.client.http.get_lobby_messages(
            self.token,
            lobby_id=lobby_id,
            limit=limit,
        )
        return [
            utils._construct_model(PartialMessage, data=message, session=self)
            for message in res
        ]

    async def create_lobby_message(
        self: _AuthorisedSessionProto,
        lobby_id: int | str,
        *,
        content: str | None = None,
        tts: bool | None = None,
        nonce: int | str | None = None,
        embeds: list[message_types.EmbedRequest] | None = None,
        allowed_mentions: message_types.AllowedMentionsRequest | None = None,
        message_reference: message_types.MessageReferenceRequest | None = None,
        components: list[component_types.ComponentRequest] | None = None,
        sticker_ids: list[int | str] | None = None,
        flags: int | None = None,
        suppress_embeds: bool | None = None,
        suppress_notifications: bool | None = None,
        voice_message: bool | None = None,
        poll: message_types.PollCreateRequest | None = None,
        shared_client_theme: message_types.SharedClientThemeRequest | None = None,
        metadata: dict[str, object] | None = None,
        files: list[File] | None = None,
    ) -> PartialMessage:
        """Creates a message in a lobby.

        .. scope: lobbies.write

        Parameters
        ----------
        lobby_id: :class:`int` | :class:`str`
            The ID of the lobby to create a message in.
        content: :class:`str` | ``None``
            The content of the message.
        tts: :class:`bool` | ``None``
            Whether the message should be sent as text-to-speech.
        nonce: :class:`int` | :class:`str` | ``None``
            The nonce for the message. Must be a string or integer up to 25 characters in length.
        embeds: :class:`list`\\[:class:`message_types.EmbedRequest`] | ``None``
            The embeds to include in the message. Supports up to 10 embeds.
        allowed_mentions: :class:`message_types.AllowedMentionsRequest` | ``None``
            The allowed mentions for the message.
        message_reference: :class:`message_types.MessageReferenceRequest` | ``None``
            The message reference for the message.
        components: :class:`list`\\[:class:`component_types.ComponentRequest`] | ``None``
            The components to include in the message.
        sticker_ids: :class:`list`\\[:class:`int` | :class:`str`] | ``None``
            The IDs of the stickers to include in the message.
        flags: :class:`int` | ``None``
            The message flags for the message.
        suppress_embeds: :class:`bool` | ``None``
            Whether to suppress embeds for the message.
        suppress_notifications: :class:`bool` | ``None``
            Whether to suppress notifications for the message.
        voice_message: :class:`bool` | ``None``
            Whether the message is a voice message.
        attachments: :class:`list`\\[:class:`message_types.PartialAttachmentRequest`] | ``None``
            The attachments to include in the message.
        poll: :class:`message_types.PollCreateRequest` | ``None``
            The poll data for the message.
        shared_client_theme: :class:`message_types.SharedClientThemeRequest` | ``None``
            The shared client theme data for the message.
        metadata: :class:`dict`\\[:class:`str`, :class:`object`] | ``None``
            The metadata for the message.
            Supports up to 50 keys, with up to 1024 characters per key and value.
        files: :class:`list`\\[:class:`File`] | ``None``
            The files to include in the message. Supports up to 10 files.

        Returns
        -------
        :class:`PartialMessage`
            The created message.
        """
        flags_ = MessageFlags(flags)
        if suppress_embeds is not None:
            if suppress_embeds:
                flags_ |= MessageFlags.suppress_embeds
            else:
                flags_ %= MessageFlags.suppress_embeds
        if suppress_notifications is not None:
            if suppress_notifications:
                flags_ |= MessageFlags.suppress_notifications
            else:
                flags_ %= MessageFlags.suppress_notifications

        if voice_message is not None:
            if voice_message:
                flags_ |= MessageFlags.is_voice_message
            else:
                flags_ %= MessageFlags.is_voice_message

        res = await self.client.http.create_lobby_message(
            self.token,
            lobby_id=lobby_id,
            content=content,
            tts=tts,
            nonce=nonce,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=components,
            sticker_ids=sticker_ids,
            flags=flags_.value if flags_ else None,
            poll=poll,
            shared_client_theme=shared_client_theme,
            metadata=metadata,
            files=files,
        )
        return utils._construct_model(PartialMessage, data=res, session=self)
