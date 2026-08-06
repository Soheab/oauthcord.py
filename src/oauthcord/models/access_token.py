from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Self, override

from .. import utils
from ..enums import Scope
from ._base import BaseModelWithHTTP

if TYPE_CHECKING:
    from ..client import AuthorisedSession, Client
    from ..enums import UnknownScope
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
        "_created_at",
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

        self._created_at: datetime.datetime = datetime.datetime.now(datetime.UTC)

    @classmethod
    @override
    def from_dict(  # type: ignore
        cls,
        client: Client | AuthorisedSession,
        data: AccessTokenResponsePayload | RefreshTokenResponsePayload,
        *,
        created_at: datetime.datetime | None = None,
    ) -> AccessToken:
        """Create an AccessToken instance from a dictionary payload.

        Parameters
        ----------
        client: :class:`Client` | :class:`AuthorisedSession`
            The client or authorised session to get the HTTP client from.
        data: :class:`dict`
            The raw access token response data as returned by Discord.
        created_at: :class:`datetime.datetime` | None
            The time when the token was created. If not provided, it will default to the current time.

            See :attr:`created_at` for more information.

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

    @property
    def expires_in(self) -> int:
        """:class:`int`: The number of seconds until the token expires."""
        return self._expires_in

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: When this object was created, representing when the token was obtained.

        This is used to calculate the expiration time of the token.
        This is also reset when the token is refreshed, so it always represents the time of the most recent token.

        This will NOT be accurate if you manually create an AccessToken instance using :meth:`from_dict` without
        specifying the `created_at` parameter, or :meth:`__init__`,  as it will be set to the current
        time at the moment of creation.

        This will be accurate if this object was received via :attr:`AuthorisedSession.token` as
        :meth:`AuthorisedSession.from_dict` will fetch the current authorization information and set this value to the
        correct time.
        """
        return self._created_at

    @property
    def expires_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: When the token expires.

        This is calculated by adding the :attr:`expires_in` value to :attr:`created_at`.
        """
        return self._created_at + datetime.timedelta(seconds=self._expires_in)

    @property
    def is_expired(self) -> bool:
        """:class:`bool`: Whether the token is expired based on the current time
        and the :attr:`expires_at` value.
        """
        return self.expires_at <= datetime.datetime.now(datetime.UTC)

    @property
    def scopes(self) -> list[Scope | UnknownScope]:
        """:class:`list[Scope | UnknownScope]`: The list of scopes associated with this token, parsed
        from the :attr:`scope` string.
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
