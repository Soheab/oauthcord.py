"""Manual smoke test for oauthcord's RPCClient.

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
   - `python examples/rpc_smoke_test.py`

What it does
------------
- Connects and performs the RPC handshake (prints the connected local user).
- Sets a rich presence activity, waits, then clears it (check your Discord profile).
- Logs in (authorize + exchange + authenticate) and lists your guilds.
- Subscribes to VOICE_CHANNEL_SELECT and prints the next 10 seconds of events
  (switch voice channels while it's running to see it fire).
"""

from __future__ import annotations

import asyncio
import time

from oauthcord import Client, Scope
from oauthcord.rpc import Activity, ActivityType, Event, RPCClient, VoiceChannelSelect

DISCORD_CLIENT_ID = 0
DISCORD_CLIENT_SECRET = ""  # required to exchange the RPC authorize code for a token


async def main() -> None:
    oauth_client = Client(
        client_id=DISCORD_CLIENT_ID,
        client_secret=DISCORD_CLIENT_SECRET,
    )

    async with RPCClient(oauth_client) as rpc:
        print(f"Connected as: {rpc.user}")

        print("Setting activity...")
        activity = Activity(
            "oauthcord RPC Smoke Test",
            type=ActivityType.PLAYING,
            state="Running oauthcord's RPC smoke test",
            details="examples/rpc_smoke_test.py",
            timestamps={"start": int(time.time())},
        )
        await rpc.set_activity(activity)
        print("Activity set. Check your Discord profile, then check back here in 10s.")
        await asyncio.sleep(10)

        print("Clearing activity...")
        await rpc.set_activity(None)

        # GET_GUILDS (and most other read commands) require an authenticated connection
        # with the "rpc" scope, which grants control over the local Discord client.
        # login() does the local Discord consent prompt, token exchange, and
        # authenticate in one call.
        print("Prompting for authorization inside Discord...")
        await rpc.login(scopes=[Scope.RPC, Scope.IDENTIFY, Scope.GUILDS])

        guilds = await rpc.get_guilds()
        print(f"Guilds ({len(guilds)}):")
        for guild in guilds[:10]:
            print(f"  - {guild.name} ({guild.id})")

        async def on_voice_channel_select(event: Event[VoiceChannelSelect]) -> None:
            print(f"VOICE_CHANNEL_SELECT: {event}")

        await rpc.events.subscribe(on_voice_channel_select, "VOICE_CHANNEL_SELECT")
        print("Subscribed to VOICE_CHANNEL_SELECT, listening for 10s...")
        await asyncio.sleep(10)
        await rpc.events.unsubscribe("VOICE_CHANNEL_SELECT")

    await oauth_client.close()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
