from __future__ import annotations

import asyncio
import datetime
import urllib.parse
import uuid
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, Self, TypedDict

import aiohttp

from .. import utils
from ..enums import Scope
from ..errors import BadRequest, DeviceCodeExchangeFailed
from ..internals.http import HTTPClient
from ..internals.state import State
from ..models.access_token import AccessToken, DeviceCode
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
    from ..enums import UnknownEnum
    from ..internals._types.token import (
        AccessTokenResponse as AccessTokenResponsePayload,
    )
    from ..internals._types.token import (
        ClientCredentialsResponse as ClientCredentialsResponsePayload,
    )
    from ..internals._types.token import (
        RefreshTokenResponse as RefreshTokenResponsePayload,
    )
else:
    AccessTokenResponsePayload = dict[str, Any]
    RefreshTokenResponsePayload = dict[str, Any]

    ClientCredentialsResponsePayload = dict[str, Any]
    RefreshTokenResponsePayload = dict[str, Any]


class AuthorisedSessionPayload(TypedDict):
    token: AccessTokenResponsePayload | RefreshTokenResponsePayload
    expires_at: float
    created_at: float
    extras: dict[str, Any]


__all__ = (
    "AuthorisedSession",
    "AuthorisedSessionPayload",
    "Client",
)


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
    redirect_uri: :class:`str` | :data:`None`
        Redirect URI configured for the Discord application.

        You may also set this per authorization URL with :meth:`get_authorization_url` in case
        of different redirect URIs for different URLs.
        This value will be used as default.

        This defaults to :data:`None`, which means that the redirect URI must be provided per authorization URL.
    scopes: :class:`list`[:class:`Scope` | :class:`str`]
        OAuth2 scopes to request during authorization.

        You may also set this per authorization URL with :meth:`get_authorization_url` in case of
        different scopes for different URLs or users.
        This value will be used as default.

        This defaults to an empty list, which means that the authorization URL will not request
        any scopes unless provided per URL.
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
    auto_refresh_token: :class:`bool`
        Whether to automatically refresh a token when it is expired. If enabled, the token will be refreshed
        automatically when making requests with an expired token.

        Defaults to ``False``.
    """

    __slots__ = (
        "__device_code_polling_tasks",
        "_auto_refresh_token",
        "_model_state",
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
        redirect_uri: str | None = None,
        scopes: Sequence[Scope | UnknownEnum | str] | None = None,
        state: str | None = None,
        session: aiohttp.ClientSession = utils.NotSet,
        store_session: bool = False,
        revoke_tokens_on_session_close: bool = False,
        auto_refresh_token: bool = False,
    ) -> None:
        self.http: HTTPClient = HTTPClient(
            self,
            client_id=int(client_id),
            client_secret=client_secret,
            session=session,
            auto_refresh_token=auto_refresh_token,
        )

        self._model_state: State = State(self.http)

        self._scopes: list[Scope | UnknownEnum] = []
        self.scopes = scopes

        self._redirect_uri: str | None = redirect_uri
        self._state: str | None = state

        self._store_session: bool = store_session
        self._sessions: dict[str, AuthorisedSession] = {}
        self._revoke_tokens_on_session_close: bool = revoke_tokens_on_session_close

        # device_code: Task
        self.__device_code_polling_tasks: dict[str, asyncio.Task[AccessToken]] = {}

    @property
    def id(self) -> int:
        """:class:`int`: Returns the provided client ID."""
        return self.http.client_id

    @property
    def secret(self) -> str:
        """:class:`str`: Returns the provided client secret."""
        return self.http.client_secret

    @property
    def scopes(self) -> list[Scope | UnknownEnum]:
        return self._scopes

    @scopes.setter
    def scopes(self, value: Sequence[Scope | UnknownEnum | str] | None) -> None:
        if not value:
            self._scopes = []
            return

        if not isinstance(value, (list, tuple)):
            raise TypeError("scopes must be a list or tuple")

        self._scopes = Scope.from_list(value)

    async def get_token(
        self,
        scopes: list[Scope | UnknownEnum | str] | None = None,
    ) -> AuthorisedSession:
        """Get a new access token using the client credentials flow.

        This is a quick and easy way to get your own bearer token for testing purposes, without
        requiring user authorization. It is not intended for use in production applications.

        You cannot refresh this token, so you will need to call this method again when it expires.

        Parameters
        ----------
        scopes: :class:`list`[:class:`Scope` | :class:`UnknownEnum` | :class:`str`] | :data:`None`
            Optional list of scopes to request. If omitted or empty, the client's configured
            :attr:`Client.scopes` are used instead. If neither is set, the token is requested
            with no scopes.

        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the new access token with the requested scopes as `extras`.
        """
        scopes_ = Scope.from_list(scopes) if scopes else []
        if not scopes_:
            scopes_ = list(self._scopes)

        res = await self.http.get_token(scopes=[str(scope) for scope in scopes_])
        return await AuthorisedSession._initialise(
            client=self, data=res, extras={"scopes": scopes_}
        )

    async def exchange_token(
        self,
        code: str,
        *,
        redirect_uri: str | None = utils.NotSet,
        session_identifier: str | None = utils.NotSet,
        code_verifier: str = utils.NotSet,
        extras: dict[str, Any] = utils.NotSet,
    ) -> AuthorisedSession:
        """Exchange an authorization code for an authorised session.

        If ``store_session`` is enabled, the new session is stored in memory
        by default unless ``session_identifier`` is explicitly set to :data:`None`.

        Parameters
        ----------
        code: :class:`str`
            Authorization code returned by Discord.
        redirect_uri: :class:`str` | :data:`None`
            Redirect URI to send with the exchange. Defaults to the client's configured
            redirect URI.

            Set explicitly to :data:`None` for codes that were not obtained through a
            redirect, such as one returned by :meth:`~oauthcord.client.rpc.RPCClient.authorize`.
        session_identifier: :class:`str` | :data:`None`
            The session's registry identifier. If :data:`None`, the session is not stored even
            if ``store_session`` is enabled.

            Defaults to a random UUID string if ``store_session`` is enabled.
        code_verifier: :class:`str`
            Optional code verifier to send with the exchange for PKCE.

            This will omit the ``client_secret`` from the request.
        extras: :class:`dict`
            Optional extra data to associate with the session.

            This is never used by the library itself, but can be used to store arbitrary data
            associated with the session, such as user IDs, guild IDs, or other metadata.

        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the exchanged access token.
        """
        redirect_uri_ = (
            redirect_uri if redirect_uri is not utils.NotSet else self._redirect_uri
        )
        code_verifier_ = code_verifier if code_verifier is not utils.NotSet else None
        res = await self.http.exchange_token(
            code, redirect_uri=redirect_uri_, code_verifier=code_verifier_
        )
        session = await AuthorisedSession._initialise(
            client=self, data=res, identifier=session_identifier, extras=extras
        )
        return session

    async def get_device_code(
        self, scopes: list[Scope | UnknownEnum | str] | None = None
    ) -> DeviceCode:
        """Get a device code for the device authorization flow.

        This is used to authorize devices that do not have a browser or input method, such as
        smart TVs or IoT devices.

        Parameters
        ----------
        scopes: :class:`list`[:class:`Scope` | :class:`UnknownEnum` | :class:`str`] | :data:`None`
            Optional list of scopes to request. If omitted or empty, the client's configured
            :attr:`Client.scopes` are used instead. If neither is set, the device code is requested
            with no scopes.

            You generally do not need any scopes to call endpoints that require it.

        Returns
        -------
        :class:`DeviceCode`
            A DeviceCode object containing the device code, user code, verification URI, expiration time,
            and polling interval.
        """
        scopes_ = Scope.from_list(scopes) if scopes else []
        if not scopes_:
            scopes_ = list(self._scopes)

        res = await self.http.get_device_code(scopes=[str(scope) for scope in scopes_])
        return DeviceCode(data=res, state=self._model_state)

    async def __device_code_polling_task(self, device_code: DeviceCode) -> AccessToken:
        interval = int(device_code.interval)
        found: AccessToken | None = None
        try:
            while not found:
                try:
                    res = await self.http.exchange_device_code(device_code.device_code)
                except BadRequest as exc:
                    if (
                        not isinstance(exc.response, dict)
                        or "error" not in exc.response
                    ):
                        raise
                    res = exc.response

                if "error" not in res:
                    found = AccessToken(
                        data=res,  # pyright: ignore[reportArgumentType]
                        state=self._model_state,
                    )
                    break

                if device_code.is_expired:
                    raise DeviceCodeExchangeFailed(
                        device_code, message="The device code has expired."
                    )

                error = res["error"]
                if error == "authorization_pending":
                    await asyncio.sleep(interval)
                elif error == "slow_down":
                    interval += 5
                    await asyncio.sleep(interval)
                elif error == "expired_token":
                    raise DeviceCodeExchangeFailed(
                        device_code, message="The device code has expired."
                    )
                elif error == "access_denied":
                    raise DeviceCodeExchangeFailed(
                        device_code,
                        message="The user denied the authorization request.",
                    )
                else:
                    raise DeviceCodeExchangeFailed(
                        device_code, message=f"Unknown error: {error}"
                    )

        finally:
            self.__device_code_polling_tasks.pop(device_code.device_code, None)

        return found

    async def exchange_device_code(
        self,
        device_code: DeviceCode,
        *,
        session_identifier: str | None = utils.NotSet,
        extras: dict[str, Any] = utils.NotSet,
    ) -> AuthorisedSession:
        """Exchange a device code for an authorised session.

        This will poll the Discord API until the user authorizes the device or the device code expires.

        If ``store_session`` is enabled, the new session is stored in memory
        by default unless ``session_identifier`` is explicitly set to :data:`None`.

        Parameters
        ----------
        device_code: :class:`DeviceCode`
            Device code returned by Discord.
        session_identifier: :class:`str` | :data:`None`
            The session's registry identifier. If :data:`None`, the session is not stored even
            if ``store_session`` is enabled.

            Defaults to a random UUID string if ``store_session`` is enabled.
        extras: :class:`dict`
            Optional extra data to associate with the session.

            This is never used by the library itself, but can be used to store arbitrary data
            associated with the session, such as user IDs, guild IDs, or other metadata.

        Raises
        ------
        :class:`DeviceCodeExchangeFailed`
            The device code expired, the user denied the authorization request, or
            Discord returned an unrecognised error while polling.

        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the exchanged access token.


        """
        if device_code in self.__device_code_polling_tasks:
            task = self.__device_code_polling_tasks[device_code.device_code]
        else:
            task = asyncio.create_task(self.__device_code_polling_task(device_code))
            self.__device_code_polling_tasks[device_code.device_code] = task

        access_token = await task
        session = await AuthorisedSession._initialise(
            client=self,
            data=access_token.to_dict(),
            identifier=session_identifier,
            extras=extras,
        )
        return session

    async def close(self) -> None:
        """Close the client and all stored sessions.

        This does not revoke any tokens.
        """
        await self.http.close()
        self.clear_sessions()
        if self.__device_code_polling_tasks:
            for task in self.__device_code_polling_tasks.values():
                try:
                    task.cancel()
                except Exception:
                    pass
        self.__device_code_polling_tasks.clear()

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
        scopes: Sequence[Scope | UnknownEnum | str] = utils.NotSet,
        append_scopes: bool = False,
        state: str = utils.NotSet,
        code_challenge: str = utils.NotSet,
        prompt: Literal["none", "consent"] | None = "consent",
    ) -> str:
        """Build the Discord OAuth2 authorization URL.

        Send users to this URL to start the authorization-code flow.

        Parameters
        ----------
        redirect_uri: :class:`str`
            Optional redirect URI to use in the URL. Defaults to the client's
            configured redirect URI.
        scopes: :class:`Sequence`[:class:`Scope` | :class:`UnknownEnum` | :class:`str`]
            Optional list or tuple of scopes to request. Defaults to the client's
            configured scopes.

            You may combine this with the client's :attr:`Client.scopes`.
            Also see the ``append_scopes`` parameter to control whether the provided
            scopes are appended or replace the client's configured scopes.
        append_scopes: :class:`bool`
            Whether to append the provided scopes to the client's configured scopes.

            Defaults to ``False``, which means you must provide the full list of scopes to request.
        state: :class:`str`
            Optional state value to include in the URL. Defaults to the client's
            configured state.

            You may combine this with the client's :attr:`Client.state`.
        code_challenge: :class:`str`
            Optional code challenge to include in the URL for PKCE.

            This also sets the ``code_challenge_method`` to ``"S256"``.

        prompt: :class:`Literal`["none", "consent"] | :class:`None`
            Optional prompt parameter to include in the URL.

            Defaults to ``"consent"``, which means the user will always be prompted to
            authorize the application.

        Returns
        -------
        :class:`str`
            Discord authorization URL for the configured OAuth2 flow.
        """
        scopes_ = Scope.from_list(scopes) if scopes else []
        if append_scopes:
            scopes_ = list(dict.fromkeys(self._scopes + scopes_))

        if not scopes_:
            scopes_ = list(self._scopes)

        redirect_uri_ = redirect_uri or self._redirect_uri
        if not redirect_uri_:
            raise ValueError(
                "redirect_uri must be provided either in the client or as a parameter"
            )

        state_ = state if state is not utils.NotSet else self._state

        params = {
            "client_id": str(self.http.client_id),
            "response_type": "code",
            "redirect_uri": redirect_uri_,
            "scope": " ".join(str(scope) for scope in scopes_),
        }
        if code_challenge is not utils.NotSet:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        if state_:
            params["state"] = state_

        if prompt is not None:
            params["prompt"] = prompt

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
        prompt: Literal["none", "consent"] | None = "consent",
        code_challenge: str = utils.NotSet,
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
        code_challenge: :class:`str`
            Optional code challenge to include in the URL for PKCE.

            This also sets the ``code_challenge_method`` to ``"S256"``.
        prompt: :class:`Literal`["none", "consent"] | :class:`None`
            Optional prompt parameter to include in the URL.

            Defaults to ``"consent"``, which means the user will always be prompted to
            authorize the application.

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
        if code_challenge is not utils.NotSet:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        if prompt is not None:
            params["prompt"] = prompt

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

    You can create a session by exchanging an authorization code with :meth:`Client.exchange_token`
    or by creating one from an existing token with :meth:`AuthorisedSession.from_token`.

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
        extras: dict[str, Any] = utils.NotSet,
    ) -> None:
        self._identifier: str | None = None

        self.client: Client = client
        self.token: AccessToken = token

        self._state: State = State(client.http, self)

        self._current_authorization_information: CurrentInformation | None = None

        self.extras: dict[str, Any] = dict(extras) if extras else {}

    @property
    def _model_state(self) -> State:
        return self._state

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass

    def __repr__(self) -> str:
        return f"<AuthorisedSession identifier={self._identifier!r}>"

    @classmethod
    async def _initialise(
        cls,
        client: Client,
        *,
        data: AccessTokenResponsePayload
        | RefreshTokenResponsePayload
        | ClientCredentialsResponsePayload,
        identifier: str | None = utils.NotSet,
        extras: dict[str, Any] = utils.NotSet,
    ) -> Self:
        # fmt: off
        token = AccessToken.from_dict(client, data)
        self = cls(client, token=token, extras=extras)
        current_auth = await self.get_current_authorization_information()
        token._set_expires_at(current_auth.expires_at)
        # fmt: on

        if identifier is not None and client._store_session:
            client.add_session(self, identifier=identifier)

        return self

    @property
    def http(self) -> HTTPClient:
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
    async def from_dict(
        cls,
        client: Client,
        data: AccessToken
        | AccessTokenResponsePayload
        | RefreshTokenResponsePayload
        | AuthorisedSessionPayload,
        *,
        identifier: str | None = utils.NotSet,
        ignore_existing_identifier: bool = False,
        replace_token_of_existing_session: bool = True,
        extras: dict[str, Any] = utils.NotSet,
    ) -> AuthorisedSession:
        """Create a new session from an access token response/payload.

        The token can be either a raw response payload or an already parsed
        :class:`AccessToken` object.

        This will also set the :attr:`.current_authorization_information` property to get the
        current token's expiration date and time.

        If ``store_session`` is enabled on the client, the session is stored in memory
        by default unless ``identifier`` is explicitly set to :data:`None`.

        Parameters
        ----------
        client: :class:`Client`
            The client to create the session for.
        data: :class:`AccessToken` | :class:`dict`
            The data to create the session from. This can be either an :class:`AccessToken` object
            or a raw response payload from the Discord API.

            Or the dict received from :meth:`AuthorisedSession.to_dict`, which can be used to create a new session with
            the same token.
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

            This can also be included in the ``data`` dict under the key ``"extras"``, or
            passed separately to this parameter. If both are given, they are merged,
            with this parameter taking precedence on conflicting keys.

            If an existing session is returned for ``identifier``, these are merged into
            that session's existing extras rather than replacing them.

            This is never used by the library itself, but can be used to store arbitrary data
            associated with the session, such as user IDs, guild IDs, or other metadata.


        Returns
        -------
        :class:`AuthorisedSession`
            Session initialized with the exchanged access token.
        """
        created_at_timestamp = None
        extras_: dict[str, Any] = {}
        if isinstance(data, AccessToken):
            token = data
        else:
            if "token" in data:
                token_data = data["token"]
                created_at_timestamp = data.get("created_at")
                extras_data = data.get("extras", {})
                extras_.update(extras_data)
                token = AccessToken.from_dict(client, token_data)
            else:
                token = AccessToken.from_dict(client, data)

        if extras is not utils.NotSet:
            extras_.update(extras)

        if created_at_timestamp is not None:
            token.created_at = datetime.datetime.fromtimestamp(
                created_at_timestamp, tz=datetime.UTC
            )

        if identifier not in (utils.NotSet, None) and not ignore_existing_identifier:
            existing_session = client.get_session(identifier)
            if existing_session is not None:
                if replace_token_of_existing_session:
                    existing_session.token = token
                    existing_session._current_authorization_information = None
                    if created_at_timestamp is None:
                        current_auth = await existing_session.get_current_authorization_information()
                        token._set_expires_at(current_auth.expires_at)
                existing_session.extras.update(extras_)
                return existing_session

        inst = cls(client, token=token, extras=extras_)
        if created_at_timestamp is None:
            current_auth = await inst.get_current_authorization_information()
            token._set_expires_at(current_auth.expires_at)

        if identifier is not None and client._store_session:
            client.add_session(inst, identifier=identifier)

        return inst

    def to_dict(
        self,
    ) -> AuthorisedSessionPayload:
        """Serialize the session's current token data.

        You can pass this to :meth:`AuthorisedSession.from_token` to create a
        new session with the same token.

        Returns
        -------
        :class:`dict`
            Dictionary containing the session's current token data, and optionally the extras and creation timestamp.
        """
        return {
            "token": self.token.to_dict(),
            "expires_at": self.token.expires_at.timestamp(),
            "created_at": self.token.created_at.timestamp(),
            "extras": self.extras,
        }

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
        old_access_token = self.token.access_token

        await self.token.refresh(check_expired=check_expired)

        if self.token.access_token != old_access_token:
            current_auth = await self.get_current_authorization_information()
            self.token._set_expires_at(current_auth.expires_at)

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
