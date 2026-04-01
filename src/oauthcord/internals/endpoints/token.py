from typing import TYPE_CHECKING

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import token as token_types
    from .base import ValidToken


class TokenHTTPClientMixin(BaseHTTPClient):
    TOKEN_URL = "https://discord.com/api/oauth2/token"
    REVOKE_URL = "https://discord.com/api/oauth2/token/revoke"

    async def exchange_token(
        self, code: int | str, *, redirect_uri: str
    ) -> token_types.AccessTokenResponse:
        data: token_types.AccessTokenRequest = {
            "grant_type": "authorization_code",
            "code": str(code),
            "redirect_uri": redirect_uri,
        }
        return await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            auth=self._auth,
        )

    async def refresh_token(
        self, refresh_token: ValidToken
    ) -> token_types.RefreshTokenResponse:
        data: token_types.RefreshTokenRequest = {
            "grant_type": "refresh_token",
            "refresh_token": self._parse_token(refresh_token, refresh=True),
        }
        return await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            auth=self._auth,
        )

    async def revoke_token(self, token: ValidToken) -> None:
        data: token_types.RevokeTokenRequest = {"token": self._parse_token(token)}
        return await self.request(
            Route("POST", self.REVOKE_URL),
            data=data,
            auth=self._auth,
        )
