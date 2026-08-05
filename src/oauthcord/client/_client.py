from __future__ import annotations

import urllib.parse
import uuid
from typing import TYPE_CHECKING, Any, Literal, Self, overload

import aiohttp

from .. import utils
from ..enums import Scope
from ..internals.http import OAuth2HTTPClient
from ..models.access_token import AccessToken
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
    from ..enums import UnknownScope
    from ..internals._types.token import (
        AccessTokenResponse as AccessTokenResponsePayload,
    )
    from ..internals._types.token import (
        RefreshTokenResponse as RefreshTokenResponsePayload,
    )

    AuthorisedSessionPayload = AccessTokenResponsePayload

    class AuthorisedSessionPayloadWithExtras(AuthorisedSessionPayload):
        extras: dict[str, Any]


def _generate_session_identifier() -> str:
    """Generate a random session identifier."""
    return str(uuid.uuid4())


class Client:
    """Discord OAuth2 client.

    Use this class to build authorization URLs, exchange OAuth2 codes, and
    create :class:`AuthorisedSession` objects for authorized API calls.

    Parameters
    ----------
    client_id: :class:`int` | :class:`str`
        Discord application client ID.
    client_secret: :class:`str`
        Discord application client secret.
    redirect_uri: :class:`str`
        Redirect URI configured for the Discord application.

        You may also set this per authorization URL with :meth:`get_authorization_url` in case
        of different redirect URIs for different URLs.
        This value will be used as default.
    scopes: :class:`list`[:class:`Scope` | :class:`str`]
        OAuth2 scopes to request during authorization.

        You may also set this per authorization URL with :meth:`get_authorization_url` in case of
        different scopes for different URLs or users.
        This value will be used as default.
    state: :class:`str` | :data:`None`
        Optional state value to include in the authorization URL.

        You may also set this per authorization URL with :meth:`get_authorization_url` in case of
        different state values for different URLs or users.
    session: :class:`aiohttp.ClientSession`
        Existing HTTP session to use for API requests.
    store_session: :class:`bool`
        Whether created sessions are stored in memory. Defaults to ``False``.

        You may choose to store a session manually with :meth:`add_session` even if this is disabled, but
        enabling this allows sessions to be automatically stored when created with :meth:`exchange_token`
        or :meth:`AuthorisedSession.from_token`.
    revoke_tokens_on_session_close: :class:`bool`
        Whether closing a session should revoke its token.

        This will call :meth:`AuthorisedSession.revoke` when a session is closed with :meth:`AuthorisedSession.close`,
        which revokes the token and removes the session from the registry.

        Defaults to ``False``.

    Attributes
    ----------
    http: :class:`OAuth2HTTPClient`
        Internal HTTP client used for Discord requests.
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
        scopes: list[Scope | UnknownScope | str],
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

        self._scopes: list[Scope | UnknownScope] = []
        self.scopes = scopes

        self._redirect_uri: str = redirect_uri
        self._state: str | None = state

        self._store_session: bool = store_session
        self._sessions: dict[str, AuthorisedSession] = {}
        self._revoke_tokens_on_session_close: bool = revoke_tokens_on_session_close

    @property
    def scopes(self) -> list[Scope | UnknownScope]:
        return self._scopes

    @scopes.setter
    def scopes(self, value: list[Scope | UnknownScope | str]) -> None:
        if not isinstance(value, list):
            raise TypeError("scopes must be a list")

        self._scopes = Scope.from_list(value)

    async def exchange_token(
        self,
        code: str,
        *,
        session_identifier: str | None = utils.NotSet,
        extras: dict[str, Any] = utils.NotSet,
    ) -> AuthorisedSession:
        """Exchange an authorization code for an authorised session.

        If ``store_session`` is enabled, the new session is stored in memory
        by default unless ``session_identifier`` is explicitly set to :data:`None`.

        Parameters
        ----------
        code: :class:`str`
            Authorization code returned by Discord.
        session_identifier: :class:`str` | :data:`None`
            The session's registry identifier. If :data:`None`, the session is not stored even
            if ``store_session`` is enabled.

            Defaults to a random UUID string if ``store_session`` is enabled.
        extras: :class:`dict`
            Optional extra data to associate with the session.

            This is never used by the library itself, but can be used to store arbitrary data
            associated with the session, such as user IDs, guild IDs, or other metadata.

        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the exchanged access token.
        """
        res = await self.http.exchange_token(code, redirect_uri=self._redirect_uri)
        session = AuthorisedSession.from_token(
            self, res, identifier=session_identifier, extras=extras
        )
        return session

    async def close(self) -> None:
        """Close the client and all stored sessions.

        This does not revoke any tokens.
        """
        await self.http.close()
        self.clear_sessions()

    @property
    def sessions(self) -> list[AuthorisedSession]:
        """list[:class:`AuthorisedSession`]: List of currently stored sessions."""
        return list(self._sessions.values())

    def get_session(self, identifier: str) -> AuthorisedSession | None:
        """Retrieve a stored session by its registry identifier.

        Parameters
        ----------
        identifier: :class:`str`
            Registry key associated with the session to retrieve.

        Returns
        -------
        :class:`AuthorisedSession` | :data:`None`
            The session associated with the given identifier, or :data:`None` if no session is found.
        """
        return self._sessions.get(identifier)

    def add_session(
        self,
        session: AuthorisedSession,
        *,
        identifier: str = utils.NotSet,
    ) -> AuthorisedSession:
        """Add an existing session to the client's in-memory registry.

        The provided identifier is used as the registry key. If no identifier is provided,
        the session's existing :attr:`AuthorisedSession.identifier` is used. If neither is
        set, a random UUID string is generated and assigned as the identifier.

        Parameters
        ----------
        session: :class:`AuthorisedSession`
            The session to add to the registry.
        identifier: :class:`str`
            Optional registry identifier to assign to the session.

        Returns
        -------
        :class:`AuthorisedSession`
            The added session, with its identifier set if it was not already.
        """
        if not isinstance(session, AuthorisedSession):
            raise ValueError(
                f"session must be an instance of AuthorisedSession not {type(session)}"
            )

        if identifier is utils.NotSet:
            identifier = session.identifier or _generate_session_identifier()

        session._identifier = identifier
        self._sessions[identifier] = session
        return session

    def remove_session(self, identifier: str) -> None:
        """Remove a session from the client's in-memory registry by its identifier.

        If the session was not found, this does nothing.

        Parameters
        ----------
        identifier: :class:`str`
            Registry key associated with the session to remove.
        """
        self._sessions.pop(identifier, None)

    def clear_sessions(self) -> None:
        """Clear all sessions from the client's in-memory registry."""
        self._sessions.clear()

    def get_authorization_url(
        self,
        *,
        redirect_uri: str = utils.NotSet,
        scopes: list[Scope | UnknownScope | str] = utils.NotSet,
        append_scopes: bool = False,
        state: str = utils.NotSet,
    ) -> str:
        """Build the Discord OAuth2 authorization URL.

        Send users to this URL to start the authorization-code flow.

        Parameters
        ----------
        redirect_uri: :class:`str`
            Optional redirect URI to use in the URL. Defaults to the client's
            configured redirect URI.
        scopes: :class:`list`[:class:`Scope` | :class:`UnknownScope` | :class:`str`]
            Optional list of scopes to request. Defaults to the client's
            configured scopes.

            You may combine this with the client's :attr:`Client.scopes`.
        append_scopes: :class:`bool`
            Whether to append the provided scopes to the client's configured scopes.

            Defaults to ``False``, which means you must provide the full list of scopes to request.
        state: :class:`str`
            Optional state value to include in the URL. Defaults to the client's
            configured state.

            You may combine this with the client's :attr:`Client.state`.

        Returns
        -------
        :class:`str`
            Discord authorization URL for the configured OAuth2 flow.
        """
        scopes_ = Scope.from_list(scopes) if scopes is not utils.NotSet else []
        if append_scopes:
            scopes_ = list(set(self._scopes + scopes_))

        if not scopes_:
            scopes = list(self._scopes)

        redirect_uri_ = (
            redirect_uri if redirect_uri is not utils.NotSet else self._redirect_uri
        )
        state_ = state if state is not utils.NotSet else self._state

        params = {
            "client_id": str(self.http.client_id),
            "response_type": "code",
            "redirect_uri": redirect_uri_,
            "scope": "+".join(str(scope) for scope in scopes_),
        }
        if state_:
            params["state"] = state_

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

        Parameters
        ----------
        permissions: :class:`int`
            Bitwise Discord permissions integer to request for the bot.
        integration_type: :class:`int`
            Discord integration type. Use ``0`` for guild installation or ``1``
            for user installation.
        guild_id: :class:`int` | :data:`None`
            Optional guild ID to pre-select in the authorization screen.
        disable_guild_select: :class:`bool`
            Whether to disable the guild selection dropdown. Requires
            ``guild_id``.
        application_id: :class:`int` | :data:`None`
            Optional application ID. Defaults to this client's application ID.

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

    A session stores one OAuth2 token and uses its parent :class:`Client` for
    HTTP requests.

    Attributes
    ----------
    client: :class:`Client`
        Parent OAuth2 client.
    token: :class:`AccessToken`
        Current access token data.
    extras: :class:`dict`
        Optional extra data associated with the session.

        This is never used by the library itself, but can be used to store arbitrary data
        associated with the session, such as user IDs, guild IDs, or other metadata.
    """

    def __init__(
        self,
        client: Client,
        *,
        token: AccessToken,
        **extras: Any,
    ) -> None:
        self._identifier: str | None = None

        self.client: Client = client
        self.token: AccessToken = token

        self._current_authorization_information: CurrentInformation | None = None

        self.extras: dict[str, Any] = extras

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass

    def __repr__(self) -> str:
        return f"<AuthorisedSession identifier={self._identifier!r}>"

    @property
    def http(self) -> OAuth2HTTPClient:
        """Parent client's internal HTTP client.

        Returns
        -------
        :class:`OAuth2HTTPClient`
            The same HTTP client exposed by :attr:`Client.http`.
        """
        return self.client.http

    @property
    def identifier(self) -> str | None:
        """The session's identifier for the client's in-memory registry.

        Returns
        -------
        :class:`str` | :data:`None`
            The registry identifier, or :data:`None` if the session is not stored.
        """
        return self._identifier

    @classmethod
    def from_token(
        cls,
        client: Client,
        token: AccessToken | AccessTokenResponsePayload | RefreshTokenResponsePayload,
        *,
        identifier: str | None = utils.NotSet,
        ignore_existing_identifier: bool = False,
        replace_token_of_existing_session: bool = True,
        extras: dict[str, Any] = utils.NotSet,
    ) -> AuthorisedSession:
        """Create a new session from an access token response/payload.

        The token can be either a raw response payload or an already parsed
        :class:`AccessToken` object.

        If ``store_session`` is enabled on the client, the session is stored in memory
        by default unless ``identifier`` is explicitly set to :data:`None`.

        Parameters
        ----------
        client: :class:`Client`
            The client to create the session for.
        token: :class:`AccessToken` | :class:`dict`
            The access token data to initialize the session with, either as a raw response payload
            or an already parsed :class:`AccessToken` object.
        identifier: :class:`str` | :data:`None`
            The session's registry identifier. If :data:`None`, the session is not stored even
            if ``store_session`` is enabled.

            Also see ``ignore_existing_identifier`` to control whether the session's existing identifier is used.
            Defaults to a random UUID string if ``store_session`` is enabled.
        ignore_existing_identifier: :class:`bool`
            Whether to ignore the session's existing identifier when storing it in the client registry.

            Defaults to ``False``, which means that if the session already has an identifier,
            it will be used instead of generating a new one.
        replace_token_of_existing_session: :class:`bool`
            Whether to replace the token of an existing session with the same identifier.

            Defaults to ``True``, which means that if the session already has an identifier,
            its token will be replaced with the new one.
        extras: :class:`dict`
            Optional extra data to associate with the session.

            This is never used by the library itself, but can be used to store arbitrary data
            associated with the session, such as user IDs, guild IDs, or other metadata.


        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the exchanged access token.
        """
        token = (
            token
            if isinstance(token, AccessToken)
            else AccessToken.from_dict(client, token)
        )

        if identifier not in (utils.NotSet, None) and not ignore_existing_identifier:
            existing_session = client.get_session(identifier)
            if existing_session is not None:
                if replace_token_of_existing_session:
                    existing_session.token = token
                return existing_session

        inst = cls(client, token=token)

        if identifier is not None and client._store_session:
            client.add_session(inst, identifier=identifier)

        return inst

    @overload
    def to_dict(
        self, *, include_extras: Literal[True] = ...
    ) -> AuthorisedSessionPayloadWithExtras: ...

    @overload
    def to_dict(
        self, *, include_extras: Literal[False] = ...
    ) -> AuthorisedSessionPayload: ...

    @overload
    def to_dict(
        self, *, include_extras: bool = ...
    ) -> AuthorisedSessionPayload | AuthorisedSessionPayloadWithExtras: ...

    @overload
    def to_dict(self) -> AuthorisedSessionPayload: ...

    def to_dict(
        self, *, include_extras: bool = False
    ) -> AuthorisedSessionPayload | AuthorisedSessionPayloadWithExtras:
        """Serialize the session's current token data.

        You can pass this to :meth:`AuthorisedSession.from_token` to create a
        new session with the same token.

        Returns
        -------
        :class:`dict`
            Dictionary containing the current OAuth2 token payload.
        """
        res = self.token.to_dict()
        if include_extras:
            res |= {"extras": self.extras}
        return res  # type: ignore

    async def close(self) -> None:
        """Close this session from the client's perspective.

        This removes the session from the client registry. If the client was
        created with ``revoke_tokens_on_session_close=True``, this also revokes
        the token.
        """
        if self.client._revoke_tokens_on_session_close:
            await self.revoke()

        if self.identifier is not None:
            self.client.remove_session(self.identifier)

    @property
    def current_authorization_information(self) -> CurrentInformation | None:
        """Cached authorization information for the session.

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
    ) -> AccessToken:
        """Refresh the current OAuth2 access token.

        Parameters
        ----------
        check_expired: :class:`bool`
            Whether to skip the request when the current token is still valid.

        Returns
        -------
        :class:`AccessToken`
            The updated access token data after refresh.
        """
        refreshed = self.token.is_expired() if check_expired else True

        await self.token.refresh(check_expired=check_expired)

        if refreshed:
            self.current_authorization_information = (
                await self.get_current_authorization_information()
            )

        return self.token

    async def revoke(
        self,
    ) -> None:
        """Revoke the current access token.

        This removes the session from the registry and clears cached
        authorization information.

        .. note::

            This will revoke all access and refresh tokens associated with the current authorization.
        """
        await self.token.revoke()
        self._current_authorization_information = None
        if self.identifier is not None:
            self.client.remove_session(self.identifier)
