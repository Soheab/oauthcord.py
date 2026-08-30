from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Iterable, TypeVar

if TYPE_CHECKING:
    from ..internals._types.rpc import events
    from ..models.entitlement import Entitlement
    from .client import RPCClient
    from .events import Event
    from .models.channels import RPCPartialChannel
    from .models.events import (
        ActivityInstanceParticipantsUpdate,
        ActivityInvite,
        ActivityJoin,
        ActivityJoinRequest,
        ActivityLayoutModeUpdate,
        ActivityPipModeUpdate,
        ActivitySpectate,
        GuildStatus,
        MessageDelete,
        MessageEvent,
        OrientationUpdate,
        OverlayUpdate,
        QuestEnrollmentStatusUpdate,
        ReadyEvent,
        RPCErrorEvent,
        ScreenshareStateUpdate,
        SpeakingStartData,
        SpeakingStopData,
        ThermalStateUpdate,
        VideoStateUpdate,
        VoiceChannelSelect,
        VoiceConnectionStatus,
        VoiceSettingsUpdate2,
    )
    from .models.guild import RPCGuild
    from .models.member import RPCGuildMember
    from .models.relationship import RPCRelationship
    from .models.user import RPCUser
    from .models.voice import RPCVoiceState, VoiceSettings


_HandlerMethodT = TypeVar("_HandlerMethodT", bound="Callable[..., Any]")

# Event names that don't fall out of a plain uppercase of the method name.
_METHOD_NAME_OVERRIDES: dict[str, str] = {
    "on_voice_settings_update2": "VOICE_SETTINGS_UPDATE_2",
}


def _method_name_to_event(method_name: str, /) -> str:
    """Derive the RPC event name from an ``on_*`` method name."""
    if (override := _METHOD_NAME_OVERRIDES.get(method_name)) is not None:
        return override

    return method_name[3:].upper()


def _merge_ids(
    single: int | None, multiple: Iterable[int] | None, /
) -> tuple[int, ...]:
    """Combine the singular and plural id arguments into one de-duplicated tuple."""
    ids: list[int] = []
    if single is not None:
        ids.append(single)
    if multiple is not None:
        ids.extend(multiple)

    # dict.fromkeys keeps the given order while dropping repeats.
    return tuple(dict.fromkeys(ids))


class _ListenerInfo:
    """Subscription details attached to a method by :func:`listens_to`."""

    __slots__ = ("channel_ids", "event_name", "extra_args", "guild_ids")

    def __init__(
        self,
        event_name: str,
        /,
        *,
        guild_ids: tuple[int, ...] = (),
        channel_ids: tuple[int, ...] = (),
        extra_args: dict[str, Any] | None = None,
    ) -> None:
        self.event_name: str = event_name
        self.guild_ids: tuple[int, ...] = guild_ids
        self.channel_ids: tuple[int, ...] = channel_ids
        self.extra_args: dict[str, Any] = extra_args or {}

    def scopes(self) -> list[tuple[int | None, int | None]]:
        """The ``(guild_id, channel_id)`` pairs this listener subscribes with.

        One subscription is made per id, so a listener given three guild ids is
        subscribed three times. With no ids at all this is a single unscoped
        ``(None, None)`` pair.
        """
        if not self.guild_ids and not self.channel_ids:
            return [(None, None)]

        pairs: list[tuple[int | None, int | None]] = []
        pairs.extend((guild_id, None) for guild_id in self.guild_ids)
        pairs.extend((None, channel_id) for channel_id in self.channel_ids)
        return pairs

    def __repr__(self) -> str:
        return (
            f"_ListenerInfo(event_name={self.event_name!r}, "
            f"guild_ids={self.guild_ids!r}, channel_ids={self.channel_ids!r})"
        )


def listens_to(
    event_name: str | None = None,
    /,
    *,
    guild_id: int | None = None,
    guild_ids: Iterable[int] | None = None,
    channel_id: int | None = None,
    channel_ids: Iterable[int] | None = None,
    **extra_args: Any,
) -> Callable[[_HandlerMethodT], _HandlerMethodT]:
    """Mark an :class:`EventsHandler` method as an event listener.

    Applying this to a method makes the override explicit, and lets you supply the
    ``guild_id``/``channel_id`` that some events need in their subscription. Those
    events are auto-subscribed with the ids you give here instead of being skipped.

    The decorator is optional: overriding an ``on_*`` method still works on its
    own. It is required only to pass subscription arguments, or to listen to an
    event from a method whose name is not the matching ``on_*``.

    Parameters
    ----------
    event_name: :class:`str` | :data:`None`
        The event to listen to, e.g. ``"GUILD_STATUS"``. Defaults to :data:`None`,
        deriving the event from the method name (``on_guild_status`` →
        ``GUILD_STATUS``). Required when the method is not named ``on_*``.
    guild_id: :class:`int` | :data:`None`
        A single guild to scope the subscription to, for events that need one.
    guild_ids: :class:`~typing.Iterable` of :class:`int` | :data:`None`
        Several guilds to scope the subscription to — one ``SUBSCRIBE`` is sent
        per id. May be combined with ``guild_id``; the ids are merged.
    channel_id: :class:`int` | :data:`None`
        A single channel to scope the subscription to, for events that need one.
    channel_ids: :class:`~typing.Iterable` of :class:`int` | :data:`None`
        Several channels to scope the subscription to — one ``SUBSCRIBE`` is sent
        per id. May be combined with ``channel_id``; the ids are merged.
    **extra_args: :data:`~typing.Any`
        Any further arguments to pass along in the ``SUBSCRIBE`` payload.

    Examples
    --------
    ::

        class MyHandler(EventsHandler):
            @listens_to(guild_id=1234)
            async def on_guild_status(self, event) -> None:
                ...

            @listens_to("MESSAGE_CREATE", channel_id=5678)
            async def log_messages(self, event) -> None:
                ...

            @listens_to(guild_ids=[1234, 5678, 9012])
            async def on_guild_status(self, event) -> None:
                ...
    """

    def decorator(func: _HandlerMethodT, /) -> _HandlerMethodT:
        name = event_name
        if name is None:
            if not func.__name__.startswith("on_"):
                raise TypeError(
                    f"{func.__name__!r} is not named 'on_*', so listens_to() needs "
                    "an explicit event name."
                )
            name = _method_name_to_event(func.__name__)

        func.__rpc_event__ = _ListenerInfo(  # pyright: ignore[reportFunctionMemberAccess]
            name,
            guild_ids=_merge_ids(guild_id, guild_ids),
            channel_ids=_merge_ids(channel_id, channel_ids),
            extra_args=extra_args,
        )
        return func

    return decorator


class EventsHandler:
    """Base class for handling RPC events by subclassing.

    Override any ``on_*`` method to handle the matching event, then pass the
    subclass (or an instance of it) to :class:`RPCClient` as ``handler``. Every
    method here is an inherited no-op, so you only implement the events you care
    about — methods you do not override are never registered or subscribed to.

    Each method receives a single :class:`~oauthcord.rpc.events.Event`, whose
    ``data`` attribute is the parsed model for that event.

    This is an alternative to registering callbacks individually with
    ``@rpc.events.event(...)``; both may be used together.

    Parameters
    ----------
    rpc_client: :class:`RPCClient`
        The client this handler is bound to. Supplied automatically when a class
        is passed to :class:`RPCClient`.

    Attributes
    ----------
    client: :class:`RPCClient`
        The client this handler is bound to.

    Examples
    --------
    ::

        from oauthcord.rpc import EventsHandler, RPCClient

        class MyHandler(EventsHandler):
            async def on_ready(self, event) -> None:
                print("ready:", event.data.user)

            async def on_guild_create(self, event) -> None:
                # `self.client` is the RPCClient this handler is bound to.
                await self.client.set_activity(None)

        rpc = RPCClient(client, handler=MyHandler)

    Notes
    -----
    ``READY``, ``ERROR``, and ``AUTHORIZE_REQUEST`` are sent unprompted by
    Discord and are never subscribed to. Events whose subscription needs a
    ``guild_id`` or ``channel_id`` (such as :meth:`on_guild_status` or
    :meth:`on_message_create`) are registered but not auto-subscribed; call
    :meth:`RPCEventsManager.subscribe` with the relevant id to receive them.
    """

    def __init__(self, rpc_client: RPCClient) -> None:
        self.client: RPCClient = rpc_client

    async def on_ready(self, event: Event[ReadyEvent]) -> None:
        """Called when the ``READY`` event is received.

        Sent unprompted by Discord; no subscription is needed.
        """

    async def on_error(self, event: Event[RPCErrorEvent]) -> None:
        """Called when the ``ERROR`` event is received.

        Sent unprompted by Discord; no subscription is needed.
        """

    async def on_current_user_update(self, event: Event[RPCUser]) -> None:
        """Called when the ``CURRENT_USER_UPDATE`` event is received."""

    async def on_current_guild_member_update(
        self, event: Event[RPCGuildMember]
    ) -> None:
        """Called when the ``CURRENT_GUILD_MEMBER_UPDATE`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_guild_status(self, event: Event[GuildStatus]) -> None:
        """Called when the ``GUILD_STATUS`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_guild_create(self, event: Event[RPCGuild]) -> None:
        """Called when the ``GUILD_CREATE`` event is received."""

    async def on_channel_create(self, event: Event[RPCPartialChannel]) -> None:
        """Called when the ``CHANNEL_CREATE`` event is received."""

    async def on_relationship_update(self, event: Event[RPCRelationship]) -> None:
        """Called when the ``RELATIONSHIP_UPDATE`` event is received."""

    async def on_voice_channel_select(self, event: Event[VoiceChannelSelect]) -> None:
        """Called when the ``VOICE_CHANNEL_SELECT`` event is received."""

    async def on_voice_state_create(self, event: Event[RPCVoiceState]) -> None:
        """Called when the ``VOICE_STATE_CREATE`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_voice_state_delete(self, event: Event[RPCVoiceState]) -> None:
        """Called when the ``VOICE_STATE_DELETE`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_voice_state_update(self, event: Event[RPCVoiceState]) -> None:
        """Called when the ``VOICE_STATE_UPDATE`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_voice_settings_update(self, event: Event[VoiceSettings]) -> None:
        """Called when the ``VOICE_SETTINGS_UPDATE`` event is received."""

    async def on_voice_settings_update2(
        self, event: Event[VoiceSettingsUpdate2]
    ) -> None:
        """Called when the ``VOICE_SETTINGS_UPDATE_2`` event is received."""

    async def on_voice_connection_status(
        self, event: Event[VoiceConnectionStatus]
    ) -> None:
        """Called when the ``VOICE_CONNECTION_STATUS`` event is received."""

    async def on_speaking_start(self, event: Event[SpeakingStartData]) -> None:
        """Called when the ``SPEAKING_START`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_speaking_stop(self, event: Event[SpeakingStopData]) -> None:
        """Called when the ``SPEAKING_STOP`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_activity_join(self, event: Event[ActivityJoin]) -> None:
        """Called when the ``ACTIVITY_JOIN`` event is received."""

    async def on_activity_join_request(self, event: Event[ActivityJoinRequest]) -> None:
        """Called when the ``ACTIVITY_JOIN_REQUEST`` event is received."""

    async def on_activity_spectate(self, event: Event[ActivitySpectate]) -> None:
        """Called when the ``ACTIVITY_SPECTATE`` event is received."""

    async def on_activity_invite(self, event: Event[ActivityInvite]) -> None:
        """Called when the ``ACTIVITY_INVITE`` event is received."""

    async def on_activity_pip_mode_update(
        self, event: Event[ActivityPipModeUpdate]
    ) -> None:
        """Called when the ``ACTIVITY_PIP_MODE_UPDATE`` event is received."""

    async def on_activity_layout_mode_update(
        self, event: Event[ActivityLayoutModeUpdate]
    ) -> None:
        """Called when the ``ACTIVITY_LAYOUT_MODE_UPDATE`` event is received."""

    async def on_thermal_state_update(self, event: Event[ThermalStateUpdate]) -> None:
        """Called when the ``THERMAL_STATE_UPDATE`` event is received."""

    async def on_orientation_update(self, event: Event[OrientationUpdate]) -> None:
        """Called when the ``ORIENTATION_UPDATE`` event is received."""

    async def on_activity_instance_participants_update(
        self, event: Event[ActivityInstanceParticipantsUpdate]
    ) -> None:
        """Called when the ``ACTIVITY_INSTANCE_PARTICIPANTS_UPDATE`` event is received."""

    async def on_notification_create(self, event: Event[MessageEvent]) -> None:
        """Called when the ``NOTIFICATION_CREATE`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_message_create(self, event: Event[MessageEvent]) -> None:
        """Called when the ``MESSAGE_CREATE`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_message_update(self, event: Event[MessageEvent]) -> None:
        """Called when the ``MESSAGE_UPDATE`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_message_delete(self, event: Event[MessageDelete]) -> None:
        """Called when the ``MESSAGE_DELETE`` event is received.

        Requires a subscription with a ``guild_id``/``channel_id``, so it
        is not auto-subscribed; call :meth:`RPCEventsManager.subscribe`.
        """

    async def on_overlay_update(self, event: Event[OverlayUpdate]) -> None:
        """Called when the ``OVERLAY_UPDATE`` event is received."""

    async def on_entitlement_create(self, event: Event[Entitlement]) -> None:
        """Called when the ``ENTITLEMENT_CREATE`` event is received."""

    async def on_entitlement_delete(self, event: Event[Entitlement]) -> None:
        """Called when the ``ENTITLEMENT_DELETE`` event is received."""

    async def on_screenshare_state_update(
        self, event: Event[ScreenshareStateUpdate]
    ) -> None:
        """Called when the ``SCREENSHARE_STATE_UPDATE`` event is received."""

    async def on_video_state_update(self, event: Event[VideoStateUpdate]) -> None:
        """Called when the ``VIDEO_STATE_UPDATE`` event is received."""

    async def on_authorize_request(
        self, event: Event[events.AuthorizeRequestEventData]
    ) -> None:
        """Called when the ``AUTHORIZE_REQUEST`` event is received.

        Sent unprompted by Discord; no subscription is needed.
        """

    async def on_quest_enrollment_status_update(
        self, event: Event[QuestEnrollmentStatusUpdate]
    ) -> None:
        """Called when the ``QUEST_ENROLLMENT_STATUS_UPDATE`` event is received."""
