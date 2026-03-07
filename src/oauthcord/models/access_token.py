import datetime
from typing import TYPE_CHECKING, Self, override

from ._base import BaseModel
from .enums import Scope

if TYPE_CHECKING:
    from .internals._types.token import (
        AccessTokenResponse as AccessTokenResponsePayload,
    )
    from .internals._types.token import (
        RefreshTokenResponse as RefreshTokenResponsePayload,
    )
    from .internals.endpoints.base import (
        AccessTokenAttr,
        RefreshTokenAttr,
        RefreshTokenDict,
        RestTokenAttrs,
        TokenDict,
    )
    from .internals.http import OAuth2HTTPClient


__all__ = ("AccessTokenResponse",)


@BaseModel.add_slots(
    "token_type", "access_token", "refresh_token", "_scope", "_expires_in"
)
class AccessTokenResponse(
    BaseModel["AccessTokenResponsePayload | RefreshTokenResponsePayload"]
):
    """Represents an OAuth2 access token response from Discord.

    Attributes
    ----------
    token_type: :class:`str`
        The type of the token, typically "Bearer".
    access_token: :class:`str`
        The access token string used for authorization.
    refresh_token: :class:`str`
        The refresh token string used to obtain new access tokens.
    """

    @override
    def _initialize(
        self,
        data: AccessTokenResponsePayload | RefreshTokenResponsePayload,
    ) -> None:
        self.token_type: str = data["token_type"]
        self.access_token: str = data["access_token"]
        self.refresh_token: str = data["refresh_token"]
        self._scope: str = data["scope"]
        self._expires_in: int = data["expires_in"]

    @classmethod
    def _from_cheap(
        cls,
        *,
        http: OAuth2HTTPClient,
        data: Self
        | str
        | AccessTokenAttr
        | RestTokenAttrs
        | TokenDict
        | RefreshTokenDict
        | RefreshTokenAttr,
        for_refresh: bool = False,
    ) -> Self:
        if isinstance(data, AccessTokenResponse):
            return data  # type: ignore

        if isinstance(data, str):
            return cls._from_str(http, data, is_refresh=for_refresh)

        token_type = (
            getattr(data, "token_type", None) or data.get("token_type", "Bearer")
            if isinstance(data, dict)
            else getattr(data, "token_type", "Bearer")
        )
        access_token = (
            getattr(data, "access_token", None)
            if not isinstance(data, dict)
            else data.get("access_token")
        )
        refresh_token = (
            getattr(data, "refresh_token", None)
            if not isinstance(data, dict)
            else data.get("refresh_token")
        )
        scope = (
            (getattr(data, "_scope", None) or getattr(data, "scope", None))
            if not isinstance(data, dict)
            else data.get("scope", "")
        )
        expires_at = (
            (getattr(data, "expires_at", None) or getattr(data, "_expires_in", None))
            if not isinstance(data, dict)
            else data.get("expires_at") or data.get("_expires_in")
        )

        if not for_refresh and access_token is None:
            raise ValueError("Access token is required to create AccessTokenResponse.")

        if for_refresh and refresh_token is None:
            raise ValueError(
                "Refresh token is required to create AccessTokenResponse for refresh."
            )

        if expires_at is not None:
            now = datetime.datetime.now(datetime.UTC)
            expires_in = max(0, int(expires_at - now.timestamp()))
        else:
            expires_in = 0

        payload: AccessTokenResponsePayload = {
            "token_type": token_type,
            "access_token": access_token or "",
            "refresh_token": refresh_token or "",
            "scope": scope or "",
            "expires_in": expires_in,
        }
        return cls(http=http, data=payload)

    @classmethod
    def _from_str(
        cls, http: OAuth2HTTPClient, token: str, is_refresh: bool = False
    ) -> Self:
        if not token:
            raise ValueError("Token string cannot be empty.")

        payload = {
            "token_type": "Bearer",
            "access_token": token if not is_refresh else "",
            "refresh_token": token if is_refresh else "",
            "scope": "",
            "expires_in": 0,
        }
        return cls(http=http, data=payload)  # type: ignore

    def expires_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: When the token expires, calculated from
        the current time and the `expires_in` value.
        """
        return datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            seconds=self._expires_in
        )

    def is_expired(self) -> bool:
        """:class:`bool`: Whether the token is expired based on the current time
        and the `expires_at` value.
        """
        return self.expires_at() <= datetime.datetime.now(datetime.UTC)

    @property
    def token_with_type(self) -> str:
        """:class:`str`: The full token string including the token type, formatted as
        "{token_type} {access_token}".
        """
        return f"{self.token_type} {self.access_token}"

    @property
    def scopes(self) -> list[Scope]:
        """:class:`list[Scope]`: The list of scopes associated with this token, parsed
        from the `scope` string.
        """
        return Scope.from_list(self._scope.split())

    @property
    def scope(self) -> str:
        """:class:`str`: The raw OAuth scope string as returned by Discord."""
        return self._scope

    async def refresh(self, *, check_exired: bool = False) -> AccessTokenResponse:
        """:class:`AccessTokenResponse`: Refresh this token.

        This invalidates the current token and returns a new one.

        Parameters
        ----------
        check_expired: :class:`bool`
            If ``True``, this method will raise a :class:`ValueError` if the token
            is not expired yet. By default, this is ``False`` and the token will be
            refreshed regardless of its expiration status.
        """
        if not self.refresh_token:
            raise ValueError("Cannot refresh token without a refresh token.")

        if check_exired and not self.is_expired():
            raise ValueError("Token is not expired yet.")

        res = await self._http.refresh_token(self)
        inst = self.__class__(http=self._http, data=res)
        self._http._store_token_if_needed(inst)
        return inst

    async def revoke(self) -> None:
        """ "Revoke this token. This will invalidate the token and it can no longer be used for authorization."""
        await self._http.revoke_token(self)
        self._http.token = None
