from typing import TYPE_CHECKING, Self

import aiohttp
import yarl

from . import utils
from .errors import MissingRequiredScopes
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
)
from .models.components import BaseComponent
from .models.connection import Connection
from .models.current_auth import CurrentInformation
from .models.embeds import Embed
from .models.entitlement import Entitlement
from .models.enums import Scope
from .models.file import File
from .models.guild import Guild
from .models.internals.http import OAuth2HTTPClient
from .models.invite import Invite
from .models.member import GuildMember
from .models.message import Message, PartialMessage
from .models.relationships import GameRelationship, Relationship
from .models.user import CurrentUser, Harvest, PartialUser

if TYPE_CHECKING:
    from .models.internals._types import components as component_types
    from .models.internals._types import message as message_types
    from .models.internals.http import ValidToken


class Client:
    def __init__(
        self,
        *,
        client_id: int | str,
        client_secret: str,
        redirect_uri: str,
        scopes: list[Scope | str],
        session: aiohttp.ClientSession = utils.NotSet,
        state: str | None = None,
    ) -> None:
        self.http: OAuth2HTTPClient = OAuth2HTTPClient(
            self,
            client_id=int(client_id),
            client_secret=client_secret,
            session=session,
        )

        if not isinstance(scopes, list):
            raise ValueError("scopes must be a list of Scope or str")

        try:
            parsed_scopes = [Scope(scope) for scope in scopes]
        except ValueError as exc:
            raise ValueError("scopes must be a list of valid Scope values") from exc

        self._scopes: list[Scope] = parsed_scopes
        self._redirect_uri: str = redirect_uri
        self._state: str | None = state

    def get_authorization_url(
        self,
    ) -> str:
        params = {
            "client_id": str(self.http.client_id),
            "response_type": "code",
            "redirect_uri": self._redirect_uri,
            "scope": "+".join(scope.value for scope in self._scopes),
        }
        if self._state:
            params["state"] = self._state

        base_url = self.http.BASE_URL
        url = yarl.URL(base_url).with_query(params)
        return str(url)

    async def exchange_token(
        self,
        code: str,
    ) -> AuthorisedSession:
        res = await self.http.exchange_token(code, redirect_uri=self._redirect_uri)
        res = utils._construct_model(AccessTokenResponse, data=res, http=self.http)
        return AuthorisedSession(self, token=res)


class AuthorisedSession:
    def __init__(
        self,
        client: Client,
        *,
        token: AccessTokenResponse,
    ) -> None:
        self.client: Client = client
        self.token: AccessTokenResponse = token

        self.current_scopes: list[Scope] = client._scopes

        self._current_authorization_information: CurrentInformation | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass

    @property
    def current_authorization_information(self) -> CurrentInformation | None:
        return self._current_authorization_information

    @current_authorization_information.setter
    def current_authorization_information(self, value: CurrentInformation) -> None:
        if not isinstance(value, CurrentInformation):
            raise TypeError(
                "current_authorization_information must be of type CurrentInformation"
            )

        self._current_authorization_information = value
        self.current_scopes = value.scopes

    async def refresh(
        self,
    ) -> AccessTokenResponse:
        return await self.token.refresh()

    async def revoke(
        self,
    ) -> None:
        await self.token.revoke()

    async def get_current_authorization_information(
        self,
    ) -> CurrentInformation:
        res = await self.client.http.get_current_authorization_information(self.token)
        self.current_authorization_information = utils._construct_model(
            CurrentInformation, data=res, session=self
        )
        return self.current_authorization_information  # type: ignore

    async def current_user(
        self,
    ) -> CurrentUser:
        """Fetch the currently authorized Discord user (`/users/@me`). Requires OAuth scope(s): IDENTIFY."""
        if not self.client.http.has_scopes(Scope.IDENTIFY):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.IDENTIFY],
            )

        res = await self.client.http.get_current_user(self.token)
        return utils._construct_model(CurrentUser, data=res, session=self)

    async def user_harvest(
        self,
    ) -> Harvest | None:
        """Fetch the current user's harvest export metadata if one exists."""
        res = await self.client.http.get_user_harvest(self.token)
        if res is None:
            return None
        return utils._construct_model(Harvest, data=res)

    async def create_user_harvest(
        self,
        *,
        backends: list[str] | None = None,
        email: str | None = None,
    ) -> Harvest:
        """Create a new user harvest export job."""
        res = await self.client.http.create_user_harvest(
            self.token,
            backends=backends,
            email=email,
        )
        return utils._construct_model(Harvest, data=res)

    async def guilds(
        self,
        *,
        limit: int | None = None,
        with_counts: bool = False,
    ) -> list[Guild]:
        """Fetch guilds for the current OAuth2 user. Requires OAuth scope(s): GUILDS, GUILDS_MEMBERS_READ."""
        if not self.client.http.has_scopes(Scope.GUILDS):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.GUILDS],
            )

        if with_counts and not self.client.http.has_scopes(Scope.GUILDS_MEMBERS_READ):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.GUILDS_MEMBERS_READ],
            )

        res = await self.client.http.get_current_user_guilds(
            self.token, limit=limit, with_counts=with_counts
        )
        return [
            utils._construct_model(Guild, data=guild, session=self) for guild in res
        ]

    async def connections(
        self,
    ) -> list[Connection]:
        """Fetch linked user connections for the current OAuth2 user. Requires OAuth scope(s): CONNECTIONS."""
        if not self.client.http.has_scopes(Scope.CONNECTIONS):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.CONNECTIONS],
            )

        res = await self.client.http.get_current_user_connections(self.token)
        return [
            utils._construct_model(Connection, data=connection, http=self.client.http)
            for connection in res
        ]

    async def guild_member(self, *, guild_id: int) -> GuildMember:
        """Fetch the current user's member object for a specific guild. Requires OAuth scope(s): GUILDS_MEMBERS_READ."""
        if not self.client.http.has_scopes(Scope.GUILDS_MEMBERS_READ):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.GUILDS_MEMBERS_READ],
            )

        res = await self.client.http.get_current_guild_member(
            self.token, guild_id=guild_id
        )
        return GuildMember(session=self, data=res, guild_id=guild_id)

    async def add_user_to_guild(
        self,
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
        res = await self.client.http.add_user_to_guild(
            self.token,
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

        return GuildMember(session=self, data=res, guild_id=guild_id)

    async def modify_current_user_account(
        self,
        *,
        global_name: str | None = utils.NotSet,
    ) -> PartialUser:
        """Edit account fields for the current OAuth2 user."""
        res = await self.client.http.modify_current_user_account(
            self.token, global_name=global_name
        )
        return utils._construct_model(PartialUser, data=res, session=self)

    async def dm_channel(self, *, user_id: int) -> DMChannel:
        """Get or create a DM channel with the given user."""
        res = await self.client.http.get_dm_channel(self.token, user_id=user_id)
        return utils._construct_model(DMChannel, data=res, session=self)

    async def create_private_channel(
        self,
        *,
        recipients: list[int | str] | None = None,
        access_tokens: list[ValidToken] | None = None,
        nicks: dict[int | str, str] | None = None,
    ) -> DMChannel | GroupDMChannel:
        """Create a DM or group DM channel."""
        res = await self.client.http.create_private_channel(
            self.token,
            recipients=recipients,
            access_tokens=access_tokens,
            nicks=nicks,
        )
        return utils._construct_model(DMChannel, data=res, session=self)

    async def dm_messages(
        self,
        *,
        user_id: int,
        limit: int | None = None,
    ) -> list[PartialMessage]:
        """List direct messages for a social layer DM channel. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.client.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        res = await self.client.http.get_dm_messages(
            self.token, user_id=user_id, limit=limit
        )
        return [
            utils._construct_model(PartialMessage, data=message, session=self)
            for message in res
        ]

    async def create_dm_message(
        self,
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
        if not self.client.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        res = await self.client.http.create_dm_message(
            self.token,
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
        return utils._construct_model(Message, data=res, session=self)

    async def edit_dm_message(
        self,
        *,
        user_id: int,
        message_id: int,
        content: str | None = None,
    ) -> Message:
        """Edit a message in a social layer DM channel. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.client.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        res = await self.client.http.edit_dm_message(
            self.token,
            user_id=user_id,
            message_id=message_id,
            content=content,
        )
        return utils._construct_model(Message, data=res, session=self)

    async def delete_dm_message(
        self,
        *,
        user_id: int,
        message_id: int,
    ) -> None:
        """Delete a message in a social layer DM channel. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.client.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        await self.client.http.delete_dm_message(
            self.token,
            user_id=user_id,
            message_id=message_id,
        )

    async def guild_channels(
        self,
        *,
        guild_id: str | int,
        permissions: bool = False,
    ) -> list[GuildChannel]:
        """List channels for a guild. Requires OAuth scope(s): SDK_SOCIAL_LAYER_PRESENCE."""
        if not self.client.http.has_scopes(Scope.SDK_SOCIAL_LAYER_PRESENCE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.SDK_SOCIAL_LAYER_PRESENCE],
            )

        res = await self.client.http.get_guild_channels(
            self.token,
            guild_id=guild_id,
            permissions=permissions,
        )
        return [
            utils._construct_model(GuildChannel, data=channel, session=self)
            for channel in res
        ]

    async def call_eligibility(self, *, channel_id: int | str) -> CallEligibility:
        """Fetch call eligibility information for the current user in a specific channel."""
        return utils._construct_model(
            CallEligibility,
            data=await self.client.http.get_call_eligibility(
                self.token, channel_id=channel_id
            ),
            http=self.client.http,
        )

    async def ring_channel_recipients(
        self,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        """Ring recipients in a call-capable channel."""
        await self.client.http.ring_channel_recipients(
            self.token, channel_id=channel_id, recipients=recipients
        )

    async def stop_ringing_channel_recipients(
        self,
        *,
        channel_id: int | str,
        recipients: list[int | str] | None = None,
    ) -> None:
        """Stop ringing recipients in a call-capable channel."""
        await self.client.http.stop_ringing_channel_recipients(
            self.token, channel_id=channel_id, recipients=recipients
        )

    async def channel_linked_accounts(
        self,
        *,
        channel_id: int | str,
        user_ids: list[int | str] | None = None,
    ) -> ChannelLinkedAccounts:
        """Fetch linked account data for users in a channel. Requires OAuth scope(s): DM_CHANNELS_READ."""
        if not self.client.http.has_scopes(Scope.DM_CHANNELS_READ):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.DM_CHANNELS_READ],
            )

        res = await self.client.http.get_channel_linked_accounts(
            self.token,
            channel_id=channel_id,
            user_ids=user_ids,
        )
        return utils._construct_model(
            ChannelLinkedAccounts,
            data=res,
        )

    async def join_or_create_lobby(
        self,
        *,
        secret: str,
        lobby_metadata: dict[str, str] | None = None,
        member_metadata: dict[str, str] | None = None,
        idle_timeout_seconds: int | None = None,
        flags: int | None = None,
    ) -> Lobby:
        """Join an existing lobby or create one from a secret."""
        res = await self.client.http.join_or_create_lobby(
            self.token,
            secret=secret,
            lobby_metadata=lobby_metadata,
            member_metadata=member_metadata,
            idle_timeout_seconds=idle_timeout_seconds,
            flags=flags,
        )
        return utils._construct_model(Lobby, data=res, http=self.client.http)

    async def leave_lobby(
        self,
        *,
        lobby_id: int | str,
    ) -> None:
        """Leave a lobby as the current user. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.client.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        await self.client.http.leave_lobby(self.token, lobby_id=lobby_id)

    async def create_lobby_invite_for_current_user(
        self,
        *,
        lobby_id: int | str,
    ) -> str:
        """Create a lobby invite code for the current user. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.client.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        res = await self.client.http.create_lobby_invite_for_current_user(
            self.token, lobby_id=lobby_id
        )
        return res["code"]

    async def edit_lobby_linked_channel(
        self,
        *,
        lobby_id: int | str,
        channel_id: int | str | None = utils.NotSet,
    ) -> Lobby:
        """Edit the channel linked to a lobby. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.client.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        res = await self.client.http.edit_lobby_linked_channel(
            self.token,
            lobby_id=lobby_id,
            channel_id=channel_id,
        )
        return utils._construct_model(Lobby, data=res, http=self.client.http)

    async def lobby_messages(
        self,
        *,
        lobby_id: int | str,
        limit: int | None = None,
    ) -> list[PartialMessage]:
        """List messages in a lobby. Requires OAuth scope(s): LOBBIES_WRITE."""
        if not self.client.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        res = await self.client.http.get_lobby_messages(
            self.token, lobby_id=lobby_id, limit=limit
        )
        return [
            utils._construct_model(PartialMessage, data=message, session=self)
            for message in res
        ]

    async def create_lobby_message(
        self,
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
        if not self.client.http.has_scopes(Scope.LOBBIES_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.LOBBIES_WRITE],
            )

        res = await self.client.http.create_lobby_message(
            self.token,
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
        return utils._construct_model(PartialMessage, data=res, session=self)

    async def relationships(self, token: ValidToken) -> list[Relationship]:
        """Fetch the current user's relationships."""
        res = await self.client.http.get_relationships(token)
        return [
            utils._construct_model(Relationship, data=relationship, session=self)
            for relationship in res
        ]

    async def create_relationship(
        self,
        *,
        user_id: int | str,
        type: int | None = None,
        from_friend_suggestion: bool = False,
        confirm_stranger_request: bool = False,
    ) -> None:
        """Create or accept a relationship with another user."""
        await self.client.http.create_relationship(
            self.token,
            user_id=user_id,
            type=type,  # pyright: ignore[reportArgumentType]
            from_friend_suggestion=from_friend_suggestion,
            confirm_stranger_request=confirm_stranger_request,
        )

    async def delete_relationship(
        self,
        *,
        user_id: int | str,
    ) -> None:
        """Delete a relationship with another user."""
        await self.client.http.delete_relationship(self.token, user_id=user_id)

    async def game_relationships(self, token: ValidToken) -> list[GameRelationship]:
        """Fetch game/social-layer relationships."""
        res = await self.client.http.get_game_relationships(token)
        return [
            utils._construct_model(GameRelationship, data=relationship, session=self)
            for relationship in res
        ]

    async def create_game_relationship(
        self,
        *,
        user_id: int | str,
        type: int | None = None,
    ) -> None:
        """Create a game/social-layer relationship."""
        await self.client.http.create_game_relationship(
            self.token,
            user_id=user_id,
            type=type,  # pyright: ignore[reportArgumentType]
        )

    async def delete_game_relationship(
        self,
        *,
        user_id: int | str,
    ) -> None:
        """Delete a game/social-layer relationship."""
        await self.client.http.delete_game_relationship(self.token, user_id=user_id)

    async def create_application_attachment(
        self,
        *,
        application_id: int | str,
        file: File,
    ) -> Attachment:
        """Create an attachment upload slot for an application."""
        res = await self.client.http.create_application_attachment(
            self.token,
            application_id=application_id,
            file=file,
        )
        return utils._construct_model(Attachment, data=res["attachment"])

    async def partial_application(
        self,
        *,
        application_id: int | str,
    ) -> PartialApplication:
        """Fetch a partial application payload."""
        res = await self.client.http.get_partial_application(
            self.token,
            application_id=application_id,
        )
        return utils._construct_model(PartialApplication, data=res, session=self)

    async def user_application_role_connection(
        self,
        *,
        application_id: int | str,
    ) -> ApplicationRoleConnection:
        """Fetch the current user's application role connection. Requires OAuth scope(s): ROLE_CONNECTIONS_WRITE."""
        if not self.client.http.has_scopes(Scope.ROLE_CONNECTIONS_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.ROLE_CONNECTIONS_WRITE],
            )

        res = await self.client.http.get_user_application_role_connection(
            self.token,
            application_id=application_id,
        )
        return utils._construct_model(ApplicationRoleConnection, data=res, session=self)

    async def edit_user_application_role_connection(
        self,
        *,
        application_id: int | str,
        platform_name: str | None = None,
        platform_username: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> ApplicationRoleConnection:
        """Edit the current user's application role connection. Requires OAuth scope(s): ROLE_CONNECTIONS_WRITE."""
        if not self.client.http.has_scopes(Scope.ROLE_CONNECTIONS_WRITE):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.ROLE_CONNECTIONS_WRITE],
            )

        res = await self.client.http.edit_user_application_role_connection(
            self.token,
            application_id=application_id,
            platform_name=platform_name,
            platform_username=platform_username,
            metadata=metadata,
        )
        return utils._construct_model(ApplicationRoleConnection, data=res, session=self)

    async def create_application_quick_link(
        self,
        *,
        application_id: int | str,
        title: str,
        description: str,
        image: File,
        custom_id: str | None = None,
    ) -> ActivityLink:
        """Create an application quick link (activity link)."""
        res = await self.client.http.create_application_quick_link(
            self.token,
            application_id=application_id,
            title=title,
            description=description,
            image=image,
            custom_id=custom_id,
        )
        return utils._construct_model(
            ActivityLink,
            data=res,
        )

    async def bulk_application_identities(
        self,
        *,
        user_ids: list[int | str],
    ) -> list[PartialApplicationIdentity]:
        res = await self.client.http.get_bulk_application_identities(
            self.token, user_ids=user_ids
        )
        return [
            utils._construct_model(
                PartialApplicationIdentity,
                data=identity,
            )
            for identity in res
        ]

    async def application_entitlements(
        self,
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
        if not self.client.http.has_scopes(Scope.APPLICATIONS_ENTITLEMENTS):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.APPLICATIONS_ENTITLEMENTS],
            )

        res = await self.client.http.get_application_entitlements(
            self.token,
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
        return [
            utils._construct_model(Entitlement, data=entitlement, session=self)
            for entitlement in res
        ]

    async def application_entitlement(
        self,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> Entitlement:
        """Fetch a single application entitlement. Requires OAuth scope(s): APPLICATIONS_ENTITLEMENTS."""
        if not self.client.http.has_scopes(Scope.APPLICATIONS_ENTITLEMENTS):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.APPLICATIONS_ENTITLEMENTS],
            )

        res = await self.client.http.get_application_entitlement(
            self.token,
            application_id=application_id,
            entitlement_id=entitlement_id,
        )
        return utils._construct_model(Entitlement, data=res, session=self)

    async def consume_application_entitlement(
        self,
        *,
        entitlement_id: int | str,
    ) -> None:
        """Consume an application entitlement. Requires OAuth scope(s): APPLICATIONS_ENTITLEMENTS."""
        if not self.client.http.has_scopes(Scope.APPLICATIONS_ENTITLEMENTS):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.APPLICATIONS_ENTITLEMENTS],
            )

        await self.client.http.consume_application_entitlement(
            self.token,
            application_id=self.client.http.client_id,
            entitlement_id=entitlement_id,
        )

    async def delete_application_entitlement(
        self,
        *,
        entitlement_id: int | str,
    ) -> None:
        """Delete an application entitlement. Requires OAuth scope(s): APPLICATIONS_ENTITLEMENTS."""
        if not self.client.http.has_scopes(Scope.APPLICATIONS_ENTITLEMENTS):
            raise MissingRequiredScopes(
                current_scopes=self.client.http.current_scopes,
                missing_scopes=[Scope.APPLICATIONS_ENTITLEMENTS],
            )

        await self.client.http.delete_application_entitlement(
            self.token,
            application_id=self.client.http.client_id,
            entitlement_id=entitlement_id,
        )

    async def accept_invite(
        self,
        *,
        code: str,
        session_id: str | None = None,
    ) -> Invite:
        """Accept a Discord invite using the current user token."""
        res = await self.client.http.accept_invite(
            self.token,
            code=code,
            session_id=session_id,
        )
        return utils._construct_model(Invite, data=res, session=self)
