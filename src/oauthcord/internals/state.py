from __future__ import annotations

from typing import TYPE_CHECKING

from ..errors import MissingSession

if TYPE_CHECKING:
    from ..client import AuthorisedSession, Client
    from .http import HTTPClient


__all__ = ("State",)


class State:
    __slots__ = ("_http", "_session")

    def __init__(
        self,
        http: HTTPClient,
        session: AuthorisedSession | None = None,
    ) -> None:
        self._http: HTTPClient = http
        self._session: AuthorisedSession | None = session

    @classmethod
    def _for_client(cls, client: Client) -> State:
        """Create a session-less state, for models built outside an authorisation."""
        return cls(client.http)

    @property
    def http(self) -> HTTPClient:
        """:class:`HTTPClient`: The shared HTTP client. Always available."""
        return self._http

    @property
    def session(self) -> AuthorisedSession:
        """:class:`AuthorisedSession`: The session this state belongs to.

        Raises
        ------
        MissingSession
            This state was not created from an authorised session.
        """
        if self._session is None:
            raise MissingSession(
                "This model was not created from an authorised session, so it "
                "cannot perform actions that require a user's access token."
            )

        return self._session

    @property
    def has_session(self) -> bool:
        """:class:`bool`: Whether :attr:`session` is available."""
        return self._session is not None

    def __repr__(self) -> str:
        return f"<State session={self._session!r}>"
