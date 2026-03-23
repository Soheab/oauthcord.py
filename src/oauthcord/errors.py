from typing import TYPE_CHECKING, Any

from .models.enums import Scope

if TYPE_CHECKING:
    from .internals.endpoints.base import Route


__all__ = (
    "BadRequest",
    "Conflict",
    "DiscordServerError",
    "Forbidden",
    "HTTPException",
    "MissingRequiredScopes",
    "NotFound",
    "OauthCordException",
    "RateLimited",
    "Unauthorized",
    "UnprocessableEntity",
)


class OauthCordException(Exception):
    pass


class MissingRequiredScopes(OauthCordException):
    def __init__(
        self,
        *,
        current_scopes: list[Scope | str],
        missing_scopes: list[Scope | str],
    ) -> None:
        self.current_scopes: list[Scope] = [Scope(scope) for scope in current_scopes]
        self.missing_scopes: list[Scope] = [Scope(scope) for scope in missing_scopes]

        msg = (
            "Missing required scopes: "
            f"{', '.join(str(scope) for scope in self.missing_scopes)}. "
            "Current scopes: "
            f"{', '.join(str(scope) for scope in self.current_scopes)}"
        )
        super().__init__(msg)


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

        return f"{self.status!r} for '{self.route.method} @ {self.route.path}': {self.message!r} (code: {self.code!r})"


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
    pass


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
