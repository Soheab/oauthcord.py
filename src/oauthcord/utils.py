import datetime
from typing import TYPE_CHECKING, Any, Literal, Protocol, overload

if TYPE_CHECKING:
    from .client import AuthorisedSession
    from .client._base import _AuthorisedSessionProto
    from .internals.http import OAuth2HTTPClient
    from .models._base import BaseModel, BaseModelWithHTTP, BaseModelWithSession
    from .models.enums import Locale

DISCORD_EPOCH = 1420070400000


class _NotSet:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "..."

    def __str__(self) -> str:
        return "..."


NotSet: Any = _NotSet()


class _BaseModelType[T: BaseModel[Any, Any]](Protocol):
    def __call__(self, *, data: Any) -> T: ...


class _BaseModelWithHTTPType[T: BaseModelWithHTTP[Any, Any]](Protocol):
    def __call__(self, *, data: Any, http: OAuth2HTTPClient) -> T: ...


class _BaseModelWithSessionType[T: BaseModelWithSession[Any, Any]](Protocol):
    def __call__(self, *, data: Any, session: AuthorisedSession) -> T: ...


@overload
def _construct_model[T: BaseModel[Any, Any]](  # pyright: ignore[reportUnusedFunction]
    kls: _BaseModelType[T],
    /,
    *,
    data: Any,
) -> T: ...


@overload
def _construct_model[T: BaseModelWithHTTP[Any, Any]](  # pyright: ignore[reportUnusedFunction]
    kls: _BaseModelWithHTTPType[T],
    /,
    *,
    data: Any,
    http: OAuth2HTTPClient,
) -> T: ...


@overload
def _construct_model[T: BaseModelWithSession[Any, Any]](  # pyright: ignore[reportUnusedFunction]
    kls: _BaseModelWithSessionType[T],
    /,
    *,
    data: Any,
    session: AuthorisedSession | _AuthorisedSessionProto,
) -> T: ...


def _construct_model(  # pyright: ignore[reportUnusedFunction]
    kls: (
        _BaseModelType[BaseModel[Any, Any]]
        | _BaseModelWithHTTPType[BaseModelWithHTTP[Any, Any]]
        | _BaseModelWithSessionType[BaseModelWithSession[Any, Any]]
    ),
    /,
    *,
    data: Any,
    session: AuthorisedSession | _AuthorisedSessionProto | None = None,
    http: OAuth2HTTPClient | None = None,
) -> BaseModel[Any, Any]:
    extra_kwargs: dict[str, Any] = {}
    if session is not None:
        extra_kwargs["session"] = session
    if http is not None:
        extra_kwargs["http"] = http

    return kls(data=data, **extra_kwargs)


def maybe_available[T: Any, D: Any = None](
    data: Any, key: str, obj: type[T], default: D = None
) -> T | D:
    try:
        return obj(data[key])
    except KeyError, TypeError:
        return default


@overload
def convert_snowflake(data: Any, key: str, always_available: Literal[True]) -> int: ...


@overload
def convert_snowflake(
    data: Any, key: str, always_available: Literal[False]
) -> int | None: ...


@overload
def convert_snowflake(
    data: Any,
    key: str,
) -> int: ...


def convert_snowflake(data: Any, key: str, always_available: bool = True) -> int | None:
    try:
        return int(data[key])
    except KeyError, TypeError, ValueError:
        if always_available:
            raise TypeError(f"Missing or invalid snowflake for key: {key}")
        return None


@overload
def iso_to_datetime(iso: None) -> None: ...


@overload
def iso_to_datetime(iso: str) -> datetime.datetime: ...


@overload
def iso_to_datetime(iso: str | None) -> datetime.datetime | None: ...


def iso_to_datetime(iso: str | None) -> datetime.datetime | None:
    if not iso:
        return None
    return datetime.datetime.fromisoformat(
        iso,
    ).replace(tzinfo=datetime.UTC)


def id_to_datetime(id: int) -> datetime.datetime:
    timestamp = ((id >> 22) + DISCORD_EPOCH) / 1000
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)


def _serialize_localizations(  # pyright: ignore[reportUnusedFunction]
    data: dict[Locale, str],
) -> dict[str, str]:
    return {locale.value: value for locale, value in data.items()}
