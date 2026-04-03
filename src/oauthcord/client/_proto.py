from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ..models.access_token import AccessTokenResponse
    from ..models.current_auth import CurrentInformation
    from . import Client


class _AuthorisedSessionProto(Protocol):
    client: Client
    token: AccessTokenResponse

    @property
    def current_authorization_information(self) -> CurrentInformation | None: ...

    @current_authorization_information.setter
    def current_authorization_information(self, value: CurrentInformation) -> None: ...
