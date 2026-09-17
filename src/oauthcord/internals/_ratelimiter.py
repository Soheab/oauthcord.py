from __future__ import annotations

import asyncio
import logging
from collections import deque
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import aiohttp

from ..errors import RateLimited
from .endpoints.base import Route

if TYPE_CHECKING:
    from ._types.http import RateLimitResponse


_log = logging.getLogger("http")


class _RatelimitTimeout(Exception):
    __slots__ = ("retry_after",)

    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        super().__init__(retry_after)


class Ratelimit:
    __slots__ = (
        "_generation",
        "_last_used",
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
        self._generation: int = 0
        self._last_used: float = 0.0

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return self._loop

    def reset(self) -> None:
        self.remaining = self.limit - self.outgoing
        self.expires = None
        self.reset_after = 0.0
        self.dirty = False
        self._generation += 1

    def hit_429(self, retry_after: float) -> None:
        """Mark this bucket as exhausted after a 429 response for its route."""
        now = self._get_loop().time()
        self.expires = max(self.expires or 0.0, now + retry_after)
        self.reset_after = self.expires - now
        self.remaining = 0
        self.dirty = True

    def is_inactive(self) -> bool:
        if self.outgoing > 0 or self._pending:
            return False
        if not self.is_expired():
            # Still inside a known cooldown window (e.g. a long 429 retry_after) -
            # evicting now would make the next request start from a fresh,
            # falsely-optimistic bucket and immediately re-trigger the limit.
            return False
        return (self._get_loop().time() - self._last_used) >= 60

    def update(
        self, response: aiohttp.ClientResponse, *, generation: int | None = None
    ) -> None:
        if generation is not None and generation != self._generation:
            return
        headers = response.headers
        self._last_used = self._get_loop().time()

        self.limit = int(headers.get("X-RateLimit-Limit", 1))

        if self.dirty:
            self.remaining = min(
                self.remaining,
                int(headers.get("X-RateLimit-Remaining", 0)),
                self.limit - self.outgoing,
            )
        else:
            self.remaining = int(headers.get("X-RateLimit-Remaining", 0))
            self.dirty = True

        self.expires = max(
            self.expires or 0.0,
            self._last_used + float(headers.get("X-RateLimit-Reset-After", 0.0)),
        )
        self.reset_after = self.expires - self._last_used

    def is_expired(self) -> bool:
        if self.expires is None:
            return True
        return self._get_loop().time() >= self.expires

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

    def _wake(self, count: int = 1, *, exception: BaseException | None = None) -> None:
        if count <= 0:
            return
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
        generation = self._generation
        async with self._lock:
            while generation == self._generation:
                delay = self.time_until_reset()
                if (
                    self._max_ratelimit_timeout is not None
                    and delay > self._max_ratelimit_timeout
                ):
                    self._wake(
                        len(self._pending),
                        exception=_RatelimitTimeout(delay),
                    )
                    return
                if delay <= 0:
                    self.reset()
                    self._wake(self.remaining)
                    return
                await asyncio.sleep(delay)

    async def acquire(self) -> None:
        loop = self._get_loop()

        if self.expires is not None and self.is_expired():
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
                raise _RatelimitTimeout(current_reset_after)

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
                    max_wait = self.time_until_reset()
                    await asyncio.wait([future], timeout=max_wait)
                    if not future.done():
                        await self._refresh()
                future.result()
            except (Exception, asyncio.CancelledError):
                future.cancel()
                if future in self._pending:
                    self._pending.remove(future)
                if self.remaining > 0 and not future.cancelled():
                    self._wake_next()
                raise

        self.remaining -= 1
        self.outgoing += 1
        self._last_used = loop.time()
        _log.debug(
            "Acquired rate limit token (remaining=%d, outgoing=%d)",
            self.remaining,
            self.outgoing,
        )

    def release(self) -> None:
        self.outgoing -= 1
        tokens = self.remaining
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
                _log.debug(
                    "Waking %d pending requests", min(tokens, len(self._pending))
                )
                self._wake(tokens)

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
    route: Route
    authentication_key: str
    route_key: str
    bucket_key: str
    ratelimit: Ratelimit
    generation: int


_BUCKET_CLEANUP_INTERVAL = 60.0


class HTTPRateLimiterMixin:
    __slots__ = ()

    _bucket_hashes: dict[str, str]
    _buckets: dict[str, Ratelimit]
    _global_expires: dict[str, float]
    _last_bucket_cleanup: float
    max_ratelimit_timeout: float | None

    def _init_ratelimiter(self) -> None:
        self._bucket_hashes = {}
        self._buckets = {}
        self._global_expires = {}
        self._last_bucket_cleanup = 0.0

    def _cleanup_stale_buckets(self) -> None:
        loop = asyncio.get_running_loop()
        now = loop.time()
        if now - self._last_bucket_cleanup < _BUCKET_CLEANUP_INTERVAL:
            return
        self._last_bucket_cleanup = now
        self._global_expires = {
            key: deadline
            for key, deadline in self._global_expires.items()
            if deadline > now
        }

        stale_keys = [
            key for key, bucket in self._buckets.items() if bucket.is_inactive()
        ]
        for key in stale_keys:
            del self._buckets[key]

        if stale_keys:
            _log.debug(
                "Cleaned up %d stale rate limit bucket(s), %d remaining",
                len(stale_keys),
                len(self._buckets),
            )

        stale_routes = [
            route_key
            for route_key, bucket_hash in self._bucket_hashes.items()
            if bucket_hash not in self._buckets
        ]
        for route_key in stale_routes:
            del self._bucket_hashes[route_key]

    def _get_route_key(self, route: Route, authentication_key: str = "") -> str:
        return (
            f"{route.method}:{route.path}:{route.major_parameters}:{authentication_key}"
        )

    def _get_ratelimit(self, key: str) -> Ratelimit:
        try:
            return self._buckets[key]
        except KeyError:
            self._buckets[key] = Ratelimit(self.max_ratelimit_timeout)
            return self._buckets[key]

    def _get_bucket_for_route(self, route_key: str) -> Ratelimit | None:
        return self._buckets.get(self._get_bucket_key(route_key))

    def _get_bucket_key(self, route_key: str) -> str:
        return self._bucket_hashes.get(route_key, route_key)

    def _update_bucket_hash(
        self,
        context: RatelimitContext,
        discord_bucket_hash: str | None,
    ) -> None:
        if discord_bucket_hash is None:
            return

        scoped_bucket_key = (
            f"{discord_bucket_hash}:{context.authentication_key}:"
            f"{context.route.major_parameters}"
        )
        if context.bucket_key == scoped_bucket_key:
            return

        _log.debug(
            "Discovered rate limit bucket for %s %s",
            context.route.method,
            context.route.path,
        )
        self._bucket_hashes[context.route_key] = scoped_bucket_key
        existing = self._buckets.setdefault(scoped_bucket_key, context.ratelimit)
        if existing is not context.ratelimit and context.ratelimit.dirty:
            # Responses from a newly discovered alias must not erase a cooldown
            # already learned from another route sharing this bucket.
            if existing.is_expired():
                existing.reset()
                existing.limit = context.ratelimit.limit
                existing.remaining = max(
                    0, context.ratelimit.remaining - existing.outgoing
                )
            else:
                existing.remaining = min(
                    existing.remaining, context.ratelimit.remaining
                )
            existing.dirty = True
            existing.expires = max(
                existing.expires or 0, context.ratelimit.expires or 0
            )
            existing.reset_after = existing.time_until_reset()
        if (
            context.bucket_key != scoped_bucket_key
            and context.bucket_key in self._buckets
            and context.bucket_key not in self._bucket_hashes.values()
        ):
            del self._buckets[context.bucket_key]

    def get_ratelimit_snapshot(self) -> list[dict[str, Any]]:
        snapshot: list[dict[str, Any]] = []
        seen: set[int] = set()
        for bucket in self._buckets.values():
            bucket_identity = id(bucket)
            if bucket_identity in seen:
                continue
            seen.add(bucket_identity)
            state = bucket.snapshot()
            state["key"] = f"bucket:{len(snapshot)}"
            snapshot.append(state)
        return snapshot

    async def _wait_for_global_ratelimit(
        self, route: Route, authentication_key: str = ""
    ) -> None:
        key = authentication_key
        loop = asyncio.get_running_loop()
        while True:
            if (deadline := self._global_expires.get(key)) is not None:
                delay = deadline - loop.time()
                if delay > 0:
                    if (
                        self.max_ratelimit_timeout is not None
                        and delay > self.max_ratelimit_timeout
                    ):
                        raise RateLimited(route, delay, is_global=True)
                    await asyncio.sleep(delay)
                    continue
                del self._global_expires[key]
            return

    @asynccontextmanager
    async def _acquire_ratelimit(
        self, route: Route, authentication_key: str = ""
    ) -> AsyncGenerator[RatelimitContext]:
        self._cleanup_stale_buckets()

        route_key = self._get_route_key(route, authentication_key)
        while True:
            await self._wait_for_global_ratelimit(route, authentication_key)
            bucket_key = self._get_bucket_key(route_key)
            ratelimit = self._get_ratelimit(bucket_key)
            _log.debug("%s %s - acquiring rate limit token", route.method, route.path)
            try:
                await ratelimit.acquire()
            except _RatelimitTimeout as error:
                raise RateLimited(route, error.retry_after) from error
            deadline = self._global_expires.get(authentication_key)
            if deadline is not None:
                if deadline > asyncio.get_running_loop().time():
                    ratelimit.release()
                    continue
                del self._global_expires[authentication_key]
            if self._get_bucket_for_route(route_key) is ratelimit:
                break
            # Discovery may have changed the route's bucket while we waited.
            ratelimit.release()
        try:
            yield RatelimitContext(
                route=route,
                authentication_key=authentication_key,
                route_key=route_key,
                bucket_key=bucket_key,
                ratelimit=ratelimit,
                generation=ratelimit._generation,
            )
        finally:
            ratelimit.release()

    def _handle_rate_limited_response(
        self,
        context: RatelimitContext,
        data: RateLimitResponse,
    ) -> float:
        retry_after = float(data.get("retry_after", 1))
        is_global = data.get("global", False)

        _log.warning(
            "Rate limited on %s %s (%s). Retry after %.2fs",
            context.route.method,
            context.route.path,
            "global" if is_global else "route",
            retry_after,
        )

        if not is_global:
            context.ratelimit.hit_429(retry_after)
            if (
                shared := self._get_bucket_for_route(context.route_key)
            ) is not None and shared is not context.ratelimit:
                shared.hit_429(max(retry_after, shared.time_until_reset()))
        else:
            key = context.authentication_key
            self._global_expires[key] = max(
                self._global_expires.get(key, 0.0),
                asyncio.get_running_loop().time() + retry_after,
            )

        if (
            self.max_ratelimit_timeout is not None
            and retry_after > self.max_ratelimit_timeout
        ):
            raise RateLimited(context.route, retry_after, is_global=is_global)

        return retry_after
