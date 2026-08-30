from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Literal

from ...enums import Service
from ...models.entitlement import Entitlement
from ...models.invite import Invite
from ...models.store import SKU
from ..enums import SendableRPCCommand
from ..models.activity import (
    Activity,
    ImageUpload,
    ShareInteractionResult,
    ShareLinkResult,
)
from ..models.application import Ticket
from ..models.channels import ChannelPermissions, RPCChannel, RPCPartialChannel
from ..models.client import Image, LocaleSettings
from ..models.connection import ProviderAccessToken
from ..models.guild import RPCGuild
from ..models.quest import QuestEnrollmentStatus, TimerResult
from ..models.relationship import RPCRelationship
from ..models.soundboard import SoundboardSound
from ..models.user import RPCActivityParticipant, RPCUser
from ..models.voice import (
    Pan,
    UserVoiceSettings,
    VoiceInputMode,
    VoiceIOSettings,
    VoiceSettings,
    VoiceSettingsMode,
)
from ._proto import _RPCClientProto

if TYPE_CHECKING:
    from ...internals._types import components as component_types
    from ...internals._types import connections as connection_types
    from ...internals._types.rpc import activity as activity_types
    from ...internals._types.rpc import client as client_types
    from ...internals._types.rpc import payloads
    from ...internals._types.rpc import voice as voice_types


class _RPCCommandsClient(_RPCClientProto):  # pyright: ignore[reportUnusedClass]
    async def send_command(
        self: _RPCClientProto,
        command: SendableRPCCommand | str,
        /,
        **args: Any,
    ) -> payloads.RPCCommandResponse:
        return await self._send_command(command, args or None)

    async def get_guild(
        self: _RPCClientProto, *, guild_id: int | str, timeout: int | None = None
    ) -> RPCGuild:
        args: payloads.GetGuildRequest = {"guild_id": guild_id}
        if timeout is not None:
            args["timeout"] = timeout
        data: payloads.GetGuildResponse = await self.send_command(
            SendableRPCCommand.GET_GUILD, **args
        )  # type: ignore
        return RPCGuild(data=data)

    async def get_guilds(self: _RPCClientProto) -> list[RPCGuild]:
        data: payloads.GetGuildsResponse = await self.send_command(
            SendableRPCCommand.GET_GUILDS
        )  # type: ignore
        return [RPCGuild(data=guild) for guild in data["guilds"]]

    async def get_channel(
        self: _RPCClientProto, *, channel_id: int | str
    ) -> RPCChannel:
        args: payloads.GetChannelRequest = {"channel_id": channel_id}
        data: payloads.GetChannelResponse = await self.send_command(
            SendableRPCCommand.GET_CHANNEL, **args
        )  # type: ignore
        return RPCChannel(data=data, state=self._model_state)

    async def get_channels(
        self: _RPCClientProto, *, guild_id: int | str
    ) -> list[RPCPartialChannel]:
        args: payloads.GetChannelsRequest = {"guild_id": guild_id}
        data: payloads.GetChannelsResponse = await self.send_command(
            SendableRPCCommand.GET_CHANNELS, **args
        )  # type: ignore
        return [
            RPCPartialChannel(data=channel, state=self._model_state)
            for channel in data["channels"]
        ]

    async def get_channel_permissions(
        self: _RPCClientProto,
    ) -> ChannelPermissions:
        data: payloads.GetChannelPermissionsResponse = await self.send_command(
            SendableRPCCommand.GET_CHANNEL_PERMISSIONS
        )  # type: ignore
        return ChannelPermissions(data=data)

    async def create_channel_invite(
        self: _RPCClientProto, *, channel_id: int | str
    ) -> Invite:
        self._ensure_session()
        args: payloads.CreateChannelInviteRequest = {"channel_id": channel_id}
        data: payloads.CreateChannelInviteResponse = await self.send_command(
            SendableRPCCommand.CREATE_CHANNEL_INVITE, **args
        )  # type: ignore
        return Invite(data=data, state=self._model_state)

    async def get_relationships(
        self: _RPCClientProto,
    ) -> list[RPCRelationship]:
        data: payloads.GetRelationshipsResponse = await self.send_command(
            SendableRPCCommand.GET_RELATIONSHIPS
        )  # type: ignore
        return [
            RPCRelationship(data=item, state=self._model_state)
            for item in data["relationships"]
        ]

    async def get_user(self: _RPCClientProto, *, id: int | str) -> RPCUser | None:
        args: payloads.GetUserRequest = {"id": id}
        data: payloads.GetUserResponse = await self.send_command(
            SendableRPCCommand.GET_USER, **args
        )  # type: ignore
        return RPCUser(data=data, state=self._model_state) if data is not None else None

    async def set_user_voice_settings(
        self: _RPCClientProto,
        *,
        user_id: int | str,
        pan: Pan | voice_types.RPCPan | None = None,
        volume: int | None = None,
        mute: bool | None = None,
    ) -> UserVoiceSettings:
        args: payloads.SetUserVoiceSettingsRequest = {"user_id": user_id}
        if pan is not None:
            args["pan"] = pan.to_dict() if isinstance(pan, Pan) else pan
        if volume is not None:
            args["volume"] = volume
        if mute is not None:
            args["mute"] = mute
        data: payloads.SetUserVoiceSettingsResponse = await self.send_command(
            SendableRPCCommand.SET_USER_VOICE_SETTINGS, **args
        )  # type: ignore
        return UserVoiceSettings(data=data)

    async def set_user_voice_settings_2(
        self: _RPCClientProto,
        *,
        user_id: int | str,
        volume: int | None = None,
        mute: bool | None = None,
    ) -> None:
        args: payloads.SetUserVoiceSettings2Request = {"user_id": user_id}
        if volume is not None:
            args["volume"] = volume
        if mute is not None:
            args["mute"] = mute
        await self.send_command(SendableRPCCommand.SET_USER_VOICE_SETTINGS_2, **args)

    async def push_to_talk(self: _RPCClientProto, *, active: bool) -> None:
        args: payloads.PushToTalkRequest = {"active": active}
        await self.send_command(SendableRPCCommand.PUSH_TO_TALK, **args)

    async def select_voice_channel(
        self: _RPCClientProto,
        *,
        channel_id: int | str | None,
        timeout: int | None = None,
        force: bool | None = None,
        navigate: bool | None = None,
    ) -> RPCChannel | None:
        args: payloads.SelectVoiceChannelRequest = {"channel_id": channel_id}
        if timeout is not None:
            args["timeout"] = timeout
        if force is not None:
            args["force"] = force
        if navigate is not None:
            args["navigate"] = navigate
        data: payloads.SelectVoiceChannelResponse = await self.send_command(
            SendableRPCCommand.SELECT_VOICE_CHANNEL, **args
        )  # type: ignore
        return (
            RPCChannel(data=data, state=self._model_state) if data is not None else None
        )

    async def get_selected_voice_channel(
        self: _RPCClientProto,
    ) -> RPCChannel | None:
        data: payloads.GetSelectedVoiceChannelResponse = await self.send_command(
            SendableRPCCommand.GET_SELECTED_VOICE_CHANNEL
        )  # type: ignore
        return (
            RPCChannel(data=data, state=self._model_state) if data is not None else None
        )

    async def select_text_channel(
        self: _RPCClientProto,
        *,
        channel_id: int | str | None,
        timeout: int | None = None,
    ) -> RPCChannel | None:
        args: payloads.SelectTextChannelRequest = {"channel_id": channel_id}
        if timeout is not None:
            args["timeout"] = timeout
        data: payloads.SelectTextChannelResponse = await self.send_command(
            SendableRPCCommand.SELECT_TEXT_CHANNEL, **args
        )  # type: ignore
        return (
            RPCChannel(data=data, state=self._model_state) if data is not None else None
        )

    async def get_voice_settings(self: _RPCClientProto) -> VoiceSettings:
        data: payloads.GetVoiceSettingsResponse = await self.send_command(
            SendableRPCCommand.GET_VOICE_SETTINGS
        )  # type: ignore
        return VoiceSettings(data=data)

    async def set_voice_settings(
        self: _RPCClientProto,
        settings: VoiceSettings | None = None,
        /,
        *,
        input: VoiceIOSettings | voice_types.RPCVoiceIOSettingsRequest | None = None,
        output: VoiceIOSettings | voice_types.RPCVoiceIOSettingsRequest | None = None,
        mode: VoiceSettingsMode
        | voice_types.PartialRPCVoiceSettingsModeRequest
        | None = None,
        automatic_gain_control: bool | None = None,
        echo_cancellation: bool | None = None,
        noise_suppression: bool | None = None,
        qos: bool | None = None,
        silence_warning: bool | None = None,
        deaf: bool | None = None,
        mute: bool | None = None,
    ) -> VoiceSettings:
        args: payloads.SetVoiceSettingsRequest = {}
        if settings is not None:
            args = settings.to_dict()
        else:
            if input is not None:
                args["input"] = (
                    input.to_dict() if isinstance(input, VoiceIOSettings) else input
                )
            if output is not None:
                args["output"] = (
                    output.to_dict() if isinstance(output, VoiceIOSettings) else output
                )
            if mode is not None:
                args["mode"] = (
                    mode.to_dict() if isinstance(mode, VoiceSettingsMode) else mode
                )
            for key, value in (
                ("automatic_gain_control", automatic_gain_control),
                ("echo_cancellation", echo_cancellation),
                ("noise_suppression", noise_suppression),
                ("qos", qos),
                ("silence_warning", silence_warning),
                ("deaf", deaf),
                ("mute", mute),
            ):
                if value is not None:
                    args[key] = value
        data: payloads.SetVoiceSettingsResponse = await self.send_command(
            SendableRPCCommand.SET_VOICE_SETTINGS, **args
        )  # type: ignore
        return VoiceSettings(data=data)

    async def set_voice_settings_2(
        self: _RPCClientProto,
        *,
        input_mode: VoiceInputMode | voice_types.RPCVoiceInputModeRequest | None = None,
        self_mute: bool | None = None,
        self_deaf: bool | None = None,
    ) -> None:
        args: payloads.SetVoiceSettings2Request = {}
        if input_mode is not None:
            args["input_mode"] = (
                input_mode.to_dict()
                if isinstance(input_mode, VoiceInputMode)
                else input_mode
            )
        if self_mute is not None:
            args["self_mute"] = self_mute
        if self_deaf is not None:
            args["self_deaf"] = self_deaf
        await self.send_command(SendableRPCCommand.SET_VOICE_SETTINGS_2, **args)

    async def set_activity(
        self: _RPCClientProto,
        activity: Activity | activity_types.ActivityRequest | None = None,
        /,
        *,
        pid: int | None = None,
    ) -> Activity | None:
        args: payloads.SetActivityRequest = {}
        if activity is not None:
            args["activity"] = (
                activity.to_dict() if isinstance(activity, Activity) else activity
            )
        args["pid"] = pid if pid is not None else os.getpid()
        data: payloads.SetActivityResponse = await self.send_command(
            SendableRPCCommand.SET_ACTIVITY, **args
        )  # type: ignore
        print(f"Set activity response data: {data}")  # Debugging line
        return (
            Activity.from_dict(data)
            if data is not None  # pyright: ignore[reportUnnecessaryComparison]
            else None
        )

    async def send_activity_join_invite(
        self: _RPCClientProto, *, user_id: int | str, pid: int | None = None
    ) -> None:
        args: payloads.SendActivityJoinInviteRequest = {
            "user_id": user_id,
            "pid": pid if pid is not None else os.getpid(),
        }
        await self.send_command(SendableRPCCommand.SEND_ACTIVITY_JOIN_INVITE, **args)

    async def close_activity_join_request(
        self: _RPCClientProto, *, user_id: int | str
    ) -> None:
        args: payloads.CloseActivityJoinRequestRequest = {"user_id": user_id}
        await self.send_command(SendableRPCCommand.CLOSE_ACTIVITY_JOIN_REQUEST, **args)

    async def activity_invite_user(
        self: _RPCClientProto,
        *,
        user_id: int | str,
        type: Literal[1],
        pid: int | None = None,
        content: str | None = None,
    ) -> None:
        args: payloads.ActivityInviteUserRequest = {
            "user_id": user_id,
            "type": type,
            "pid": pid if pid is not None else os.getpid(),
        }
        if content is not None:
            args["content"] = content
        await self.send_command(SendableRPCCommand.ACTIVITY_INVITE_USER, **args)

    async def accept_activity_invite(
        self: _RPCClientProto,
        *,
        type: Literal[1],
        user_id: int | str,
        session_id: str,
        channel_id: int | str,
        message_id: int | str,
        application_id: int | str | None = None,
    ) -> None:
        args: payloads.AcceptActivityInviteRequest = {
            "type": type,
            "user_id": user_id,
            "session_id": session_id,
            "channel_id": channel_id,
            "message_id": message_id,
        }
        if application_id is not None:
            args["application_id"] = application_id
        await self.send_command(SendableRPCCommand.ACCEPT_ACTIVITY_INVITE, **args)

    async def open_invite_dialog(self: _RPCClientProto) -> None:
        await self.send_command(SendableRPCCommand.OPEN_INVITE_DIALOG)

    async def open_share_moment_dialog(
        self: _RPCClientProto, *, media_url: str
    ) -> None:
        args: payloads.OpenShareMomentDialogRequest = {"mediaUrl": media_url}
        await self.send_command(SendableRPCCommand.OPEN_SHARE_MOMENT_DIALOG, **args)

    async def share_interaction(
        self: _RPCClientProto,
        *,
        command: str,
        options: list[activity_types.InteractionOptionRequest] | None = None,
        content: str | None = None,
        require_launch_channel: bool | None = None,
        preview_image: activity_types.InteractionResponsePreviewImageRequest
        | None = None,
        components: list[component_types.ActionRowRequest] | None = None,
        pid: int | None = None,
    ) -> ShareInteractionResult:
        args: payloads.ShareInteractionRequest = {"command": command}
        if options is not None:
            args["options"] = options
        if content is not None:
            args["content"] = content
        if require_launch_channel is not None:
            args["require_launch_channel"] = require_launch_channel
        if preview_image is not None:
            args["preview_image"] = preview_image
        if components is not None:
            args["components"] = components
        args["pid"] = pid if pid is not None else os.getpid()
        data: payloads.ShareInteractionResponse = await self.send_command(
            SendableRPCCommand.SHARE_INTERACTION, **args
        )  # type: ignore
        return ShareInteractionResult(data=data)

    async def initiate_image_upload(
        self: _RPCClientProto,
    ) -> ImageUpload:
        data: payloads.InitiateImageUploadResponse = await self.send_command(
            SendableRPCCommand.INITIATE_IMAGE_UPLOAD
        )  # type: ignore
        return ImageUpload(data=data)

    async def share_link(
        self: _RPCClientProto,
        *,
        message: str,
        custom_id: str | None = None,
        link_id: str | None = None,
    ) -> ShareLinkResult:
        args: payloads.ShareLinkRequest = {"message": message}
        if custom_id is not None:
            args["custom_id"] = custom_id
        if link_id is not None:
            args["link_id"] = link_id
        data: payloads.ShareLinkResponse = await self.send_command(
            SendableRPCCommand.SHARE_LINK, **args
        )  # type: ignore
        return ShareLinkResult(data=data)

    async def open_message(
        self: _RPCClientProto,
        *,
        channel_id: int | str,
        message_id: int | str,
        pid: int | None = None,
        guild_id: int | str | None = None,
    ) -> None:
        args: payloads.OpenMessageRequest = {
            "channel_id": channel_id,
            "message_id": message_id,
            "pid": pid if pid is not None else os.getpid(),
        }
        if guild_id is not None:
            args["guild_id"] = guild_id
        await self.send_command(SendableRPCCommand.OPEN_MESSAGE, **args)

    async def set_certified_devices(
        self: _RPCClientProto, *, devices: list[client_types.CertifiedDeviceRequest]
    ) -> None:
        args: payloads.SetCertifiedDevicesRequest = {"devices": devices}
        await self.send_command(SendableRPCCommand.SET_CERTIFIED_DEVICES, **args)

    async def get_image(
        self: _RPCClientProto,
        *,
        type: Literal["user"],
        id: int | str,
        format: Literal["png", "webp", "jpg"],
        size: int,
    ) -> Image:
        args: payloads.GetImageRequest = {
            "type": type,
            "id": id,
            "format": format,
            "size": size,
        }
        data: payloads.GetImageResponse = await self.send_command(
            SendableRPCCommand.GET_IMAGE, **args
        )  # type: ignore
        return Image(data=data)

    async def set_overlay_locked(
        self: _RPCClientProto, *, locked: bool, pid: int | None = None
    ) -> None:
        args: payloads.SetOverlayLockedRequest = {
            "locked": locked,
            "pid": pid if pid is not None else os.getpid(),
        }
        await self.send_command(SendableRPCCommand.SET_OVERLAY_LOCKED, **args)

    async def open_overlay_activity_invite(
        self: _RPCClientProto, *, type: Literal[1], pid: int | None = None
    ) -> None:
        args: payloads.OpenOverlayActivityInviteRequest = {
            "type": type,
            "pid": pid if pid is not None else os.getpid(),
        }
        await self.send_command(SendableRPCCommand.OPEN_OVERLAY_ACTIVITY_INVITE, **args)

    async def open_overlay_guild_invite(
        self: _RPCClientProto, *, code: str, pid: int | None = None
    ) -> None:
        args: payloads.OpenOverlayGuildInviteRequest = {
            "code": code,
            "pid": pid if pid is not None else os.getpid(),
        }
        await self.send_command(SendableRPCCommand.OPEN_OVERLAY_GUILD_INVITE, **args)

    async def open_overlay_voice_settings(
        self: _RPCClientProto, *, pid: int | None = None
    ) -> None:
        args: payloads.OpenOverlayVoiceSettingsRequest = {
            "pid": pid if pid is not None else os.getpid()
        }
        await self.send_command(SendableRPCCommand.OPEN_OVERLAY_VOICE_SETTINGS, **args)

    async def validate_application(self: _RPCClientProto) -> None:
        await self.send_command(SendableRPCCommand.VALIDATE_APPLICATION)

    async def get_entitlement_ticket(
        self: _RPCClientProto,
    ) -> Ticket:
        data: payloads.GetEntitlementTicketResponse = await self.send_command(
            SendableRPCCommand.GET_ENTITLEMENT_TICKET
        )  # type: ignore
        return Ticket(data=data)

    async def get_application_ticket(
        self: _RPCClientProto,
    ) -> Ticket:
        data: payloads.GetApplicationTicketResponse = await self.send_command(
            SendableRPCCommand.GET_APPLICATION_TICKET
        )  # type: ignore
        return Ticket(data=data)

    async def start_purchase(
        self: _RPCClientProto, *, sku_id: int | str, pid: int | None = None
    ) -> list[Entitlement]:
        self._ensure_session()
        args: payloads.StartPurchaseRequest = {"sku_id": sku_id}
        if pid is not None:
            args["pid"] = pid
        data: payloads.StartPurchaseResponse = await self.send_command(
            SendableRPCCommand.START_PURCHASE, **args
        )  # type: ignore
        return [
            Entitlement(data=entitlement, state=self._model_state)
            for entitlement in data
        ]

    async def start_premium_purchase(
        self: _RPCClientProto, *, pid: int | None = None
    ) -> None:
        args: payloads.StartPremiumPurchaseRequest = {}
        if pid is not None:
            args["pid"] = pid
        await self.send_command(SendableRPCCommand.START_PREMIUM_PURCHASE, **args)

    async def get_skus(self: _RPCClientProto) -> list[SKU]:
        self._ensure_session()
        data: payloads.GetSKUsResponse = await self.send_command(
            SendableRPCCommand.GET_SKUS
        )  # type: ignore
        return [SKU(data=sku, state=self._model_state) for sku in data]

    async def get_entitlements(
        self: _RPCClientProto,
    ) -> list[Entitlement]:
        self._ensure_session()
        data: payloads.GetEntitlementsResponse = await self.send_command(
            SendableRPCCommand.GET_ENTITLEMENTS
        )  # type: ignore
        return [
            Entitlement(data=entitlement, state=self._model_state)
            for entitlement in data
        ]

    async def get_skus_embedded(self: _RPCClientProto) -> list[SKU]:
        self._ensure_session()
        data: payloads.GetSKUsEmbeddedResponse = await self.send_command(
            SendableRPCCommand.GET_SKUS_EMBEDDED
        )  # type: ignore
        return [SKU(data=sku, state=self._model_state) for sku in data["skus"]]

    async def get_entitlements_embedded(
        self: _RPCClientProto,
    ) -> list[Entitlement]:
        self._ensure_session()
        data: payloads.GetEntitlementsEmbeddedResponse = await self.send_command(
            SendableRPCCommand.GET_ENTITLEMENTS_EMBEDDED
        )  # type: ignore
        return [
            Entitlement(data=entitlement, state=self._model_state)
            for entitlement in data["entitlements"]
        ]

    async def user_settings_get_locale(
        self: _RPCClientProto,
    ) -> LocaleSettings:
        data: payloads.UserSettingsGetLocaleResponse = await self.send_command(
            SendableRPCCommand.USER_SETTINGS_GET_LOCALE
        )  # type: ignore
        return LocaleSettings(data=data)

    async def open_external_link(self: _RPCClientProto, *, url: str) -> None:
        args: payloads.OpenExternalLinkRequest = {"url": url}
        await self.send_command(SendableRPCCommand.OPEN_EXTERNAL_LINK, **args)

    async def get_soundboard_sounds(
        self: _RPCClientProto,
    ) -> list[SoundboardSound]:
        data: payloads.GetSoundboardSoundsResponse = await self.send_command(
            SendableRPCCommand.GET_SOUNDBOARD_SOUNDS
        )  # type: ignore
        return [SoundboardSound(data=sound) for sound in data]

    async def play_soundboard_sound(
        self: _RPCClientProto,
        *,
        guild_id: int | str | None = None,
        sound_id: int | str | None = None,
    ) -> None:
        args: payloads.PlaySoundboardSoundRequest = {}
        if guild_id is not None:
            args["guild_id"] = guild_id
        if sound_id is not None:
            args["sound_id"] = sound_id
        await self.send_command(SendableRPCCommand.PLAY_SOUNDBOARD_SOUND, **args)

    async def toggle_video(self: _RPCClientProto) -> None:
        await self.send_command(SendableRPCCommand.TOGGLE_VIDEO)

    async def toggle_screenshare(
        self: _RPCClientProto, *, pid: int | None = None
    ) -> None:
        args: payloads.ToggleScreenshareRequest = {}
        if pid is not None:
            args["pid"] = pid
        await self.send_command(SendableRPCCommand.TOGGLE_SCREENSHARE, **args)

    async def get_activity_instance_connected_participants(
        self: _RPCClientProto,
    ) -> list[RPCActivityParticipant]:
        data: payloads.GetActivityInstanceConnectedParticipantsResponse = (
            await self.send_command(
                SendableRPCCommand.GET_ACTIVITY_INSTANCE_CONNECTED_PARTICIPANTS
            )  # type: ignore
        )
        return [
            RPCActivityParticipant(
                data=participant,
                state=self._model_state,
            )
            for participant in data["participants"]
        ]

    async def get_provider_access_token(
        self: _RPCClientProto,
        *,
        provider: Service | connection_types.Service,
        connection_redirect: str | None = None,
    ) -> ProviderAccessToken:
        args: payloads.GetProviderAccessTokenRequest = {
            "provider": provider.value if isinstance(provider, Service) else provider
        }
        if connection_redirect is not None:
            args["connection_redirect"] = connection_redirect
        data: payloads.GetProviderAccessTokenResponse = await self.send_command(
            SendableRPCCommand.GET_PROVIDER_ACCESS_TOKEN, **args
        )  # type: ignore
        return ProviderAccessToken(data=data)

    async def maybe_get_provider_access_token(
        self: _RPCClientProto,
        *,
        provider: Service | connection_types.Service,
    ) -> ProviderAccessToken:
        args: payloads.MaybeGetProviderAccessTokenRequest = {
            "provider": provider.value if isinstance(provider, Service) else provider
        }
        data: payloads.MaybeGetProviderAccessTokenResponse = await self.send_command(
            SendableRPCCommand.MAYBE_GET_PROVIDER_ACCESS_TOKEN, **args
        )  # type: ignore
        return ProviderAccessToken(data=data)

    async def navigate_to_connections(self: _RPCClientProto) -> None:
        await self.send_command(SendableRPCCommand.NAVIGATE_TO_CONNECTIONS)

    async def invite_user_embedded(
        self: _RPCClientProto, *, user_id: int | str, content: str | None = None
    ) -> None:
        args: payloads.InviteUserEmbeddedRequest = {"user_id": user_id}
        if content is not None:
            args["content"] = content
        await self.send_command(SendableRPCCommand.INVITE_USER_EMBEDDED, **args)

    async def request_proxy_ticket_refresh(
        self: _RPCClientProto,
    ) -> Ticket:
        data: payloads.RequestProxyTicketRefreshResponse = await self.send_command(
            SendableRPCCommand.REQUEST_PROXY_TICKET_REFRESH
        )  # type: ignore
        return Ticket(data=data)

    async def get_quest_enrollment_status(
        self: _RPCClientProto, *, quest_id: int | str
    ) -> QuestEnrollmentStatus:
        args: payloads.GetQuestEnrollmentStatusRequest = {"quest_id": quest_id}
        data: payloads.GetQuestEnrollmentStatusResponse = await self.send_command(
            SendableRPCCommand.GET_QUEST_ENROLLMENT_STATUS, **args
        )  # type: ignore
        return QuestEnrollmentStatus(data=data)

    async def quest_start_timer(
        self: _RPCClientProto, *, quest_id: int | str
    ) -> TimerResult:
        args: payloads.QuestStartTimerRequest = {"quest_id": quest_id}
        data: payloads.QuestStartTimerResponse = await self.send_command(
            SendableRPCCommand.QUEST_START_TIMER, **args
        )  # type: ignore
        return TimerResult(data=data)
