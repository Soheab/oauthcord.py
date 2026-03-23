from typing import TYPE_CHECKING

from ...utils import NotSet
from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import user as user_types
    from .base import ValidToken


class UserHTTPClientMixin(BaseHTTPClient):
    async def modify_current_user_account(
        self,
        token: ValidToken,
        *,
        global_name: str | None = NotSet,
    ) -> user_types.ModifyCurrentUserAccountResponse:
        data: user_types.ModifyCurrentUserAccountRequest = {}
        if global_name is not NotSet:
            data["global_name"] = global_name

        return await self.request(
            Route("PATCH", "/users/@me/account"),
            token=token,
            data=data,
        )

    async def get_current_user(
        self,
        token: ValidToken,
    ) -> user_types.CurrentUserResponse:
        return await self.request(
            Route("GET", "/users/@me"),
            token=token,
        )

    async def get_user_harvest(
        self,
        token: ValidToken,
    ) -> user_types.GetUserHarvestResponse:
        return await self.request(
            Route("GET", "/users/@me/harvest"),
            token=token,
        )

    async def create_user_harvest(
        self,
        token: ValidToken,
        *,
        backends: list[str] | None = None,
        email: str | None = None,
    ) -> user_types.CreateUserHarvestResponse:
        data: user_types.CreateUserHarvestRequest = {}
        if backends is not None:
            data["backends"] = backends
        if email is not None:
            data["email"] = email

        return await self.request(
            Route("POST", "/users/@me/harvest"),
            token=token,
            data=data,
        )
