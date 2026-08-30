"""Manual smoke test for oauthcord's RPC event handling.

This talks to the real Discord desktop client over its local IPC socket, so it can't
run in CI — it's meant to be run by hand while Discord is open on the same machine.

How to run
----------
1. Open https://discord.com/developers/applications and create/select an application.
2. Copy its Application ID (`client_id`) and Client Secret (`client_secret`).
3. Make sure the Discord desktop client is running and you're logged in.
4. Install dependencies:
   - `python -m pip install aiohttp`
5. Set `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET` below.
6. Run:
   - `python examples/rpc_events_handler.py`

What it does
------------
Shows the two ways to handle RPC events:

- Subclassing :class:`~oauthcord.rpc.EventsHandler` and overriding its ``on_*``
  methods, passed to :class:`~oauthcord.rpc.RPCClient` as ``handler``. Also uses
  :func:`~oauthcord.rpc.listens_to` to scope ``on_guild_status`` to a specific
  guild, since that event requires a ``guild_id`` subscription.
- Registering plain callbacks without a subclass, either with the
  ``@rpc.events.event(...)`` decorator or by calling
  :meth:`~oauthcord.rpc.events.RPCEventsManager.subscribe` directly.

Both are wired up to the same connection here so you can compare them; you would
normally pick one style per project, not mix them like this.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from oauthcord import Client, Scope
from oauthcord.rpc import (
    Event,
    EventsHandler,
    ReadyEvent,
    RPCClient,
    RPCGuild,
    VoiceChannelSelect,
    listens_to,
)

if TYPE_CHECKING:
    from oauthcord.rpc.models.events import GuildStatus

DISCORD_CLIENT_ID = 0
DISCORD_CLIENT_SECRET = ""  # required to exchange the RPC authorize code for a token

# Set this to a guild ID you're in to see GUILD_STATUS fire for it.
GUILD_ID = 0


# -- Subclass style -----------------------------------------------------------
#
# Override the on_* method for any event you care about; every other event is
# ignored automatically (the base class methods are no-ops and are never
# registered or subscribed to unless overridden).
class MyHandler(EventsHandler):
    async def on_ready(self, event: Event[ReadyEvent]) -> None:
        print(f"[handler] ready, connected as: {self.client.user}")

    async def on_guild_create(self, event: Event[RPCGuild]) -> None:
        print(f"[handler] guild available: {event.data.name} ({event.data.id})")

    async def on_voice_channel_select(self, event: Event[VoiceChannelSelect]) -> None:
        print(f"[handler] voice channel select: {event.data}")

    # GUILD_STATUS requires a guild_id/channel_id subscription, so it's not
    # auto-subscribed like the events above. listens_to() supplies the id
    # that auto_subscribe needs to wire this up on connect.
    @listens_to(guild_id=GUILD_ID)
    async def on_guild_status(self, event: Event[GuildStatus]) -> None:
        print(f"[handler] guild status: {event.data}")


async def main() -> None:
    oauth_client = Client(
        client_id=DISCORD_CLIENT_ID,
        client_secret=DISCORD_CLIENT_SECRET,
    )

    async with RPCClient(oauth_client, handler=MyHandler) as rpc:
        # -- Non-subclass style ------------------------------------------
        #
        # Registering callbacks directly on rpc.events works alongside the
        # handler above; both fire for the same events.
        @rpc.events.event("GUILD_CREATE")
        async def on_guild_create_callback(event: Event[RPCGuild]) -> None:
            print(f"[callback] guild available: {event.data.name} ({event.data.id})")

        async def on_voice_channel_select_callback(
            event: Event[VoiceChannelSelect],
        ) -> None:
            print(f"[callback] voice channel select: {event.data}")

        # subscribe() works the same way, without the decorator.
        await rpc.events.subscribe(
            on_voice_channel_select_callback, "VOICE_CHANNEL_SELECT"
        )

        print("Prompting for authorization inside Discord...")
        await rpc.login(scopes=[Scope.RPC, Scope.IDENTIFY, Scope.GUILDS])

        print("Listening for 15s (switch voice channels to see it fire)...")
        await asyncio.sleep(15)

        await rpc.events.unsubscribe("VOICE_CHANNEL_SELECT")

    await oauth_client.close()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
