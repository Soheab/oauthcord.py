from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import quote as _uriquote

import aiohttp

if TYPE_CHECKING:
    from ...utils import ValidAccessToken

type HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
type ResponsePayload = dict[str, Any] | list[Any] | str


class Route:
    __slots__ = ("method", "parameters", "path")

    def __init__(
        self, method: HTTPMethod, path: str, /, **parameters: int | str
    ) -> None:
        self.method: HTTPMethod = method
        self.path: str = path
        self.parameters: dict[str, int | str] = parameters

    @property
    def major_parameters(self) -> str:
        parts: list[str] = []
        for name in ("guild_id", "channel_id", "webhook_id", "webhook_token"):
            if (value := self.parameters.get(name)) is not None:
                parts.append(str(value))
        return ":".join(parts)

    def get_constructed_url(self, base_url: str) -> str:
        if self.path.startswith(("http://", "https://")):
            url = self.path
        else:
            url = f"{base_url.rstrip('/')}/{self.path.lstrip('/')}"

        if self.parameters:
            url = url.format_map(
                {
                    k: _uriquote(v, safe="") if isinstance(v, str) else v
                    for k, v in self.parameters.items()
                }
            )

        return url


class BaseHTTPClient:
    redirect_uri: str
    _auth: aiohttp.BasicAuth

    @property
    def client_id(self) -> int:
        raise NotImplementedError

    @property
    def client_secret(self) -> str:
        raise NotImplementedError

    async def request(
        self,
        route: Route,
        *,
        token: ValidAccessToken | None = None,
        bot_token: str | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError
