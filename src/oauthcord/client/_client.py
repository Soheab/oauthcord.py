from __future__ import annotations

import urllib.parse
from typing import TYPE_CHECKING, Literal, Self

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

if TYPE_CHECKING:
    from ..internals._types.token import (
        AccessTokenResponse as AccessTokenResponsePayload,
    )
    from ..internals._types.token import (
        RefreshTokenResponse as RefreshTokenResponsePayload,
    )


class Client:
    """Discord OAuth2 client.

    This class owns the OAuth2 application configuration and the internal HTTP
    client used for Discord requests. It builds authorization URLs, exchanges
    callback codes for token responses, and creates :class:`AuthorisedSession`
    objects that carry those tokens for user-authorized API calls.

    The client also contains an optional in-memory session registry. The
    registry is a convenience mapping for applications that need to retrieve a
    session by a stable key after the OAuth callback has completed. It is not a
    persistence layer and is cleared when the process exits or when
    :meth:`clear_sessions` is called.

    Parameters
    ----------
    client_id: :class:`int` | :class:`str`
        Discord application client ID. The value is converted to
        :class:`int` before being passed to the internal HTTP client.
    client_secret: :class:`str`
        Discord application client secret used for OAuth2 token exchange,
        refresh, and revoke requests.
    redirect_uri: :class:`str`
        Redirect URI configured for the Discord application. This exact value
        is sent during authorization-code exchange.
    scopes: :class:`list`[:class:`Scope` | :class:`str`]
        OAuth2 scopes to request during authorization. String values are
        normalized to :class:`Scope` instances during initialization.
    state: :class:`str` | :data:`None`
        Optional state value to include in the authorization URL for caller-side
        CSRF protection or request correlation.
    session: :class:`aiohttp.ClientSession`
        Existing HTTP session to reuse for API requests. When provided, the
        internal HTTP client uses it instead of creating its own
        :class:`aiohttp.ClientSession`.
    store_session: :class:`bool`
        Whether sessions created by :meth:`exchange_token` are automatically
        added to the in-memory session registry.

        This setting only controls automatic registry insertion. It does not
        affect token exchange, session creation, refresh, revoke, or any
        Discord API call. Sessions can still be added manually with
        :meth:`add_session`, and individual calls to :meth:`exchange_token` can
        opt out of registry insertion by passing ``session_identifier=None``.

        Defaults to ``False``.
    revoke_tokens_on_session_close: :class:`bool`
        Whether :meth:`AuthorisedSession.close` should revoke the session's
        current access token before removing the session from the registry.

        This is a client-wide policy used by all sessions created from this
        client. Calling :meth:`AuthorisedSession.revoke` directly always revokes
        the token regardless of this setting.

        Defaults to ``False``.

    Attributes
    ----------
    http: :class:`OAuth2HTTPClient`
        Internal HTTP client used by the library. It owns the Discord base URL,
        application authentication, request execution, and token endpoint
        helpers.
    """

    __slots__ = (
        "_redirect_uri",
        "_revoke_tokens_on_session_close",
        "_scopes",
        "_sessions",
        "_state",
        "_store_session",
        "http",
    )

    def __init__(
        self,
        *,
        client_id: int | str,
        client_secret: str,
        redirect_uri: str,
        scopes: list[Scope | str],
        state: str | None = None,
        session: aiohttp.ClientSession = utils.NotSet,
        store_session: bool = False,
        revoke_tokens_on_session_close: bool = False,
    ) -> None:
        self.http: OAuth2HTTPClient = OAuth2HTTPClient(
            self,
            client_id=int(client_id),
            client_secret=client_secret,
            session=session,
        )

        if not isinstance(scopes, list):
            raise ValueError("scopes must be a list of Scope or str")

        scopes_: list[Scope | str] = []
        for scope in scopes:
            if isinstance(scope, Scope):
                scopes_.append(scope)
                continue

            if not isinstance(scope, str):
                raise ValueError(
                    f"scopes must be a list of Scope or str, got {type(scope)}"
                )

            try:
                scopes_.append(Scope(scope))
            except ValueError:
                scopes_.append(scope)

        self._scopes: list[Scope | str] = scopes_
        self._redirect_uri: str = redirect_uri
        self._state: str | None = state

        self._store_session: bool = store_session
        self._sessions: dict[str, AuthorisedSession] = {}
        self._revoke_tokens_on_session_close: bool = revoke_tokens_on_session_close

    async def exchange_token(
        self,
        code: str,
        *,
        session_identifier: str | None = utils.NotSet,
    ) -> AuthorisedSession:
        """Exchange an authorization code for an authorised session.

        This method sends the temporary OAuth2 authorization code to Discord's
        token endpoint using the client's configured redirect URI. The token
        response is wrapped in :class:`AccessTokenResponse` and attached to a
        new :class:`AuthorisedSession`.

        If :attr:`store_session` is enabled, the created session is added to the
        client's registry unless ``session_identifier`` is explicitly
        :data:`None`. Registry storage is only an in-memory lookup convenience;
        the returned session is fully usable whether it is stored or not.

        Parameters
        ----------
        code: :class:`str`
            Authorization code returned by Discord.
        session_identifier: :class:`str` | :data:`None`
            Optional key to use when storing the created session in
            :attr:`sessions`.

            If omitted, the session's access token string is used as the
            registry key when automatic storage is enabled. If set to
            :data:`None`, this specific session is not inserted into the
            registry even when :attr:`store_session` is ``True``. The session is
            still returned and can be added later with :meth:`add_session`.

            Supplying a stable application-level key, such as an internal user
            ID, avoids needing to look up the session by its access token.

        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the exchanged access token. The returned
            object is the same instance that is stored in the registry when
            automatic storage applies.
        """
        res = await self.http.exchange_token(code, redirect_uri=self._redirect_uri)
        return self.create_session(
            res, identifier=session_identifier, store=self._store_session
        )

    async def close(self) -> None:
        """Close the client's HTTP resources and clear the session registry.

        This closes the internal :class:`OAuth2HTTPClient` and then removes all
        entries from the in-memory registry with :meth:`clear_sessions`.
        Clearing the registry does not revoke user access tokens. Use
        :meth:`AuthorisedSession.revoke`, or create the client with
        ``revoke_tokens_on_session_close=True`` and close individual sessions,
        when token revocation is required.
        """
        await self.http.close()
        self.clear_sessions()

    @property
    def sessions(self) -> dict[str, AuthorisedSession]:
        """Active authorised sessions stored on this client.

        This property exposes the live in-memory registry used by
        :meth:`get_session`, :meth:`add_session`, :meth:`remove_session`, and
        :meth:`clear_sessions`. Keys are either caller-provided identifiers or
        access token strings when no custom identifier was supplied. Values are
        the corresponding :class:`AuthorisedSession` objects.

        The returned dictionary is not copied. Mutating it directly mutates the
        client's registry.

        Returns
        -------
        dict[:class:`str`, :class:`AuthorisedSession`]
            The current session registry.
        """
        return self._sessions

    def get_session(self, identifier: str) -> AuthorisedSession | None:
        """Get a stored session by its registry identifier.

        This is a dictionary lookup against :attr:`sessions`. It only returns
        sessions that were automatically stored during :meth:`exchange_token` or
        manually stored with :meth:`add_session`.

        Parameters
        ----------
        identifier: :class:`str`
            Registry key associated with the session. This can be a custom
            string provided during session creation or the session's access
            token string.

        Returns
        -------
        :class:`AuthorisedSession` | :data:`None`
            The stored session for ``identifier``, or :data:`None` if the key is
            not present.
        """
        return self._sessions.get(identifier)

    def add_session(
        self, session: AuthorisedSession, identifier: str | None = utils.NotSet
    ) -> AuthorisedSession:
        """Add a session to the client's in-memory registry.

        This method is useful when :attr:`store_session` is disabled, when a
        session was created from persisted token data, or when the caller wants
        to store a session under an additional application-level key.

        If ``identifier`` is omitted, :attr:`AuthorisedSession.identifier` is
        used. If ``identifier`` is :data:`None`, no registry entry is written and
        the session is returned unchanged.

        Parameters
        ----------
        session: :class:`AuthorisedSession`
            Session instance to store. It must belong to this class hierarchy.
        identifier: :class:`str` | :data:`None`
            Optional registry key to associate with the session.

            Defaults to :attr:`AuthorisedSession.identifier`, which falls back
            to the access token string when the session has no custom
            identifier.

        Returns
        -------
        :class:`AuthorisedSession`
            The same session instance that was passed in.
        """
        if not isinstance(session, AuthorisedSession):
            raise ValueError(
                f"session must be an instance of AuthorisedSession not {type(session)}"
            )

        identifier = identifier or session.identifier
        if identifier is not None:
            self._sessions[identifier] = session
        return session

    def create_session(
        self,
        token: AccessTokenResponse
        | AccessTokenResponsePayload
        | RefreshTokenResponsePayload,
        *,
        identifier: str | None = utils.NotSet,
        store: bool = False,
    ) -> AuthorisedSession:
        """Create an authorised session from token data.

        This method wraps an existing token payload in
        :class:`AccessTokenResponse` when needed and creates an
        :class:`AuthorisedSession` bound to this client. It is the shared
        construction path used by :meth:`exchange_token` and by callers that
        restore sessions from persisted token data.

        Registry storage is controlled by ``store`` and ``identifier``. Passing
        ``store=True`` inserts the session into :attr:`sessions`, unless
        ``identifier`` is explicitly :data:`None`.

        Parameters
        ----------
        token: :class:`AccessTokenResponse` | :class:`AccessTokenResponsePayload` | :class:`RefreshTokenResponsePayload`
            Existing token model or raw token payload to initialize the session
            with.
        identifier: :class:`str` | :data:`None`
            Optional registry key to associate with the session.

            If omitted, the access token string is used when ``store`` is
            ``True``. If set to :data:`None`, this session is not inserted into
            the registry even when ``store`` is ``True``.
        store: :class:`bool`
            Whether to add the created session to the in-memory registry.
            Defaults to ``False``.

        Returns
        -------
        :class:`AuthorisedSession`
            The newly created session.
        """
        session = AuthorisedSession.from_token(self, token)
        if store and identifier is not None:
            self.add_session(session, identifier=identifier)
        return session

    def refresh_session(
        self,
        session: AuthorisedSession,
        *,
        old_identifier: str | None = utils.NotSet,
        identifier: str | None = utils.NotSet,
    ) -> AuthorisedSession:
        """Update a stored session's registry key after token refresh.

        This is an internal registry maintenance hook used by
        :meth:`AuthorisedSession.refresh`. Refreshing an OAuth token can change
        the access token string. When a session was stored under the old token
        value, this method removes the stale key and stores the same session
        under the new key.

        Custom identifiers remain stable unless a replacement ``identifier`` is
        provided.

        Parameters
        ----------
        session: :class:`AuthorisedSession`
            Session whose registry entry should be refreshed.
        old_identifier: :class:`str` | :data:`None`
            Previous registry key. Defaults to the session's current identifier
            when omitted.
        identifier: :class:`str` | :data:`None`
            Replacement registry key. Defaults to the session's current
            identifier when omitted.

        Returns
        -------
        :class:`AuthorisedSession`
            The same session instance that was passed in.
        """
        old_identifier_ = old_identifier or session.identifier
        if old_identifier_ is None:
            return session

        if old_identifier_ != identifier:
            self._sessions.pop(old_identifier_, None)

        identifier_ = identifier or session.identifier
        if identifier_ is not None:
            self._sessions[identifier_] = session
        return session

    def remove_session(self, identifier: str) -> None:
        """Remove a session from the client's in-memory registry.

        This only removes the registry entry. It does not close the session,
        revoke the access token, clear cached authorization information, or
        affect the underlying HTTP client.

        Missing identifiers are ignored.

        Parameters
        ----------
        identifier: :class:`str`
            Registry key associated with the session to remove.
        """
        self._sessions.pop(identifier, None)

    def clear_sessions(self) -> None:
        """Remove every session from the client's in-memory registry.

        This is a registry-only operation. It does not revoke tokens and does
        not mutate the :class:`AuthorisedSession` objects themselves.
        """
        self._sessions.clear()

    def get_authorization_url(
        self,
    ) -> str:
        """Build the Discord OAuth2 authorization URL.

        The URL is built from the client's configured application ID, redirect
        URI, scopes, and optional state value. Send users to this URL to begin
        the authorization-code flow.

        Returns
        -------
        :class:`str`
            Discord authorization URL for the configured OAuth2 flow.
        """
        params = {
            "client_id": str(self.http.client_id),
            "response_type": "code",
            "redirect_uri": self._redirect_uri,
            "scope": "+".join(str(scope) for scope in self._scopes),
        }
        if self._state:
            params["state"] = self._state

        url = urllib.parse.urljoin(self.http.BASE_URL, "/oauth2/authorize")
        url += "?" + urllib.parse.urlencode(params)
        return url

    async def get_bot_authorization_url(
        self,
        *,
        permissions: int = utils.NotSet,
        integration_type: Literal[0, 1] = utils.NotSet,
        guild_id: int = utils.NotSet,
        disable_guild_select: bool = False,
        application_id: int | str = utils.NotSet,
    ) -> str:
        """Build a Discord OAuth2 URL for bot or command authorization.

        This helper builds an authorization URL for installing a bot or
        application commands. It uses this client's application ID by default,
        but ``application_id`` can override that for applications that need to
        generate URLs for a different Discord application.

        Parameters
        ----------
        permissions: :class:`int`
            Bitwise Discord permissions integer to request for the bot.
        guild_id: :class:`int` | :data:`None`
            Optional guild ID to pre-select in the authorization screen.
        disable_guild_select: :class:`bool`
            Whether to disable the guild selection dropdown in the
            authorization screen.

            ``guild_id`` must be provided if this is set to ``True``.
        application_id: :class:`int` | :data:`None`
            Optional application ID to use in the generated URL. Defaults to the
            current client's application ID.
        integration_type: :class:`int`
            Discord integration type. Must be ``0`` for guild installation or
            ``1`` for user installation.

            Defaults to ``0``. When set to ``1``, the generated scope is
            ``applications.commands``. Otherwise the generated scope is
            ``bot+applications.commands``.

        Returns
        -------
        :class:`str`
            Discord authorization URL containing the requested installation
            parameters.
        """
        params = {
            "client_id": str(self.http.client_id)
            if application_id is utils.NotSet
            else str(application_id),
        }

        if permissions is not utils.NotSet:
            params["permissions"] = str(permissions)
        if guild_id is not utils.NotSet:
            params["guild_id"] = str(guild_id)
        if disable_guild_select:
            if guild_id is utils.NotSet:
                raise ValueError(
                    "guild_id must be provided if disable_guild_select is True"
                )

            params["disable_guild_select"] = "true"

        integration_type = (
            integration_type if integration_type is not utils.NotSet else 0
        )

        if integration_type is not utils.NotSet:
            if integration_type not in (0, 1):
                raise ValueError(
                    "integration_type must be either 0 (Guild) or 1 (User)"
                )

            params["integration_type"] = str(integration_type)

        if integration_type == 1:
            params["scope"] = "applications.commands"
        else:
            params["scope"] = "bot+applications.commands"

        url = urllib.parse.urljoin(self.http.BASE_URL, "/oauth2/authorize")
        url += "?" + urllib.parse.urlencode(params)
        return url


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

    A session represents one Discord OAuth2 authorization for one user token.
    It stores the current :class:`AccessTokenResponse`, keeps a reference to the
    parent :class:`Client`, and exposes the route mixins that make authorized
    Discord API calls.

    Sessions do not own an HTTP connection directly. All requests go through
    ``session.client.http`` so rate limiting, authentication helpers, and the
    underlying :class:`aiohttp.ClientSession` stay centralized on the parent
    client.

    Sessions may be placed in the client's in-memory registry. The registry is
    only a lookup convenience; direct references to a session remain usable even
    if the session is not stored.

    Attributes
    ----------
    client: :class:`Client`
        Parent OAuth2 client that created the session and owns the internal HTTP
        client used for all requests.
    token: :class:`AccessTokenResponse`
        Current access token data for the session. Refreshing the session
        updates this object in place.
    identifier: :class:`str`
        Effective identifier for the session. This is a custom identifier when
        one was provided, otherwise it falls back to the current access token
        string.
    """

    def __init__(
        self,
        client: Client,
        *,
        token: AccessTokenResponse,
        identifier: str | None = utils.NotSet,
    ) -> None:
        self._identifier: str | None = identifier
        self.__identifier_is_access_token: bool = identifier is utils.NotSet

        self.client: Client = client
        self.token: AccessTokenResponse = token

        self._current_authorization_information: CurrentInformation | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass

    def __repr__(self) -> str:
        identifier = (
            self.identifier
            if not self.__identifier_is_access_token
            else "<access_token redacted>"
        )
        return f"<AuthorisedSession identifier={identifier!r}>"

    @property
    def http(self) -> OAuth2HTTPClient:
        """Shortcut to the parent client's internal HTTP client.

        Returns
        -------
        :class:`OAuth2HTTPClient`
            The same HTTP client exposed by :attr:`Client.http`.
        """
        return self.client.http

    @property
    def identifier(self) -> str | None:
        """:class:`str` | :data:`None`: Effective registry identifier.

        If a custom identifier was provided when the session was created, that
        value is returned. Otherwise the current access token string is used as
        the fallback identifier.

        Passing ``identifier=None`` to :meth:`Client.create_session` or
        ``session_identifier=None`` to :meth:`Client.exchange_token` prevents
        automatic registry insertion for that call.

        Returns
        -------
        :class:`str` | :data:`None`
            Custom identifier, access token string, or :data:`None` if the
            session was created with ``identifier=None``. When the session has no custom
            identifier, this returns the current access token string, which changes on
            refresh. When the session has a custom identifier, that value is returned and
            does not change on refresh.
        """
        if self._identifier is None:
            return None

        if self._identifier is not utils.NotSet:
            return self._identifier

        self.__identifier_is_access_token = True
        return self.token.access_token

    @classmethod
    def from_token(
        cls,
        client: Client,
        token: AccessTokenResponse
        | AccessTokenResponsePayload
        | RefreshTokenResponsePayload,
        *,
        identifier: str | None = utils.NotSet,
    ) -> AuthorisedSession:
        """Create an authorised session from an existing access token.

        This constructor is used when token data already exists, for example
        after :meth:`Client.exchange_token` receives a Discord response or when
        persisted token data is loaded from storage. Raw token payloads are
        converted into :class:`AccessTokenResponse` so the session always stores
        the typed token model internally.

        Parameters
        ----------
        client: :class:`Client`
            Parent OAuth2 client that the session should use for HTTP requests.
        token: :class:`AccessTokenResponse` | :class:`AccessTokenResponsePayload` | :class:`RefreshTokenResponsePayload`
            Existing access token model or raw Discord token payload.
        identifier: :class:`str` | :data:`None`
            Optional custom identifier to associate with the session.

            This value is stored on the session and used by
            :attr:`identifier`. Registry insertion is handled by
            :meth:`Client.create_session` or :meth:`Client.add_session`, not by
            this class method.

        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the provided token data.
        """
        if not isinstance(token, AccessTokenResponse):
            token = AccessTokenResponse.from_dict(client, token)

        return cls(client, token=token, identifier=identifier)

    def to_dict(
        self,
    ) -> AccessTokenResponsePayload | RefreshTokenResponsePayload:
        """Serialize the session's current token data.

        The returned payload can be persisted by the caller and passed back into
        :meth:`Client.create_session` later to recreate an authorized session.
        Only token data is serialized; the parent client, registry key, cached
        authorization information, and other runtime state are not included.

        Returns
        -------
        :class:`dict`
            Dictionary containing the current OAuth2 token payload.
        """
        return self.token.to_dict()

    async def close(self) -> None:
        """Close this session from the client's perspective.

        Closing removes the session from the parent client's registry when it is
        present. If the parent client was created with
        ``revoke_tokens_on_session_close=True``, this also calls
        :meth:`revoke` before removing the registry entry.

        This method does not close the shared HTTP client. Use
        :meth:`Client.close` for HTTP cleanup.
        """
        if self.client._revoke_tokens_on_session_close:
            await self.revoke()

        if self.identifier is not None:
            self.client.remove_session(self.identifier)

    @property
    def current_authorization_information(self) -> CurrentInformation | None:
        """Current authorization information for the session.

        This cache is populated by calls that fetch Discord's current OAuth2
        authorization information, and it is refreshed after a successful token
        refresh. It is cleared when the token is revoked.

        Returns
        -------
        :class:`CurrentInformation` | :data:`None`
            Cached authorization information for the current token, or
            :data:`None` if it has not been loaded.
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
        """Refresh the current OAuth2 access token.

        This delegates to :meth:`AccessTokenResponse.refresh`, which updates the
        stored token model in place. When a refresh actually happens, the
        session reloads current authorization information and asks the parent
        client to update the registry key if the session was stored under its
        previous access token.

        If ``check_expired`` is ``True`` and the token is still valid, no HTTP
        refresh request is made and the existing token is returned.

        Parameters
        ----------
        check_expired: :class:`bool`
            Whether to refresh only when the current token is expired.

        Returns
        -------
        :class:`AccessTokenResponse`
            Current token data after the refresh check completes. This is the
            same token object stored on :attr:`token`.
        """
        current_identifier = self.identifier

        refreshed = self.token.is_expired() if check_expired else True

        await self.token.refresh(check_expired=check_expired)

        if refreshed:
            self.current_authorization_information = (
                await self.get_current_authorization_information()
            )

            if current_identifier is not None:
                self.client.refresh_session(
                    self, old_identifier=current_identifier, identifier=self.identifier
                )

        return self.token

    async def revoke(
        self,
    ) -> None:
        """Revoke the current access token.

        This sends the session's current access token to Discord's revoke
        endpoint, clears cached current authorization information, and removes
        the session from the parent client's registry when present.

        After revocation, the token should be treated as unusable. The user must
        complete the OAuth2 authorization flow again before the application can
        make further authorized requests for that user.
        """
        await self.token.revoke()
        self._current_authorization_information = None
        if self.identifier is not None:
            self.client.remove_session(self.identifier)
