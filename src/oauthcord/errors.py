from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .internals.endpoints.base import Route
    from .models.access_token import DeviceCode


__all__ = (
    "BadRequest",
    "Conflict",
    "DeviceCodeExchangeFailed",
    "DiscordServerError",
    "Forbidden",
    "HTTPException",
    "MissingSession",
    "MissingState",
    "NotFound",
    "OauthCordException",
    "RateLimited",
    "Unauthorized",
    "UnprocessableEntity",
)


class OauthCordException(Exception):
    pass


class MissingState(OauthCordException):
    """Raised when a model needs to call back into the library but is not bound to a client.

    This happens when a model was constructed directly rather than being
    created from a Discord API response.
    """


class MissingSession(MissingState):
    """Raised when a model needs an authorised session but was not created from one."""


class HTTPException(OauthCordException):
    def __init__(
        self, route: Route, response: str | dict[str, Any] | list[Any], status: int
    ) -> None:
        self.route: Route = route
        self.response = response
        self.status = status
        self.message: str | None = None
        self.code: int | None = None
        super().__init__(str(self))

    def __str__(self) -> str:
        if self.message is None:
            try:
                data = self.response
                if isinstance(data, dict):
                    self.message = data.get("message", data.get("error", str(data)))
                else:
                    self.message = str(data)
            except Exception:
                self.message = "No message"

        if self.code is None:
            try:
                data = self.response
                if isinstance(data, dict):
                    self.code = data.get("code", 0)
            except Exception:
                self.code = None

        return f"{self.status!r} for {self.route.method!r} @ {self.route.path!r}: {self.message} (code: {self.code!r})"


class RateLimited(HTTPException):
    def __init__(
        self,
        route: Route,
        response: str | dict[str, Any] | list[Any],
        retry_after: float,
        is_global: bool = False,
    ) -> None:
        self.retry_after = retry_after
        self.is_global = is_global
        super().__init__(route, response, 429)

    def __str__(self) -> str:
        scope = "Global" if self.is_global else "Route"
        return f"{scope} rate limited. Retry after {self.retry_after:.2f}s"


class BadRequest(HTTPException):
    pass


class Unauthorized(HTTPException):
    def __init__(
        self, route: Route, response: str | dict[str, Any] | list[Any], status: int
    ) -> None:
        super().__init__(route, response, status)
        self.message = (
            f"{self.message} (check that your client ID/secret are correct, that any token "
            "you passed is still valid and not revoked, and that it was granted the scopes "
            "required for this endpoint)"
        )


class Forbidden(HTTPException):
    pass


class NotFound(HTTPException):
    pass


class Conflict(HTTPException):
    pass


class UnprocessableEntity(HTTPException):
    pass


class DiscordServerError(HTTPException):
    pass


class DeviceCodeExchangeFailed(OauthCordException):
    """Raised when the device code exchange fails."""

    def __init__(self, device_code: DeviceCode, message: str | None = None) -> None:
        self.device_code: DeviceCode = device_code
        self.message: str = message or "The device code exchange failed."
        super().__init__(self.message)


def create_http_exception(
    route: Route, response: str | dict[str, Any] | list[Any], status: int
) -> HTTPException:
    match status:
        case 400:
            return BadRequest(route, response, status)
        case 401:
            return Unauthorized(route, response, status)
        case 403:
            return Forbidden(route, response, status)
        case 404:
            return NotFound(route, response, status)
        case 409:
            return Conflict(route, response, status)
        case 422:
            return UnprocessableEntity(route, response, status)
        case status if status >= 500:
            return DiscordServerError(route, response, status)
        case _:
            return HTTPException(route, response, status)
