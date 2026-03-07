from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Concatenate, Self, TypeVar, final

if TYPE_CHECKING:
    from .internals.http import OAuth2HTTPClient

StatelessBaseModelT = TypeVar(
    "StatelessBaseModelT", bound="StatelessBaseModel[Any, Any]"
)


class StatelessBaseModel[D: Any, R: Any = None]:
    __slots__ = ("data",)

    def __init__(self, *, data: D) -> None:
        self.data: D = data
        self._initialize(data)

    def _initialize(self, data: D) -> None:
        pass

    def _to_request(self) -> R | None:
        pass

    @classmethod
    def _from_response(cls, data: D) -> Self:
        return cls(data=data)

    def _initialize_subclass[C: StatelessBaseModel[Any, Any]](
        self, cls: type[C], data: Any
    ) -> C:
        return cls(data=data)

    def get_asset[**P, AR](
        self,
        http: OAuth2HTTPClient,
        method: Callable[Concatenate[OAuth2HTTPClient, P], AR],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AR:
        return method(http, *args, **kwargs)


class BaseModel[D: Any, R: Any = None](StatelessBaseModel[D, R]):
    __slots__ = ("_http", "data")
    __check_slots__: bool = True

    def __init_subclass__(cls, check_slots: bool | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if check_slots is not None:
            cls.__check_slots__ = check_slots

    def __init__(self, *, http: OAuth2HTTPClient, data: D) -> None:
        self._http: OAuth2HTTPClient = http
        super().__init__(data=data)

    @final
    def _initialize_subclass_with_http[T: BaseModel[Any, Any]](
        self,
        cls: type[T],
        data: Any,
        key: str | None = None,
        *,
        on_key_error: Any | None = None,
    ) -> T:
        if not issubclass(cls, BaseModel):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"{cls} is not a subclass of BaseModel")

        if key:
            data = data.get(key, on_key_error) or on_key_error
        return cls(http=self._http, data=data)

    @final
    def _maybe_subclass_with_http[T: BaseModel[Any, Any]](
        self, cls: type[T], data: Any, key: str | None = None
    ) -> T | None:
        data = data if not key else data.get(key)
        if not data:
            return
        try:
            return cls(http=self._http, data=data)
        except KeyError:
            return None

    @final
    def get_asset[**P, AR](
        self,
        method: Callable[Concatenate[OAuth2HTTPClient, P], AR],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AR:
        return method(self._http, *args, **kwargs)
