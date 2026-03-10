import datetime
from typing import TYPE_CHECKING, override

from ._base import BaseModel
from .enums import Scope

if TYPE_CHECKING:
    from .internals._types.token import (
        AccessTokenResponse as AccessTokenResponsePayload,
    )
    from .internals._types.token import (
        RefreshTokenResponse as RefreshTokenResponsePayload,
    )


__all__ = ("AccessTokenResponse",)


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

    __slots__ = ("_expires_in", "_scope", "access_token", "refresh_token", "token_type")

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
        """Refresh this token.

        This invalidates the current token and returns a new one.

        Parameters
        ----------
        check_expired: :class:`bool`
            If ``True``, this method will raise a :class:`ValueError` if the token
            is not expired yet. By default, this is ``False`` and the token will be
            refreshed regardless of its expiration status.

        Returns
        -------
        :class:`AccessTokenResponse`
            The new access token response obtained from refreshing.
        """
        if not self.refresh_token:
            raise ValueError("Cannot refresh token without a refresh token.")

        if check_exired and not self.is_expired():
            raise ValueError("Token is not expired yet.")

        res = await self._http.refresh_token(self)
        return self.__class__(http=self._http, data=res)

    async def revoke(self) -> None:
        """Revoke this token. This will invalidate the token and it can no longer be used for authorization."""
        await self._http.revoke_token(self)
