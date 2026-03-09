from typing import TYPE_CHECKING

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from ...file import File
    from .._types import components as component_types
    from .._types import message as message_types
    from .base import ValidToken


class MessageHTTPClientMixin(BaseHTTPClient):
    async def edit_dm_message(
        self,
        token: ValidToken,
        *,
        user_id: int | str,
        message_id: int | str,
        content: str | None = None,
    ) -> message_types.EditDMMessageResponse:
        data: message_types.EditDMMessageRequest = {}
        if content is not None:
            data["content"] = content

        return await self.request(
            Route("PATCH", f"/users/{user_id}/messages/{message_id}"),
            token=token,
            json=data,
        )

    async def delete_dm_message(
        self,
        token: ValidToken,
        *,
        user_id: int | str,
        message_id: int | str,
    ) -> None:
        return await self.request(
            Route("DELETE", f"/users/{user_id}/messages/{message_id}"),
            token=token,
        )

    async def get_dm_messages(
        self,
        token: ValidToken,
        *,
        user_id: int | str,
        limit: int | None = None,
    ) -> message_types.GetDMMessagesResponse:
        params: message_types.GetDMMessagesRequest = {}
        if limit is not None:
            params["limit"] = limit

        return await self.request(
            Route("GET", f"/users/{user_id}/messages"),
            token=token,
            params=params,
        )

    async def create_dm_message(
        self,
        token: ValidToken,
        *,
        user_id: int | str,
        content: str | None = None,
        tts: bool | None = None,
        nonce: int | str | None = None,
        embeds: list[message_types.EmbedRequest] | None = None,
        allowed_mentions: message_types.AllowedMentionsRequest | None = None,
        message_reference: message_types.MessageReferenceRequest | None = None,
        components: list[component_types.ComponentRequest] | None = None,
        sticker_ids: list[int | str] | None = None,
        attachments: list[message_types.PartialAttachmentRequest] | None = None,
        flags: int | None = None,
        metadata: dict[str, object] | None = None,
        files: list[File] | None = None,
    ) -> message_types.CreateDMMessageResponse:
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
        )

        return await self.request(
            Route("POST", f"/users/{user_id}/messages"),
            token=token,
            **kwargs,
        )
