"""The RPC packet envelopes and the unions of every command's arguments and data.

Every command listed in :class:`~oauthcord.rpc._command._RPCCommand` has a
``...Request`` type for its arguments (omitted when the command takes none) and a
``...Response`` type for the ``data`` field of the incoming payload it produces.
Those live in the per-topic modules alongside the resource types they reference;
this module only collects them.

Commands gated behind the ``rpc.private`` / ``rpc.private.limited`` scopes and the
deprecated GameSDK networking commands are omitted, matching ``_RPCCommand``.

See https://docs.discord.food/topics/rpc#packet-payloads.
"""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from .activity import (
    AcceptActivityInviteRequest,
    ActivityInviteUserRequest,
    CloseActivityJoinRequestRequest,
    GetActivityInstanceConnectedParticipantsResponse,
    InitiateImageUploadResponse,
    OpenShareMomentDialogRequest,
    SendActivityJoinInviteRequest,
    SetActivityRequest,
    SetActivityResponse,
    ShareInteractionRequest,
    ShareInteractionResponse,
    ShareLinkRequest,
    ShareLinkResponse,
)
from .application import (
    GetApplicationTicketResponse,
    GetEntitlementsEmbeddedResponse,
    GetEntitlementsResponse,
    GetEntitlementTicketResponse,
    GetSKUsEmbeddedResponse,
    GetSKUsResponse,
    RequestProxyTicketRefreshResponse,
    StartPremiumPurchaseRequest,
    StartPurchaseRequest,
    StartPurchaseResponse,
)
from .auth import (
    AuthenticateRequest,
    AuthenticateResponse,
    AuthorizeRequest,
    AuthorizeResponse,
)
from .channels import (
    CreateChannelInviteRequest,
    CreateChannelInviteResponse,
    GetChannelPermissionsResponse,
    GetChannelRequest,
    GetChannelResponse,
    GetChannelsRequest,
    GetChannelsResponse,
    GetSelectedVoiceChannelResponse,
    SelectTextChannelRequest,
    SelectTextChannelResponse,
    SelectVoiceChannelRequest,
    SelectVoiceChannelResponse,
)
from .client import (
    GetImageRequest,
    GetImageResponse,
    OpenExternalLinkRequest,
    SetCertifiedDevicesRequest,
    UserSettingsGetLocaleResponse,
)
from .connection import (
    GetProviderAccessTokenRequest,
    GetProviderAccessTokenResponse,
    InviteUserEmbeddedRequest,
    MaybeGetProviderAccessTokenRequest,
    MaybeGetProviderAccessTokenResponse,
)
from .events import (
    SubscribeRequest,
    SubscribeResponse,
    UnsubscribeRequest,
    UnsubscribeResponse,
)
from .guild import GetGuildRequest, GetGuildResponse, GetGuildsResponse
from .message import OpenMessageRequest
from .overlay import (
    OpenOverlayActivityInviteRequest,
    OpenOverlayGuildInviteRequest,
    OpenOverlayVoiceSettingsRequest,
    SetOverlayLockedRequest,
)
from .quest import (
    GetQuestEnrollmentStatusRequest,
    GetQuestEnrollmentStatusResponse,
    QuestStartTimerRequest,
    QuestStartTimerResponse,
)
from .relationship import GetRelationshipsResponse
from .soundboard import GetSoundboardSoundsResponse, PlaySoundboardSoundRequest
from .user import GetUserRequest, GetUserResponse
from .video import ToggleScreenshareRequest
from .voice import (
    GetVoiceSettingsResponse,
    PushToTalkRequest,
    SetUserVoiceSettings2Request,
    SetUserVoiceSettingsRequest,
    SetUserVoiceSettingsResponse,
    SetVoiceSettings2Request,
    SetVoiceSettingsRequest,
    SetVoiceSettingsResponse,
)

RPCCommandType = Literal[
    "DISPATCH",
    "AUTHORIZE",
    "AUTHENTICATE",
    "SUBSCRIBE",
    "UNSUBSCRIBE",
    "GET_GUILD",
    "GET_GUILDS",
    "GET_CHANNEL",
    "GET_CHANNELS",
    "GET_CHANNEL_PERMISSIONS",
    "CREATE_CHANNEL_INVITE",
    "GET_RELATIONSHIPS",
    "GET_USER",
    "SET_USER_VOICE_SETTINGS",
    "SET_USER_VOICE_SETTINGS_2",
    "PUSH_TO_TALK",
    "SELECT_VOICE_CHANNEL",
    "GET_SELECTED_VOICE_CHANNEL",
    "SELECT_TEXT_CHANNEL",
    "GET_VOICE_SETTINGS",
    "SET_VOICE_SETTINGS",
    "SET_VOICE_SETTINGS_2",
    "SET_ACTIVITY",
    "SEND_ACTIVITY_JOIN_INVITE",
    "CLOSE_ACTIVITY_JOIN_REQUEST",
    "ACTIVITY_INVITE_USER",
    "ACCEPT_ACTIVITY_INVITE",
    "OPEN_INVITE_DIALOG",
    "OPEN_SHARE_MOMENT_DIALOG",
    "SHARE_INTERACTION",
    "INITIATE_IMAGE_UPLOAD",
    "SHARE_LINK",
    "OPEN_MESSAGE",
    "SET_CERTIFIED_DEVICES",
    "GET_IMAGE",
    "SET_OVERLAY_LOCKED",
    "OPEN_OVERLAY_ACTIVITY_INVITE",
    "OPEN_OVERLAY_GUILD_INVITE",
    "OPEN_OVERLAY_VOICE_SETTINGS",
    "VALIDATE_APPLICATION",
    "GET_ENTITLEMENT_TICKET",
    "GET_APPLICATION_TICKET",
    "START_PURCHASE",
    "START_PREMIUM_PURCHASE",
    "GET_SKUS",
    "GET_ENTITLEMENTS",
    "GET_SKUS_EMBEDDED",
    "GET_ENTITLEMENTS_EMBEDDED",
    "USER_SETTINGS_GET_LOCALE",
    "OPEN_EXTERNAL_LINK",
    "GET_SOUNDBOARD_SOUNDS",
    "PLAY_SOUNDBOARD_SOUND",
    "TOGGLE_VIDEO",
    "TOGGLE_SCREENSHARE",
    "GET_ACTIVITY_INSTANCE_CONNECTED_PARTICIPANTS",
    "GET_PROVIDER_ACCESS_TOKEN",
    "MAYBE_GET_PROVIDER_ACCESS_TOKEN",
    "NAVIGATE_TO_CONNECTIONS",
    "INVITE_USER_EMBEDDED",
    "REQUEST_PROXY_TICKET_REFRESH",
    "GET_QUEST_ENROLLMENT_STATUS",
    "QUEST_START_TIMER",
]

RPCCommandRequest = (
    AuthorizeRequest
    | AuthenticateRequest
    | SubscribeRequest
    | UnsubscribeRequest
    | GetGuildRequest
    | GetChannelRequest
    | GetChannelsRequest
    | CreateChannelInviteRequest
    | GetUserRequest
    | SetUserVoiceSettingsRequest
    | SetUserVoiceSettings2Request
    | PushToTalkRequest
    | SelectVoiceChannelRequest
    | SelectTextChannelRequest
    | SetVoiceSettingsRequest
    | SetVoiceSettings2Request
    | SetActivityRequest
    | SendActivityJoinInviteRequest
    | CloseActivityJoinRequestRequest
    | ActivityInviteUserRequest
    | AcceptActivityInviteRequest
    | OpenShareMomentDialogRequest
    | ShareInteractionRequest
    | ShareLinkRequest
    | OpenMessageRequest
    | SetCertifiedDevicesRequest
    | GetImageRequest
    | SetOverlayLockedRequest
    | OpenOverlayActivityInviteRequest
    | OpenOverlayGuildInviteRequest
    | OpenOverlayVoiceSettingsRequest
    | StartPurchaseRequest
    | StartPremiumPurchaseRequest
    | OpenExternalLinkRequest
    | PlaySoundboardSoundRequest
    | ToggleScreenshareRequest
    | GetProviderAccessTokenRequest
    | MaybeGetProviderAccessTokenRequest
    | InviteUserEmbeddedRequest
    | GetQuestEnrollmentStatusRequest
    | QuestStartTimerRequest
)
"""The arguments of any command that takes them."""


class _RPCCommandRequest(  # type: ignore
    AuthorizeRequest,
    AuthenticateRequest,
    SubscribeRequest,
    GetGuildRequest,
    GetChannelRequest,
    GetChannelsRequest,
    CreateChannelInviteRequest,
    GetUserRequest,
    SetUserVoiceSettingsRequest,
    SetUserVoiceSettings2Request,
    PushToTalkRequest,
    SelectVoiceChannelRequest,
    SelectTextChannelRequest,
    SetVoiceSettingsRequest,
    SetVoiceSettings2Request,
    SetActivityRequest,
    SendActivityJoinInviteRequest,
    CloseActivityJoinRequestRequest,
    ActivityInviteUserRequest,
    AcceptActivityInviteRequest,
    OpenShareMomentDialogRequest,
    ShareInteractionRequest,
    ShareLinkRequest,
    OpenMessageRequest,
    SetCertifiedDevicesRequest,
    GetImageRequest,
    SetOverlayLockedRequest,
    OpenOverlayActivityInviteRequest,
    OpenOverlayGuildInviteRequest,
    OpenOverlayVoiceSettingsRequest,
    StartPurchaseRequest,
    StartPremiumPurchaseRequest,
    OpenExternalLinkRequest,
    PlaySoundboardSoundRequest,
    ToggleScreenshareRequest,
    GetProviderAccessTokenRequest,
    MaybeGetProviderAccessTokenRequest,
    InviteUserEmbeddedRequest,
    GetQuestEnrollmentStatusRequest,
    QuestStartTimerRequest,
): ...


RPCCommandResponse = (
    AuthorizeResponse
    | AuthenticateResponse
    | SubscribeResponse
    | UnsubscribeResponse
    | GetGuildResponse
    | GetGuildsResponse
    | GetChannelResponse
    | GetChannelsResponse
    | GetChannelPermissionsResponse
    | CreateChannelInviteResponse
    | GetRelationshipsResponse
    | GetUserResponse
    | SetUserVoiceSettingsResponse
    | SelectVoiceChannelResponse
    | GetSelectedVoiceChannelResponse
    | SelectTextChannelResponse
    | GetVoiceSettingsResponse
    | SetVoiceSettingsResponse
    | SetActivityResponse
    | ShareInteractionResponse
    | InitiateImageUploadResponse
    | ShareLinkResponse
    | GetImageResponse
    | GetEntitlementTicketResponse
    | GetApplicationTicketResponse
    | StartPurchaseResponse
    | GetSKUsResponse
    | GetEntitlementsResponse
    | GetSKUsEmbeddedResponse
    | GetEntitlementsEmbeddedResponse
    | UserSettingsGetLocaleResponse
    | GetSoundboardSoundsResponse
    | GetActivityInstanceConnectedParticipantsResponse
    | GetProviderAccessTokenResponse
    | MaybeGetProviderAccessTokenResponse
    | RequestProxyTicketRefreshResponse
    | GetQuestEnrollmentStatusResponse
    | QuestStartTimerResponse
    | None
)
"""The ``data`` of any command response, excluding ``DISPATCH`` (which carries the
payload of the dispatched event instead)."""


class _RPCCommandResponse(  # type: ignore
    AuthorizeResponse,
    AuthenticateResponse,
    SubscribeResponse,
    GetGuildResponse,
    GetGuildsResponse,
    GetChannelResponse,
    GetChannelsResponse,
    GetChannelPermissionsResponse,
    CreateChannelInviteResponse,
    GetRelationshipsResponse,
    SetUserVoiceSettingsResponse,
    GetVoiceSettingsResponse,
    SetActivityResponse,
    ShareInteractionResponse,
    InitiateImageUploadResponse,
    ShareLinkResponse,
    GetImageResponse,
    GetEntitlementTicketResponse,
    GetApplicationTicketResponse,
    StartPurchaseResponse,
    GetSKUsEmbeddedResponse,
    GetEntitlementsEmbeddedResponse,
    UserSettingsGetLocaleResponse,
    GetActivityInstanceConnectedParticipantsResponse,
    GetProviderAccessTokenResponse,
    RequestProxyTicketRefreshResponse,
    GetQuestEnrollmentStatusResponse,
    QuestStartTimerResponse,
): ...


class RPCOutgoingPayload(TypedDict):
    cmd: RPCCommandType
    args: RPCCommandRequest
    nonce: str
    evt: NotRequired[str]  # required when cmd is SUBSCRIBE or UNSUBSCRIBE


class RPCIncomingPayload(TypedDict):
    cmd: RPCCommandType
    data: RPCCommandResponse
    nonce: str | None
    evt: NotRequired[str | None]  # only present in DISPATCH/(UN)SUBSCRIBE payloads
