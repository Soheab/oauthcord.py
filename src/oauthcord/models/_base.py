from __future__ import annotations

from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    Literal,
    Self,
    overload,
)

from ..errors import MissingState
from ..utils import NotSet, _construct_model

if TYPE_CHECKING:
    from ..client._client import AuthorisedSession
    from ..internals.http import HTTPClient
    from ..internals.state import State


__all__ = ("BaseModel",)

type _PossibleKeys = str | tuple[str, ...] | None


class BaseModel[D: Any, R: Any = None]:
    __slots__ = ("__state", "data")

    def __init__(self, *, data: D, state: State | None = None) -> None:
        self.__state: State | None = state
        self.data: D = data
        self._initialize(data)

    def _initialize(self, data: D) -> None:
        pass

    def to_dict(self) -> R:
        return self.data  # pyright: ignore[reportReturnType]

    # Subclasses commonly override this with a narrower, hand-written signature
    # (extra keyword arguments, or a positional `client`), so the base signature
    # is deliberately permissive rather than a contract they must satisfy.
    @classmethod
    def from_dict(cls, data: D, *args: Any, **kwargs: Any) -> Self:
        """Construct this model from a payload."""
        return cls(*args, data=data, **kwargs)

    @property
    def _state(self) -> State:
        """The state this model was created with.

        Raises
        ------
        MissingState
            This model was constructed directly rather than from an API
            response, so it has no way to call back into the library.
        """
        if self.__state is None:
            raise MissingState(
                f"{type(self).__name__} was constructed directly and is not bound "
                "to a client, so it cannot perform API actions."
            )

        return self.__state

    @property
    def _http(self) -> HTTPClient:
        """:class:`HTTPClient`: The shared HTTP client.

        Raises
        ------
        MissingState
            This model is not bound to a client.
        """
        return self._state.http

    @property
    def _session(self) -> AuthorisedSession:
        """:class:`AuthorisedSession`: The authorised session this model came from.

        Raises
        ------
        MissingSession
            This model was not created from an authorised session.
        """
        return self._state.session

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

    @overload
    def _initialize_other[C: BaseModel[Any, Any]](
        self,
        cls: type[C],
        /,
        data: Any,
        *,
        optional: Literal[False] = ...,
        possible_keys: _PossibleKeys = ...,
        **extra_kwargs: Any,
    ) -> C: ...

    @overload
    def _initialize_other[C: BaseModel[Any, Any]](
        self,
        cls: type[C],
        /,
        data: Any | None,
        *,
        optional: Literal[True],
        possible_keys: _PossibleKeys = ...,
        **extra_kwargs: Any,
    ) -> C | None: ...

    def _initialize_other[C: BaseModel[Any, Any]](
        self,
        cls: type[C],
        /,
        data: Any | None,
        *,
        optional: bool = False,
        possible_keys: _PossibleKeys = None,
        **extra_kwargs: Any,
    ) -> C | None:
        if not data:
            if not optional:
                raise ValueError(
                    f"Data for {cls.__name__} is required but got {data!r}"
                )

            return None

        if not possible_keys:
            return _construct_model(cls, data=data, state=self.__state, **extra_kwargs)

        if isinstance(possible_keys, str):
            possible_keys = (possible_keys,)

        for key in possible_keys:
            value = data.get(key, NotSet)
            if value is NotSet or (value is None and optional):
                continue

            return _construct_model(cls, data=value, state=self.__state, **extra_kwargs)

        if optional:
            return None

        raise ValueError(
            f"Data for {cls.__name__} under any of {possible_keys!r} is required but none were found"
        )

    def get_asset[**P, AR](
        self,
        method: Callable[Concatenate["State | None", P], AR],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AR:
        """Build an :class:`Asset` bound to this model's state.

        Passes the state through unresolved, so constructing an asset never
        requires a client; only fetching one does.
        """
        return method(self.__state, *args, **kwargs)
