import datetime
from typing import TYPE_CHECKING, Any, Literal, overload

if TYPE_CHECKING:
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
