from __future__ import annotations

import asyncio
import copy
import json
import logging
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

import aiohttp

from ..errors import HTTPException, RateLimited, create_http_exception
from ..utils import NotSet, _get_access_token
from ._ratelimiter import HTTPRateLimiterMixin, RatelimitContext
from ._types.http import RateLimitResponse
from .endpoints.application import ApplicationHTTPClientMixin
from .endpoints.base import (
    Route,
)
from .endpoints.channel import ChannelHTTPClientMixin
from .endpoints.connection import ConnectionHTTPClientMixin
from .endpoints.current_auth import CurrentAuthHTTPClientMixin
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
    from ..utils import ValidAccessToken
    from ._types import (
        components as component_types,
    )
    from ._types import (
        message as message_types,
    )
    from .endpoints.base import (
        ResponsePayload,
    )


_log = logging.getLogger("http")


@dataclass(slots=True, frozen=True)
class _RetryRequest:
    delay: float


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
    data: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    payload: dict[str, object] = dict(data) if data else {}
    if not files:
        if attachments is not None:
            payload["attachments"] = attachments.copy()
        return {"json": payload}

    form = aiohttp.FormData()

    prepared_files: list[tuple[bytes, str, str | None]] = []
    for file in files:
        data_bytes, filename = file.read()
        prepared_files.append((data_bytes, filename, file.description))

    payload_attachments = (attachments or []).copy()

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
    attachments: list[message_types.PartialAttachmentRequest] | None = None,
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

    payload: dict[str, object] = dict(data)
    payload.update({key: value for key, value in extras.items() if value is not None})

    return get_multipart_payload(attachments=attachments, files=files, data=payload)


class HTTPClient(
    HTTPRateLimiterMixin,
    ApplicationHTTPClientMixin,
    ChannelHTTPClientMixin,
    ConnectionHTTPClientMixin,
    CurrentAuthHTTPClientMixin,
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
    API_BASE: ClassVar[str] = "https://discord.com/api/v10"
    BASE_URL: ClassVar[str] = "https://discord.com/oauth2/authorize"
    CDN_URL: ClassVar[str] = "https://cdn.discordapp.com"

    RETRYABLE_SERVER_STATUSES: ClassVar[frozenset[int]] = frozenset({
        500,
        502,
        503,
        504,
        521,
        522,
        523,
        524,
    })
    RETRYABLE_ACCEPTED_CODES: ClassVar[frozenset[int]] = frozenset({110000, 110001})
    CONNECTION_RESET_ERRNOS: ClassVar[frozenset[int]] = frozenset({54, 104, 10054})

    __get_client: Callable[[], Client]
    __slots__ = (
        "__get_client",
        "__session",
        "_auth",
        "_auto_refresh_token",
        "_bucket_hashes",
        "_buckets",
        "_client_id",
        "_client_secret",
        "_global_expires",
        "_last_bucket_cleanup",
        "_session_provided",
        "_store_token",
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
        auto_refresh_token: bool = False,
    ) -> None:
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")
        if max_ratelimit_timeout is not None and max_ratelimit_timeout < 0:
            raise ValueError("max_ratelimit_timeout cannot be negative")

        self.__get_client = lambda: client

        self._client_id: int = client_id
        self._client_secret: str = client_secret
        self.max_retries: int = max_retries
        self.max_ratelimit_timeout: float | None = max_ratelimit_timeout
        self._auto_refresh_token: bool = auto_refresh_token

        self._auth = aiohttp.BasicAuth(str(client_id), client_secret)
        self.__session: aiohttp.ClientSession | None = session or None
        self._session_provided = session is not NotSet

        self._init_ratelimiter()

    @property
    def client_id(self) -> int:
        """:class:`int`: The client ID of the application associated with this HTTP client."""
        return self._client_id

    @property
    def client_secret(self) -> str:
        """:class:`str`: The client secret of the application associated with this HTTP client.

        This must be kept secret and should not be shared or exposed in client-side code.
        """
        return self._client_secret

    async def close(self) -> None:
        if self._session_provided:
            return

        if self.__session and not self.__session.closed:
            await self.__session.close()
            self.__session = None

    @staticmethod
    def _get_retry_delay(attempt: int) -> int:
        return 1 + attempt * 2

    @staticmethod
    def _parse_retry_after(value: object, *, default: float) -> float:
        try:
            retry_after = float(value)  # pyright: ignore[reportArgumentType]
        except (TypeError, ValueError):
            return default
        if not math.isfinite(retry_after) or retry_after < 0:
            return default
        return retry_after

    def _get_accepted_retry_after(
        self,
        status: int,
        data: ResponsePayload,
    ) -> float | None:
        if status != 202 or not isinstance(data, dict):
            return None

        code = data.get("code")
        if (
            not isinstance(code, int)
            or isinstance(code, bool)
            or code not in self.RETRYABLE_ACCEPTED_CODES
        ):
            return None

        return self._parse_retry_after(data.get("retry_after") or 5, default=5.0)

    async def __get_session(self) -> aiohttp.ClientSession:
        if self._session_provided:
            if not self.__session or self.__session.closed:
                raise RuntimeError(
                    "The provided aiohttp.ClientSession is closed. Please provide a valid session."
                )

            return self.__session

        if not self.__session or self.__session.closed:
            self.__session = aiohttp.ClientSession()
        return self.__session

    def __get_token_header(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    async def __get_token(self, token: ValidAccessToken) -> str:
        if isinstance(token, str):
            return token

        from ..models.access_token import AccessToken

        if isinstance(token, AccessToken):
            if self._auto_refresh_token:
                await token.refresh(check_expired=True)

            return token.access_token

        if isinstance(token, dict):
            if not self._auto_refresh_token:
                return _get_access_token(token)

            token = AccessToken.from_dict(self.__get_client(), token)
            await token.refresh(check_expired=True)
            return token.access_token

        from ..client import AuthorisedSession

        if isinstance(token, AuthorisedSession):
            if self._auto_refresh_token:
                await token.refresh(check_expired=True)

            return token.token.access_token

        return _get_access_token(token)

    async def get_from_cdn(
        self,
        url: str,
    ) -> bytes:
        url = url if url.startswith("https") else f"{self.CDN_URL}/{url.lstrip('/')}"
        session = await self.__get_session()
        route = Route("GET", url)
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(route, await response.text(), response.status)
            return await response.read()

    async def _prepare_request_authentication(
        self,
        token: ValidAccessToken | None,
        bot_token: str | None,
        headers: dict[str, str] | None,
    ) -> tuple[dict[str, str], str]:
        prepared_headers = dict(headers or {})
        if any(key.casefold() == "authorization" for key in prepared_headers):
            raise TypeError(
                "Pass authentication with 'token' or 'bot_token', not through headers"
            )
        if token is not None and bot_token is not None:
            raise TypeError("'token' and 'bot_token' are mutually exclusive")

        if token is not None:
            token_str = await self.__get_token(token)
            prepared_headers.update(self.__get_token_header(token_str))
            return prepared_headers, f"bearer:{token_str}"
        if bot_token is not None:
            prepared_headers["Authorization"] = f"Bot {bot_token}"
            return prepared_headers, f"bot:{bot_token}"
        return prepared_headers, ""

    def _update_ratelimit_from_response(
        self,
        context: RatelimitContext,
        response: aiohttp.ClientResponse,
    ) -> None:
        has_ratelimit_headers = "X-RateLimit-Remaining" in response.headers
        if has_ratelimit_headers and response.status != 429:
            context.ratelimit.update(response, generation=context.generation)

        self._update_bucket_hash(
            context,
            response.headers.get("X-RateLimit-Bucket"),
        )
        if has_ratelimit_headers and response.status != 429:
            _log.debug(
                "Rate limit updated: %d/%d remaining, resets in %.2fs",
                context.ratelimit.remaining,
                context.ratelimit.limit,
                context.ratelimit.reset_after,
            )

    def _handle_successful_response(
        self,
        route: Route,
        status: int,
        data: ResponsePayload,
    ) -> ResponsePayload | None:
        _log.debug("%s %s completed successfully", route.method, route.path)
        if status == 204:
            return None
        if not isinstance(data, (dict, list)):
            if not data:
                return None
            raise TypeError(f"Expected dict or list, got {type(data).__name__}")
        return data

    def _handle_429_response(
        self,
        route: Route,
        response: aiohttp.ClientResponse,
        data: ResponsePayload,
        context: RatelimitContext,
        attempt: int,
    ) -> _RetryRequest:
        if not response.headers.get("Via") or not isinstance(data, dict):
            _log.error("Cloudflare ban detected on %s %s", route.method, route.path)
            raise create_http_exception(route, data, response.status)

        rate_limit_data: RateLimitResponse = {
            "message": str(data.get("message", "Rate limit exceeded")),
            "retry_after": self._parse_retry_after(
                data.get(
                    "retry_after",
                    response.headers.get("Retry-After", 1),
                ),
                default=1.0,
            ),
            "global": bool(data.get("global", False)),
        }
        if isinstance(code := data.get("code"), int) and not isinstance(code, bool):
            rate_limit_data["code"] = code

        retry_after = self._handle_rate_limited_response(
            context,
            data=rate_limit_data,
        )
        if attempt >= self.max_retries - 1:
            raise RateLimited(
                route,
                retry_after,
                is_global=rate_limit_data["global"],
            )
        return _RetryRequest(retry_after)

    def _handle_response(
        self,
        route: Route,
        response: aiohttp.ClientResponse,
        data: ResponsePayload,
        attempt: int,
        context: RatelimitContext,
    ) -> ResponsePayload | _RetryRequest | None:
        if (
            accepted_retry_after := self._get_accepted_retry_after(
                response.status, data
            )
        ) is not None:
            if attempt >= self.max_retries - 1:
                raise create_http_exception(route, data, response.status)
            _log.debug(
                "%s %s is not ready, retrying in %.2fs",
                route.method,
                route.path,
                accepted_retry_after,
            )
            return _RetryRequest(accepted_retry_after)

        if 200 <= response.status < 300:
            return self._handle_successful_response(route, response.status, data)
        if response.status == 429:
            return self._handle_429_response(
                route,
                response,
                data,
                context,
                attempt,
            )
        if response.status in self.RETRYABLE_SERVER_STATUSES:
            if attempt < self.max_retries - 1:
                retry_after = self._get_retry_delay(attempt)
                _log.warning(
                    "Server error %d on %s %s, retrying in %ds",
                    response.status,
                    route.method,
                    route.path,
                    retry_after,
                )
                return _RetryRequest(retry_after)
            _log.error(
                "Server error %d on %s %s: %s",
                response.status,
                route.method,
                route.path,
                data,
            )
            raise create_http_exception(route, data, response.status)

        _log.error(
            "HTTP error %d on %s %s: %s",
            response.status,
            route.method,
            route.path,
            data,
        )
        raise create_http_exception(route, data, response.status)

    async def _perform_request(
        self,
        session: aiohttp.ClientSession,
        route: Route,
        url: str,
        authentication_key: str,
        attempt: int,
        kwargs: dict[str, Any],
    ) -> ResponsePayload | _RetryRequest | None:
        async with (
            self._acquire_ratelimit(route, authentication_key) as context,
            session.request(route.method, url=url, **kwargs) as response,
        ):
            data = await json_or_text(response)
            _log.debug(
                "%s %s returned status %d",
                route.method,
                route.path,
                response.status,
            )
            self._update_ratelimit_from_response(context, response)
            return self._handle_response(route, response, data, attempt, context)

    def _get_connection_retry_delay(
        self,
        error: aiohttp.ServerDisconnectedError | OSError,
        attempt: int,
    ) -> int | None:
        is_retryable = isinstance(error, aiohttp.ServerDisconnectedError) or (
            error.errno in self.CONNECTION_RESET_ERRNOS
        )
        if is_retryable and attempt < self.max_retries - 1:
            return self._get_retry_delay(attempt)
        return None

    @staticmethod
    def _prepare_attempt_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(kwargs.get("data"), aiohttp.FormData):
            return kwargs

        prepared_kwargs = kwargs.copy()
        prepared_kwargs["data"] = copy.deepcopy(kwargs["data"])
        return prepared_kwargs

    async def request(
        self,
        route: Route,
        *,
        token: ValidAccessToken | None = None,
        bot_token: str | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        params: dict[str, Any] = kwargs.get("params", {})
        if params:
            if not isinstance(params, dict):
                raise TypeError(
                    f"Expected dict for 'params', got {type(params).__name__}"
                )

            params = {
                key: str(value) if isinstance(value, (int, float)) else value
                for key, value in params.items()
                if value is not None
            }

        session = await self.__get_session()
        (
            prepared_headers,
            authentication_key,
        ) = await self._prepare_request_authentication(token, bot_token, headers)
        kwargs["headers"] = prepared_headers

        url = route.get_constructed_url(self.API_BASE)

        for attempt in range(self.max_retries):
            _log.debug(
                "%s %s - attempt %d/%d",
                route.method,
                route.path,
                attempt + 1,
                self.max_retries,
            )
            try:
                result = await self._perform_request(
                    session,
                    route,
                    url,
                    authentication_key,
                    attempt,
                    self._prepare_attempt_kwargs(kwargs),
                )
            except (aiohttp.ServerDisconnectedError, OSError) as error:
                retry_delay = self._get_connection_retry_delay(error, attempt)
                if retry_delay is None:
                    raise
                _log.warning(
                    "Connection reset on %s %s, retrying in %ds",
                    route.method,
                    route.path,
                    retry_delay,
                )
            else:
                if not isinstance(result, _RetryRequest):
                    return result

                retry_delay = result.delay

            await asyncio.sleep(retry_delay)

        raise RuntimeError("Request retry loop exited unexpectedly")
