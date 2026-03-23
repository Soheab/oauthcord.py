from typing import Self

import aiohttp
import yarl

from .. import utils
from ..internals.http import OAuth2HTTPClient
from ..models.access_token import AccessTokenResponse
from ..models.current_auth import CurrentInformation
from ..models.enums import Scope
from ._application import ApplicationClient
from ._channel import ChannelClient
from ._connection import ConnectionClient
from ._guild import GuildClient
from ._invite import InviteClient
from ._lobby import LobbyClient
from ._message import MessageClient
from ._relationship import RelationshipClient
from ._store import StoreClient
from ._user import UserClient


class Client:
    def __init__(
        self,
        *,
        client_id: int | str,
        client_secret: str,
        redirect_uri: str,
        scopes: list[Scope | str],
        session: aiohttp.ClientSession = utils.NotSet,
        state: str | None = None,
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
        params = {
            "client_id": str(self.http.client_id),
            "response_type": "code",
            "redirect_uri": self._redirect_uri,
            "scope": "+".join(scope.value for scope in self._scopes),
        }
        if self._state:
            params["state"] = self._state

        base_url = self.http.BASE_URL
        url = yarl.URL(base_url).with_query(params)
        return str(url)

    async def exchange_token(
        self,
        code: str,
    ) -> AuthorisedSession:
        res = await self.http.exchange_token(code, redirect_uri=self._redirect_uri)
        res = utils._construct_model(AccessTokenResponse, data=res, http=self.http)
        return AuthorisedSession(self, token=res)


class AuthorisedSession(
    ApplicationClient,
    ChannelClient,
    ConnectionClient,
    GuildClient,
    InviteClient,
    LobbyClient,
    MessageClient,
    RelationshipClient,
    StoreClient,
    UserClient,
):
    def __init__(
        self,
        client: Client,
        *,
        token: AccessTokenResponse,
    ) -> None:
        self.client: Client = client
        self.token: AccessTokenResponse = token

        self.current_scopes: list[Scope] = client._scopes

        self._current_authorization_information: CurrentInformation | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass

    @property
    def current_authorization_information(self) -> CurrentInformation | None:
        return self._current_authorization_information

    @current_authorization_information.setter
    def current_authorization_information(self, value: CurrentInformation) -> None:
        if not isinstance(value, CurrentInformation):
            raise TypeError(
                "current_authorization_information must be of type CurrentInformation"
            )

        self._current_authorization_information = value
        self.current_scopes = value.scopes

    async def refresh(
        self,
    ) -> AccessTokenResponse:
        return await self.token.refresh()

    async def revoke(
        self,
    ) -> None:
        await self.token.revoke()
