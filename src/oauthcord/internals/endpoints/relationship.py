from typing import TYPE_CHECKING

from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from .._types import relationship as relationship_types
    from .base import ValidToken


class RelationshipHTTPClientMixin(BaseHTTPClient):
    async def get_relationships(
        self,
        token: ValidToken,
    ) -> list[relationship_types.RelationshipResponse]:
        return await self.request(
            Route("GET", "/users/@me/relationships"),
            token=token,
        )

    async def create_relationship(
        self,
        token: ValidToken,
        *,
        user_id: int | str,
        type: relationship_types.RelationshipType | None = None,
        from_friend_suggestion: bool = False,
        confirm_stranger_request: bool = False,
    ) -> None:
        data: relationship_types.CreateRelationshipRequest = {
            "type": type or -1,
            "from_friend_suggestion": from_friend_suggestion,
            "confirm_stranger_request": confirm_stranger_request,
        }
        await self.request(
            Route("PUT", f"/users/@me/relationships/{user_id}"),
            token=token,
            json=data,
        )

    async def delete_relationship(
        self,
        token: ValidToken,
        *,
        user_id: int | str,
    ) -> None:
        await self.request(
            Route("DELETE", f"/users/@me/relationships/{user_id}"),
            token=token,
        )

    async def get_game_relationships(
        self,
        token: ValidToken,
    ) -> list[relationship_types.GameRelationshipResponse]:
        return await self.request(
            Route("GET", "/users/@me/game-relationships"),
            token=token,
        )

    async def create_game_relationship(
        self,
        token: ValidToken,
        *,
        user_id: int | str,
        type: relationship_types.RelationshipType | None = None,
    ) -> None:
        data: relationship_types.CreateGameRelationshipRequest = {
            "type": type or -1,
        }
        await self.request(
            Route("PUT", f"/users/@me/game-relationships/{user_id}"),
            token=token,
            json=data,
        )

    async def delete_game_relationship(
        self,
        token: ValidToken,
        *,
        user_id: int | str,
    ) -> None:
        await self.request(
            Route("DELETE", f"/users/@me/game-relationships/{user_id}"),
            token=token,
        )

    async def send_friend_request(
        self,
        token: ValidToken,
        *,
        username: str,
    ) -> None:
        data: relationship_types.SendFriendRequestRequest = {
            "username": username,
        }
        await self.request(
            Route("POST", "/users/@me/relationships"),
            token=token,
            json=data,
        )
