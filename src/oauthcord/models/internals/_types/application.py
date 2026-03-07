from typing import Literal, NotRequired, TypedDict

from .attachment import Attachment
from .base import Snowflake
from .user import PartialUserResponse

ApplicationType = Literal[1, 2, 3, 4, 5]
ApplicationIntegrationType = Literal[0, 1]
ApplicationSKUDistributor = Literal[
    "discord",
    "steam",
    "twitch",
    "uplay",
    "battlenet",
    "origin",
    "gog",
    "epic",
    "microsoft",
    "igdb",
    "glyph",
    "google_play",
    "nvidia_gdn_app",
    "gop",
    "roblox",
    "gdco",
    "xbox",
    "playstation",
]
EmbeddedActivityPlatform = Literal["web", "android", "ios"]
EmbeddedActivityOrientationLockState = Literal[1, 2, 3]
EmbeddedActivityLabelType = Literal[0, 1, 2]
EmbeddedActivityReleasePhase = Literal[
    "in_development",
    "activities_team",
    "employee_release",
    "soft_launch",
    "soft_launch_multi_geo",
    "global_launch",
]
EmbeddedActivitySurface = Literal["voice_launcher", "text_launcher"]


class CreateApplicationAttachmentResponse(TypedDict):
    attachment: Attachment


class ApplicationExecutableResponse(TypedDict):
    os: str
    name: str
    is_launcher: bool


class ApplicationSKUResponse(TypedDict):
    distributor: ApplicationSKUDistributor | str
    id: NotRequired[str | None]
    sku: NotRequired[str | None]


class CompanyResponse(TypedDict):
    id: Snowflake
    name: str


class ApplicationInstallParamsResponse(TypedDict):
    scopes: list[str]
    permissions: str


class ApplicationIntegrationTypeConfigurationResponse(TypedDict):
    oauth2_install_params: NotRequired[ApplicationInstallParamsResponse]


class EmbeddedActivityPlatformConfigResponse(TypedDict):
    label_type: EmbeddedActivityLabelType | int
    release_phase: EmbeddedActivityReleasePhase | str
    label_until: NotRequired[str | None]
    omit_badge_from_surfaces: NotRequired[list[EmbeddedActivitySurface | str]]


class EmbeddedActivityConfigResponse(TypedDict):
    activity_preview_video_asset_id: Snowflake | None
    supported_platforms: list[EmbeddedActivityPlatform | str]
    default_orientation_lock_state: EmbeddedActivityOrientationLockState | int
    tablet_default_orientation_lock_state: EmbeddedActivityOrientationLockState | int
    requires_age_gate: bool
    legacy_responsive_aspect_ratio: bool
    premium_tier_requirement: int | None
    free_period_starts_at: str | None
    free_period_ends_at: str | None
    client_platform_config: dict[
        EmbeddedActivityPlatform | str, EmbeddedActivityPlatformConfigResponse
    ]
    shelf_rank: int
    has_csp_exception: bool
    displays_advertisements: bool
    application_id: NotRequired[Snowflake]
    supported_locales: NotRequired[list[str]]
    blocked_locales: NotRequired[list[str]]


class ApplicationRoleConnectionMetadataResponse(TypedDict):
    type: int
    key: str
    name: str
    description: str
    name_localizations: NotRequired[dict[str, str]]
    description_localizations: NotRequired[dict[str, str]]


class ApplicationRoleConnectionResponse(TypedDict):
    metadata: dict[str, str]
    platform_name: NotRequired[str | None]
    platform_username: NotRequired[str | None]
    application: NotRequired["PartialApplicationResponse | None"]
    application_metadata: NotRequired[list[ApplicationRoleConnectionMetadataResponse]]


class ModifyUserApplicationRoleConnectionRequest(TypedDict):
    platform_name: NotRequired[str | None]
    platform_username: NotRequired[str | None]
    metadata: NotRequired[dict[str, str] | None]


class ActivityLinkResponse(TypedDict):
    application_id: Snowflake
    link_id: str
    title: str
    description: str
    asset_path: NotRequired[str]
    asset_id: NotRequired[Snowflake]
    custom_id: NotRequired[str | None]
    primary_cta: NotRequired[str | None]


class CreateApplicationQuickLinkRequest(TypedDict):
    title: str
    description: str
    image: str
    custom_id: NotRequired[str | None]


class PartialApplicationIdentityResponse(TypedDict):
    user_id: Snowflake
    external_user_id: str


class GetBulkApplicationIdentitiesRequest(TypedDict):
    user_ids: list[Snowflake]


GetBulkApplicationIdentitiesResponse = list[PartialApplicationIdentityResponse]


class PartialApplicationResponse(TypedDict):
    id: Snowflake
    name: str
    description: str
    icon: str | None
    type: ApplicationType | int | None
    flags: int
    verify_key: str
    hook: bool
    is_verified: bool
    is_discoverable: bool
    is_monetized: bool
    storefront_available: bool
    cover_image: NotRequired[str]
    splash: NotRequired[str]
    primary_sku_id: NotRequired[Snowflake]
    eula_id: NotRequired[Snowflake]
    slug: NotRequired[str]
    aliases: NotRequired[list[str]]
    executables: NotRequired[list[ApplicationExecutableResponse]]
    third_party_skus: NotRequired[list[ApplicationSKUResponse]]
    overlay: NotRequired[bool]
    overlay_methods: NotRequired[int]
    overlay_warn: NotRequired[bool]
    overlay_compatibility_hook: NotRequired[bool]
    bot: NotRequired[PartialUserResponse]
    developers: NotRequired[list[CompanyResponse]]
    publishers: NotRequired[list[CompanyResponse]]
    rpc_origins: NotRequired[list[str]]
    deeplink_uri: NotRequired[str]
    integration_public: NotRequired[bool]
    integration_require_code_grant: NotRequired[bool]
    bot_public: NotRequired[bool]
    bot_require_code_grant: NotRequired[bool]
    terms_of_service_url: NotRequired[str | None]
    privacy_policy_url: NotRequired[str | None]
    tags: NotRequired[list[str]]
    install_params: NotRequired[ApplicationInstallParamsResponse]
    custom_install_url: NotRequired[str]
    integration_types_config: NotRequired[
        dict[
            int | ApplicationIntegrationType,
            ApplicationIntegrationTypeConfigurationResponse | None,
        ]
    ]
    connection_entrypoint_url: NotRequired[str]
    max_participants: NotRequired[int]
    embedded_activity_config: NotRequired[EmbeddedActivityConfigResponse]
    parent_id: NotRequired[Snowflake]


PartialApplication = PartialApplicationResponse
