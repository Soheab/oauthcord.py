from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ..internals.state import State
    from ..models.access_token import AccessToken
    from ..models.current_auth import CurrentInformation
    from . import Client


class _AuthorisedSessionProto(Protocol):  # pyright: ignore[reportUnusedClass]
    client: Client
    token: AccessToken
    _state: State

    @property
    def current_authorization_information(self) -> CurrentInformation | None: ...

    @current_authorization_information.setter
    def current_authorization_information(self, value: CurrentInformation) -> None: ...
