import asyncio
import logging
from abc import ABC
from collections import deque
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import aiohttp

from ...errors import RateLimited

if TYPE_CHECKING:
    from .endpoints.base import Route

_log = logging.getLogger("http")


class Ratelimit:
    __slots__ = (
        "_lock",
        "_loop",
        "_max_ratelimit_timeout",
        "_pending",
        "dirty",
        "expires",
        "limit",
        "outgoing",
        "remaining",
        "reset_after",
    )

    def __init__(self, max_ratelimit_timeout: float | None = None) -> None:
        self.limit: int = 1
        self.remaining: int = self.limit
        self.outgoing: int = 0
        self.reset_after: float = 0.0
        self.expires: float | None = None
        self.dirty: bool = False
        self._max_ratelimit_timeout = max_ratelimit_timeout
        self._loop: asyncio.AbstractEventLoop | None = None
        self._pending: deque[asyncio.Future[Any]] = deque()
        self._lock: asyncio.Lock = asyncio.Lock()

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return self._loop

    def reset(self) -> None:
        self.remaining = self.limit - self.outgoing
        self.expires = None
        self.reset_after = 0.0
        self.dirty = False

    def update(self, response: aiohttp.ClientResponse) -> None:
        headers = response.headers

        self.limit = int(headers.get("X-RateLimit-Limit", 1))

        if self.dirty:
            self.remaining = min(
                int(headers.get("X-RateLimit-Remaining", 0)),
                self.limit - self.outgoing,
            )
        else:
            self.remaining = int(headers.get("X-RateLimit-Remaining", 0))
            self.dirty = True

        if reset_after := headers.get("X-RateLimit-Reset-After"):
            self.reset_after = float(reset_after)
        else:
            self.reset_after = 0.0

        self.expires = self._get_loop().time() + self.reset_after

    def is_expired(self) -> bool:
        if self.expires is None:
            return True
        return self._get_loop().time() > self.expires

    def time_until_reset(self) -> float:
        if self.expires is None:
            return 0.0
        return max(0.0, self.expires - self._get_loop().time())

    def _wake_next(self) -> None:
        while self._pending:
            future = self._pending.popleft()
            if not future.done():
                future.set_result(None)
                break

    def _wake(self, count: int = 1, *, exception: RateLimited | None = None) -> None:
        awoken = 0
        while self._pending:
            future = self._pending.popleft()
            if not future.done():
                if exception:
                    future.set_exception(exception)
                else:
                    future.set_result(None)
                awoken += 1

            if awoken >= count:
                break

    async def _refresh(self) -> None:
        error = (
            self._max_ratelimit_timeout is not None
            and self.reset_after > self._max_ratelimit_timeout
        )
        exception = (
            RateLimited({}, self.reset_after, is_global=False) if error else None
        )

        async with self._lock:
            if not error:
                _log.debug(
                    "Rate limit bucket sleeping for %.2f seconds", self.reset_after
                )
                await asyncio.sleep(self.reset_after)
                _log.debug("Rate limit bucket done sleeping")

        self.reset()
        _log.debug(
            "Rate limit bucket reset, waking %d pending requests", self.remaining
        )
        self._wake(self.remaining, exception=exception)

    async def acquire(self) -> None:
        loop = self._get_loop()

        if self.is_expired():
            _log.debug("Rate limit bucket expired, resetting")
            self.reset()

        if self._max_ratelimit_timeout is not None and self.expires is not None:
            current_reset_after = self.expires - loop.time()
            if current_reset_after > self._max_ratelimit_timeout:
                _log.warning(
                    "Rate limit timeout %.2fs exceeds max %.2fs, failing fast",
                    current_reset_after,
                    self._max_ratelimit_timeout,
                )
                raise RateLimited({}, current_reset_after, is_global=False)

        while self.remaining <= 0:
            if self.expires is None:
                _log.debug("No expiry info yet, proceeding with request")
                break

            wait_time = self.expires - loop.time()
            _log.debug(
                "Rate limit exhausted (remaining=%d), waiting %.2fs for reset",
                self.remaining,
                wait_time,
            )

            future: asyncio.Future[Any] = loop.create_future()
            self._pending.append(future)
            try:
                while not future.done():
                    max_wait = max(0.1, self.expires - loop.time())
                    await asyncio.wait([future], timeout=max_wait)
                    if not future.done():
                        await self._refresh()
            except Exception:
                future.cancel()
                if self.remaining > 0 and not future.cancelled():
                    self._wake_next()
                raise

        self.remaining -= 1
        self.outgoing += 1
        _log.debug(
            "Acquired rate limit token (remaining=%d, outgoing=%d)",
            self.remaining,
            self.outgoing,
        )

    def release(self) -> None:
        self.outgoing -= 1
        tokens = self.remaining - self.outgoing
        _log.debug(
            "Released rate limit token (remaining=%d, outgoing=%d, pending=%d)",
            self.remaining,
            self.outgoing,
            len(self._pending),
        )

        if not self._lock.locked():
            if tokens <= 0 and self._pending:
                _log.debug(
                    "No tokens available, scheduling refresh for pending requests"
                )
                asyncio.create_task(self._refresh())  # noqa: RUF006
            elif self._pending:
                exception = (
                    RateLimited({}, self.reset_after, is_global=False)
                    if self._max_ratelimit_timeout
                    and self.reset_after > self._max_ratelimit_timeout
                    else None
                )
                _log.debug(
                    "Waking %d pending requests", min(tokens, len(self._pending))
                )
                self._wake(tokens, exception=exception)

    def snapshot(self) -> dict[str, Any]:
        return {
            "limit": self.limit,
            "remaining": self.remaining,
            "reset_after": self.reset_after,
            "time_until_reset": self.time_until_reset(),
            "outgoing": self.outgoing,
            "pending": len(self._pending),
        }


@dataclass(slots=True, frozen=True)
class RatelimitContext:
    route_key: str
    bucket_hash: str | None
    bucket_key: str
    ratelimit: Ratelimit


class HTTPRateLimiterMixin(ABC):
    __slots__ = ()

    _bucket_hashes: dict[str, str]
    _buckets: dict[str, Ratelimit]
    _global_over: asyncio.Event | None
    max_ratelimit_timeout: float | None

    def _init_ratelimiter(self) -> None:
        self._bucket_hashes = {}
        self._buckets = {}
        self._global_over = None

    def _get_global_event(self) -> asyncio.Event:
        if self._global_over is None:
            self._global_over = asyncio.Event()
            self._global_over.set()
        return self._global_over

    def _get_route_key(self, method: str, path: str) -> str:
        return f"{method}:{path}"

    def _get_ratelimit(self, key: str) -> Ratelimit:
        try:
            return self._buckets[key]
        except KeyError:
            self._buckets[key] = Ratelimit(self.max_ratelimit_timeout)
            return self._buckets[key]

    def _get_bucket_for_route(self, route_key: str) -> Ratelimit | None:
        if bucket_hash := self._bucket_hashes.get(route_key):
            return self._buckets.get(bucket_hash)
        return self._buckets.get(route_key)

    def _get_bucket_key(self, route_key: str) -> str:
        return self._bucket_hashes.get(route_key, route_key)

    def _update_bucket_hash(
        self,
        *,
        route_key: str,
        current_bucket_key: str,
        current_bucket_hash: str | None,
        discord_bucket_hash: str | None,
        ratelimit: Ratelimit,
    ) -> None:
        if discord_bucket_hash is None or current_bucket_hash == discord_bucket_hash:
            return

        _log.debug(
            "Bucket hash for %s: %s -> %s",
            route_key,
            current_bucket_hash,
            discord_bucket_hash,
        )
        self._bucket_hashes[route_key] = discord_bucket_hash
        self._buckets[discord_bucket_hash] = ratelimit
        if (
            current_bucket_key != discord_bucket_hash
            and current_bucket_key in self._buckets
        ):
            del self._buckets[current_bucket_key]

    def get_ratelimit_snapshot(self) -> list[dict[str, Any]]:
        snapshot: list[dict[str, Any]] = []
        for key, bucket in self._buckets.items():
            state = bucket.snapshot()
            state["key"] = key
            snapshot.append(state)
        return snapshot

    async def _wait_for_global_ratelimit(self) -> None:
        global_event = self._get_global_event()
        if global_event.is_set():
            return

        _log.warning("Global rate limit active, waiting...")
        await global_event.wait()
        _log.debug("Global rate limit cleared, proceeding")

    @asynccontextmanager
    async def _acquire_ratelimit(
        self, method: str, path: str
    ) -> AsyncGenerator[RatelimitContext]:
        route_key = self._get_route_key(method, path)
        bucket_hash = self._bucket_hashes.get(route_key)
        bucket_key = self._get_bucket_key(route_key)
        ratelimit = self._get_ratelimit(bucket_key)

        await self._wait_for_global_ratelimit()
        _log.debug("%s %s - acquiring rate limit token", method, path)
        await ratelimit.acquire()
        try:
            yield RatelimitContext(
                route_key=route_key,
                bucket_hash=bucket_hash,
                bucket_key=bucket_key,
                ratelimit=ratelimit,
            )
        finally:
            ratelimit.release()

    async def _handle_rate_limited_response(
        self,
        *,
        route: Route,
        method: str,
        url: str,
        data: dict[str, Any] | list[Any] | str,
    ) -> None:
        retry_after = (
            float(data.get("retry_after", 1)) if isinstance(data, dict) else 1.0
        )
        is_global = isinstance(data, dict) and data.get("global", False)

        _log.warning(
            "Rate limited on %s %s (%s). Retry after %.2fs",
            method,
            url,
            "global" if is_global else "route",
            retry_after,
        )

        if (
            self.max_ratelimit_timeout is not None
            and retry_after > self.max_ratelimit_timeout
        ):
            _log.error(
                "Rate limit retry_after %.2fs exceeds max timeout %.2fs",
                retry_after,
                self.max_ratelimit_timeout,
            )
            raise RateLimited(route, data, retry_after, is_global=is_global)

        global_event = self._get_global_event()
        if is_global:
            _log.warning("Setting global rate limit lock")
            global_event.clear()

        try:
            _log.info("Sleeping %.2fs for rate limit...", retry_after)
            await asyncio.sleep(retry_after)
            _log.debug("Done sleeping, retrying request")
        finally:
            if is_global:
                _log.info("Clearing global rate limit lock")
                global_event.set()
