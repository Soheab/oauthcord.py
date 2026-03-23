from typing import TYPE_CHECKING

from .. import utils
from ..models.flags import MessageFlags
from ..models.message import Message, PartialMessage

if TYPE_CHECKING:
    from ..internals._types import (
        components as component_types,
    )
    from ..internals._types import (
        message as message_types,
    )
    from ..models.file import File
    from ._base import _AuthorisedSessionProto


class MessageClient:
    async def get_dm_messages(
        self: _AuthorisedSessionProto,
        *,
        user_id: int | str,
        limit: int = 50,
    ) -> list[PartialMessage]:
        """Get a list of messages in the DM channel with an user.

        .. note::
            This has the following limitations:

            1. A DM channel must already exist with the user and the recipient.
            2. Both users must have authorized the applcation for messages history to be accessible.
            3. Only a maximum of 200 messages and up to 32 hours of history can be retrieved.

        .. scope:: dm_channels.messages.read

        Parameters
        ----------
        user_id: :class:`int` | :class:`str`
            The ID of the user to retrieve messages from.
        limit: :class:`int`
            The maximum number of messages to return. Can be between 1 and 200. Defaults to 50.
        """
        res = await self.client.http.get_dm_messages(
            self.token,
            user_id=user_id,
            limit=limit,
        )
        return [
            utils._construct_model(PartialMessage, data=message, session=self)
            for message in res
        ]

    async def create_dm_message(
        self: _AuthorisedSessionProto,
        user_id: int | str,
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
    ) -> Message:
        """Send a message to an user.

        .. note::
            A message can be sent between two users in the following situations:
            - Both users must be online and have a presence corresponding to the OAuth2 application.
            - Both users must be friends with each other.
            - Both users must share a mutual guild with DMs allowed and have previously DM'd each other on Discord.

        .. scope: dm_channels.messages.write

        Parameters
        ----------
        user_id: :class:`int` | :class:`str`
            The ID of the user to send the message to.
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
        :class:`Message`
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

        res = await self.client.http.create_dm_message(
            self.token,
            user_id=user_id,
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
        return utils._construct_model(Message, data=res, session=self)

    async def edit_dm_message(
        self: _AuthorisedSessionProto,
        user_id: int | str,
        message_id: int | str,
        *,
        content: str | None = None,
    ) -> Message:
        """Edit a message in the DM channel with an user.

        .. scope:: dm_channels.messages.write

        Parameters
        ----------
        user_id: :class:`int` | :class:`str`
            The ID of the user to edit the message with.
        message_id: :class:`int` | :class:`str`
            The ID of the message to edit.
        content: :class:`str` | ``None``
            The new content of the message.
        """
        res = await self.client.http.edit_dm_message(
            self.token,
            user_id=user_id,
            message_id=message_id,
            content=content,
        )
        return utils._construct_model(Message, data=res, session=self)

    async def delete_dm_message(
        self: _AuthorisedSessionProto,
        user_id: int | str,
        message_id: int | str,
    ) -> None:
        """Delete a message in the DM channel with an user.

        .. scope:: dm_channels.messages.write

        Parameters
        ----------
        user_id: :class:`int` | :class:`str`
            The ID of the user to delete the message with.
        message_id: :class:`int` | :class:`str`
            The ID of the message to delete.
        """
        await self.client.http.delete_dm_message(
            self.token,
            user_id=user_id,
            message_id=message_id,
        )
