import io
import os
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self

if TYPE_CHECKING:
    from ..internals.http import OAuth2HTTPClient

__all__ = ("Asset",)


class Asset:
    """Represents a CDN asset and provides helper methods to transform and fetch it."""

    __slots__ = ("_animated", "_extension", "_http", "_key", "_size", "_url")

    BASE: ClassVar[str] = "https://cdn.discordapp.com"

    def __init__(
        self,
        http: OAuth2HTTPClient,
        *,
        url: str,
        key: str,
        extension: str,
        size: int,
        animated: bool = False,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self._http: OAuth2HTTPClient = http
        self._url: str = url
        self._animated: bool = animated
        self._extension: str = extension
        self._size: int = size
        self._key: str = key

    async def read(self) -> bytes:
        """Public method for working with this model."""
        return await self._http.get_from_cdn(self.url)

    async def save(
        self,
        fp: str | bytes | os.PathLike[Any] | io.BufferedIOBase,
        *,
        seek_begin: bool = True,
    ) -> int:
        """:class:`int`: Save the asset to a file-like object or path and return the number of bytes written."""
        data = await self.read()
        if isinstance(fp, io.BufferedIOBase):
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written
        else:
            with open(fp, "wb") as f:
                return f.write(data)

    @classmethod
    def _from_default_avatar(cls, http: OAuth2HTTPClient, index: int) -> Self:
        ext: str = "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/embed/avatars/{index}.{ext}?size={size}",
            key=str(index),
            animated=False,
            size=size,
            extension=ext,
        )

    @classmethod
    def _from_avatar(cls, http: OAuth2HTTPClient, user_id: int, avatar: str) -> Self:
        animated = avatar.startswith("a_")
        ext = "gif" if animated else "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/avatars/{user_id}/{avatar}.{ext}?size={size}",
            key=avatar,
            animated=animated,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_guild_avatar(
        cls, http: OAuth2HTTPClient, guild_id: int, member_id: int, avatar: str
    ) -> Self:
        animated = avatar.startswith("a_")
        ext = "gif" if animated else "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/guilds/{guild_id}/users/{member_id}/avatars/{avatar}.{ext}?size={size}",
            key=avatar,
            animated=animated,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_guild_banner(
        cls, http: OAuth2HTTPClient, guild_id: int, member_id: int, banner: str
    ) -> Self:
        animated = banner.startswith("a_")
        ext = "gif" if animated else "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/guilds/{guild_id}/users/{member_id}/banners/{banner}.{ext}?size={size}",
            key=banner,
            animated=animated,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_avatar_decoration(
        cls, http: OAuth2HTTPClient, avatar_decoration: str
    ) -> Self:
        ext = "png"
        size = 96
        return cls(
            http,
            url=f"{cls.BASE}/avatar-decoration-presets/{avatar_decoration}.png?size={size}",
            key=avatar_decoration,
            animated=True,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_icon(
        cls, http: OAuth2HTTPClient, object_id: int, icon_hash: str, path: str
    ) -> Self:
        ext = "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/{path}-icons/{object_id}/{icon_hash}.{ext}?size={size}",
            key=icon_hash,
            animated=False,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_app_icon(
        cls,
        http: OAuth2HTTPClient,
        object_id: int,
        icon_hash: str,
        asset_type: Literal["icon", "cover_image"],
    ) -> Self:
        ext = "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/app-icons/{object_id}/{asset_type}.png?size={size}",
            key=icon_hash,
            animated=False,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_cover_image(
        cls, http: OAuth2HTTPClient, object_id: int, cover_image_hash: str
    ) -> Self:
        ext = "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/app-assets/{object_id}/store/{cover_image_hash}.{ext}?size={size}",
            key=cover_image_hash,
            animated=False,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_guild_image(
        cls, http: OAuth2HTTPClient, guild_id: int, image: str, path: str
    ) -> Self:
        animated = image.startswith("a_")
        ext = "gif" if animated else "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/{path}/{guild_id}/{image}.{ext}?size={size}",
            key=image,
            animated=animated,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_guild_icon(
        cls, http: OAuth2HTTPClient, guild_id: int, icon_hash: str
    ) -> Self:
        animated = icon_hash.startswith("a_")
        ext = "gif" if animated else "png"
        size = 1024
        return cls(
            http,
            url=f"{cls.BASE}/icons/{guild_id}/{icon_hash}.{ext}?size={size}",
            key=icon_hash,
            animated=animated,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_user_banner(
        cls, http: OAuth2HTTPClient, user_id: int, banner_hash: str
    ) -> Self:
        animated = banner_hash.startswith("a_")
        ext = "gif" if animated else "png"
        size = 512
        return cls(
            http,
            url=f"{cls.BASE}/banners/{user_id}/{banner_hash}.{ext}?size={size}",
            key=banner_hash,
            animated=animated,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_primary_guild(
        cls, http: OAuth2HTTPClient, guild_id: int, icon_hash: str
    ) -> Self:
        ext = "png"
        size = 64
        return cls(
            http,
            url=f"{cls.BASE}/guild-tag-badges/{guild_id}/{icon_hash}.{ext}?size={size}",
            key=icon_hash,
            animated=False,
            extension=ext,
            size=size,
        )

    @classmethod
    def _from_user_collectible(
        cls, http: OAuth2HTTPClient, asset: str, animated: bool = False
    ) -> Self:
        ext = "webm" if animated else "png"
        size = 1024
        name = f"static.{ext}" if not animated else f"asset.{ext}"
        return cls(
            http,
            url=f"{cls.BASE}/assets/collectibles/{asset}{name}",
            key=asset,
            animated=animated,
            extension=ext,
            size=size,
        )

    def __str__(self) -> str:
        return self._url

    def __len__(self) -> int:
        return len(self._url)

    def __repr__(self) -> str:
        shorten = self._url.replace(self.BASE, "")
        return f"<Asset url={shorten!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Asset) and self._url == other._url

    def __hash__(self) -> int:
        return hash(self._url)

    @property
    def url(self) -> str:
        """:class:`str`: Returns the underlying URL of the asset."""
        return self._url

    @property
    def key(self) -> str:
        """:class:`str`: Returns the identifying key of the asset."""
        return self._key

    @property
    def extension(self) -> str:
        """:class:`str`: Returns the file extension of the asset."""
        return self._extension

    @extension.setter
    def extension(self, value: str) -> None:
        self._extension = value

    @property
    def size(self) -> int:
        """:class:`int`: Returns the size of the asset."""
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = value

    def is_animated(self) -> bool:
        """:class:`bool`: Returns whether the asset is animated."""
        return self._animated
