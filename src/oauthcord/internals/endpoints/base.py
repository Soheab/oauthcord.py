from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import aiohttp

if TYPE_CHECKING:
    from ...utils import ValidAccessToken

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

    async def request(
        self,
        route: Route,
        *,
        token: ValidAccessToken | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError
