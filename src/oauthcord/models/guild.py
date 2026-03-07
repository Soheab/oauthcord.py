from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake
from ._base import BaseModel
from .asset import Asset
from .flags import Permissions

if TYPE_CHECKING:
    from .channel import GuildChannel
    from .internals._types.guild import CurrentUserGuildResponse as GuildPayload
    from .internals.http import ValidToken


__all__ = ("Guild",)


@BaseModel.add_slots("id", "name", "icon", "banner", "owner", "permissions", "features")
class Guild(BaseModel["GuildPayload"]):
    """Represents a Discord guild available to the authorized user."""

    @override
    def _initialize(self, data: GuildPayload) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]

        icon = data["icon"]
        self.icon: Asset | None = (
            self.get_asset(Asset._from_guild_icon, self.id, icon) if icon else None
        )

        banner = data["banner"]
        self.banner: Asset | None = (
            self.get_asset(Asset._from_guild_image, self.id, banner, "banners")
            if banner
            else None
        )

        self.owner: bool = data["owner"]
        self.permissions: Permissions = Permissions(int(data["permissions"]))
        self.features: list[str] = data["features"]

    async def get_channels(
        self, token: ValidToken, *, permissions: bool = False
    ) -> list[GuildChannel]:
        return await self._http.__get_client().guild_channels(
            token=token, guild_id=self.id, permissions=permissions
        )
