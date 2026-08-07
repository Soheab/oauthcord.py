from __future__ import annotations

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
        path: str,
        key: str,
        size: int,
        animated: bool | None = None,
        extension: str | None = None,
        sized: bool = True,
    ) -> None:
        """Initialize this object from explicit constructor arguments."""
        self._http: OAuth2HTTPClient = http
        self._animated: bool = key.startswith("a_") if animated is None else animated
        self._extension: str = extension or ("webp" if self._animated else "png")
        self._size: int = size
        self._key: str = key

        self._url: str = f"{self.BASE}/{path}.{self._extension}"
        if sized:
            query = f"size={size}" + ("&animated=true" if self._animated else "")
            self._url += f"?{query}"

    async def read(self) -> bytes:
        """:class:`bytes`: Read the asset from the CDN and return its bytes."""
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
        return cls(
            http,
            path=f"embed/avatars/{index}",
            key=str(index),
            size=1024,
        )

    @classmethod
    def _from_avatar(cls, http: OAuth2HTTPClient, user_id: int, avatar: str) -> Self:
        return cls(
            http,
            path=f"avatars/{user_id}/{avatar}",
            key=avatar,
            size=1024,
        )

    @classmethod
    def _from_guild_avatar(
        cls, http: OAuth2HTTPClient, guild_id: int, member_id: int, avatar: str
    ) -> Self:
        return cls(
            http,
            path=f"guilds/{guild_id}/users/{member_id}/avatars/{avatar}",
            key=avatar,
            size=1024,
        )

    @classmethod
    def _from_guild_banner(
        cls, http: OAuth2HTTPClient, guild_id: int, member_id: int, banner: str
    ) -> Self:
        return cls(
            http,
            path=f"guilds/{guild_id}/users/{member_id}/banners/{banner}",
            key=banner,
            size=1024,
        )

    @classmethod
    def _from_avatar_decoration(
        cls, http: OAuth2HTTPClient, avatar_decoration: str
    ) -> Self:
        return cls(
            http,
            path=f"avatar-decoration-presets/{avatar_decoration}",
            key=avatar_decoration,
            animated=True,
            extension="png",
            size=96,
        )

    @classmethod
    def _from_icon(
        cls, http: OAuth2HTTPClient, object_id: int, icon_hash: str, path: str
    ) -> Self:
        return cls(
            http,
            path=f"{path}-icons/{object_id}/{icon_hash}",
            key=icon_hash,
            size=1024,
        )

    @classmethod
    def _from_app_icon(
        cls,
        http: OAuth2HTTPClient,
        object_id: int,
        icon_hash: str,
        asset_type: Literal["icon", "cover_image"],
    ) -> Self:
        return cls(
            http,
            path=f"app-icons/{object_id}/{asset_type}",
            key=icon_hash,
            animated=False,
            size=1024,
        )

    @classmethod
    def _from_cover_image(
        cls, http: OAuth2HTTPClient, object_id: int, cover_image_hash: str
    ) -> Self:
        return cls(
            http,
            path=f"app-assets/{object_id}/store/{cover_image_hash}",
            key=cover_image_hash,
            size=1024,
        )

    @classmethod
    def _from_guild_image(
        cls, http: OAuth2HTTPClient, guild_id: int, image: str, path: str
    ) -> Self:
        return cls(
            http,
            path=f"{path}/{guild_id}/{image}",
            key=image,
            size=1024,
        )

    @classmethod
    def _from_guild_icon(
        cls, http: OAuth2HTTPClient, guild_id: int, icon_hash: str
    ) -> Self:
        return cls(
            http,
            path=f"icons/{guild_id}/{icon_hash}",
            key=icon_hash,
            size=1024,
        )

    @classmethod
    def _from_user_banner(
        cls, http: OAuth2HTTPClient, user_id: int, banner_hash: str
    ) -> Self:
        return cls(
            http,
            path=f"banners/{user_id}/{banner_hash}",
            key=banner_hash,
            size=512,
        )

    @classmethod
    def _from_guild_member_banner(
        cls, http: OAuth2HTTPClient, guild_id: int, member_id: int, banner_hash: str
    ) -> Self:
        return cls(
            http,
            path=f"guilds/{guild_id}/users/{member_id}/banners/{banner_hash}",
            key=banner_hash,
            size=1024,
        )

    @classmethod
    def _from_primary_guild(
        cls, http: OAuth2HTTPClient, guild_id: int, icon_hash: str
    ) -> Self:
        return cls(
            http,
            path=f"guild-tag-badges/{guild_id}/{icon_hash}",
            key=icon_hash,
            animated=False,
            size=64,
        )

    @classmethod
    def _from_user_collectible(
        cls, http: OAuth2HTTPClient, asset: str, animated: bool = False
    ) -> Self:
        ext = "webm" if animated else "png"
        name = "asset" if animated else "static"
        return cls(
            http,
            path=f"assets/collectibles/{asset}{name}",
            key=asset,
            animated=animated,
            extension=ext,
            size=1024,
            sized=False,
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

    @property
    def animated(self) -> bool:
        """:class:`bool`: Returns whether the asset is animated."""
        return self._animated
