from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Coroutine, Iterator

from ..models.entitlement import Entitlement
from .enums import InternalRPCCommand
from .errors import RPCError, RPCSubscriptionError
from .handler import EventsHandler, _ListenerInfo
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

if TYPE_CHECKING:
    from ..internals._types.rpc import events as event_types
    from ..internals._types.rpc.events import AuthorizeRequestEventData
    from .client._client import RPCClient
    from .enums import ReceivedRPCEvent, SubscribeableRPCEvent


__all__ = ("Event",)

_log = logging.getLogger("oauthcord.rpc.events")

# Discord's error code for a command needing an authenticated connection.
_NOT_AUTHENTICATED_CODE = 4006

type EventName = str | SubscribeableRPCEvent | ReceivedRPCEvent

# The parsed model types Event.data can hold, one per dispatchable RPC event -
# what callbacks actually receive, as opposed to RPCDispatchEventData's raw
# wire payloads.
type RPCDispatchEventModel = (
    ReadyEvent
    | RPCErrorEvent
    | RPCUser
    | RPCGuildMember
    | GuildStatus
    | RPCGuild
    | RPCPartialChannel
    | RPCRelationship
    | VoiceChannelSelect
    | RPCVoiceState
    | VoiceSettings
    | VoiceSettingsUpdate2
    | VoiceConnectionStatus
    | SpeakingStartData
    | SpeakingStopData
    | ActivityJoin
    | ActivityJoinRequest
    | ActivitySpectate
    | ActivityInvite
    | ActivityPipModeUpdate
    | ActivityLayoutModeUpdate
    | ThermalStateUpdate
    | OrientationUpdate
    | ActivityInstanceParticipantsUpdate
    | MessageEvent
    | MessageDelete
    | OverlayUpdate
    | Entitlement
    | ScreenshareStateUpdate
    | VideoStateUpdate
    | AuthorizeRequestEventData
    | QuestEnrollmentStatusUpdate
)


def _iter_handler_methods(cls: type, /) -> Iterator[tuple[str, Any]]:
    """Yield ``(name, function)`` for every method defined on ``cls`` or its bases."""
    seen: set[str] = set()
    for klass in cls.__mro__:
        for name, value in vars(klass).items():
            if name in seen or not callable(value):
                continue
            seen.add(name)
            yield name, value


class _PendingSubscription:
    """An event registered from a handler that still needs a ``SUBSCRIBE`` sent."""

    __slots__ = ("channel_id", "event_name", "extra_args", "guild_id")

    def __init__(
        self,
        event_name: str,
        /,
        *,
        guild_id: int | None = None,
        channel_id: int | None = None,
        extra_args: dict[str, Any] | None = None,
    ) -> None:
        self.event_name: str = event_name
        self.guild_id: int | None = guild_id
        self.channel_id: int | None = channel_id
        self.extra_args: dict[str, Any] = extra_args or {}

    @property
    def _key(self) -> tuple[str, int | None, int | None]:
        return (self.event_name, self.guild_id, self.channel_id)

    def __hash__(self) -> int:
        return hash(self._key)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _PendingSubscription):
            return NotImplemented

        return self._key == other._key

    def __repr__(self) -> str:
        return (
            f"_PendingSubscription(event_name={self.event_name!r}, "
            f"guild_id={self.guild_id!r}, channel_id={self.channel_id!r})"
        )


# Maps each ``EventsHandler.on_*`` method to the RPC event it handles.
_HANDLER_METHOD_EVENTS: dict[str, str] = {
    "on_ready": "READY",
    "on_error": "ERROR",
    "on_current_user_update": "CURRENT_USER_UPDATE",
    "on_current_guild_member_update": "CURRENT_GUILD_MEMBER_UPDATE",
    "on_guild_status": "GUILD_STATUS",
    "on_guild_create": "GUILD_CREATE",
    "on_channel_create": "CHANNEL_CREATE",
    "on_relationship_update": "RELATIONSHIP_UPDATE",
    "on_voice_channel_select": "VOICE_CHANNEL_SELECT",
    "on_voice_state_create": "VOICE_STATE_CREATE",
    "on_voice_state_delete": "VOICE_STATE_DELETE",
    "on_voice_state_update": "VOICE_STATE_UPDATE",
    "on_voice_settings_update": "VOICE_SETTINGS_UPDATE",
    "on_voice_settings_update2": "VOICE_SETTINGS_UPDATE_2",
    "on_voice_connection_status": "VOICE_CONNECTION_STATUS",
    "on_speaking_start": "SPEAKING_START",
    "on_speaking_stop": "SPEAKING_STOP",
    "on_activity_join": "ACTIVITY_JOIN",
    "on_activity_join_request": "ACTIVITY_JOIN_REQUEST",
    "on_activity_spectate": "ACTIVITY_SPECTATE",
    "on_activity_invite": "ACTIVITY_INVITE",
    "on_activity_pip_mode_update": "ACTIVITY_PIP_MODE_UPDATE",
    "on_activity_layout_mode_update": "ACTIVITY_LAYOUT_MODE_UPDATE",
    "on_thermal_state_update": "THERMAL_STATE_UPDATE",
    "on_orientation_update": "ORIENTATION_UPDATE",
    "on_activity_instance_participants_update": "ACTIVITY_INSTANCE_PARTICIPANTS_UPDATE",
    "on_notification_create": "NOTIFICATION_CREATE",
    "on_message_create": "MESSAGE_CREATE",
    "on_message_update": "MESSAGE_UPDATE",
    "on_message_delete": "MESSAGE_DELETE",
    "on_overlay_update": "OVERLAY_UPDATE",
    "on_entitlement_create": "ENTITLEMENT_CREATE",
    "on_entitlement_delete": "ENTITLEMENT_DELETE",
    "on_screenshare_state_update": "SCREENSHARE_STATE_UPDATE",
    "on_video_state_update": "VIDEO_STATE_UPDATE",
    "on_authorize_request": "AUTHORIZE_REQUEST",
    "on_quest_enrollment_status_update": "QUEST_ENROLLMENT_STATUS_UPDATE",
}

# Events sent unprompted by Discord; SUBSCRIBE must never be sent for these.
_NON_SUBSCRIBABLE_EVENT_NAMES = frozenset({"READY", "ERROR", "AUTHORIZE_REQUEST"})

_SUBSCRIBABLE_EVENT_NAMES = (
    frozenset(_HANDLER_METHOD_EVENTS.values()) - _NON_SUBSCRIBABLE_EVENT_NAMES
)

# Subscribing to these requires a guild_id or channel_id we cannot infer, so
# they are registered locally and left for the user to subscribe explicitly.
_SUBSCRIPTION_REQUIRES_ARGS = frozenset(
    {
        "CURRENT_GUILD_MEMBER_UPDATE",
        "GUILD_STATUS",
        "MESSAGE_CREATE",
        "MESSAGE_UPDATE",
        "MESSAGE_DELETE",
        "NOTIFICATION_CREATE",
        "SPEAKING_START",
        "SPEAKING_STOP",
        "VOICE_STATE_CREATE",
        "VOICE_STATE_DELETE",
        "VOICE_STATE_UPDATE",
    }
)


class Event[D]:
    def __init__(
        self,
        data: D,
        /,
        subscription_guild_id: int | None = None,
        subscription_channel_id: int | None = None,
    ) -> None:
        self.data: D = data
        # The guild/channel this event was subscribed under, not a field of
        # the payload itself. Kept off `guild_id`/`channel_id` so those names
        # stay free for `__getattr__` to reach a same-named field on the
        # payload (e.g. VOICE_CHANNEL_SELECT's own channel_id/guild_id).
        self.subscription_guild_id: int | None = subscription_guild_id
        self.subscription_channel_id: int | None = subscription_channel_id

    def __getattr__(self, name: str) -> Any:
        # Only reached when normal attribute lookup on Event itself fails, so
        # this never shadows subscription_guild_id/subscription_channel_id/data.
        # Lets `event.x` reach fields on the payload directly (event.x instead
        # of event.data.x), including ones not declared on the payload's
        # class - new keys Discord adds show up here automatically instead of
        # requiring a code change first.
        data = self.data
        try:
            return getattr(data, name)
        except AttributeError:
            pass

        try:
            return data[name]  # type: ignore[index]
        except (KeyError, TypeError, IndexError):
            raise AttributeError(
                f"{type(self).__name__!r} object (event payload {type(data).__name__!r}) "
                f"has no attribute {name!r}"
            ) from None


class EventKey:
    def __init__(
        self,
        name: EventName,
        guild_id: int | str | None = None,
        channel_id: int | str | None = None,
        /,
    ) -> None:
        self.name: EventName = name
        self.guild_id: int | None = int(guild_id) if guild_id is not None else None
        self.channel_id: int | None = (
            int(channel_id) if channel_id is not None else None
        )

    def __hash__(self) -> int:
        included: list[int | str] = [self.name]
        if self.guild_id is not None:
            included.append(self.guild_id)

        if self.channel_id is not None:
            included.append(self.channel_id)

        return hash(tuple(included))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EventKey):
            return NotImplemented

        return (
            self.name == other.name
            and self.guild_id == other.guild_id
            and self.channel_id == other.channel_id
        )

    def __repr__(self) -> str:
        return f"EventKey(name={self.name!r}, guild_id={self.guild_id!r}, channel_id={self.channel_id!r})"


type EventCallback[EventData: RPCDispatchEventModel] = Callable[
    [Event[EventData]], Coroutine[Any, Any, None] | None
]


class RPCEventsManager:
    def __init__(self, rpc_client: RPCClient, /) -> None:
        self.__rpc_client: RPCClient = rpc_client

        self._handlers: dict[EventKey, list[EventCallback[RPCDispatchEventModel]]] = {}
        self._handlers_tasks: dict[str, list[asyncio.Task[None]]] = {}
        # Events registered from an EventsHandler that still need a SUBSCRIBE
        # sent for them once we are connected.
        self._pending_subscriptions: set[_PendingSubscription] = set()
        self._subscribed: set[_PendingSubscription] = set()
        self._login_watch_task: asyncio.Task[None] | None = None

    def register_handler(self, handler: EventsHandler, /) -> list[str]:
        """Wire every overridden ``on_*`` method of ``handler`` into this manager.

        Only methods the subclass actually overrides are registered; the no-op
        stubs on :class:`~oauthcord.rpc.EventsHandler` itself are skipped, so a
        handler is never subscribed to events it does not implement.

        Registration is local only — this does not talk to Discord. Subscribing
        happens on connect, in :meth:`start`.

        Parameters
        ----------
        handler: :class:`~oauthcord.rpc.EventsHandler`
            The handler instance whose overridden methods should be registered.

        Returns
        -------
        :class:`list`[:class:`str`]
            The names of the events that were registered.
        """
        registered: list[str] = []
        seen: set[str] = set()

        for method_name, method in _iter_handler_methods(type(handler)):
            info: _ListenerInfo | None = getattr(method, "__rpc_event__", None)

            if info is not None:
                # Explicitly marked with @listens_to - always registered, and it
                # carries any guild_id/channel_id the subscription needs.
                event_name = info.event_name
            elif method_name in _HANDLER_METHOD_EVENTS:
                # A plain override of a known on_* stub.
                if method is getattr(EventsHandler, method_name, None):
                    # Not overridden - the base stub does nothing, so skip it.
                    continue
                event_name = _HANDLER_METHOD_EVENTS[method_name]
            else:
                continue

            if method_name in seen:
                continue
            seen.add(method_name)

            bound = getattr(handler, method_name)
            # A listener may be scoped to several guilds/channels at once; each
            # gets its own registration and its own SUBSCRIBE.
            scopes = info.scopes() if info is not None else [(None, None)]

            for guild_id, channel_id in scopes:
                key = EventKey(event_name, guild_id, channel_id)
                self._handlers.setdefault(key, []).append(bound)

                # READY/ERROR/AUTHORIZE_REQUEST are sent unprompted and must
                # never be SUBSCRIBE'd. Everything else needs a subscription.
                if event_name in _SUBSCRIBABLE_EVENT_NAMES:
                    self._pending_subscriptions.add(
                        _PendingSubscription(
                            event_name,
                            guild_id=guild_id,
                            channel_id=channel_id,
                            extra_args=info.extra_args if info is not None else None,
                        )
                    )

                _log.debug(
                    "Registered %s.%s for event %s (guild_id=%s, channel_id=%s)",
                    type(handler).__name__,
                    method_name,
                    event_name,
                    guild_id,
                    channel_id,
                )

            registered.append(event_name)

        return registered

    def _watch_for_login(self, timeout: float, /) -> None:
        """Complain if deferred subscriptions are never flushed by a login.

        Subscribing to most events needs an authenticated connection, so they are
        queued until :meth:`RPCClient.login` runs. If that never happens the
        handlers simply never fire, which is impossible to diagnose - so after
        ``timeout`` seconds this reports the events that are still waiting.
        """
        if timeout <= 0 or self._login_watch_task is not None:
            return

        async def watch() -> None:
            try:
                await asyncio.sleep(timeout)
            except asyncio.CancelledError:
                return

            pending = sorted(p.event_name for p in self._pending_subscriptions)
            if not pending or self.__rpc_client._authorized:
                return

            error = RPCSubscriptionError(", ".join(pending))
            _log.error("%s", error)

        self._login_watch_task = asyncio.ensure_future(watch())

    def _cancel_login_watch(self) -> None:
        """Stop the deferred-subscription watchdog, if one is running."""
        if self._login_watch_task is not None:
            self._login_watch_task.cancel()
            self._login_watch_task = None

    async def _subscribe_pending(self, *, authenticated: bool = False) -> None:
        """Send SUBSCRIBE for events registered from an :class:`EventsHandler`.

        Events whose subscription requires an argument we do not have (a
        ``guild_id`` or ``channel_id``) are skipped: the callback stays
        registered, and the user subscribes explicitly with the id.

        Most RPC events require an authenticated connection. Subscribing to one
        before :meth:`RPCClient.login` raises :exc:`RPCSubscriptionError` rather
        than failing quietly, since a silently skipped subscription means the
        handler never fires and nothing says why.

        Parameters
        ----------
        authenticated: :class:`bool`
            Whether the connection has been authenticated. Only used to word the
            error raised when Discord refuses a subscription.

        Raises
        ------
        RPCSubscriptionError
            Discord refused a subscription because the connection is not
            authenticated, or the granted scopes do not cover that event.
        """
        for pending in sorted(self._pending_subscriptions, key=lambda p: p._key[0]):
            event_name = pending.event_name
            args: dict[str, Any] = dict(pending.extra_args)
            if pending.guild_id is not None:
                args["guild_id"] = str(pending.guild_id)
            if pending.channel_id is not None:
                args["channel_id"] = str(pending.channel_id)

            if event_name in _SUBSCRIPTION_REQUIRES_ARGS and not args:
                _log.debug(
                    "Not auto-subscribing to %s: it requires a guild_id/channel_id. "
                    "Pass one with @listens_to(...), or call rpc.events.subscribe(...)",
                    event_name,
                )
                self._subscribed.add(pending)
                continue

            try:
                await self.__rpc_client._send_command(
                    InternalRPCCommand.SUBSCRIBE, args, evt=event_name
                )
            except RPCError as exc:
                if exc.code == _NOT_AUTHENTICATED_CODE and not authenticated:
                    # Needs an authenticated connection. Keep it queued:
                    # authenticate() flushes the queue once login happens, and
                    # _watch_for_login complains if that never comes.
                    _log.debug(
                        "Deferring subscription to %s until authenticated",
                        event_name,
                    )
                    continue

                if exc.code == _NOT_AUTHENTICATED_CODE:
                    # Already authenticated and still refused: a scope problem
                    # that waiting will never fix.
                    raise RPCSubscriptionError(event_name, True) from exc

                _log.error("Failed to auto-subscribe to %s: %s", event_name, exc)
                self._subscribed.add(pending)
                continue
            except Exception:
                _log.exception("Failed to auto-subscribe to %s", event_name)
                self._subscribed.add(pending)
                continue

            self._subscribed.add(pending)
            _log.debug("Auto-subscribed to %s (args=%s)", event_name, args)

        # Anything successfully handled above should not be retried.
        self._pending_subscriptions -= self._subscribed

        if self._pending_subscriptions and not authenticated:
            # Still waiting on a login to flush these.
            self._watch_for_login(self.__rpc_client._login_timeout)
        else:
            self._cancel_login_watch()

    async def start(self) -> None:
        """Re-subscribe to every currently-registered event with Discord.

        Called after a (re)connect so handlers registered via :meth:`subscribe`
        are subscribed to on the wire again. This also flushes the subscriptions
        queued by :meth:`register_handler` for an
        :class:`~oauthcord.rpc.EventsHandler`.
        """
        authenticated = self.__rpc_client._authorized
        await self._subscribe_pending(authenticated=authenticated)

        # Re-subscribe callbacks registered through subscribe()/event(). Handler
        # methods are covered by _subscribe_pending above, so skip those keys to
        # avoid subscribing twice.
        handler_keys = {
            EventKey(pending.event_name, pending.guild_id, pending.channel_id)
            for pending in self._pending_subscriptions | self._subscribed
        }
        for event in self._handlers:
            if (
                event in handler_keys
                or str(event.name) in _NON_SUBSCRIBABLE_EVENT_NAMES
            ):
                continue

            args: dict[str, Any] = {}
            if event.guild_id is not None:
                args["guild_id"] = str(event.guild_id)
            if event.channel_id is not None:
                args["channel_id"] = str(event.channel_id)

            try:
                await self.__rpc_client._send_command(
                    InternalRPCCommand.SUBSCRIBE,
                    args,
                    evt=event.name,
                )
            except RPCError as exc:
                if exc.code == _NOT_AUTHENTICATED_CODE and not authenticated:
                    _log.debug(
                        "Deferring re-subscription to %s until authenticated",
                        event.name,
                    )
                    continue

                if exc.code == _NOT_AUTHENTICATED_CODE:
                    raise RPCSubscriptionError(str(event.name), True) from exc

                _log.error("Failed to re-subscribe to %s: %s", event.name, exc)

    async def subscribe[EventData: RPCDispatchEventModel](
        self,
        callback: EventCallback[EventData],
        event_name: EventName | None = None,
        *,
        guild_id: int | None = None,
        channel_id: int | None = None,
        **extra_args: Any,
    ) -> None:
        """Subscribe to an event.

        Parameters
        ----------
        callback: Callable[[:class:`Event`], Coroutine[Any, Any, None]]
            The function to call when the event is received. It must be a
            coroutine function that takes a single :class:`Event` argument.
        event_name: :class:`str` | :class:`SubscribeableRPCEvent` | :class:`ReceivedRPCEvent` | None
            The name of the event to subscribe to. If ``None``, the name is inferred from the callback's ``__name__``.
        guild_id: :class:`int` | None
            The guild ID to scope the subscription to, if applicable. Some events
            require a guild ID to subscribe to.
        channel_id: :class:`int` | None
            The channel ID to scope the subscription to, if applicable. Some events
            require a channel ID to subscribe to.
        extra_args: Any
            Additional keyword arguments to include in the subscription request.
            These are sent to Discord as part of the SUBSCRIBE command and may be
            required for certain events.
        """
        event_name = event_name or callback.__name__
        args: dict[str, Any] = dict(extra_args)
        if guild_id is not None:
            args["guild_id"] = str(guild_id)
        if channel_id is not None:
            args["channel_id"] = str(channel_id)

        await self.__rpc_client._send_command(
            InternalRPCCommand.SUBSCRIBE, args, evt=event_name
        )

        key = EventKey(event_name, guild_id, channel_id)
        # The dispatch table is necessarily untyped past this point - it holds
        # callbacks for many different event models side by side, so the
        # specific EventData narrowing subscribe() gives callers can't survive
        # storage here. dispatch() only ever calls a callback with the event
        # it was actually subscribed to, so this is safe despite the erasure.
        self._handlers.setdefault(key, []).append(callback)  # pyright: ignore[reportArgumentType]
        _log.debug(
            "Subscribed to event: %s (guild_id=%s, channel_id=%s)",
            event_name,
            guild_id,
            channel_id,
        )

    async def unsubscribe(
        self,
        event_name: EventName,
        /,
        guild_id: int | None = None,
        channel_id: int | None = None,
    ) -> None:
        """Unsubscribe from an event.

        Parameters
        ----------
        event_name: :class:`str` | :class:`SubscribeableRPCEvent` | :class:`ReceivedRPCEvent`
            The name of the event to unsubscribe from.
        guild_id: :class:`int` | None
            The guild ID to scope the unsubscription to, if applicable. Some events
            require a guild ID to unsubscribe from.
        channel_id: :class:`int` | None
            The channel ID to scope the unsubscription to, if applicable. Some events
            require a channel ID to unsubscribe from.
        """
        args: dict[str, Any] = {}
        if guild_id is not None:
            args["guild_id"] = str(guild_id)
        if channel_id is not None:
            args["channel_id"] = str(channel_id)

        await self.__rpc_client._send_command(
            InternalRPCCommand.UNSUBSCRIBE, args, evt=event_name
        )

        key = EventKey(event_name, guild_id, channel_id)
        if key in self._handlers:
            del self._handlers[key]

        _log.debug(
            "Unsubscribed from event: %s (guild_id=%s, channel_id=%s)",
            event_name,
            guild_id,
            channel_id,
        )

    async def unsubscribe_all(self) -> None:
        for event_key in list(self._handlers.keys()):
            await self.unsubscribe(
                event_key.name,
                guild_id=event_key.guild_id,
                channel_id=event_key.channel_id,
            )

        self._handlers.clear()
        _log.debug("Unsubscribed from all events.")

    async def __maybe_coroutine(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            await result

    def _parse_message_event(
        self,
        data: event_types.NotificationCreateEventData
        | event_types.MessageCreateEventData
        | event_types.MessageUpdateEventData,
    ) -> MessageEvent:
        return MessageEvent(data=data, state=self.__rpc_client._model_state)

    def _parse_ready(self, data: event_types.ReadyEventData) -> ReadyEvent:
        return ReadyEvent(data=data, state=self.__rpc_client._model_state)

    def _parse_current_user_update(
        self, data: event_types.CurrentUserUpdateEventData
    ) -> RPCUser:
        return RPCUser(data=data, state=self.__rpc_client._model_state)

    def _parse_current_guild_member_update(
        self, data: event_types.CurrentGuildMemberUpdateEventData
    ) -> RPCGuildMember:
        return RPCGuildMember(data=data, state=self.__rpc_client._model_state)

    def _parse_guild_status(
        self, data: event_types.GuildStatusEventData
    ) -> GuildStatus:
        return GuildStatus(data=data, state=self.__rpc_client._model_state)

    def _parse_guild_create(self, data: event_types.GuildCreateEventData) -> RPCGuild:
        return RPCGuild(data=data)

    def _parse_channel_create(
        self, data: event_types.ChannelCreateEventData
    ) -> RPCPartialChannel:
        return RPCPartialChannel(data=data, state=self.__rpc_client._model_state)

    def _parse_relationship_update(
        self, data: event_types.RelationshipUpdateEventData
    ) -> RPCRelationship:
        return RPCRelationship(data=data, state=self.__rpc_client._model_state)

    def _parse_voice_state_event(
        self,
        data: event_types.VoiceStateCreateEventData
        | event_types.VoiceStateDeleteEventData
        | event_types.VoiceStateUpdateEventData,
    ) -> RPCVoiceState:
        return RPCVoiceState(data=data, state=self.__rpc_client._model_state)

    def _parse_voice_settings_update(
        self, data: event_types.VoiceSettingsUpdateEventData
    ) -> VoiceSettings:
        return VoiceSettings(data=data)

    def _parse_activity_join_request(
        self, data: event_types.ActivityJoinRequestEventData
    ) -> ActivityJoinRequest:
        return ActivityJoinRequest(data=data, state=self.__rpc_client._model_state)

    def _parse_activity_invite(
        self, data: event_types.ActivityInviteEventData
    ) -> ActivityInvite:
        return ActivityInvite(data=data, state=self.__rpc_client._model_state)

    def _parse_activity_instance_participants_update(
        self, data: event_types.ActivityInstanceParticipantsUpdateEventData
    ) -> ActivityInstanceParticipantsUpdate:
        return ActivityInstanceParticipantsUpdate(
            data=data,
            state=self.__rpc_client._model_state,
        )

    def _parse_entitlement_event(
        self,
        data: event_types.EntitlementCreateEventData
        | event_types.EntitlementDeleteEventData,
    ) -> Entitlement | None:
        return Entitlement(data=data, state=self.__rpc_client._model_state)

    def _parse_message_delete(
        self, data: event_types.MessageDeleteEventData
    ) -> MessageDelete:
        return MessageDelete(data=data)

    def _parse_error(self, data: event_types.ErrorEventData) -> RPCErrorEvent:
        return RPCErrorEvent(data=data)

    def _parse_voice_channel_select(
        self, data: event_types.VoiceChannelSelectEventData
    ) -> VoiceChannelSelect:
        return VoiceChannelSelect(data=data)

    def _parse_voice_settings_update_2(
        self, data: event_types.VoiceSettingsUpdate2EventData
    ) -> VoiceSettingsUpdate2:
        return VoiceSettingsUpdate2(data=data)

    def _parse_voice_connection_status(
        self, data: event_types.VoiceConnectionStatusEventData
    ) -> VoiceConnectionStatus:
        return VoiceConnectionStatus(data=data)

    def _parse_speaking_start(
        self, data: event_types.SpeakingStartEventData
    ) -> SpeakingStartData:
        return SpeakingStartData(data=data)

    def _parse_speaking_stop(
        self, data: event_types.SpeakingStopEventData
    ) -> SpeakingStopData:
        return SpeakingStopData(data=data)

    def _parse_activity_join(
        self, data: event_types.ActivityJoinEventData
    ) -> ActivityJoin:
        return ActivityJoin(data=data)

    def _parse_activity_spectate(
        self, data: event_types.ActivitySpectateEventData
    ) -> ActivitySpectate:
        return ActivitySpectate(data=data)

    def _parse_activity_pip_mode_update(
        self, data: event_types.ActivityPipModeUpdateEventData
    ) -> ActivityPipModeUpdate:
        return ActivityPipModeUpdate(data=data)

    def _parse_activity_layout_mode_update(
        self, data: event_types.ActivityLayoutModeUpdateEventData
    ) -> ActivityLayoutModeUpdate:
        return ActivityLayoutModeUpdate(data=data)

    def _parse_thermal_state_update(
        self, data: event_types.ThermalStateUpdateEventData
    ) -> ThermalStateUpdate:
        return ThermalStateUpdate(data=data)

    def _parse_orientation_update(
        self, data: event_types.OrientationUpdateEventData
    ) -> OrientationUpdate:
        return OrientationUpdate(data=data)

    def _parse_overlay_update(
        self, data: event_types.OverlayUpdateEventData
    ) -> OverlayUpdate:
        return OverlayUpdate(data=data)

    def _parse_screenshare_state_update(
        self, data: event_types.ScreenshareStateUpdateEventData
    ) -> ScreenshareStateUpdate:
        return ScreenshareStateUpdate(data=data)

    def _parse_video_state_update(
        self, data: event_types.VideoStateUpdateEventData
    ) -> VideoStateUpdate:
        return VideoStateUpdate(data=data)

    def _parse_quest_enrollment_status_update(
        self, data: event_types.QuestEnrollmentStatusUpdateEventData
    ) -> QuestEnrollmentStatusUpdate:
        return QuestEnrollmentStatusUpdate(data=data)

    _PARSERS: ClassVar[dict[str, Callable[[RPCEventsManager, Any], Any]]] = {
        "READY": _parse_ready,
        "ERROR": _parse_error,
        "NOTIFICATION_CREATE": _parse_message_event,
        "MESSAGE_CREATE": _parse_message_event,
        "MESSAGE_UPDATE": _parse_message_event,
        "MESSAGE_DELETE": _parse_message_delete,
        "CURRENT_USER_UPDATE": _parse_current_user_update,
        "CURRENT_GUILD_MEMBER_UPDATE": _parse_current_guild_member_update,
        "GUILD_STATUS": _parse_guild_status,
        "GUILD_CREATE": _parse_guild_create,
        "CHANNEL_CREATE": _parse_channel_create,
        "RELATIONSHIP_UPDATE": _parse_relationship_update,
        "VOICE_CHANNEL_SELECT": _parse_voice_channel_select,
        "VOICE_STATE_CREATE": _parse_voice_state_event,
        "VOICE_STATE_DELETE": _parse_voice_state_event,
        "VOICE_STATE_UPDATE": _parse_voice_state_event,
        "VOICE_SETTINGS_UPDATE": _parse_voice_settings_update,
        "VOICE_SETTINGS_UPDATE_2": _parse_voice_settings_update_2,
        "VOICE_CONNECTION_STATUS": _parse_voice_connection_status,
        "SPEAKING_START": _parse_speaking_start,
        "SPEAKING_STOP": _parse_speaking_stop,
        "ACTIVITY_JOIN": _parse_activity_join,
        "ACTIVITY_JOIN_REQUEST": _parse_activity_join_request,
        "ACTIVITY_SPECTATE": _parse_activity_spectate,
        "ACTIVITY_INVITE": _parse_activity_invite,
        "ACTIVITY_PIP_MODE_UPDATE": _parse_activity_pip_mode_update,
        "ACTIVITY_LAYOUT_MODE_UPDATE": _parse_activity_layout_mode_update,
        "THERMAL_STATE_UPDATE": _parse_thermal_state_update,
        "ORIENTATION_UPDATE": _parse_orientation_update,
        "ACTIVITY_INSTANCE_PARTICIPANTS_UPDATE": (
            _parse_activity_instance_participants_update
        ),
        "OVERLAY_UPDATE": _parse_overlay_update,
        "ENTITLEMENT_CREATE": _parse_entitlement_event,
        "ENTITLEMENT_DELETE": _parse_entitlement_event,
        "SCREENSHARE_STATE_UPDATE": _parse_screenshare_state_update,
        "VIDEO_STATE_UPDATE": _parse_video_state_update,
        "QUEST_ENROLLMENT_STATUS_UPDATE": _parse_quest_enrollment_status_update,
    }

    def __call_handler(
        self,
        callback: EventCallback[RPCDispatchEventModel],
        event: Event[RPCDispatchEventModel],
        event_name: EventName,
    ) -> None:
        task = asyncio.ensure_future(self.__maybe_coroutine(callback, event))
        self._handlers_tasks.setdefault(event_name, []).append(task)
        task.add_done_callback(lambda t: self._handlers_tasks[event_name].remove(t))

    async def dispatch(
        self,
        event_name: EventName | EventCallback[RPCDispatchEventModel],
        data: dict[str, Any],
        /,
        guild_id: int | None = None,
        channel_id: int | None = None,
    ) -> None:
        _log.debug(
            "Dispatching event: %s (guild_id=%s, channel_id=%s), payload=%s",
            event_name,
            guild_id,
            channel_id,
            data,
        )

        event_name = event_name.__name__ if callable(event_name) else event_name
        parser = self._PARSERS.get(event_name)
        model: Any = parser(self, data) if parser is not None else data
        if model is None:
            # A parser can decline to produce an object (e.g. an entitlement
            # event with no active session); nothing to dispatch in that case.
            return

        event = Event(model)

        # ``guild_id``/``channel_id`` identify the *subscription* an event
        # arrived on, but many payloads also carry those names as ordinary
        # content (ACTIVITY_JOIN_REQUEST's channel_id, say). Prefer the scoped
        # key when something is registered for it, and otherwise fall back to
        # the unscoped one so listeners are not silently skipped.
        event_key = EventKey(event_name, guild_id, channel_id)
        if event_key not in self._handlers:
            unscoped = EventKey(event_name)
            if unscoped in self._handlers:
                event_key = unscoped
            else:
                _log.debug(
                    "Unknown event received: %s (guild_id=%s, channel_id=%s), "
                    "payload=%s",
                    event_name,
                    guild_id,
                    channel_id,
                    data,
                )
                return

        for callback in self._handlers[event_key]:
            self.__call_handler(callback, event, event_name)
            _log.debug(
                "Dispatched event: %s (guild_id=%s, channel_id=%s) to callback %s, payload=%s",
                event_name,
                guild_id,
                channel_id,
                callback,
                data,
            )

    def event[E: RPCDispatchEventModel](
        self,
        event_name: str | ReceivedRPCEvent | SubscribeableRPCEvent | None = None,
        /,
        guild_id: int | None = None,
        channel_id: int | None = None,
    ) -> Callable[[EventCallback[E]], EventCallback[E]]:
        """Decorator to register a function as an event handler.

        Parameters
        ----------
        event_name: :class:`str` | :class:`SubscribeableRPCEvent` | :class:`ReceivedRPCEvent` | None
            The name of the event to subscribe to. If ``None``, the name is inferred from the callback's ``__name__``.

        guild_id: :class:`int` | None
            The guild ID to scope the subscription to, if applicable.
        channel_id: :class:`int` | None
            The channel ID to scope the subscription to, if applicable.
        """

        def decorator(func: EventCallback[E], /) -> EventCallback[E]:
            event_name_: str = func.__name__ or str(event_name)
            key = EventKey(event_name_, guild_id, channel_id)
            self._handlers.setdefault(key, []).append(func)  # pyright: ignore[reportArgumentType]
            return func

        return decorator

    def close(self) -> None:
        """Close the manager and cancel all pending tasks."""
        self._cancel_login_watch()
        if self._handlers_tasks:
            for tasks in self._handlers_tasks.values():
                for task in tasks:
                    task.cancel()
            self._handlers_tasks.clear()

        self._handlers.clear()
