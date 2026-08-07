from __future__ import annotations

from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    Literal,
    Protocol,
    Self,
    TypeVar,
    overload,
)

from ..utils import NotSet, _construct_model

if TYPE_CHECKING:
    from ..client._client import AuthorisedSession
    from ..internals.http import OAuth2HTTPClient


__all__ = (
    "BaseModel",
    "BaseModelWithHTTP",
    "BaseModelWithSession",
)

type _PossibleKeys = str | tuple[str, ...] | None

_BaseModelT_co = TypeVar("_BaseModelT_co", bound="BaseModel[Any, Any]", covariant=True)
_HTTPBaseModelT_co = TypeVar(
    "_HTTPBaseModelT_co", bound="BaseModelWithHTTP[Any, Any]", covariant=True
)
_SessionBaseModelT_co = TypeVar(
    "_SessionBaseModelT_co", bound="BaseModelWithSession[Any, Any]", covariant=True
)


class _BaseModelType(Protocol[_BaseModelT_co]):
    __name__: str

    def __call__(self, *, data: Any) -> _BaseModelT_co: ...


class _BaseModelWithHTTPType(Protocol[_HTTPBaseModelT_co]):
    __name__: str

    def __call__(self, *, data: Any, http: OAuth2HTTPClient) -> _HTTPBaseModelT_co: ...


class _BaseModelWithSessionType(Protocol[_SessionBaseModelT_co]):
    __name__: str

    def __call__(
        self, *, data: Any, session: AuthorisedSession
    ) -> _SessionBaseModelT_co: ...


class BaseModel[D: Any, R: Any = None]:
    __slots__ = ("data",)

    def __init__(self, *, data: D) -> None:
        self.data: D = data
        self._initialize(data)

    def _initialize(self, data: D) -> None:
        pass

    def to_dict(self) -> R:
        return self.data  # pyright: ignore[reportReturnType]

    @classmethod
    def from_dict(cls, data: D) -> Self:
        return cls(data=data)

    def __repr__(self) -> str:
        attributes = getattr(self, "__slots__") or [
            attr for attr in dir(self) if not attr.startswith("_")
        ]

        attributes = ", ".join(
            f"{attr}={value!r}"
            for attr in attributes
            if not attr.startswith("_") and not callable((value := getattr(self, attr)))
        )
        return f"{self.__class__.__name__}({attributes})"

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            return self.data[key]

    def _construct_other(
        self,
        cls: type[BaseModel[Any, Any]],
        /,
        data: Any | None,
        *,
        optional: bool = False,
        possible_keys: _PossibleKeys = None,
        extra_kwargs: dict[str, Any] | None = None,
    ) -> BaseModel[Any, Any] | None:
        if not data:
            if not optional:
                raise ValueError(
                    f"Data for {cls.__name__} is required but got {data!r}"
                )

            return None

        if extra_kwargs is None:
            extra_kwargs = {}

        if not possible_keys:
            return _construct_model(cls, data=data, **extra_kwargs)

        if isinstance(possible_keys, str):
            possible_keys = (possible_keys,)

        for key in possible_keys:
            value = data.get(key, NotSet)
            if value is NotSet or (value is None and optional):
                continue

            return _construct_model(cls, data=value, **extra_kwargs)

        if optional:
            return None
        raise ValueError(
            f"Data for {cls.__name__} under any of {possible_keys!r} is required but none were found"
        )

    @overload
    def _initialize_other(
        self: BaseModel[Any, Any],
        cls: _BaseModelType[_BaseModelT_co],
        /,
        data: Any,
        *,
        optional: Literal[False] = ...,
        possible_keys: _PossibleKeys = ...,
    ) -> _BaseModelT_co: ...

    @overload
    def _initialize_other(
        self: BaseModel[Any, Any],
        cls: _BaseModelType[_BaseModelT_co],
        /,
        data: Any | None,
        *,
        optional: Literal[True],
        possible_keys: _PossibleKeys = ...,
    ) -> _BaseModelT_co | None: ...

    def _initialize_other(
        self: BaseModel[Any, Any],
        cls: _BaseModelType[BaseModel[Any, Any]],
        /,
        data: Any | None,
        *,
        optional: bool = False,
        possible_keys: _PossibleKeys = None,
    ) -> BaseModel[Any, Any] | None:
        return self._construct_other(
            cls,  # pyright: ignore[reportArgumentType]
            data,
            optional=optional,
            possible_keys=possible_keys,
        )


class BaseModelWithHTTP[D: Any, R: Any = None](BaseModel[D, R]):
    __slots__ = (*BaseModel.__slots__, "_http")

    def __init__(self, *, data: D, http: OAuth2HTTPClient) -> None:
        self._http = http
        super().__init__(data=data)

    @overload
    def _initialize_other(
        self: BaseModelWithHTTP[Any, Any],
        cls: _BaseModelType[_BaseModelT_co],
        /,
        data: Any,
        *,
        optional: Literal[False] = ...,
        possible_keys: _PossibleKeys = ...,
    ) -> _BaseModelT_co: ...

    @overload
    def _initialize_other(
        self: BaseModelWithHTTP[Any, Any],
        cls: _BaseModelType[_BaseModelT_co],
        /,
        data: Any | None,
        *,
        optional: Literal[True],
        possible_keys: _PossibleKeys = ...,
    ) -> _BaseModelT_co | None: ...

    @overload
    def _initialize_other(
        self: BaseModelWithHTTP[Any, Any],
        cls: _BaseModelWithHTTPType[_HTTPBaseModelT_co],
        /,
        data: Any,
        *,
        optional: Literal[False] = ...,
        possible_keys: _PossibleKeys = ...,
    ) -> _HTTPBaseModelT_co: ...

    @overload
    def _initialize_other(
        self: BaseModelWithHTTP[Any, Any],
        cls: _BaseModelWithHTTPType[_HTTPBaseModelT_co],
        /,
        data: Any | None,
        *,
        optional: Literal[True],
        possible_keys: _PossibleKeys = ...,
    ) -> _HTTPBaseModelT_co | None: ...

    def _initialize_other(
        self: BaseModelWithHTTP[Any, Any],
        cls: (
            _BaseModelType[BaseModel[Any, Any]]
            | _BaseModelWithHTTPType[BaseModelWithHTTP[Any, Any]]
        ),
        /,
        data: Any | None,
        *,
        optional: bool = False,
        possible_keys: _PossibleKeys = None,
    ) -> BaseModel[Any, Any] | None:
        extra_kwargs: dict[str, Any] = {}
        if issubclass(cls, BaseModelWithHTTP):  # pyright: ignore[reportArgumentType]
            extra_kwargs["http"] = self._http

        return self._construct_other(
            cls,  # pyright: ignore[reportArgumentType]
            data,
            optional=optional,
            possible_keys=possible_keys,
            extra_kwargs=extra_kwargs,
        )

    def get_asset[**P, AR](
        self,
        method: Callable[Concatenate[OAuth2HTTPClient, P], AR],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AR:
        return method(self._http, *args, **kwargs)


class BaseModelWithSession[D: Any, R: Any = None](BaseModel[D, R]):
    __slots__ = (
        *BaseModel.__slots__,
        "_session",
    )

    def __init__(self, *, data: D, session: AuthorisedSession) -> None:
        self._session = session
        super().__init__(data=data)

    @overload
    def _initialize_other(
        self: BaseModelWithSession[Any, Any],
        cls: _BaseModelType[_BaseModelT_co],
        /,
        data: Any,
        *,
        optional: Literal[False] = ...,
        possible_keys: _PossibleKeys = ...,
    ) -> _BaseModelT_co: ...

    @overload
    def _initialize_other(
        self: BaseModelWithSession[Any, Any],
        cls: _BaseModelType[_BaseModelT_co],
        /,
        data: Any | None,
        *,
        optional: Literal[True],
        possible_keys: _PossibleKeys = ...,
    ) -> _BaseModelT_co | None: ...

    @overload
    def _initialize_other(
        self: BaseModelWithSession[Any, Any],
        cls: _BaseModelWithHTTPType[_HTTPBaseModelT_co],
        /,
        data: Any,
        *,
        optional: Literal[False] = ...,
        possible_keys: _PossibleKeys = ...,
    ) -> _HTTPBaseModelT_co: ...

    @overload
    def _initialize_other(
        self: BaseModelWithSession[Any, Any],
        cls: _BaseModelWithHTTPType[_HTTPBaseModelT_co],
        /,
        data: Any | None,
        *,
        optional: Literal[True],
        possible_keys: _PossibleKeys = ...,
    ) -> _HTTPBaseModelT_co | None: ...

    @overload
    def _initialize_other(
        self: BaseModelWithSession[Any, Any],
        cls: _BaseModelWithSessionType[_SessionBaseModelT_co],
        /,
        data: Any,
        *,
        optional: Literal[False] = ...,
        possible_keys: _PossibleKeys = ...,
    ) -> _SessionBaseModelT_co: ...

    @overload
    def _initialize_other(
        self: BaseModelWithSession[Any, Any],
        cls: _BaseModelWithSessionType[_SessionBaseModelT_co],
        /,
        data: Any | None,
        *,
        optional: Literal[True],
        possible_keys: _PossibleKeys = ...,
    ) -> _SessionBaseModelT_co | None: ...

    def _initialize_other(
        self: BaseModelWithSession[Any, Any],
        cls: (
            _BaseModelType[BaseModel[Any, Any]]
            | _BaseModelWithHTTPType[BaseModelWithHTTP[Any, Any]]
            | _BaseModelWithSessionType[BaseModelWithSession[Any, Any]]
        ),
        /,
        data: Any | None,
        *,
        optional: bool = False,
        possible_keys: _PossibleKeys = None,
    ) -> BaseModel[Any, Any] | None:
        extra_kwargs: dict[str, Any] = {}
        if issubclass(cls, BaseModelWithHTTP):  # pyright: ignore[reportArgumentType]
            extra_kwargs["http"] = self._session.client.http
        elif issubclass(cls, BaseModelWithSession):  # pyright: ignore[reportArgumentType]
            extra_kwargs["session"] = self._session

        return self._construct_other(
            cls,  # pyright: ignore[reportArgumentType]
            data,
            optional=optional,
            possible_keys=possible_keys,
            extra_kwargs=extra_kwargs,
        )

    def get_asset[**P, AR](
        self,
        method: Callable[Concatenate[OAuth2HTTPClient, P], AR],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AR:
        return method(self._session.client.http, *args, **kwargs)
