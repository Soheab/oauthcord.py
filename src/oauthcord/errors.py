from __future__ import annotations

"""Exception types raised by oauthcord.py HTTP and model operations."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .internals.endpoints.base import Route


__all__ = (
    "BadRequest",
    "Conflict",
    "DiscordServerError",
    "Forbidden",
    "HTTPException",
    "NotFound",
    "OauthCordException",
    "RateLimited",
    "Unauthorized",
    "UnprocessableEntity",
)


class OauthCordException(Exception):
    """Base exception for all library-specific errors."""

    pass


class HTTPException(OauthCordException):
    """Base exception for Discord HTTP responses that indicate failure."""

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

        return f"{self.status!r} for '{self.route.method} @ {self.route.path}': {self.message!r} (code: {self.code!r})"


class RateLimited(HTTPException):
    """Exception raised when Discord rate limits the current request."""

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
    """Exception raised for HTTP 400 responses."""

    pass


class Unauthorized(HTTPException):
    """Exception raised for HTTP 401 responses."""

    pass


class Forbidden(HTTPException):
    """Exception raised for HTTP 403 responses."""

    pass


class NotFound(HTTPException):
    """Exception raised for HTTP 404 responses."""

    pass


class Conflict(HTTPException):
    """Exception raised for HTTP 409 responses."""

    pass


class UnprocessableEntity(HTTPException):
    """Exception raised for HTTP 422 responses."""

    pass


class DiscordServerError(HTTPException):
    """Exception raised for HTTP 5xx responses from Discord."""

    pass


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
