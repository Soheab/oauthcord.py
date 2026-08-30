from __future__ import annotations

import datetime
import re
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Protocol,
    overload,
)

from .enums import UnknownEnum

if TYPE_CHECKING:
    from .client import AuthorisedSession
    from .enums import Locale
    from .internals._types.token import (
        AccessTokenResponse as AccessTokenResponsePayload,
    )
    from .internals._types.token import (
        RefreshTokenResponse as RefreshTokenResponsePayload,
    )
    from .internals.state import State
    from .models._base import BaseModel
    from .models.access_token import AccessToken

__all__ = (
    "NotSet",
    "convert_snowflake",
    "id_to_datetime",
    "iso_to_datetime",
    "parse_invite",
    "to_enum",
)

DISCORD_EPOCH = 1420070400000


class _NotSet:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "..."

    def __str__(self) -> str:
        return "..."


NotSet: Any = _NotSet()


def _construct_model[T: BaseModel[Any, Any]](  # pyright: ignore[reportUnusedFunction]
    kls: type[T],
    /,
    *,
    data: Any,
    state: State | None = None,
    **extra_kwargs: Any,
) -> T:
    return kls(data=data, state=state, **extra_kwargs)


@overload
def to_enum[E: Enum](
    enum: type[E], value: Literal[None], /, *, unknown_ok: bool = ...
) -> None: ...


@overload
def to_enum[E: Enum](
    enum: type[E], value: str | int, /, *, unknown_ok: bool = ...
) -> E: ...


def to_enum[E: Enum](
    enum: type[E], value: str | int | None, /, *, unknown_ok: bool = True
) -> E | None:
    """Convert a raw value to a member of ``enum``.

    Parameters
    ----------
    enum: type[:class:`enum.Enum`]
        The enumeration to convert to.
    value: :class:`str` | :class:`int` | :data:`None`
        The raw value as returned by Discord. :data:`None` is passed through.
    unknown_ok: :class:`bool`
        Whether to wrap a value that is not a member of ``enum`` in an
        :class:`~oauthcord.enums.UnknownEnum` instead of raising. Defaults to
        ``True``, so that new values added by Discord never break parsing.

    Returns
    -------
    :class:`enum.Enum` | :data:`None`
        The matching member. If the value is unrecognised and ``unknown_ok``
        is ``True``, an :class:`~oauthcord.enums.UnknownEnum` standing in for
        that member is returned instead. It is typed as ``E`` so that model
        annotations stay readable; check with ``isinstance(value, UnknownEnum)``
        if you need to handle values Discord added after this library was
        released.

    Raises
    ------
    ValueError
        The value is not a member of ``enum`` and ``unknown_ok`` is ``False``.
    """
    if value is None:
        return None

    try:
        return enum(value)
    except ValueError:
        try:
            return enum[value]  # type: ignore
        except KeyError:
            if unknown_ok:
                # Typed as E so callers are not forced to union every
                # annotation with UnknownEnum; see the docstring.
                return UnknownEnum(value)  # pyright: ignore[reportReturnType]
            raise ValueError(f"{value} is not a valid {enum.__name__}") from None


def maybe_available[T: Any, D: Any = None](
    data: Any, key: str, obj: type[T], default: D = None
) -> T | D:
    try:
        return obj(data[key])
    except (KeyError, TypeError):
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
    value = data.get(key)
    if not value:
        if always_available:
            raise TypeError(
                f"Cannot get key {key!r} to convert to snowflake: key not found in data"
            )

        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        raise TypeError(
            f"Cannot convert value of {key!r}: {value!r} to snowflake: value is not an int or str"
        )


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


class AccessTokenAttr(Protocol):
    access_token: str


class RefreshTokenAttr(Protocol):
    refresh_token: str


type ValidAccessToken = (
    str | AccessTokenResponsePayload | AccessTokenAttr | AccessToken | AuthorisedSession
)

type ValidRefreshToken = (
    str
    | RefreshTokenResponsePayload
    | RefreshTokenAttr
    | AccessToken
    | AuthorisedSession
)


def _get_access_token(access_token: ValidAccessToken) -> str:  # pyright: ignore[reportUnusedFunction]
    if isinstance(access_token, str):
        return access_token

    if isinstance(access_token, dict):
        if "access_token" in access_token:
            return access_token["access_token"]
        raise TypeError(
            "Invalid access token payload. Expected a dict with an 'access_token' key."
        )

    if hasattr(access_token, "access_token"):
        return access_token.access_token  # type: ignore

    from .models.access_token import AccessToken

    if isinstance(access_token, AccessToken):
        return access_token.access_token

    from .client import AuthorisedSession

    if isinstance(access_token, AuthorisedSession):
        return access_token.token.access_token

    raise TypeError(
        "Invalid access token type. Expected str, dict, AccessToken, or AuthorisedSession."
    )


def _get_refresh_token(refresh_token: ValidRefreshToken) -> str:  # pyright: ignore[reportUnusedFunction]
    if isinstance(refresh_token, str):
        return refresh_token

    if isinstance(refresh_token, dict):
        if "refresh_token" in refresh_token:
            return refresh_token["refresh_token"]
        raise TypeError(
            "Invalid refresh token payload. Expected a dict with a 'refresh_token' key."
        )

    if hasattr(refresh_token, "refresh_token"):
        return refresh_token.refresh_token  # type: ignore

    from .models.access_token import AccessToken

    if isinstance(refresh_token, AccessToken):
        return refresh_token.refresh_token

    from .client import AuthorisedSession

    if isinstance(refresh_token, AuthorisedSession):
        return refresh_token.token.refresh_token

    raise TypeError(
        "Invalid refresh token type. Expected str, dict, AccessToken, or AuthorisedSession."
    )


INVITE_RE = re.compile(
    r"(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/(?P<code>[a-zA-Z0-9]+)/?",
    re.IGNORECASE,
)


def parse_invite(invite: str) -> str | None:
    """Parse an invite code or URL and return the invite code.

    Parameters
    ----------
    invite: :class:`str`
        The invite code or URL to parse.

    Returns
    -------
    :class:`str` | :data:`None`
        The invite code extracted from the input, or ``None`` if the
        input is not a valid invite code or URL.
    """
    match = INVITE_RE.fullmatch(invite.strip())
    return match and match.group("code")
