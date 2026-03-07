from typing import TYPE_CHECKING

from ... import Scope
from .base import Route
from .current_auth import CurrentAuthHTTPClientMixin

if TYPE_CHECKING:
    from .._types import token as token_types
    from .base import ValidToken


class TokenHTTPClientMixin(CurrentAuthHTTPClientMixin):
    TOKEN_URL = "https://discord.com/api/oauth2/token"
    REVOKE_URL = "https://discord.com/api/oauth2/token/revoke"

    async def get_token(self, code: int | str) -> token_types.AccessTokenResponse:
        from ...access_token import AccessTokenResponse

        data: token_types.AccessTokenRequest = {
            "grant_type": "authorization_code",
            "code": str(code),
            "redirect_uri": self.redirect_uri,
        }
        res = await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            auth=self._auth,
            include_token=False,
        )

        inst = AccessTokenResponse._from_cheap(http=self, data=res)  # pyright: ignore[reportArgumentType]

        self._store_token_if_needed(inst)

        current_auth_info = await self.get_current_authorization_information(
            res["access_token"]
        )
        self.current_scopes = Scope.from_list(current_auth_info["scopes"])
        return res

    async def refresh_token(
        self, refresh_token: ValidToken | None = None
    ) -> token_types.RefreshTokenResponse:
        data: token_types.RefreshTokenRequest = {
            "grant_type": "refresh_token",
            "refresh_token": (
                await self._get_current_token(
                    refresh_token, refresh=False, for_refresh=True
                )
            ).refresh_token,
        }
        return await self.request(
            Route("POST", self.TOKEN_URL),
            data=data,
            auth=self._auth,
            include_token=False,
        )

    async def revoke_token(self, token: ValidToken | None = None) -> None:
        data: token_types.RevokeTokenRequest = {
            "token": (await self._get_current_token(token, refresh=False)).access_token,
        }
        return await self.request(
            Route("POST", self.REVOKE_URL),
            data=data,
            auth=self._auth,
            include_token=False,
        )
