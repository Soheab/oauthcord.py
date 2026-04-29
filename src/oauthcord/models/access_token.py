from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Self, override

from .. import utils
from ..enums import Scope
from ._base import BaseModelWithHTTP

if TYPE_CHECKING:
    from ..client import AuthorisedSession, Client
    from ..internals._types.token import (
        AccessTokenResponse as AccessTokenResponsePayload,
    )
    from ..internals._types.token import (
        RefreshTokenResponse as RefreshTokenResponsePayload,
    )


__all__ = ("AccessToken",)


class AccessToken(
    BaseModelWithHTTP[
        "AccessTokenResponsePayload | RefreshTokenResponsePayload",
        "AccessTokenResponsePayload | RefreshTokenResponsePayload",
    ]
):
    """Represents an OAuth2 access token from Discord.

    Attributes
    ----------
    token_type: :class:`str`
        The type of the token, typically "Bearer".
    access_token: :class:`str`
        The access token string used for authorization.
    refresh_token: :class:`str`
        The refresh token string used to obtain new access tokens.
    """

    __slots__ = (
        *BaseModelWithHTTP.__slots__,
        "token_type",
        "access_token",
        "refresh_token",
        "_scope",
        "_expires_in",
    )

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
    @override
    def from_dict(  # type: ignore
        cls,
        client: Client | AuthorisedSession,
        data: AccessTokenResponsePayload | RefreshTokenResponsePayload,
    ) -> AccessToken:
        """Create an AccessToken instance from a dictionary payload.

        Parameters
        ----------
        client: :class:`Client` | :class:`AuthorisedSession`
            The client or authorised session to get the HTTP client from.
        data: :class:`dict`
            The raw access token response data as returned by Discord.

        Returns
        -------
        :class:`AccessToken`
            The initialized AccessToken instance.
        """
        instance = utils._construct_model(cls, data=data, http=client.http)
        return instance

    @override
    def to_dict(self) -> AccessTokenResponsePayload | RefreshTokenResponsePayload:
        return {
            "token_type": self.token_type,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "scope": self._scope,
            "expires_in": self._expires_in,
        }

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
    def scopes(self) -> list[Scope]:
        """:class:`list[Scope]`: The list of scopes associated with this token, parsed
        from the `scope` string.
        """
        return Scope.from_list(self._scope.split())

    @property
    def scope(self) -> str:
        """:class:`str`: The raw OAuth scope string as returned by Discord."""
        return self._scope

    def _update(
        self, data: AccessTokenResponsePayload | RefreshTokenResponsePayload
    ) -> Self:
        self._initialize(data)
        return self

    async def refresh(self, *, check_expired: bool = False) -> AccessToken:
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
        :class:`AccessToken`
            The new access token response obtained from refreshing.
        """
        if not self.refresh_token:
            raise ValueError("Cannot refresh token without a refresh token.")

        if check_expired and not self.is_expired():
            return self

        res = await self._http.refresh_token(self)
        return self._update(res)

    async def revoke(self) -> None:
        """Revoke this token.

        .. note::

            This will revoke all access and refresh tokens associated with the current authorization.
        """
        await self._http.revoke_token(self)
