from __future__ import annotations

import urllib.parse
from typing import Self

import aiohttp

from .. import utils
from ..enums import Scope
from ..internals.http import OAuth2HTTPClient
from ..models.access_token import AccessTokenResponse
from ..models.current_auth import CurrentInformation
from ._application import ApplicationClientMixin
from ._channel import ChannelClientMixin
from ._connection import ConnectionClientMixin
from ._guild import GuildClientMixin
from ._invite import InviteClientMixin
from ._lobby import LobbyClientMixin
from ._message import MessageClientMixin
from ._oauth2 import Oauth2ClientMixin
from ._relationship import RelationshipClientMixin
from ._store import StoreClientMixin
from ._user import UserClientMixin


class Client:
    """Discord OAuth2 client.

    This class stores the application credentials required to start the OAuth2
    authorization flow. Use :meth:`get_authorization_url` to build the user
    authorization URL, then call :meth:`exchange_token` with the returned code
    to create an :class:`AuthorisedSession`.

    Parameters
    ----------
    client_id: :class:`int` | :class:`str`
        Discord application client ID.
    client_secret: :class:`str`
        Discord application client secret.
    redirect_uri: :class:`str`
        Redirect URI configured for the application.
    scopes: :class:`list`[:class:`Scope` | :class:`str`]
        OAuth2 scopes to request during authorization.
    state: :class:`str` | :data:`None`
        Optional state value to include in the authorization URL.
    session: :class:`aiohttp.ClientSession`
        Existing HTTP session to reuse for API requests.

    Attributes
    ----------
    http: :class:`OAuth2HTTPClient`
        Internal HTTP client used by the library.
    """

    __slots__ = ("_redirect_uri", "_scopes", "_state", "http")

    def __init__(
        self,
        *,
        client_id: int | str,
        client_secret: str,
        redirect_uri: str,
        scopes: list[Scope | str],
        state: str | None = None,
        session: aiohttp.ClientSession = utils.NotSet,
    ) -> None:
        self.http: OAuth2HTTPClient = OAuth2HTTPClient(
            self,
            client_id=int(client_id),
            client_secret=client_secret,
            session=session,
        )

        if not isinstance(scopes, list):
            raise ValueError("scopes must be a list of Scope or str")

        try:
            parsed_scopes = [Scope(scope) for scope in scopes]
        except ValueError as exc:
            raise ValueError("scopes must be a list of valid Scope values") from exc

        self._scopes: list[Scope] = parsed_scopes
        self._redirect_uri: str = redirect_uri
        self._state: str | None = state

    def get_authorization_url(
        self,
    ) -> str:
        """Build the Discord OAuth2 authorization URL.

        Returns
        -------
        :class:`str`
            Authorization URL containing the configured redirect URI, scopes,
            and optional state value.
        """
        params = {
            "client_id": str(self.http.client_id),
            "response_type": "code",
            "redirect_uri": self._redirect_uri,
            "scope": "+".join(scope.value for scope in self._scopes),
        }
        if self._state:
            params["state"] = self._state

        url = urllib.parse.urljoin(self.http.BASE_URL, "/oauth2/authorize?")
        url += urllib.parse.urlencode(params)
        return url

    async def exchange_token(
        self,
        code: str,
    ) -> AuthorisedSession:
        """Exchange an authorization code for an authorised session.

        Parameters
        ----------
        code: :class:`str`
            Authorization code returned by Discord.

        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the exchanged access token.
        """
        res = await self.http.exchange_token(code, redirect_uri=self._redirect_uri)
        res = utils._construct_model(AccessTokenResponse, data=res, http=self.http)
        return AuthorisedSession(self, token=res)


class AuthorisedSession(
    ApplicationClientMixin,
    ChannelClientMixin,
    ConnectionClientMixin,
    GuildClientMixin,
    InviteClientMixin,
    LobbyClientMixin,
    MessageClientMixin,
    Oauth2ClientMixin,
    RelationshipClientMixin,
    StoreClientMixin,
    UserClientMixin,
):
    """Authenticated Discord OAuth2 session.

    Instances are returned by :meth:`Client.exchange_token`.

    Attributes
    ----------
    client: :class:`Client`
        Parent OAuth2 client that created the session.
    token: :class:`AccessTokenResponse`
        Current access token data for the session.
    """

    def __init__(
        self,
        client: Client,
        *,
        token: AccessTokenResponse,
    ) -> None:
        self.client: Client = client
        self.token: AccessTokenResponse = token

        self._current_authorization_information: CurrentInformation | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass

    @property
    def current_authorization_information(self) -> CurrentInformation | None:
        """Current authorization information for the session.

        Returns
        -------
        :class:`CurrentInformation` | :data:`None`
            Cached authorization information for the current token, if it has
            been loaded.
        """
        return self._current_authorization_information

    @current_authorization_information.setter
    def current_authorization_information(self, value: CurrentInformation) -> None:
        if not isinstance(value, CurrentInformation):
            raise TypeError(
                "current_authorization_information must be of type CurrentInformation"
            )

        self._current_authorization_information = value

    async def refresh(
        self,
        *,
        check_expired: bool = False,
    ) -> AccessTokenResponse:
        """Refresh the current access token.

        Parameters
        ----------
        check_expired: :class:`bool`
            Whether to refresh only when the token is expired.

        Returns
        -------
        :class:`AccessTokenResponse`
            Updated token data after the refresh request completes.
        """
        token = await self.token.refresh(check_expired=check_expired)
        self.current_authorization_information = (
            await self.get_current_authorization_information()
        )
        return token

    async def revoke(
        self,
    ) -> None:
        """Revoke the current access token.

        Revoking clears cached authorization information for this session. Any
        application tokens invalidated by Discord must be re-authorized through
        the OAuth2 flow before the session can be used again.
        """
        await self.token.revoke()
        self._current_authorization_information = None
