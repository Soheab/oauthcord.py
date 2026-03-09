from typing import TYPE_CHECKING

from ....utils import NotSet
from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from ...file import File
    from .._types import (
        components as component_types,
    )
    from .._types import (
        lobby as lobby_types,
    )
    from .._types import (
        message as message_types,
    )
    from .base import ValidToken


class LobbyHTTPClientMixin(BaseHTTPClient):
    async def join_or_create_lobby(
        self,
        token: ValidToken,
        *,
        secret: str,
        lobby_metadata: dict[str, str] | None = None,
        member_metadata: dict[str, str] | None = None,
        idle_timeout_seconds: int | None = None,
        flags: int | None = None,
    ) -> lobby_types.JoinOrCreateLobbyResponse:
        data: lobby_types.JoinOrCreateLobbyRequest = {"secret": secret}
        if lobby_metadata is not None:
            data["lobby_metadata"] = lobby_metadata
        if member_metadata is not None:
            data["member_metadata"] = member_metadata
        if idle_timeout_seconds is not None:
            data["idle_timeout_seconds"] = idle_timeout_seconds
        if flags is not None:
            data["flags"] = flags

        return await self.request(
            Route("PUT", "/lobbies"),
            token=token,
            json=data,
        )

    async def leave_lobby(
        self,
        token: ValidToken,
        *,
        lobby_id: int | str,
    ) -> None:
        await self.request(
            Route("DELETE", f"/lobbies/{lobby_id}/members/@me"),
            token=token,
        )

    async def create_lobby_invite_for_current_user(
        self,
        token: ValidToken,
        *,
        lobby_id: int | str,
    ) -> lobby_types.CreateLobbyInviteResponse:
        return await self.request(
            Route("POST", f"/lobbies/{lobby_id}/members/@me/invites"),
            token=token,
        )

    async def edit_lobby_linked_channel(
        self,
        token: ValidToken,
        *,
        lobby_id: int | str,
        channel_id: int | str | None = NotSet,
    ) -> lobby_types.ModifyLobbyLinkedChannelResponse:
        data: lobby_types.ModifyLobbyLinkedChannelRequest = {}
        if channel_id is not NotSet:
            data["channel_id"] = channel_id

        return await self.request(
            Route("PATCH", f"/lobbies/{lobby_id}/channel-linking"),
            token=token,
            json=data,
        )

    async def get_lobby_messages(
        self,
        token: ValidToken,
        *,
        lobby_id: int | str,
        limit: int | None = None,
    ) -> lobby_types.GetLobbyMessagesResponse:
        params: lobby_types.GetLobbyMessagesRequest = {}
        if limit is not None:
            params["limit"] = limit

        return await self.request(
            Route("GET", f"/lobbies/{lobby_id}/messages"),
            token=token,
            params=params,
        )

    async def create_lobby_message(
        self,
        token: ValidToken,
        *,
        lobby_id: int | str,
        content: str | None = None,
        tts: bool | None = None,
        nonce: int | str | None = None,
        embeds: list[message_types.EmbedRequest] | None = None,
        allowed_mentions: message_types.AllowedMentionsRequest | None = None,
        message_reference: message_types.MessageReferenceRequest | None = None,
        components: list[component_types.ComponentRequest] | None = None,
        sticker_ids: list[int | str] | None = None,
        activity: message_types.MessageActivityRequest | None = None,
        application_id: int | str | None = None,
        flags: int | None = None,
        attachments: list[message_types.PartialAttachmentRequest] | None = None,
        poll: dict[str, object] | None = None,
        shared_client_theme: message_types.SharedClientThemeRequest | None = None,
        metadata: dict[str, object] | None = None,
        files: list[File] | None = None,
    ) -> lobby_types.CreateLobbyMessageResponse:
        from ..http import get_message_create_payload

        kwargs = get_message_create_payload(
            content=content,
            tts=tts,
            nonce=nonce,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=components,
            sticker_ids=sticker_ids,
            attachments=attachments,
            flags=flags,
            metadata=metadata,
            files=files,
            activity=activity,
            application_id=application_id,
            poll=poll,
            shared_client_theme=shared_client_theme,
        )

        return await self.request(
            Route("POST", f"/lobbies/{lobby_id}/messages"),
            token=token,
            **kwargs,
        )
