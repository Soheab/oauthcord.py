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
    """Represents an OAuth2 client for Discord. This is the main entry point for using the library.

    Use :meth:`get_authorization_url` to get the URL to redirect users to for authorizing your application, then
    use :meth:`exchange_token` to exchange the temporary authorization code for an access token, which is used to
    create an :class:`AuthorisedSession` that can make authenticated requests to the Discord API.

    This class takes the base information needed to perform the OAuth2 flow, and the :class:`AuthorisedSession`
      class handles the authenticated requests after the token is obtained.

    Parameters
    ----------
    client_id: :class:`int` | :class:`str`
        The client ID of your Discord application.
    client_secret: :class:`str`
        The client secret of your Discord application.
    redirect_uri: :class:`str`
        The redirect URI you set in the Discord Developer Portal for your application. This is where users
        will be redirected after authorizing your application.
    scopes: :class:`list`[:class:`Scope` | :class:`str`]
        A list of scopes your application is requesting access to. These determines which endpoints and data your
        application can access.
    state: :class:`str` | :class:`None`
        An optional state parameter to include in the authorization URL. This can be used to maintain state between
        the authorization request and the callback, and can help prevent CSRF attacks.

        See more in the Discord documentation: https://docs.discord.com/developers/topics/oauth2#state-and-security
    session: :class:`aiohttp.ClientSession`
        An optional aiohttp ClientSession to use for making HTTP requests. If not provided, a new session will be
        created internally.

    Attributes
    ----------
    http: :class:`OAuth2HTTPClient`
        The internal HTTP client used for making requests to the Discord API. This is not typically accessed
        directly by users of the library, but is available for advanced use cases.

        You can use the `data` attribute on all models to get the raw response data from the API too.

    Example
    -------

    .. code-block:: python

        from oauthcord import Client, Scope

        client = Client(
            client_id=123456789012345678,
            client_secret="your_client_secret",
            redirect_uri="http://localhost:8000/callback",
            scopes=[Scope.IDENTIFY, Scope.GUILDS],
        )
        authorize_url = client.get_authorization_url()
        print(f"Open this URL to authorize: {authorize_url}")
    """

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
        """Generates the URL to redirect users to for authorizing your application.

        This URL includes the necessary query parameters based on the client configuration, such as the client ID,
        redirect URI, requested scopes, and optional state.

        Returns
        -------
        :class:`str`
            The URL to redirect users to for authorizing your application.
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
        """Exchanges the temporary authorization code for an access token

        This is typically called in the callback route after the user authorizes your application and is redirected back
        to your redirect URI with a `code` query parameter.

        Parameters
        ----------
        code: :class:`str`
            The authorization code received from Discord after the user authorizes your application.

        Returns
        -------
        :class:`AuthorisedSession`
            An AuthorisedSession instance that can be used to make authenticated requests to the Discord API.
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
    """Represents an authorized session with an access token. This is created after exchanging the authorization code,
    and can be used to make authenticated requests to the Discord API.

    You may only get this from :meth:`Client.exchange_token`, and it will have the token already set up for making requests.

    Attributes
    ----------
    client: :class:`Client`
        The parent Client instance that created this session. This can be used to access the base client
        configuration and HTTP client if needed.
    token: :class:`AccessTokenResponse`
        The access token response containing the access token and related information. This is used internally for
        making authenticated requests, and can also be used to refresh or revoke the token if needed.
    current_authorization_information: :class:`CurrentInformation` | :class:`None`
        The current authorization information for this session, which includes details about the authorized user and
        their permissions. This is typically set after the first authenticated request is made, and can be
        used to check the current scopes and permissions of the token.
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
        """:class:`CurrentInformation` | :class:`None`: The current authorization information for this session,
        which includes details about the authorized user and their permissions. This is typically set after
        the first authenticated request is made, and can be used to check the current scopes and permissions of the token.
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
        """Refreshes the access token using the refresh token.

        The current token information will be updated with the new token data after refreshing.

        Parameters
        ----------
        check_expired: :class:`bool`
            If set to True, the token will only be refreshed if it is expired. If False
            (the default), the token will be refreshed regardless of its expiration status.


        Returns
        -------
        :class:`AccessTokenResponse`
            The new access token response obtained from refreshing.
        """
        token = await self.token.refresh(check_expired=check_expired)
        self.current_authorization_information = (
            await self.get_current_authorization_information()
        )
        return token

    async def revoke(
        self,
    ) -> None:
        """Revokes the current access token, invalidating it for future use.

        .. warning::
            This revokes any active tokens associated with the current application.

            After revoking, the current token information will be cleared, and the session will no longer be able to make
            authenticated requests until a new token is obtained through the OAuth2 flow again.
        """
        await self.token.revoke()
        self._current_authorization_information = None
