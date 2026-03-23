from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake
from ._base import BaseModelWithSession
from .asset import Asset
from .flags import Permissions

if TYPE_CHECKING:
    from .channel import GuildChannel
    from ..internals._types.guild import CurrentUserGuildResponse as GuildPayload


__all__ = ("Guild",)


class Guild(BaseModelWithSession["GuildPayload"]):
    """Represents a Discord guild available to the authorized user."""

    __slots__ = ("banner", "features", "icon", "id", "name", "owner", "permissions")

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

    async def channels(self, *, permissions: bool = False) -> list[GuildChannel]:
        return await self._session.guild_channels(
            guild_id=self.id, permissions=permissions
        )
