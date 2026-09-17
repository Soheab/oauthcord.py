from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import channels
    from .base import ValidAccessToken


class ChannelHTTPClientMixin(BaseHTTPClient):
    async def get_dm_channel(
        self,
        token: ValidAccessToken,
        *,
        user_id: int | str,
    ) -> channels.DMChannelResponse:
        return await self.request(
            Route("GET", "/users/@me/dms/{user_id}", user_id=user_id),
            token=token,
        )

    async def create_private_channel(
        self,
        token: ValidAccessToken,
        *,
        recipients: list[int | str] | None = None,
        nicks: dict[str | int, str] | None = None,
    ) -> channels.PrivateChannelResponse:
        data: channels.CreatePrivateChannelRequest = {}
        if recipients is not None:
            data["recipients"] = recipients
        if nicks is not None:
            data["nicks"] = nicks

        return await self.request(
            Route("POST", "/users/@me/channels"),
            token=token,
            json=data,
        )

    async def get_guild_channels(
        self,
        token: ValidAccessToken,
        *,
        guild_id: str | int,
        permissions: bool = False,
        with_can_link_lobby: bool = False,
    ) -> list[channels.GuildChannelResponse]:
        return await self.request(
            Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id),
            token=token,
            params={
                "permissions": int(permissions),
                "with_can_link_lobby": int(with_can_link_lobby),
            },
        )

    async def get_call_eligibility(
        self, token: ValidAccessToken, *, channel_id: int | str
    ) -> channels.CallEligibilityResponse:
        return await self.request(
            Route("GET", "/channels/{channel_id}/call", channel_id=channel_id),
            token=token,
        )

    async def ring_channel_recipients(
        self,
        token: ValidAccessToken,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        data: channels.RingChannelRecipientsRequest = {}
        if recipients is not None:
            data["recipients"] = recipients

        await self.request(
            Route("POST", "/channels/{channel_id}/call/ring", channel_id=channel_id),
            token=token,
            json=data,
        )

    async def stop_ringing_channel_recipients(
        self,
        token: ValidAccessToken,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        data: dict[str, Any] = {}
        if recipients is not None:
            data["recipients"] = recipients

        await self.request(
            Route(
                "POST",
                "/channels/{channel_id}/call/stop-ringing",
                channel_id=channel_id,
            ),
            token=token,
            json=data,
        )

    async def get_channel_linked_accounts(
        self,
        token: ValidAccessToken,
        *,
        channel_id: int | str,
        user_ids: list[int | str] | None = None,
    ) -> channels.GetChannelLinkedAccountsResponse:
        params: channels.GetChannelLinkedAccountsRequest = {}
        if user_ids is not None:
            params["user_ids"] = user_ids

        return await self.request(
            Route(
                "GET", "/channels/{channel_id}/linked-accounts", channel_id=channel_id
            ),
            token=token,
            params=params,
        )
