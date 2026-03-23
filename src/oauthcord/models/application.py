import datetime
from typing import TYPE_CHECKING, override

from ..utils import convert_snowflake, iso_to_datetime
from ._base import *
from .enums import (
    ActivityLinkType,
    ApplicationSKUDistributor,
    ApplicationType,
    EmbeddedActivityLabelType,
    EmbeddedActivityOrientationLockStateType,
    EmbeddedActivityPlatformType,
    EmbeddedActivityReleasePhase,
    EmbeddedActivitySurface,
    IntegrationInstallType,
    to_enum,
)
from .user import PartialUser

if TYPE_CHECKING:
    from .attachment import Attachment
    from .file import File
    from ..internals._types.application import (
        ActivityLinkResponse,
        ApplicationExecutableResponse,
        ApplicationInstallParamsResponse,
        ApplicationIntegrationTypeConfigurationResponse,
        ApplicationRoleConnectionMetadataResponse,
        ApplicationRoleConnectionResponse,
        ApplicationSKUResponse,
        CompanyResponse,
        EmbeddedActivityConfigResponse,
        EmbeddedActivityPlatformConfigResponse,
        PartialApplicationIdentityResponse,
        PartialApplicationResponse,
    )


__all__ = (
    "ActivityLink",
    "ApplicationExecutable",
    "ApplicationInstallParams",
    "ApplicationIntegrationTypeConfiguration",
    "ApplicationRoleConnection",
    "ApplicationRoleConnectionMetadata",
    "ApplicationSKU",
    "Company",
    "EmbeddedActivityConfig",
    "EmbeddedActivityPlatformConfig",
    "PartialApplication",
    "PartialApplicationIdentity",
)


class ApplicationExecutable(BaseModel["ApplicationExecutableResponse"]):
    """Executable metadata for a Discord application build.

    This model represents an executable entry returned for game or application
    distributions, including the target operating system and launcher status.

    Attributes
    ----------
    os: :class:`str`
        The target operating system identifier.
    name: :class:`str`
        The executable name.
    is_launcher: :class:`bool`
        Whether this executable is the primary launcher.
    """

    __slots__ = ("is_launcher", "name", "os")

    @override
    def _initialize(self, data: ApplicationExecutableResponse) -> None:
        self.os: str = data["os"]
        self.name: str = data["name"]
        self.is_launcher: bool = data["is_launcher"]


class ApplicationSKU(BaseModel["ApplicationSKUResponse"]):
    """Third-party SKU metadata associated with an application.

    This model stores external store identifiers and the distributor platform
    for a linked SKU.

    Attributes
    ----------
    id: :class:`str`
        The external SKU identifier, if provided.
    sku: :class:`str`
        The store SKU value, if provided.
    distributor: :class:`ApplicationSKUDistributor`
        The distributor platform for the SKU.
    """

    __slots__ = ("distributor", "id", "sku")

    @override
    def _initialize(self, data: ApplicationSKUResponse) -> None:
        self.id: str | None = data.get("id")
        self.sku: str | None = data.get("sku")
        self.distributor: ApplicationSKUDistributor = to_enum(
            ApplicationSKUDistributor, data["distributor"]
        )


class Company(BaseModel["CompanyResponse"]):
    """Developer or publisher company information for an application.


    Discord uses this payload to represent organizations attached to an
    application, such as developers and publishers.

    Attributes
    ----------
    id: :class:`int`
        The company snowflake identifier.
    name: :class:`str`
        The company display name.
    """

    __slots__ = ("id", "name")

    @override
    def _initialize(self, data: CompanyResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]


class ApplicationInstallParams(BaseModel["ApplicationInstallParamsResponse"]):
    """OAuth2 install parameters for an application.

    This model contains the scopes and permissions Discord uses when building
    an installation or authorization URL for the application.

    Attributes
    ----------
    scopes: :class:`list` of :class:`str`
        The OAuth2 scopes requested for installation.
    permissions: :class:`str`
        The permissions bitset represented as a string.
    """

    __slots__ = ("permissions", "scopes")

    @override
    def _initialize(self, data: ApplicationInstallParamsResponse) -> None:
        self.scopes: list[str] = data["scopes"]
        self.permissions: str = data["permissions"]


class ApplicationIntegrationTypeConfiguration(
    BaseModel["ApplicationIntegrationTypeConfigurationResponse"]
):
    """Configuration for a specific application integration install type.


    Discord may return install settings keyed by integration type. This model
    currently exposes the optional OAuth2 install parameters for that entry.

    Attributes
    ----------
    oauth2_install_params: :class:`ApplicationInstallParams`
        The OAuth2 install parameters for this integration type, if present.
    """

    __slots__ = ("oauth2_install_params",)

    @override
    def _initialize(
        self, data: ApplicationIntegrationTypeConfigurationResponse
    ) -> None:
        self.oauth2_install_params: ApplicationInstallParams | None = (
            self._initialize_other(ApplicationInstallParams, data, optional=True)
        )


class EmbeddedActivityPlatformConfig(
    BaseModel["EmbeddedActivityPlatformConfigResponse"]
):
    __slots__ = (
        "label_type",
        "label_until",
        "omit_badge_from_surfaces",
        "release_phase",
    )
    """Per-platform configuration for an embedded activity.

    This model describes release labeling and badge visibility settings for a
    specific embedded activity platform.

    Attributes
    ----------
    label_type: :class:`EmbeddedActivityLabelType`
        The label type shown for the activity on this platform.
    release_phase: :class:`EmbeddedActivityReleasePhase`
        The release phase for the activity.
    label_until: :class:`datetime.datetime`
        The datetime until which the label should be shown, if provided.
    omit_badge_from_surfaces: :class:`list` of :class:`EmbeddedActivitySurface`
        Surfaces where the label badge should be hidden.
    """

    @override
    def _initialize(self, data: EmbeddedActivityPlatformConfigResponse) -> None:
        self.label_type: EmbeddedActivityLabelType = to_enum(
            EmbeddedActivityLabelType, data["label_type"]
        )
        self.release_phase: EmbeddedActivityReleasePhase = to_enum(
            EmbeddedActivityReleasePhase, data["release_phase"]
        )
        self.label_until: datetime.datetime | None = iso_to_datetime(
            data.get("label_until")
        )
        self.omit_badge_from_surfaces: list[EmbeddedActivitySurface] = [
            to_enum(EmbeddedActivitySurface, surface)
            for surface in data.get("omit_badge_from_surfaces", [])
        ]


class EmbeddedActivityConfig(BaseModel["EmbeddedActivityConfigResponse"]):
    """Configuration payload for a Discord embedded activity.

    This model contains platform support, orientation behavior, availability
    windows, locale restrictions, and other runtime settings for activities.

    Attributes
    ----------
    application_id: :class:`int`
        The parent application snowflake, if available.
    activity_preview_video_asset_id: :class:`int`
        The preview video asset snowflake, if available.
    supported_platforms: :class:`list` of :class:`EmbeddedActivityPlatformType`
        Platforms supported by the activity.
    default_orientation_lock_state: :class:`EmbeddedActivityOrientationLockStateType`
        The default orientation lock state.
    tablet_default_orientation_lock_state: :class:`EmbeddedActivityOrientationLockStateType`
        The default orientation lock state on tablets.
    requires_age_gate: :class:`bool`
        Whether the activity is age gated.
    legacy_responsive_aspect_ratio: :class:`bool`
        Whether the activity uses legacy responsive aspect ratio behavior.
    premium_tier_requirement: :class:`int`
        The premium tier required to access the activity, if provided.
    free_period_starts_at: :class:`datetime.datetime`
        The start datetime of the free period, if provided.
    free_period_ends_at: :class:`datetime.datetime`
        The end datetime of the free period, if provided.
    client_platform_config: :class:`dict`
        Per-platform configuration entries.
    shelf_rank: :class:`int`
        The shelf rank assigned to the activity.
    has_csp_exception: :class:`bool`
        Whether the activity has a CSP exception.
    displays_advertisements: :class:`bool`
        Whether the activity displays advertisements.
    supported_locales: :class:`list` of :class:`str`
        Locale codes supported by the activity.
    blocked_locales: :class:`list` of :class:`str`
        Locale codes blocked for the activity.
    """

    __slots__ = (
        "activity_preview_video_asset_id",
        "application_id",
        "blocked_locales",
        "client_platform_config",
        "default_orientation_lock_state",
        "displays_advertisements",
        "free_period_ends_at",
        "free_period_starts_at",
        "has_csp_exception",
        "legacy_responsive_aspect_ratio",
        "premium_tier_requirement",
        "requires_age_gate",
        "shelf_rank",
        "supported_locales",
        "supported_platforms",
        "tablet_default_orientation_lock_state",
    )

    @override
    def _initialize(self, data: EmbeddedActivityConfigResponse) -> None:
        self.application_id: int | None = convert_snowflake(
            data, "application_id", always_available=False
        )
        self.activity_preview_video_asset_id: int | None = convert_snowflake(
            data, "activity_preview_video_asset_id", always_available=False
        )
        self.supported_platforms: list[EmbeddedActivityPlatformType] = [
            to_enum(EmbeddedActivityPlatformType, platform)
            for platform in data["supported_platforms"]
        ]
        self.default_orientation_lock_state: EmbeddedActivityOrientationLockStateType = to_enum(
            EmbeddedActivityOrientationLockStateType,
            data["default_orientation_lock_state"],
        )
        self.tablet_default_orientation_lock_state: EmbeddedActivityOrientationLockStateType = to_enum(
            EmbeddedActivityOrientationLockStateType,
            data["tablet_default_orientation_lock_state"],
        )
        self.requires_age_gate: bool = data["requires_age_gate"]
        self.legacy_responsive_aspect_ratio: bool = data[
            "legacy_responsive_aspect_ratio"
        ]
        self.premium_tier_requirement: int | None = data["premium_tier_requirement"]
        self.free_period_starts_at: datetime.datetime | None = iso_to_datetime(
            data["free_period_starts_at"]
        )
        self.free_period_ends_at: datetime.datetime | None = iso_to_datetime(
            data["free_period_ends_at"]
        )
        self.client_platform_config: dict[
            EmbeddedActivityPlatformType, EmbeddedActivityPlatformConfig
        ] = {
            to_enum(EmbeddedActivityPlatformType, platform): self._initialize_other(
                EmbeddedActivityPlatformConfig, cfg
            )
            for platform, cfg in data["client_platform_config"].items()
        }
        self.shelf_rank: int = data["shelf_rank"]
        self.has_csp_exception: bool = data["has_csp_exception"]
        self.displays_advertisements: bool = data["displays_advertisements"]
        self.supported_locales: list[str] = data.get("supported_locales", [])
        self.blocked_locales: list[str] = data.get("blocked_locales", [])


class ApplicationRoleConnectionMetadata(
    BaseModel["ApplicationRoleConnectionMetadataResponse"]
):
    __slots__ = (
        "description",
        "description_localizations",
        "key",
        "name",
        "name_localizations",
        "type",
    )
    """Metadata schema entry for application role connections.

    Each entry defines one metadata field that can be attached to a user's
    application role connection, including localized names and descriptions.

    Attributes
    ----------
    type: :class:`int`
        The metadata value type as defined by Discord.
    key: :class:`str`
        The metadata field key.
    name: :class:`str`
        The default display name.
    name_localizations: :class:`dict`
        Localized names keyed by locale.
    description: :class:`str`
        The default description.
    description_localizations: :class:`dict`
        Localized descriptions keyed by locale.
    """

    @override
    def _initialize(self, data: ApplicationRoleConnectionMetadataResponse) -> None:
        self.type: int = data["type"]
        self.key: str = data["key"]
        self.name: str = data["name"]
        self.name_localizations: dict[str, str] = data.get("name_localizations", {})
        self.description: str = data["description"]
        self.description_localizations: dict[str, str] = data.get(
            "description_localizations", {}
        )


class ApplicationRoleConnection(
    BaseModelWithSession["ApplicationRoleConnectionResponse"]
):
    """A user's application role connection payload.

    This model includes the connected platform identity metadata and may also
    include partial application details and metadata schema entries.

    Attributes
    ----------
    platform_name: :class:`str`
        The connected platform name, if provided.
    platform_username: :class:`str`
        The connected platform username, if provided.
    metadata: :class:`dict`
        Key-value metadata supplied for the connection.
    application: :class:`PartialApplication`
        The associated application payload, if provided.
    application_metadata: :class:`list` of :class:`ApplicationRoleConnectionMetadata`
        The metadata schema entries, if provided.
    """

    __slots__ = (
        "application",
        "application_metadata",
        "metadata",
        "platform_name",
        "platform_username",
    )

    @override
    def _initialize(self, data: ApplicationRoleConnectionResponse) -> None:
        self.platform_name: str | None = data.get("platform_name")
        self.platform_username: str | None = data.get("platform_username")
        self.metadata: dict[str, str] = data["metadata"]
        self.application: PartialApplication = self._initialize_other(
            PartialApplication,
            data,
            possible_keys="application",
        )

        self.application_metadata: list[ApplicationRoleConnectionMetadata] = [
            self._initialize_other(ApplicationRoleConnectionMetadata, metadata)
            for metadata in data.get("application_metadata", [])
        ]


class ActivityLink(BaseModel["ActivityLinkResponse"]):
    """Rich link metadata for an activity deep link.

    This model represents activity link content, including link type, display
    text, and optional media assets used by Discord clients.

    Attributes
    ----------
    application_id: :class:`int`
        The parent application snowflake.
    link_id: :class:`str`
        The activity link identifier.
    type: :class:`ActivityLinkType`
        The link type derived from the identifier.
    asset_path: :class:`str`
        The asset path, if provided.
    asset_id: :class:`int`
        The asset snowflake, if provided.
    title: :class:`str`
        The link title text.
    description: :class:`str`
        The link description text.
    custom_id: :class:`str`
        The custom identifier, if provided.
    primary_cta: :class:`str`
        The primary call-to-action text, if provided.
    """

    __slots__ = (
        "application_id",
        "asset_id",
        "asset_path",
        "custom_id",
        "description",
        "link_id",
        "primary_cta",
        "title",
        "type",
    )

    @override
    def _initialize(self, data: ActivityLinkResponse) -> None:
        self.application_id: int = convert_snowflake(data, "application_id")
        self.link_id: str = data["link_id"]
        self.type: ActivityLinkType = ActivityLinkType(
            int(self.link_id.split("-", 1)[0])
        )
        self.asset_path: str | None = data.get("asset_path")
        self.asset_id: int | None = convert_snowflake(
            data, "asset_id", always_available=False
        )
        self.title: str = data["title"]
        self.description: str = data["description"]
        self.custom_id: str | None = data.get("custom_id")
        self.primary_cta: str | None = data.get("primary_cta")


class PartialApplicationIdentity(BaseModel["PartialApplicationIdentityResponse"]):
    """External identity mapping for an application user.

    This payload links a Discord user ID to an external user identifier within
    the context of an application integration.

    Attributes
    ----------
    user_id: :class:`int`
        The Discord user snowflake.
    external_user_id: :class:`str`
        The external user identifier.
    """

    __slots__ = ("external_user_id", "user_id")

    @override
    def _initialize(self, data: PartialApplicationIdentityResponse) -> None:
        self.user_id: int = convert_snowflake(data, "user_id")
        self.external_user_id: str = data["external_user_id"]


class PartialApplication(BaseModelWithSession["PartialApplicationResponse"]):
    """Partial Discord application metadata payload.

    This model aggregates core application identity, bot/install settings,
    store-related metadata, and embedded activity configuration when available.

    Attributes
    ----------
    id: :class:`int`
        The application snowflake identifier.
    name: :class:`str`
        The application name.
    description: :class:`str`
        The application description.
    icon: :class:`str`
        The icon hash, if present.
    cover_image: :class:`str`
        The cover image hash, if present.
    splash: :class:`str`
        The splash image hash, if present.
    type: :class:`ApplicationType`
        The application type, if provided.
    flags: :class:`int`
        Application flags bitset.
    primary_sku_id: :class:`int`
        The primary SKU snowflake, if present.
    verify_key: :class:`str`
        The application's public verify key.
    eula_id: :class:`int`
        The EULA snowflake, if present.
    slug: :class:`str`
        The store slug, if present.
    aliases: :class:`list` of :class:`str`
        Alternate application names.
    executables: :class:`list` of :class:`ApplicationExecutable`
        Executable entries for the application.
    third_party_skus: :class:`list` of :class:`ApplicationSKU`
        Linked third-party SKU entries.
    hook: :class:`bool`
        Whether this application is a game hook.
    overlay: :class:`bool`
        Whether the overlay is enabled, if provided.
    overlay_methods: :class:`int`
        Overlay method bitset, if provided.
    overlay_warn: :class:`bool`
        Whether to show overlay warnings, if provided.
    overlay_compatibility_hook: :class:`bool`
        Whether the overlay compatibility hook is enabled, if provided.
    bot: :class:`PartialUser`
        The bot user, if provided.
    developers: :class:`list` of :class:`Company`
        Developer company entries.
    publishers: :class:`list` of :class:`Company`
        Publisher company entries.
    rpc_origins: :class:`list` of :class:`str`
        Allowed RPC origin URLs.
    deeplink_uri: :class:`str`
        The deep link URI, if provided.
    integration_public: :class:`bool`
        Whether integrations are public, if provided.
    integration_require_code_grant: :class:`bool`
        Whether code grants are required for integrations, if provided.
    bot_public: :class:`bool`
        Whether the bot is public, if provided.
    bot_require_code_grant: :class:`bool`
        Whether the bot requires a code grant, if provided.
    terms_of_service_url: :class:`str`
        The terms of service URL, if provided.
    privacy_policy_url: :class:`str`
        The privacy policy URL, if provided.
    tags: :class:`list` of :class:`str`
        Discovery tags for the application.
    install_params: :class:`ApplicationInstallParams`
        OAuth2 install parameters, if provided.
    custom_install_url: :class:`str`
        Custom install URL, if provided.
    integration_types_config: :class:`dict`
        Integration type configuration entries.
    connection_entrypoint_url: :class:`str`
        Connection entrypoint URL, if provided.
    is_verified: :class:`bool`
        Whether the application is verified.
    is_discoverable: :class:`bool`
        Whether the application is discoverable.
    is_monetized: :class:`bool`
        Whether the application is monetized.
    storefront_available: :class:`bool`
        Whether the storefront is available.
    max_participants: :class:`int`
        The maximum participants for embedded activities, if provided.
    embedded_activity_config: :class:`EmbeddedActivityConfig`
        Embedded activity configuration, if provided.
    parent_id: :class:`int`
        The parent application snowflake, if provided.
    summary: :class:`str`
        The application summary, if provided.
    """

    __slots__ = (
        "aliases",
        "bot",
        "bot_public",
        "bot_require_code_grant",
        "connection_entrypoint_url",
        "cover_image",
        "custom_install_url",
        "deeplink_uri",
        "description",
        "developers",
        "embedded_activity_config",
        "eula_id",
        "executables",
        "flags",
        "hook",
        "icon",
        "id",
        "install_params",
        "integration_public",
        "integration_require_code_grant",
        "integration_types_config",
        "is_discoverable",
        "is_monetized",
        "is_verified",
        "max_participants",
        "name",
        "overlay",
        "overlay_compatibility_hook",
        "overlay_methods",
        "overlay_warn",
        "parent_id",
        "primary_sku_id",
        "privacy_policy_url",
        "publishers",
        "rpc_origins",
        "slug",
        "splash",
        "storefront_available",
        "summary",
        "tags",
        "terms_of_service_url",
        "third_party_skus",
        "type",
        "verify_key",
    )

    @override
    def _initialize(self, data: PartialApplicationResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.icon: str | None = data["icon"]
        self.cover_image: str | None = data.get("cover_image")
        self.splash: str | None = data.get("splash")
        self.type: ApplicationType | None = to_enum(ApplicationType, data["type"])
        self.flags: int = data["flags"]
        self.primary_sku_id: int | None = convert_snowflake(
            data, "primary_sku_id", always_available=False
        )
        self.verify_key: str = data["verify_key"]
        self.eula_id: int | None = convert_snowflake(
            data, "eula_id", always_available=False
        )
        self.slug: str | None = data.get("slug")
        self.aliases: list[str] = data.get("aliases", [])
        self.executables: list[ApplicationExecutable] = [
            self._initialize_other(ApplicationExecutable, executable)
            for executable in data.get("executables", [])
        ]
        self.third_party_skus: list[ApplicationSKU] = [
            self._initialize_other(ApplicationSKU, sku)
            for sku in data.get("third_party_skus", [])
        ]
        self.hook: bool = data["hook"]
        self.overlay: bool | None = data.get("overlay")
        self.overlay_methods: int | None = data.get("overlay_methods")
        self.overlay_warn: bool | None = data.get("overlay_warn")
        self.overlay_compatibility_hook: bool | None = data.get(
            "overlay_compatibility_hook"
        )
        self.bot: PartialUser | None = self._initialize_other(
            PartialUser, data, possible_keys="bot"
        )
        self.developers: list[Company] = [
            self._initialize_other(Company, company)
            for company in data.get("developers", [])
        ]
        self.publishers: list[Company] = [
            self._initialize_other(Company, company)
            for company in data.get("publishers", [])
        ]
        self.rpc_origins: list[str] = data.get("rpc_origins", [])
        self.deeplink_uri: str | None = data.get("deeplink_uri")
        self.integration_public: bool | None = data.get("integration_public")
        self.integration_require_code_grant: bool | None = data.get(
            "integration_require_code_grant"
        )
        self.bot_public: bool | None = data.get("bot_public")
        self.bot_require_code_grant: bool | None = data.get("bot_require_code_grant")
        self.terms_of_service_url: str | None = data.get("terms_of_service_url")
        self.privacy_policy_url: str | None = data.get("privacy_policy_url")
        self.tags: list[str] = data.get("tags", [])
        self.install_params: ApplicationInstallParams | None = self._initialize_other(
            ApplicationInstallParams,
            data,
            possible_keys="install_params",
            optional=True,
        )
        self.custom_install_url: str | None = data.get("custom_install_url")
        config: dict[
            IntegrationInstallType, ApplicationIntegrationTypeConfiguration | None
        ] = {}
        for raw_key, raw_value in data.get("integration_types_config", {}).items():
            try:
                key = to_enum(IntegrationInstallType, int(raw_key))
            except TypeError, ValueError:
                continue

            if raw_value is None:
                config[key] = None
                continue

            config[key] = self._initialize_other(
                ApplicationIntegrationTypeConfiguration, raw_value
            )

        self.integration_types_config = config
        self.connection_entrypoint_url: str | None = data.get(
            "connection_entrypoint_url"
        )
        self.is_verified: bool = data["is_verified"]
        self.is_discoverable: bool = data["is_discoverable"]
        self.is_monetized: bool = data["is_monetized"]
        self.storefront_available: bool = data["storefront_available"]
        self.max_participants: int | None = data.get("max_participants")
        self.embedded_activity_config: EmbeddedActivityConfig | None = (
            self._initialize_other(
                EmbeddedActivityConfig,
                data,
                possible_keys="embedded_activity_config",
                optional=True,
            )
        )
        self.parent_id: int | None = convert_snowflake(
            data, "parent_id", always_available=False
        )
        self.summary: str | None = data.get("summary")

    async def create_attachment(self, file: File) -> Attachment:
        return await self._session.create_application_attachment(
            application_id=self.id, file=file
        )

    async def get_user_role_connection(
        self,
    ) -> ApplicationRoleConnection:
        return await self._session.user_application_role_connection(
            application_id=self.id
        )

    async def edit_user_role_connection(
        self,
        *,
        platform_name: str | None = None,
        platform_username: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> ApplicationRoleConnection:
        return await self._session.edit_user_application_role_connection(
            application_id=self.id,
            platform_name=platform_name,
            platform_username=platform_username,
            metadata=metadata,
        )

    async def create_quick_link(
        self,
        *,
        description: str,
        image: File,
        title: str,
        custom_id: str | None = None,
    ) -> ActivityLink:
        return await self._session.create_application_quick_link(
            application_id=self.id,
            description=description,
            image=image,
            title=title,
            custom_id=custom_id,
        )
