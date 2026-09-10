from __future__ import annotations

from typing import TYPE_CHECKING

from ... import utils
from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import token as token_types


class TokenHTTPClientMixin(BaseHTTPClient):
    TOKEN_URL = "https://discord.com/api/oauth2/token"
    REVOKE_URL = "https://discord.com/api/oauth2/token/revoke"
    DEVICE_CODE_AUTH_URL = "https://discord.com/api/oauth2/device/authorize"

    async def get_token(
        self,
        *,
        scopes: list[str] | None = None,
    ) -> token_types.ClientCredentialsResponse:
        data: token_types.ClientCredentialsRequest = {
            "grant_type": "client_credentials",
        }
        if scopes is not None:
            data["scope"] = " ".join(scopes)

        return await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=self._auth,
        )

    async def exchange_token(
        self,
        code: int | str,
        *,
        redirect_uri: str | None,
        code_verifier: str | None = None,
    ) -> token_types.AccessTokenResponse:
        data: token_types.AccessTokenRequest = {
            "grant_type": "authorization_code",
            "code": str(code),
        }
        if redirect_uri is not None:
            data["redirect_uri"] = redirect_uri
        if code_verifier is not None:
            data["code_verifier"] = code_verifier
            data["client_id"] = str(self.client_id)  # type: ignore # Add client_id for PKCE flow

        return await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=self._auth
            if code_verifier is None
            else None,  # Omit auth if using PKCE
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
            headers={"Content-Type": "application/x-www-form-urlencoded"},
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

    async def get_device_code(
        self, *, scopes: list[str] | None = None
    ) -> token_types.DeviceCodeResponse:
        data: token_types.DeviceCodeRequest = {
            "scope": " ".join(scopes) if scopes is not None else "",
        }
        return await self.request(
            Route("POST", self.DEVICE_CODE_AUTH_URL),
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=self._auth,
        )

    async def exchange_device_code(
        self, device_code: str
    ) -> token_types.DeviceCodeExchangeResponse:
        data: token_types.DeviceCodeExchangeRequest = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
        }
        return await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=self._auth,
        )
