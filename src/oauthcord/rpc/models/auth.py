from __future__ import annotations

from typing import TYPE_CHECKING, override

from ...models._base import BaseModel
from ...models.access_token import AccessToken
from ...utils import convert_snowflake

if TYPE_CHECKING:
    from ...internals._types.current_auth_info import (
        CurrentAuthApplicationResponse,
        CurrentAuthUserResponse,
    )
    from ...internals._types.rpc.auth import AuthenticateResponse

__all__ = ("RPCAuthentication", "RPCAuthenticationApplication", "RPCAuthenticationUser")


class RPCAuthenticationApplication(BaseModel["CurrentAuthApplicationResponse"]):
    __slots__ = (
        "bot_public",
        "bot_require_code_grant",
        "description",
        "hook",
        "icon",
        "id",
        "name",
        "verify_key",
    )

    @override
    def _initialize(self, data: CurrentAuthApplicationResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.icon: str | None = data["icon"]
        self.description: str = data["description"]
        self.hook: bool = data["hook"]
        self.bot_public: bool = data["bot_public"]
        self.bot_require_code_grant: bool = data["bot_require_code_grant"]
        self.verify_key: str = data["verify_key"]


class RPCAuthenticationUser(BaseModel["CurrentAuthUserResponse"]):
    __slots__ = (
        "avatar",
        "discriminator",
        "global_name",
        "id",
        "public_flags",
        "username",
    )

    @override
    def _initialize(self, data: CurrentAuthUserResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.username: str = data["username"]
        self.avatar: str | None = data["avatar"]
        self.discriminator: str = data["discriminator"]
        self.public_flags: int = data["public_flags"]
        self.global_name: str | None = data["global_name"]


class RPCAuthentication(BaseModel["AuthenticateResponse"]):
    __slots__ = (
        "application",
        "token",
        "user",
    )

    @override
    def _initialize(self, data: AuthenticateResponse) -> None:
        self.token: AccessToken = self._initialize_other(AccessToken, data)

        self.application: RPCAuthenticationApplication = self._initialize_other(
            RPCAuthenticationApplication, data["application"]
        )
        self.user: RPCAuthenticationUser | None = self._initialize_other(
            RPCAuthenticationUser, data.get("user"), optional=True
        )
