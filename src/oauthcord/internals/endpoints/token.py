from __future__ import annotations

from typing import TYPE_CHECKING

from ... import utils
from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import token as token_types


class TokenHTTPClientMixin(BaseHTTPClient):
    TOKEN_URL = "https://discord.com/api/oauth2/token"
    REVOKE_URL = "https://discord.com/api/oauth2/token/revoke"

    async def exchange_token(
        self, code: int | str, *, redirect_uri: str | None
    ) -> token_types.AccessTokenResponse:
        data: token_types.AccessTokenRequest = {
            "grant_type": "authorization_code",
            "code": str(code),
        }
        if redirect_uri is not None:
            data["redirect_uri"] = redirect_uri
        return await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            auth=self._auth,
        )

    async def refresh_token(
        self, refresh_token: utils.ValidRefreshToken
    ) -> token_types.RefreshTokenResponse:
        data: token_types.RefreshTokenRequest = {
            "grant_type": "refresh_token",
            "refresh_token": utils._get_refresh_token(refresh_token),
        }
        return await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            auth=self._auth,
        )

    async def revoke_token(
        self, token: utils.ValidAccessToken | utils.ValidRefreshToken
    ) -> None:
        try:
            token_ = utils._get_access_token(token)  # type: ignore
        except TypeError:
            token_ = utils._get_refresh_token(token)  # type: ignore

        data: token_types.RevokeTokenRequest = {"token": token_}
        return await self.request(
            Route("POST", self.REVOKE_URL),
            data=data,
            auth=self._auth,
        )
