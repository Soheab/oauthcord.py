import asyncio
import json
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal

import aiohttp

from ..errors import HTTPException, create_http_exception
from ..models.access_token import AccessTokenResponse
from ..models.enums import Scope
from ..utils import NotSet
from ._ratelimiter import HTTPRateLimiterMixin
from .endpoints.application import ApplicationHTTPClientMixin
from .endpoints.base import (
    Route,
)
from .endpoints.channel import ChannelHTTPClientMixin
from .endpoints.connection import ConnectionHTTPClientMixin
from .endpoints.guild import GuildHTTPClientMixin
from .endpoints.invite import InviteHTTPClientMixin
from .endpoints.lobby import LobbyHTTPClientMixin
from .endpoints.member import MemberHTTPClientMixin
from .endpoints.message import MessageHTTPClientMixin
from .endpoints.relationship import RelationshipHTTPClientMixin
from .endpoints.store import StoreHTTPClientMixin
from .endpoints.token import TokenHTTPClientMixin
from .endpoints.user import UserHTTPClientMixin

if TYPE_CHECKING:
    from ..client import Client
    from ..models.file import File
    from ._types import (
        components as component_types,
    )
    from ._types import (
        message as message_types,
    )
    from .endpoints.base import (
        RefreshTokenAttr,
        RefreshTokenDict,
        ResponsePayload,
        ValidToken,
    )


_log = logging.getLogger("http")

__all__ = (
    "Route",
    "get_message_create_payload",
    "get_multipart_payload",
    "json_or_text",
)


async def json_or_text(
    response: aiohttp.ClientResponse,
) -> ResponsePayload:
    text = await response.text(encoding="utf-8")
    try:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(text)
    except Exception:
        pass

    return text


def get_multipart_payload(
    *,
    attachments: list[message_types.PartialAttachmentRequest] | None = None,
    files: list[File] | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    form = aiohttp.FormData()
    payload: dict[str, object] = dict(data) if data else {}
    if not files and not attachments:
        return {"json": payload}

    files = files or []

    prepared_files: list[tuple[bytes, str, str | None]] = []
    for file in files:
        data_bytes, filename = file.read()
        prepared_files.append((data_bytes, filename, file.description))

    if attachments:
        payload_attachments: list[message_types.PartialAttachmentRequest] = []

        for index, (_, filename, description) in enumerate(prepared_files):
            if not any(att.get("id") == index for att in payload_attachments):
                entry: message_types.PartialAttachmentRequest = {
                    "id": index,
                    "filename": filename,
                }
                if description is not None:
                    entry["description"] = description
                payload_attachments.append(entry)

        payload["attachments"] = payload_attachments

    form.add_field(
        "payload_json",
        json.dumps(payload),
        content_type="application/json",
    )

    for index, (data_bytes, filename, _) in enumerate(prepared_files):
        form.add_field(
            f"files[{index}]",
            data_bytes,
            filename=filename,
            content_type=files[index].content_type,
        )

    return {"data": form}


def get_message_create_payload(
    *,
    content: str | None = None,
    tts: bool | None = None,
    nonce: int | str | None = None,
    embeds: list[message_types.EmbedRequest] | None = None,
    allowed_mentions: message_types.AllowedMentionsRequest | None = None,
    message_reference: message_types.MessageReferenceRequest | None = None,
    components: list[component_types.ComponentRequest] | None = None,
    sticker_ids: list[int | str] | None = None,
    flags: int | None = None,
    metadata: dict[str, object] | None = None,
    files: list[File] | None = None,
    **extras: Any,
) -> dict[str, Any]:
    data: message_types.CreateDMMessageRequest = {}
    if content is not None:
        data["content"] = content
    if tts is not None:
        data["tts"] = tts
    if nonce is not None:
        data["nonce"] = nonce
    if embeds is not None:
        data["embeds"] = embeds
    if allowed_mentions is not None:
        data["allowed_mentions"] = allowed_mentions
    if message_reference is not None:
        data["message_reference"] = message_reference
    if components is not None:
        data["components"] = components
    if sticker_ids is not None:
        data["sticker_ids"] = sticker_ids
    if flags is not None:
        data["flags"] = flags
    if metadata is not None:
        data["metadata"] = metadata

    for k, v in extras.items():
        if v:
            data[k] = v

    return get_multipart_payload(files=files, data=data)  # pyright: ignore[reportArgumentType]


class OAuth2HTTPClient(
    HTTPRateLimiterMixin,
    ApplicationHTTPClientMixin,
    ChannelHTTPClientMixin,
    ConnectionHTTPClientMixin,
    GuildHTTPClientMixin,
    InviteHTTPClientMixin,
    LobbyHTTPClientMixin,
    MemberHTTPClientMixin,
    MessageHTTPClientMixin,
    RelationshipHTTPClientMixin,
    StoreHTTPClientMixin,
    TokenHTTPClientMixin,
    UserHTTPClientMixin,
):
    API_BASE = "https://discord.com/api/v10"
    BASE_URL = "https://discord.com/oauth2/authorize"

    RETRYABLE_SERVER_STATUSES = frozenset({500, 502, 503, 504, 521, 522, 523, 524})
    CONNECTION_RESET_ERRNOS = frozenset({54, 10054})

    __get_client: Callable[[], Client]
    __slots__ = (
        "__get_client",
        "__session",
        "_auth",
        "_auto_refresh_token",
        "_bucket_hashes",
        "_buckets",
        "_global_over",
        "_store_token",
        "client_id",
        "current_scopes",
        "max_ratelimit_timeout",
        "max_retries",
        "redirect_uri",
        "state",
        "token",
    )

    def __init__(
        self,
        client: Client,
        *,
        client_id: int,
        client_secret: str,
        session: aiohttp.ClientSession = NotSet,
        max_retries: int = 5,
        max_ratelimit_timeout: float | None = None,
    ) -> None:
        self.__get_client = lambda: client

        self.client_id: int = client_id
        self.max_retries: int = max_retries
        self.max_ratelimit_timeout: float | None = max_ratelimit_timeout

        self._auth = aiohttp.BasicAuth(str(client_id), client_secret)
        self.__session: aiohttp.ClientSession | None = session or None

        self._init_ratelimiter()

        self.token: AccessTokenResponse | None = None

    async def close(self) -> None:
        if self.__session and not self.__session.closed:
            await self.__session.close()

    @staticmethod
    def _get_retry_delay(attempt: int) -> int:
        return 1 + attempt * 2

    def _parse_token(
        self,
        token: ValidToken | RefreshTokenAttr | RefreshTokenDict,
        *,
        refresh: bool = False,
    ) -> str:
        key = "access_token" if not refresh else "refresh_token"
        if isinstance(token, str):
            return token
        elif isinstance(token, dict) and key in token:
            return token[key]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        elif hasattr(token, key):
            return getattr(token, key)  # type: ignore
        else:
            raise ValueError("Invalid token type")

    async def __get_session(self) -> aiohttp.ClientSession:
        if not self.__session or self.__session.closed:
            self.__session = aiohttp.ClientSession()
        return self.__session

    def __get_token_header(
        self,
        token: ValidToken | RefreshTokenAttr | RefreshTokenDict,
    ) -> dict[Literal["Authorization"], str]:
        return {"Authorization": f"Bearer {self._parse_token(token)}"}

    def has_scopes(self, *scopes: Scope | str) -> bool:
        return all(Scope(scope) in self.current_scopes for scope in scopes)

    async def get_from_cdn(
        self,
        url: str,
    ) -> bytes:
        session = await self.__get_session()
        route = Route("GET", url)
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(route, await response.text(), response.status)
            return await response.read()

    async def request(
        self,
        route: Route,
        *,
        token: ValidToken | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        session = await self.__get_session()
        prepared_headers = headers or {}
        if token:
            prepared_headers.update(self.__get_token_header(token))  # type: ignore
        kwargs["headers"] = prepared_headers

        method = route.method
        url = route.get_constructed_url(self.API_BASE)

        async with self._acquire_ratelimit(method, url) as ratelimit_context:
            for attempt in range(self.max_retries):
                _log.debug(
                    "%s %s - attempt %d/%d",
                    method,
                    url,
                    attempt + 1,
                    self.max_retries,
                )
                try:
                    async with session.request(method, url=url, **kwargs) as response:
                        data = await json_or_text(response)
                        _log.debug(
                            "%s %s returned status %d",
                            method,
                            url,
                            response.status,
                        )

                        discord_hash = response.headers.get("X-RateLimit-Bucket")
                        has_ratelimit_headers = (
                            "X-RateLimit-Remaining" in response.headers
                        )
                        self._update_bucket_hash(
                            route_key=ratelimit_context.route_key,
                            current_bucket_key=ratelimit_context.bucket_key,
                            current_bucket_hash=ratelimit_context.bucket_hash,
                            discord_bucket_hash=discord_hash,
                            ratelimit=ratelimit_context.ratelimit,
                        )

                        if has_ratelimit_headers and response.status != 429:
                            ratelimit_context.ratelimit.update(response)
                            _log.debug(
                                "Rate limit updated: %d/%d remaining, resets in %.2fs",
                                ratelimit_context.ratelimit.remaining,
                                ratelimit_context.ratelimit.limit,
                                ratelimit_context.ratelimit.reset_after,
                            )

                        if 200 <= response.status < 300:
                            _log.debug("%s %s completed successfully", method, url)
                            if response.status == 204:
                                return None
                            if not isinstance(data, (dict, list)):
                                if not data:
                                    return None
                                raise TypeError(
                                    f"Expected dict or list, got {type(data).__name__}"
                                )
                            return data

                        if response.status == 429:
                            if not response.headers.get("Via") or isinstance(data, str):
                                _log.error(
                                    "Cloudflare ban detected on %s %s", method, url
                                )
                                raise create_http_exception(
                                    route, data, response.status
                                )
                            await self._handle_rate_limited_response(
                                method=method,
                                url=url,
                                data=data,
                                route=route,
                            )
                            continue

                        if response.status in self.RETRYABLE_SERVER_STATUSES:
                            if attempt < self.max_retries - 1:
                                sleep_time = self._get_retry_delay(attempt)
                                _log.warning(
                                    "Server error %d on %s %s, retrying in %ds",
                                    response.status,
                                    method,
                                    url,
                                    sleep_time,
                                )
                                await asyncio.sleep(sleep_time)
                                continue
                            _log.error(
                                "Server error %d on %s %s: %s",
                                response.status,
                                method,
                                url,
                                data,
                            )
                            raise create_http_exception(route, data, response.status)

                        _log.error(
                            "HTTP error %d on %s %s: %s",
                            response.status,
                            method,
                            url,
                            data,
                        )
                        raise create_http_exception(route, data, response.status)
                except OSError as e:
                    if (
                        attempt < self.max_retries - 1
                        and e.errno in self.CONNECTION_RESET_ERRNOS
                    ):
                        sleep_time = self._get_retry_delay(attempt)
                        _log.warning(
                            "Connection reset on %s %s, retrying in %ds",
                            method,
                            url,
                            sleep_time,
                        )
                        await asyncio.sleep(sleep_time)
                        continue
                    raise

        _log.error("Max retries exceeded for %s %s", method, url)
        raise HTTPException(route=route, response="Max retries exceeded", status=429)
