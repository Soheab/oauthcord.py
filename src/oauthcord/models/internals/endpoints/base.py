from typing import TYPE_CHECKING, Any, Literal, NotRequired, Protocol, TypedDict

import aiohttp

if TYPE_CHECKING:
    from ...access_token import AccessTokenResponse


class AccessTokenAttr(Protocol):
    access_token: str


class RefreshTokenAttr(Protocol):
    refresh_token: str


class RestTokenAttrs(Protocol):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    scope: str


class TokenDict(
    TypedDict,
):
    access_token: str
    token_type: NotRequired[str]
    expires_in: NotRequired[int]
    refresh_token: NotRequired[str]
    scope: NotRequired[str]


class RefreshTokenDict(TypedDict):
    refresh_token: str
    access_token: NotRequired[str]
    expires_at: NotRequired[float]


type ValidToken = (
    AccessTokenResponse | AccessTokenAttr | RestTokenAttrs | TokenDict | str
)
type HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
type ResponsePayload = dict[str, Any] | list[Any] | str
type RequestAttemptResult = tuple[Literal["return", "retry"], Any]


class Route:
    def __init__(self, method: HTTPMethod, path: str, /) -> None:
        self.method: HTTPMethod = method
        self.path: str = path

    def get_constructed_url(self, base_url: str) -> str:
        if self.path.startswith("http"):
            return self.path

        return base_url.lstrip("/") + self.path


class BaseHTTPClient:
    redirect_uri: str
    _auth: aiohttp.BasicAuth

    def _parse_token(self, token: ValidToken, *, refresh: bool = False) -> str:
        raise NotImplementedError

    async def request(
        self,
        route: Route,
        *,
        token: ValidToken | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError
