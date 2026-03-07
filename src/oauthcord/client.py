from typing import TYPE_CHECKING, Any

import aiohttp

from . import utils
from .models import GuildChannel, Lobby
from .models.access_token import AccessTokenResponse
from .models.application import (
    ActivityLink,
    ApplicationRoleConnection,
    PartialApplication,
    PartialApplicationIdentity,
)
from .models.attachment import Attachment
from .models.channel import (
    CallEligibility,
    ChannelLinkedAccounts,
    DMChannel,
    GroupDMChannel,
    _from_data,
)
from .models.components import BaseComponent
from .models.connection import Connection
from .models.current_auth import CurrentInformation
from .models.embeds import Embed
from .models.entitlement import Entitlement
from .models.enums import Scope
from .models.errors import MissingRequiredScopes
from .models.file import File
from .models.guild import Guild
from .models.internals.http import OAuth2HTTPClient
from .models.invite import Invite
from .models.member import GuildMember
from .models.message import Message, PartialMessage
from .models.relationships import GameRelationship, Relationship
from .models.user import CurrentUser, Harvest, PartialUser

if TYPE_CHECKING:
    from .models._base import BaseModel
    from .models.internals._types import components as component_types
    from .models.internals._types import message as message_types
    from .models.internals.http import ValidToken


class OAuth2Cord:
    """High-level asynchronous OAuth2 client for Oauth2 endpoints.

    This client is designed to be used with user access tokens and provides
    methods for interacting with various Discord API endpoints that require user
    authorization. It handles token management, scope checking, and provides convenient
    methods for common operations such as fetching the current user, managing guilds,
    sending messages, and more.

    Parameters
    ----------
    client_id: :class:`int`
        The client ID of the application.
    client_secret: :class:`str`
        The client secret of the application.
    redirect_uri: class:`str`
        The redirect URI configured for the application.
    scopes: :class:`list[Scope]`
        The list of OAuth2 scopes to request during authorization.
    state: class:`str` | None
        An optional state parameter to include in the authorization URL for CSRF protection.
    session: :class:`aiohttp.ClientSession` | None
        An optional aiohttp session to use for HTTP requests. If not provided, a
        :class:`aiohttp.ClientSession` will be created internally for the client.
    auto_refresh_token: :class:`bool`
        Whether to automatically refresh the access token when it expires. If set to
        ``True``, the client will attempt to refresh the token using the refresh token
        when it detects that the access token has expired. Defaults to ``False``.
    store_token: :class:`bool`
        Whether to store the access token in memory after fetching it. If set to
        ``True``, the client will store the token in memory and use for each endpoint.

        The can still be set per endpoint regardless of this setting, but if ``store_token`` is ``False``,
        the client will not store the token and it must be provided for each endpoint call.

        Defaults to ``False``.

    Attributes
    ----------
    http: :class:`OauthHTTPClient`
        The underlying HTTP client used for making API requests. This is exposed as an
        attribute for advanced use cases where direct access to the HTTP client is needed.
    """

    def __init__(
        self,
        *,
        client_id: int,
        client_secret: str,
        redirect_uri: str,
        scopes: list[Scope],
        state: str | None = None,
        auto_refresh_token: bool = False,
        store_token: bool = False,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self.http: OAuth2HTTPClient = OAuth2HTTPClient(
            self,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            state=state,
            session=session,
            scopes=scopes,
            auto_refresh_token=auto_refresh_token,
            store_token=store_token,
        )

    def __with_http[T: BaseModel[Any, Any]](
        self, cls: type[T], data: Any, **extras: Any
    ) -> T:
        return cls(http=self.http, data=data, **extras)

    def oauth2_url(self) -> str:
        return self.http.get_url()

    async def get_token(self, code: str) -> AccessTokenResponse:
        """Exchange an OAuth2 authorization code for an access token response.

        Parameters
        ----------
        code: :class:`str`
            The authorization code received from the OAuth2 authorization flow.

        Returns
        -------
        :class:`AccessTokenResponse`
            An object containing the access token, refresh token, expiration time, and scopes.
        """
        res = await self.http.get_token(code)
        return self.http._last_stored_token() or self.__with_http(
            AccessTokenResponse, res
        )

    async def refresh_token(
        self, refresh_token: ValidToken | None = None
    ) -> AccessTokenResponse:
        """Refresh an OAuth2 token using a refresh token or `AccessTokenResponse`.

        Parameters
        ----------
        refresh_token: :class:`AccessTokenResponse` | :class:`str`
            The refresh token to use for refreshing the access token. This can be either
            a string representing the refresh token or an `AccessTokenResponse` object
            containing the refresh token.

        Returns
        -------
        :class:`AccessTokenResponse`
            An object containing the new access token, and more.
        """
        res = await self.http.refresh_token(refresh_token)
        return self.__with_http(AccessTokenResponse, res)

    async def revoke_token(self, token: ValidToken | None = None) -> None:
        """Revoke an OAuth2 access or refresh token.

        Parameters
        ----------
        token: :class:`AccessTokenResponse` | :class:`str`
            The access or refresh token to revoke. This can be either a string representing
            the token or an `AccessTokenResponse` object containing the token.
        """
        await self.http.revoke_token(token)

    async def current_authorization_information(
        self, token: ValidToken | None = None
    ) -> CurrentInformation:
        """Fetch metadata about the current OAuth2 authorization.

        Parameters
        ----------
        token: :class:`AccessTokenResponse` | :class:`str`
            The access token to fetch information for. This can be either a string representing
            the token or an `AccessTokenResponse` object containing the token.

        Returns
        -------
        :class:`CurrentInformation`
            An object containing metadata about the current OAuth2 authorization, such as scopes and expiration.
        """
        res = await self.http.get_current_authorization_information(token)
        return self.__with_http(CurrentInformation, res)

    async def current_user(self, token: ValidToken | None = None) -> CurrentUser:
        """Fetch the currently authorized Discord user (`/users/@me`). Requires OAuth scope(s): IDENTIFY."""
        if not self.http.has_scopes(Scope.IDENTIFY):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes, missing_scopes=[Scope.IDENTIFY]
            )

        res = await self.http.get_current_user(token)
        return self.__with_http(CurrentUser, res)

    async def user_harvest(self, token: ValidToken | None = None) -> Harvest | None:
        """Fetch the current user's harvest export metadata if one exists."""
        res = await self.http.get_user_harvest(token)
        if res is None:
            return None
        return self.__with_http(Harvest, res)

    async def create_user_harvest(
        self,
        token: ValidToken | None = None,
        *,
        backends: list[str] | None = None,
        email: str | None = None,
    ) -> Harvest:
        """Create a new user harvest export job."""
        res = await self.http.create_user_harvest(
            token,
            backends=backends,
            email=email,
        )
        return self.__with_http(Harvest, res)

    async def guilds(
        self,
        token: ValidToken | None = None,
        *,
        limit: int | None = None,
        with_counts: bool = False,
    ) -> list[Guild]:
        """Fetch guilds for the current OAuth2 user. Requires OAuth scope(s): GUILDS, GUILDS_MEMBERS_READ."""
        if not self.http.has_scopes(Scope.GUILDS):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes, missing_scopes=[Scope.GUILDS]
            )

        if with_counts and not self.http.has_scopes(Scope.GUILDS_MEMBERS_READ):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.GUILDS_MEMBERS_READ],
            )

        res = await self.http.get_current_user_guilds(
            token, limit=limit, with_counts=with_counts
        )
        return [self.__with_http(Guild, guild) for guild in res]

    async def connections(self, token: ValidToken | None = None) -> list[Connection]:
        """Fetch linked user connections for the current OAuth2 user. Requires OAuth scope(s): CONNECTIONS."""
        if not self.http.has_scopes(Scope.CONNECTIONS):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.CONNECTIONS],
            )

        res = await self.http.get_current_user_connections(token)
        return [self.__with_http(Connection, connection) for connection in res]

    async def guild_member(
        self, token: ValidToken | None = None, *, guild_id: int
    ) -> GuildMember:
        """Fetch the current user's member object for a specific guild. Requires OAuth scope(s): GUILDS_MEMBERS_READ."""
        if not self.http.has_scopes(Scope.GUILDS_MEMBERS_READ):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.GUILDS_MEMBERS_READ],
            )

        res = await self.http.get_current_guild_member(token, guild_id=guild_id)
        return self.__with_http(GuildMember, res, guild_id=guild_id)

    async def add_user_to_guild(
        self,
        token: ValidToken | None = None,
        *,
        bot_token: str,
        guild_id: int,
        user_id: int,
        nick: str | None = None,
        roles: list[int | str] | None = None,
        deaf: bool | None = None,
        mute: bool | None = None,
        bypass_verification: bool | None = None,
    ) -> GuildMember | None:
        """Add a user to a guild using an OAuth2 access token and bot token."""
        res = await self.http.add_user_to_guild(
            token,
            bot_token=bot_token,
            guild_id=guild_id,
            user_id=user_id,
            nick=nick,
            roles=roles,
            deaf=deaf,
            mute=mute,
            bypass_verification=bypass_verification,
        )
        if res is None:
            return None

        return self.__with_http(GuildMember, res, guild_id=guild_id)

    async def modify_current_user_account(
        self,
        token: ValidToken | None = None,
        *,
        global_name: str | None = utils.NotSet,
    ) -> PartialUser:
        """Edit account fields for the current OAuth2 user."""
        res = await self.http.modify_current_user_account(
            token, global_name=global_name
        )
        return self.__with_http(PartialUser, res)

    async def dm_channel(
        self, token: ValidToken | None = None, *, user_id: int
    ) -> DMChannel:
        """Get or create a DM channel with the given user."""
        res = await self.http.get_dm_channel(token, user_id=user_id)
        return self.__with_http(DMChannel, res)

    async def create_private_channel(
        self,
        token: ValidToken | None = None,
        *,
        recipients: list[int | str] | None = None,
        access_tokens: list[ValidToken] | None = None,
        nicks: dict[int | str, str] | None = None,
    ) -> DMChannel | GroupDMChannel:
        """Create a DM or group DM channel."""
        res = await self.http.create_private_channel(
            token,
            recipients=recipients,
            access_tokens=access_tokens,
            nicks=nicks,
        )
        return _from_data(self.http, res)  # type: ignore

    async def dm_messages(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int,
        limit: int | None = None,
    ) -> list[PartialMessage]:
        """List direct messages for a social layer DM channel. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        res = await self.http.get_dm_messages(token, user_id=user_id, limit=limit)
        return [self.__with_http(PartialMessage, message) for message in res]

    async def create_dm_message(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int,
        content: str | None = None,
        tts: bool | None = None,
        nonce: int | str | None = None,
        embeds: list[Embed | message_types.EmbedRequest] | None = None,
        allowed_mentions: message_types.AllowedMentionsRequest | None = None,
        message_reference: message_types.MessageReferenceRequest | None = None,
        components: list[BaseComponent | component_types.ComponentRequest]
        | None = None,
        sticker_ids: list[int | str] | None = None,
        attachments: list[Attachment | message_types.PartialAttachmentRequest]
        | None = None,
        flags: int | None = None,
        metadata: dict[str, object] | None = None,
        files: list[File] | None = None,
    ) -> Message:
        """Create a message in a social layer DM channel. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        res = await self.http.create_dm_message(
            token,
            user_id=user_id,
            content=content,
            tts=tts,
            nonce=nonce,
            embeds=[
                e._to_request() if isinstance(e, Embed) else e for e in embeds or []
            ],
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=[
                c._to_request() if isinstance(c, BaseComponent) else c
                for c in components or []
            ],
            sticker_ids=sticker_ids,
            attachments=[
                a._to_request() if isinstance(a, Attachment) else a
                for a in attachments or []
            ],
            flags=flags,
            metadata=metadata,
            files=files,
        )
        return self.__with_http(Message, res)

    async def create_message(
        self,
        token: ValidToken | None = None,
        *,
        channel_id: int | str,
        content: str | None = None,
        tts: bool | None = None,
        nonce: int | str | None = None,
        embeds: list[Embed | message_types.EmbedRequest] | None = None,
        allowed_mentions: message_types.AllowedMentionsRequest | None = None,
        message_reference: message_types.MessageReferenceRequest | None = None,
        components: list[BaseComponent | component_types.ComponentRequest]
        | None = None,
        sticker_ids: list[int | str] | None = None,
        activity: message_types.MessageActivityRequest | None = None,
        application_id: int | str | None = None,
        flags: int | None = None,
        attachments: list[Attachment | message_types.PartialAttachmentRequest]
        | None = None,
        poll: dict[str, object] | None = None,
        shared_client_theme: message_types.SharedClientThemeRequest | None = None,
        files: list[File] | None = None,
    ) -> Message:
        """Create a message in a channel."""
        res = await self.http.create_message(
            token,
            channel_id=channel_id,
            content=content,
            tts=tts,
            nonce=nonce,
            embeds=[
                e._to_request() if isinstance(e, Embed) else e for e in embeds or []
            ],
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=[
                c._to_request() if isinstance(c, BaseComponent) else c
                for c in components or []
            ],
            sticker_ids=sticker_ids,
            activity=activity,
            application_id=application_id,
            flags=flags,
            attachments=[
                a._to_request() if isinstance(a, Attachment) else a
                for a in attachments or []
            ],
            poll=poll,
            shared_client_theme=shared_client_theme,
            files=files,
        )
        return self.__with_http(Message, res)

    async def edit_dm_message(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int,
        message_id: int,
        content: str | None = None,
    ) -> Message:
        """Edit a message in a social layer DM channel. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        res = await self.http.edit_dm_message(
            token,
            user_id=user_id,
            message_id=message_id,
            content=content,
        )
        return self.__with_http(Message, res)

    async def delete_dm_message(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int,
        message_id: int,
    ) -> None:
        """Delete a message in a social layer DM channel. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        await self.http.delete_dm_message(
            token,
            user_id=user_id,
            message_id=message_id,
        )

    async def guild_channels(
        self,
        token: ValidToken | None = None,
        *,
        guild_id: str | int,
        permissions: bool = False,
    ) -> list[GuildChannel]:
        """List channels for a guild. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        res = await self.http.get_guild_channels(
            token,
            guild_id=guild_id,
            permissions=permissions,
        )
        return [_from_data(self.http, channel) for channel in res]  # type: ignore

    async def call_eligibility(
        self, token: ValidToken | None = None, *, channel_id: int | str
    ) -> CallEligibility:
        """Fetch call eligibility information for the current user in a specific channel."""
        return self.__with_http(
            CallEligibility,
            await self.http.get_call_eligibility(token, channel_id=channel_id),
        )

    async def ring_channel_recipients(
        self,
        token: ValidToken | None = None,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        """Ring recipients in a call-capable channel."""
        await self.http.ring_channel_recipients(
            token, channel_id=channel_id, recipients=recipients
        )

    async def stop_ringing_channel_recipients(
        self,
        token: ValidToken | None = None,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        """Stop ringing recipients in a call-capable channel."""
        await self.http.stop_ringing_channel_recipients(
            token, channel_id=channel_id, recipients=recipients
        )

    async def channel_linked_accounts(
        self,
        token: ValidToken | None = None,
        *,
        channel_id: int | str,
        user_ids: list[int | str] | None = None,
    ) -> ChannelLinkedAccounts:
        """Fetch linked account data for users in a channel. Requires OAuth scope(s): DM_CHANNELS_READ."""
        if not self.http.has_scopes(Scope.DM_CHANNELS_READ):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.DM_CHANNELS_READ],
            )

        res = await self.http.get_channel_linked_accounts(
            token,
            channel_id=channel_id,
            user_ids=user_ids,
        )
        return self.__with_http(ChannelLinkedAccounts, res)

    async def join_or_create_lobby(
        self,
        token: ValidToken | None = None,
        *,
        secret: str,
        lobby_metadata: dict[str, str] | None = None,
        member_metadata: dict[str, str] | None = None,
        idle_timeout_seconds: int | None = None,
        flags: int | None = None,
    ) -> Lobby:
        """Join an existing lobby or create one from a secret."""
        res = await self.http.join_or_create_lobby(
            token,
            secret=secret,
            lobby_metadata=lobby_metadata,
            member_metadata=member_metadata,
            idle_timeout_seconds=idle_timeout_seconds,
            flags=flags,
        )
        return self.__with_http(Lobby, res)

    async def leave_lobby(
        self,
        token: ValidToken | None = None,
        *,
        lobby_id: int | str,
    ) -> None:
        """Leave a lobby as the current user. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        await self.http.leave_lobby(token, lobby_id=lobby_id)

    async def create_lobby_invite_for_current_user(
        self,
        token: ValidToken | None = None,
        *,
        lobby_id: int | str,
    ) -> str:
        """Create a lobby invite code for the current user. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        res = await self.http.create_lobby_invite_for_current_user(
            token, lobby_id=lobby_id
        )
        return res["code"]

    async def edit_lobby_linked_channel(
        self,
        token: ValidToken | None = None,
        *,
        lobby_id: int | str,
        channel_id: int | str | None = utils.NotSet,
    ) -> Lobby:
        """Edit the channel linked to a lobby. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        res = await self.http.edit_lobby_linked_channel(
            token,
            lobby_id=lobby_id,
            channel_id=channel_id,
        )
        return self.__with_http(Lobby, res)

    async def modify_lobby_linked_channel(
        self,
        token: ValidToken | None = None,
        *,
        lobby_id: int | str,
        channel_id: int | str | None = utils.NotSet,
    ) -> Lobby:
        """Alias for `edit_lobby_linked_channel`."""
        return await self.edit_lobby_linked_channel(
            token,
            lobby_id=lobby_id,
            channel_id=channel_id,
        )

    async def lobby_messages(
        self,
        token: ValidToken | None = None,
        *,
        lobby_id: int | str,
        limit: int | None = None,
    ) -> list[PartialMessage]:
        """List messages in a lobby. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        res = await self.http.get_lobby_messages(token, lobby_id=lobby_id, limit=limit)
        return [self.__with_http(PartialMessage, message) for message in res]

    async def create_lobby_message(
        self,
        token: ValidToken | None = None,
        *,
        lobby_id: int | str,
        content: str | None = None,
        tts: bool | None = None,
        nonce: int | str | None = None,
        embeds: list[Embed | message_types.EmbedRequest] | None = None,
        allowed_mentions: message_types.AllowedMentionsRequest | None = None,
        message_reference: message_types.MessageReferenceRequest | None = None,
        components: list[BaseComponent | component_types.ComponentRequest]
        | None = None,
        sticker_ids: list[int | str] | None = None,
        activity: message_types.MessageActivityRequest | None = None,
        application_id: int | str | None = None,
        flags: int | None = None,
        attachments: list[Attachment | message_types.PartialAttachmentRequest]
        | None = None,
        poll: dict[str, object] | None = None,
        shared_client_theme: message_types.SharedClientThemeRequest | None = None,
        metadata: dict[str, object] | None = None,
        files: list[File] | None = None,
    ) -> PartialMessage:
        """Create a message in a lobby. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        res = await self.http.create_lobby_message(
            token,
            lobby_id=lobby_id,
            content=content,
            tts=tts,
            nonce=nonce,
            embeds=[
                e._to_request() if isinstance(e, Embed) else e for e in embeds or []
            ],
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=[
                c._to_request() if isinstance(c, BaseComponent) else c
                for c in components or []
            ],
            sticker_ids=sticker_ids,
            activity=activity,
            application_id=application_id,
            flags=flags,
            attachments=[
                a._to_request() if isinstance(a, Attachment) else a
                for a in attachments or []
            ],
            poll=poll,
            shared_client_theme=shared_client_theme,
            metadata=metadata,
            files=files,
        )
        return self.__with_http(PartialMessage, res)

    async def relationships(self, token: ValidToken) -> list[Relationship]:
        """Fetch the current user's relationships."""
        res = await self.http.get_relationships(token)
        return [self.__with_http(Relationship, relationship) for relationship in res]

    async def create_relationship(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int | str,
        type: int | None = None,
        from_friend_suggestion: bool = False,
        confirm_stranger_request: bool = False,
    ) -> None:
        """Create or accept a relationship with another user."""
        await self.http.create_relationship(
            token,
            user_id=user_id,
            type=type,  # pyright: ignore[reportArgumentType]
            from_friend_suggestion=from_friend_suggestion,
            confirm_stranger_request=confirm_stranger_request,
        )

    async def delete_relationship(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int | str,
    ) -> None:
        """Delete a relationship with another user."""
        await self.http.delete_relationship(token, user_id=user_id)

    async def game_relationships(self, token: ValidToken) -> list[GameRelationship]:
        """Fetch game/social-layer relationships."""
        res = await self.http.get_game_relationships(token)
        return [
            self.__with_http(GameRelationship, relationship) for relationship in res
        ]

    async def create_game_relationship(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int | str,
        type: int | None = None,
    ) -> None:
        """Create a game/social-layer relationship."""
        await self.http.create_game_relationship(
            token,
            user_id=user_id,
            type=type,  # pyright: ignore[reportArgumentType]
        )

    async def delete_game_relationship(
        self,
        token: ValidToken | None = None,
        *,
        user_id: int | str,
    ) -> None:
        """Delete a game/social-layer relationship."""
        await self.http.delete_game_relationship(token, user_id=user_id)

    async def create_application_attachment(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
        file: File,
    ) -> Attachment:
        """Create an attachment upload slot for an application."""
        res = await self.http.create_application_attachment(
            token,
            application_id=application_id,
            file=file,
        )
        return self.__with_http(Attachment, res["attachment"])

    async def partial_application(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
    ) -> PartialApplication:
        """Fetch a partial application payload."""
        res = await self.http.get_partial_application(
            token,
            application_id=application_id,
        )
        return self.__with_http(PartialApplication, res)

    async def user_application_role_connection(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
    ) -> ApplicationRoleConnection:
        """Fetch the current user's application role connection. Requires OAuth scope(s): ROLE_CONNECTIONS_WRITE."""
        if not self.http.has_scopes(Scope.ROLE_CONNECTIONS_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.ROLE_CONNECTIONS_WRITE],
            )

        res = await self.http.get_user_application_role_connection(
            token,
            application_id=application_id,
        )
        return self.__with_http(ApplicationRoleConnection, res)

    async def edit_user_application_role_connection(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
        platform_name: str | None = None,
        platform_username: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> ApplicationRoleConnection:
        """Edit the current user's application role connection. Requires OAuth scope(s): ROLE_CONNECTIONS_WRITE."""
        if not self.http.has_scopes(Scope.ROLE_CONNECTIONS_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.ROLE_CONNECTIONS_WRITE],
            )

        res = await self.http.edit_user_application_role_connection(
            token,
            application_id=application_id,
            platform_name=platform_name,
            platform_username=platform_username,
            metadata=metadata,
        )
        return self.__with_http(ApplicationRoleConnection, res)

    async def create_application_quick_link(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
        title: str,
        description: str,
        image: File,
        custom_id: str | None = None,
    ) -> ActivityLink:
        """Create an application quick link (activity link)."""
        res = await self.http.create_application_quick_link(
            token,
            application_id=application_id,
            title=title,
            description=description,
            image=image,
            custom_id=custom_id,
        )
        return self.__with_http(ActivityLink, res)

    async def bulk_application_identities(
        self,
        token: ValidToken | None = None,
        *,
        user_ids: list[int | str],
    ) -> list[PartialApplicationIdentity]:
        res = await self.http.get_bulk_application_identities(token, user_ids=user_ids)
        return [
            self.__with_http(PartialApplicationIdentity, identity) for identity in res
        ]

    async def application_entitlements(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
        user_id: int | str | None = None,
        sku_ids: list[int | str] | None = None,
        guild_id: int | str | None = None,
        exclude_ended: bool | None = None,
        exclude_deleted: bool | None = None,
        before: int | str | None = None,
        after: int | str | None = None,
        limit: int | None = None,
    ) -> list[Entitlement]:
        """List entitlements for an application. Requires OAuth scope(s): APPLICATIONS_ENTITLEMENTS."""
        if not self.http.has_scopes(Scope.APPLICATIONS_ENTITLEMENTS):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.APPLICATIONS_ENTITLEMENTS],
            )

        res = await self.http.get_application_entitlements(
            token,
            application_id=application_id,
            user_id=user_id,
            sku_ids=sku_ids,
            guild_id=guild_id,
            exclude_ended=exclude_ended,
            exclude_deleted=exclude_deleted,
            before=before,
            after=after,
            limit=limit,
        )
        return [self.__with_http(Entitlement, entitlement) for entitlement in res]

    async def application_entitlement(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> Entitlement:
        """Fetch a single application entitlement. Requires OAuth scope(s): APPLICATIONS_ENTITLEMENTS."""
        if not self.http.has_scopes(Scope.APPLICATIONS_ENTITLEMENTS):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.APPLICATIONS_ENTITLEMENTS],
            )

        res = await self.http.get_application_entitlement(
            token,
            application_id=application_id,
            entitlement_id=entitlement_id,
        )
        return self.__with_http(Entitlement, res)

    async def consume_application_entitlement(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> None:
        """Consume an application entitlement. Requires OAuth scope(s): APPLICATIONS_ENTITLEMENTS."""
        if not self.http.has_scopes(Scope.APPLICATIONS_ENTITLEMENTS):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.APPLICATIONS_ENTITLEMENTS],
            )

        await self.http.consume_application_entitlement(
            token,
            application_id=application_id,
            entitlement_id=entitlement_id,
        )

    async def delete_application_entitlement(
        self,
        token: ValidToken | None = None,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> None:
        """Delete an application entitlement. Requires OAuth scope(s): APPLICATIONS_ENTITLEMENTS."""
        if not self.http.has_scopes(Scope.APPLICATIONS_ENTITLEMENTS):
            raise MissingRequiredScopes(
                current_scopes=self.http.current_scopes,
                missing_scopes=[Scope.APPLICATIONS_ENTITLEMENTS],
            )

        await self.http.delete_application_entitlement(
            token,
            application_id=application_id,
            entitlement_id=entitlement_id,
        )

    async def accept_invite(
        self,
        token: ValidToken | None = None,
        *,
        code: str,
        session_id: str | None = None,
    ) -> Invite:
        """Accept a Discord invite using the current user token."""
        res = await self.http.accept_invite(
            token,
            code=code,
            session_id=session_id,
        )
        return self.__with_http(Invite, res)
