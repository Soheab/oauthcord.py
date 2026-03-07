from typing import TYPE_CHECKING, Any

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import channels
    from .base import ValidToken


class ChannelHTTPClientMixin(BaseHTTPClient):
    async def get_dm_channel(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int | str,
    ) -> channels.DMChannelResponse:
        return await self.request(
            Route("GET", f"/users/@me/dms/{user_id}"),
            token=token,
        )

    async def create_private_channel(
        self,
        token: ValidToken | None = None,
        *,
        recipients: list[int | str] | None = None,
        access_tokens: list[ValidToken] | None = None,
        nicks: dict[str | int, str] | None = None,
    ) -> channels.PrivateChannelResponse:
        current_access_token = (await self._get_current_token(token)).access_token

        data: channels.CreatePrivateChannelRequest = {}
        if recipients is not None:
            data["recipients"] = recipients
        if access_tokens is not None:
            data["access_tokens"] = [
                self._parse_token(token) for token in access_tokens
            ] + [current_access_token]
        if nicks is not None:
            data["nicks"] = nicks

        return await self.request(
            Route("POST", "/users/@me/channels"),
            token=token,
            json=data,
        )

    async def get_guild_channels(
        self,
        token: ValidToken | None = None,
        *,
        guild_id: str | int,
        permissions: bool = False,
    ) -> list[channels.GuildChannelResponse]:
        return await self.request(
            Route("GET", f"/guilds/{guild_id}/channels"),
            token=token,
            params={"permissions": int(permissions)},
        )

    async def get_call_eligibility(
        self, token: ValidToken | None = None, *, channel_id: int | str
    ) -> channels.CallEligibilityResponse:
        return await self.request(
            Route("GET", f"/channels/{channel_id}/call"),
            token=token,
        )

    async def ring_channel_recipients(
        self,
        token: ValidToken | None = None,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        data: channels.RingChannelRecipientsRequest = {}
        if recipients is not None:
            data["recipients"] = recipients

        await self.request(
            Route("POST", f"/channels/{channel_id}/call/ring"),
            token=token,
            json=data,
        )

    async def stop_ringing_channel_recipients(
        self,
        token: ValidToken | None = None,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        data: dict[str, Any] = {}
        if recipients is not None:
            data["recipients"] = recipients

        await self.request(
            Route("POST", f"/channels/{channel_id}/call/stop-ringing"),
            token=token,
            json=data,
        )

    async def get_channel_linked_accounts(
        self,
        token: ValidToken | None = None,
        *,
        channel_id: int | str,
        user_ids: list[int | str] | None = None,
    ) -> channels.GetChannelLinkedAccountsResponse:
        params: channels.GetChannelLinkedAccountsRequest = {}
        if user_ids is not None:
            params["user_ids"] = user_ids

        return await self.request(
            Route("GET", f"/channels/{channel_id}/linked-accounts"),
            token=token,
            params=params,
        )
