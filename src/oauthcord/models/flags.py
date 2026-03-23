from collections.abc import Iterator
from typing import (
    TYPE_CHECKING,
    Any,
    TypedDict,
    Unpack,
)

if TYPE_CHECKING:

    class _UserFlagsKwargs(TypedDict, total=False):
        staff: bool
        partner: bool
        hypesquad: bool
        bug_hunter_level_1: bool
        hypesquad_online_house_1: bool
        hypesquad_online_house_2: bool
        hypesquad_online_house_3: bool
        premium_early_supporter: bool
        team_pseudo_user: bool
        bug_hunter_level_2: bool
        verified_bot: bool
        early_verified_developer: bool
        certified_moderator: bool
        bot_http_interactions: bool
        active_developer: bool

    class _PermissionsKwargs(TypedDict, total=False):
        create_instant_invite: bool
        kick_members: bool
        ban_members: bool
        administrator: bool
        manage_channels: bool
        manage_guild: bool
        add_reactions: bool
        view_audit_log: bool
        priority_speaker: bool
        stream: bool
        view_channel: bool
        send_messages: bool
        send_tts_messages: bool
        manage_messages: bool
        embed_links: bool
        attach_files: bool
        read_message_history: bool
        mention_everyone: bool
        use_external_emojis: bool
        view_guild_insights: bool
        connect: bool
        speak: bool
        mute_members: bool
        deafen_members: bool
        move_members: bool
        use_vad: bool
        change_nickname: bool
        manage_nicknames: bool
        manage_roles: bool
        manage_webhooks: bool
        manage_guild_expressions: bool
        use_application_commands: bool
        request_to_speak: bool
        manage_events: bool
        manage_threads: bool
        create_public_threads: bool
        create_private_threads: bool
        use_external_stickers: bool
        send_messages_in_threads: bool
        use_embedded_activities: bool
        moderate_members: bool
        view_creator_monetization_analytics: bool
        use_soundboard: bool
        create_guild_expressions: bool
        create_events: bool
        use_external_sounds: bool
        send_voice_messages: bool
        send_polls: bool
        use_external_apps: bool
        pin_messages: bool
        bypass_slowmode: bool

    class _MemberFlagsKwargs(TypedDict, total=False):
        did_rejoin: bool
        completed_onboarding: bool
        bypasses_verification: bool
        started_onboarding: bool
        is_guest: bool
        started_home_actions: bool
        completed_home_actions: bool
        automod_quarantined_username: bool
        dm_settings_upsell_acknowledged: bool
        automod_quarantined_guild_tag: bool

    class _ChannelFlagsKwargs(TypedDict, total=False):
        guild_feed_removed: bool
        pinned: bool
        active_channels_removed: bool
        require_tag: bool
        is_spam: bool
        is_guild_resource_channel: bool
        clyde_ai: bool
        is_scheduled_for_deletion: bool
        is_media_channel: bool
        summaries_disabled: bool
        application_shelf_consent: bool
        is_role_subscription_template_preview_channel: bool
        is_broadcasting: bool
        hide_media_download_options: bool
        is_join_request_interview_channel: bool
        obfuscated: bool
        is_moderator_report_channel: bool

    class _RecipientFlagsKwargs(TypedDict, total=False):
        dismissed_in_game_message_nux: bool

    class _MessageFlagsKwargs(TypedDict, total=False):
        crossposted: bool
        is_crosspost: bool
        suppress_embeds: bool
        source_message_deleted: bool
        urgent: bool
        has_thread: bool
        ephemeral: bool
        loading: bool
        failed_to_mention_some_roles_in_thread: bool
        guild_feed_hidden: bool
        should_show_link_not_discord_warning: bool
        suppress_notifications: bool
        is_voice_message: bool
        has_snapshot: bool
        is_components_v2: bool
        sent_by_social_layer_integration: bool

    class _EmbedFlagsKwargs(TypedDict, total=False):
        contains_explicit_media: bool
        content_inventory_entry: bool
        contains_gore_content: bool
        contains_self_harm_content: bool

    class _AttachmentFlagsKwargs(TypedDict, total=False):
        is_clip: bool
        is_thumbnail: bool
        is_remix: bool
        is_spoiler: bool
        contains_explicit_media: bool
        is_animated: bool
        contains_gore_content: bool
        contains_self_harm_content: bool

    class _ApplicationFlagsKwargs(TypedDict, total=False):
        embedded_released: bool
        auto_moderation_rule_create_badge: bool
        game_profile_disabled: bool
        contextless_activity: bool
        social_layer_integration_limited: bool
        gateway_presence: bool
        gateway_presence_limited: bool
        gateway_guild_members: bool
        gateway_guild_members_limited: bool
        verification_pending_guild_limit: bool
        embedded: bool
        gateway_message_content: bool
        gateway_message_content_limited: bool
        embedded_first_party: bool
        application_command_migrated: bool
        application_command_badge: bool
        iframe_modal: bool
        social_layer_integration: bool
        promoted: bool
        partner: bool
        parent: bool
        disable_relationship_access: bool

    class _SKUFlagsKwargs(TypedDict, total=False):
        premium_purchase: bool
        has_free_premium_content: bool
        available: bool
        premium_and_distribution: bool
        sticker: bool
        guild_role: bool
        available_for_subscription_gifting: bool
        application_guild_subscription: bool
        application_user_subscription: bool
        creator_monetization: bool
        guild_product: bool
        available_for_application_gifting: bool

    class _LobbyFlagsKwargs(TypedDict, total=False):
        require_application_authorization: bool

    class _LobbyMemberFlagsKwargs(TypedDict, total=False):
        can_link_lobby: bool


__all__ = (
    "ApplicationFlags",
    "AttachmentFlags",
    "BaseFlags",
    "ChannelFlags",
    "EmbedFlags",
    "Flag",
    "FlagsMeta",
    "LobbyFlags",
    "LobbyMemberFlags",
    "MemberFlags",
    "MessageFlags",
    "Permissions",
    "RecipientFlags",
    "SKUFlags",
    "UserFlags",
)


class Flag:
    __slots__ = ("name", "value")

    def __init__(self, value: int) -> None:
        self.name: str = ""
        self.value: int = value

    def __set_name__(self, _owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: BaseFlags | None, _owner: type) -> Flag | bool:
        if obj is None:
            return self
        return bool(obj.value & self.value)

    def __set__(self, obj: BaseFlags, value: bool) -> None:
        if value:
            obj.value |= self.value
        else:
            obj.value &= ~self.value

    def __repr__(self) -> str:
        return f"<Flag {self.name}={self.value}>"

    def __str__(self) -> str:
        return self.name


class FlagsMeta(type):
    _flags: dict[str, Flag]

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> FlagsMeta:
        flags: dict[str, Flag] = {}

        for base in bases:
            if hasattr(base, "_flags"):
                flags.update(base._flags)  # type: ignore

        flags.update(
            {
                attr_name: attr_value
                for attr_name, attr_value in namespace.items()
                if isinstance(attr_value, Flag)
            }
        )

        instance = super().__new__(cls, name, bases, namespace)
        instance._flags = flags
        return instance


class BaseFlags(metaclass=FlagsMeta):
    def __init__(self, value: int | None = None, /, **flags: bool) -> None:
        self.value: int = value if value is not None else 0
        for flag_name, flag_value in flags.items():
            if flag_value:
                flag = self._flags.get(flag_name)
                if flag is not None:
                    self.value |= flag.value
                else:
                    raise ValueError(f"Unknown flag: {flag_name}")

    @staticmethod
    def _resolve_value(other: int | Flag | BaseFlags) -> int:
        if isinstance(other, int):
            return other
        if isinstance(other, Flag):
            return other.value
        if isinstance(other, BaseFlags):
            return other.value

        other_type = type(other).__name__
        raise TypeError(
            f"unsupported operand type(s) for flags operation: {other_type!r}"
        )

    def __iter__(self) -> Iterator[Flag]:
        for flag in self._flags.values():
            if self.value & flag.value:
                yield flag

    def __contains__(self, flag: Flag) -> bool:
        return bool(self.value & flag.value)

    def __ior__(self, other: int | Flag | BaseFlags) -> BaseFlags:
        self.value |= self._resolve_value(other)
        return self

    def __imod__(self, other: int | Flag | BaseFlags) -> BaseFlags:
        self.value &= ~self._resolve_value(other)
        return self

    def __repr__(self) -> str:
        set_flags = ", ".join(f.name for f in self)
        return f"<{self.__class__.__name__} value={self.value} [{set_flags}]>"

    def all(self) -> list[Flag]:
        return list(self)


class UserFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_UserFlagsKwargs]
        ) -> None: ...

    staff = Flag(1 << 0)
    partner = Flag(1 << 1)
    hypesquad = Flag(1 << 2)
    bug_hunter_level_1 = Flag(1 << 3)
    hypesquad_online_house_1 = Flag(1 << 6)
    hypesquad_online_house_2 = Flag(1 << 7)
    hypesquad_online_house_3 = Flag(1 << 8)
    premium_early_supporter = Flag(1 << 9)
    team_pseudo_user = Flag(1 << 10)
    bug_hunter_level_2 = Flag(1 << 14)
    verified_bot = Flag(1 << 16)
    early_verified_developer = Flag(1 << 17)
    certified_moderator = Flag(1 << 18)
    bot_http_interactions = Flag(1 << 19)
    active_developer = Flag(1 << 22)


class Permissions(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_PermissionsKwargs]
        ) -> None: ...

    create_instant_invite = Flag(1 << 0)
    kick_members = Flag(1 << 1)
    ban_members = Flag(1 << 2)
    administrator = Flag(1 << 3)
    manage_channels = Flag(1 << 4)
    manage_guild = Flag(1 << 5)
    add_reactions = Flag(1 << 6)
    view_audit_log = Flag(1 << 7)
    priority_speaker = Flag(1 << 8)
    stream = Flag(1 << 9)
    view_channel = Flag(1 << 10)
    send_messages = Flag(1 << 11)
    send_tts_messages = Flag(1 << 12)
    manage_messages = Flag(1 << 13)
    embed_links = Flag(1 << 14)
    attach_files = Flag(1 << 15)
    read_message_history = Flag(1 << 16)
    mention_everyone = Flag(1 << 17)
    use_external_emojis = Flag(1 << 18)
    view_guild_insights = Flag(1 << 19)
    connect = Flag(1 << 20)
    speak = Flag(1 << 21)
    mute_members = Flag(1 << 22)
    deafen_members = Flag(1 << 23)
    move_members = Flag(1 << 24)
    use_vad = Flag(1 << 25)
    change_nickname = Flag(1 << 26)
    manage_nicknames = Flag(1 << 27)
    manage_roles = Flag(1 << 28)
    manage_webhooks = Flag(1 << 29)
    manage_guild_expressions = Flag(1 << 30)
    use_application_commands = Flag(1 << 31)
    request_to_speak = Flag(1 << 32)
    manage_events = Flag(1 << 33)
    manage_threads = Flag(1 << 34)
    create_public_threads = Flag(1 << 35)
    create_private_threads = Flag(1 << 36)
    use_external_stickers = Flag(1 << 37)
    send_messages_in_threads = Flag(1 << 38)
    use_embedded_activities = Flag(1 << 39)
    moderate_members = Flag(1 << 40)
    view_creator_monetization_analytics = Flag(1 << 41)
    use_soundboard = Flag(1 << 42)
    create_guild_expressions = Flag(1 << 43)
    create_events = Flag(1 << 44)
    use_external_sounds = Flag(1 << 45)
    send_voice_messages = Flag(1 << 46)
    send_polls = Flag(1 << 49)
    use_external_apps = Flag(1 << 50)
    pin_messages = Flag(1 << 51)
    bypass_slowmode = Flag(1 << 52)


class MemberFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_MemberFlagsKwargs]
        ) -> None: ...

    did_rejoin = Flag(1 << 0)
    completed_onboarding = Flag(1 << 1)
    bypasses_verification = Flag(1 << 2)
    started_onboarding = Flag(1 << 3)
    is_guest = Flag(1 << 4)
    started_home_actions = Flag(1 << 5)
    completed_home_actions = Flag(1 << 6)
    automod_quarantined_username = Flag(1 << 7)
    dm_settings_upsell_acknowledged = Flag(1 << 9)
    automod_quarantined_guild_tag = Flag(1 << 10)


class ChannelFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_ChannelFlagsKwargs]
        ) -> None: ...

    guild_feed_removed = Flag(1 << 0)
    pinned = Flag(1 << 1)
    active_channels_removed = Flag(1 << 2)
    require_tag = Flag(1 << 4)
    is_spam = Flag(1 << 5)
    is_guild_resource_channel = Flag(1 << 7)
    clyde_ai = Flag(1 << 8)
    is_scheduled_for_deletion = Flag(1 << 9)
    is_media_channel = Flag(1 << 10)
    summaries_disabled = Flag(1 << 11)
    application_shelf_consent = Flag(1 << 12)
    is_role_subscription_template_preview_channel = Flag(1 << 13)
    is_broadcasting = Flag(1 << 14)
    hide_media_download_options = Flag(1 << 15)
    is_join_request_interview_channel = Flag(1 << 16)
    obfuscated = Flag(1 << 17)
    is_moderator_report_channel = Flag(1 << 19)


class RecipientFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_RecipientFlagsKwargs]
        ) -> None: ...

    dismissed_in_game_message_nux = Flag(1 << 0)


class MessageFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_MessageFlagsKwargs]
        ) -> None: ...

    crossposted = Flag(1 << 0)
    is_crosspost = Flag(1 << 1)
    suppress_embeds = Flag(1 << 2)
    source_message_deleted = Flag(1 << 3)
    urgent = Flag(1 << 4)
    has_thread = Flag(1 << 5)
    ephemeral = Flag(1 << 6)
    loading = Flag(1 << 7)
    failed_to_mention_some_roles_in_thread = Flag(1 << 8)
    guild_feed_hidden = Flag(1 << 9)
    should_show_link_not_discord_warning = Flag(1 << 10)
    suppress_notifications = Flag(1 << 12)
    is_voice_message = Flag(1 << 13)
    has_snapshot = Flag(1 << 14)
    is_components_v2 = Flag(1 << 15)
    sent_by_social_layer_integration = Flag(1 << 16)


class EmbedFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_EmbedFlagsKwargs]
        ) -> None: ...

    contains_explicit_media = Flag(1 << 4)
    content_inventory_entry = Flag(1 << 5)
    contains_gore_content = Flag(1 << 6)
    contains_self_harm_content = Flag(1 << 7)


class AttachmentFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_AttachmentFlagsKwargs]
        ) -> None: ...

    is_clip = Flag(1 << 0)
    is_thumbnail = Flag(1 << 1)
    is_remix = Flag(1 << 2)
    is_spoiler = Flag(1 << 3)
    contains_explicit_media = Flag(1 << 4)
    is_animated = Flag(1 << 5)
    contains_gore_content = Flag(1 << 6)
    contains_self_harm_content = Flag(1 << 7)


class ApplicationFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_ApplicationFlagsKwargs]
        ) -> None: ...

    embedded_released = Flag(1 << 1)
    auto_moderation_rule_create_badge = Flag(1 << 6)
    game_profile_disabled = Flag(1 << 7)
    contextless_activity = Flag(1 << 9)
    social_layer_integration_limited = Flag(1 << 10)
    gateway_presence = Flag(1 << 12)
    gateway_presence_limited = Flag(1 << 13)
    gateway_guild_members = Flag(1 << 14)
    gateway_guild_members_limited = Flag(1 << 15)
    verification_pending_guild_limit = Flag(1 << 16)
    embedded = Flag(1 << 17)
    gateway_message_content = Flag(1 << 18)
    gateway_message_content_limited = Flag(1 << 19)
    embedded_first_party = Flag(1 << 20)
    application_command_migrated = Flag(1 << 21)
    application_command_badge = Flag(1 << 23)
    iframe_modal = Flag(1 << 26)
    social_layer_integration = Flag(1 << 27)
    promoted = Flag(1 << 29)
    partner = Flag(1 << 30)
    parent = Flag(1 << 33)
    disable_relationship_access = Flag(1 << 34)


class SKUFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_SKUFlagsKwargs]
        ) -> None: ...

    premium_purchase = Flag(1 << 0)
    has_free_premium_content = Flag(1 << 1)
    available = Flag(1 << 2)
    premium_and_distribution = Flag(1 << 3)
    sticker = Flag(1 << 4)
    guild_role = Flag(1 << 5)
    available_for_subscription_gifting = Flag(1 << 6)
    application_guild_subscription = Flag(1 << 7)
    application_user_subscription = Flag(1 << 8)
    creator_monetization = Flag(1 << 9)
    guild_product = Flag(1 << 10)
    available_for_application_gifting = Flag(1 << 11)


class LobbyFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_LobbyFlagsKwargs]
        ) -> None: ...

    require_application_authorization = Flag(1 << 0)


class LobbyMemberFlags(BaseFlags):
    if TYPE_CHECKING:

        def __init__(
            self, value: int | None = None, /, **flags: Unpack[_LobbyMemberFlagsKwargs]
        ) -> None: ...

    can_link_lobby = Flag(1 << 0)
