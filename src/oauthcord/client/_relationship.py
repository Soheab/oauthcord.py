from typing import TYPE_CHECKING

from .. import utils
from ..models.enums import RelationshipType
from ..models.relationships import GameRelationship, Relationship

if TYPE_CHECKING:
    from ._base import _AuthorisedSessionProto


class RelationshipClient:
    async def get_current_user_relationships(
        self: _AuthorisedSessionProto,
    ) -> list[Relationship]:
        """Get a list of the current user's relationships.

        Only relationships of type ``FRIEND`` are returned.

        Returns
        -------
        list[:class:`Relationship`]
            List of objects representing the user's relationships.
        """
        res = await self.client.http.get_relationships(self.token)
        return [
            utils._construct_model(Relationship, data=relationship, session=self)
            for relationship in res
        ]

    async def send_friend_request(
        self: _AuthorisedSessionProto,
        *,
        username: str,
    ) -> None:
        """Send a friend request to a user by their username.

        Parameters
        ----------
        username: str
            The username of the user to send a friend request to.
        """
        await self.client.http.send_friend_request(self.token, username=username)

    async def create_relationship(
        self: _AuthorisedSessionProto,
        *,
        user_id: int | str,
        type: RelationshipType | int = utils.NotSet,
        from_friend_suggestion: bool = False,
        confirm_stranger_request: bool = False,
    ) -> None:
        """Create a relationship with another user.

        .. warning::
            This should not be used to create many friend requests in a short period of time.
            Suspicious friend request activity may be flagged by Discord and require additional
            verification steps or lead to immediate account termination.

        Parameters
        ----------
        user_id: :class:`int` | :class:`str`
            The ID of the user to create a relationship with.
        type: RelationshipType | int
            The type of relationship to create. If not provided, defaults to ``-1``,
            whihc accept an existing or creates a new friend request.
        from_friend_suggestion: :class:`bool`
            Whether the relationship is being created from a friend suggestion.

            Defaults to ``False``.
        confirm_stranger_request: :class:`bool`
            Whether the user consents to a ceeping a stranger's friend request.

            Defaults to ``False``.
        """
        await self.client.http.create_relationship(
            self.token,
            user_id=user_id,
            type=type,  # pyright: ignore[reportArgumentType]
            from_friend_suggestion=from_friend_suggestion,
            confirm_stranger_request=confirm_stranger_request,
        )

    async def delete_relationship(
        self: _AuthorisedSessionProto,
        *,
        user_id: int | str,
    ) -> None:
        """Remove a relationship with another user."""
        await self.client.http.delete_relationship(self.token, user_id=user_id)

    async def game_relationships(
        self: _AuthorisedSessionProto,
    ) -> list[GameRelationship]:
        """Get a list of the current user's game/social-layer relationships.

        .. note::
            Oonly game relationships originating from the current application as
            the requestor are returned.

        Returns
        -------
        list[:class:`GameRelationship`]
            List of objects representing the user's game/social-layer relationships.
        """
        res = await self.client.http.get_game_relationships(self.token)
        return [
            utils._construct_model(GameRelationship, data=relationship, session=self)
            for relationship in res
        ]

    async def create_game_relationship(
        self: _AuthorisedSessionProto,
        *,
        user_id: int | str,
        type: RelationshipType | int | None = None,
    ) -> None:
        """Create a game/social-layer relationship with another user.

        The target user must have the same application as the requestor
        authorized to create a game relationship.

        .. scope:: relationship.write

        Parameters
        ----------
        user_id: :class:`int` | :class:`str`
            The ID of the user to create a game relationship with.
        type: RelationshipType | int | None
            The type of relationship to create. If not provided, defaults to ``-1``,
            which accepts an existing or creates a new game relationship.
        """
        await self.client.http.create_game_relationship(
            self.token,
            user_id=user_id,
            type=type,  # pyright: ignore[reportArgumentType]
        )

    async def delete_game_relationship(
        self: _AuthorisedSessionProto,
        *,
        user_id: int | str,
    ) -> None:
        """Remove a game/social-layer relationship with another user.

        .. scope:: relationship.write
        """
        await self.client.http.delete_game_relationship(self.token, user_id=user_id)
