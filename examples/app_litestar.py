"""Minimal Litestar OAuth callback example for oauthcord.

How to run
----------
1. Open https://discord.com/developers/applications and create/select an application.
2. In the Developer Portal, open `OAuth2` and add your callback URL to Redirects
   (example: `http://127.0.0.1:8000/callback`).
3. Copy your Application ID (`client_id`) and Client Secret (`client_secret`).
4. Install dependencies:
   - `python -m pip install litestar[standard]`
5. Set the constants (example for environment variables):
   - `DISCORD_CLIENT_ID`
   - `DISCORD_CLIENT_SECRET`
   - `DISCORD_REDIRECT_URI` (for example: `http://127.0.0.1:8000/callback`)
   - Optional: `DISCORD_OAUTH_STATE`
6. Start the server:
   - `python -m litestar --app examples.app_litestar:app run`
7. Open the printed authorize URL, approve scopes, and Discord will redirect to `/callback`.
"""

from __future__ import annotations

from typing import Any

from litestar import Litestar, Response, get  # pyright: ignore[reportMissingImports]

from oauthcord import Client, Scope

DISCORD_CLIENT_ID = 0
DISCORD_CLIENT_SECRET = ""
DISCORD_REDIRECT_URI = ""
DISCORD_OAUTH_STATE = None

scopes = [Scope.IDENTIFY, Scope.GUILDS]
client = Client(
    client_id=DISCORD_CLIENT_ID,
    client_secret=DISCORD_CLIENT_SECRET,
    redirect_uri=DISCORD_REDIRECT_URI,
    scopes=scopes,
    state=DISCORD_OAUTH_STATE,
)

authorize_url = client.get_authorization_url()
print(f"Open this URL to authorize: {authorize_url}")


@get("/callback")
async def callback(code: str) -> Response[dict[str, Any]]:
    # Discord redirects here with ?code=... after the user approves access.
    if not code:
        return Response({"error": "Missing OAuth code"}, status_code=400)

    # Exchange the temporary authorization code for an access token.
    session = await client.exchange_token(code)

    # Fetch the current user and the user's guild list with that token.
    # don't need to pass the token here, it's stored after get_token() is called.
    me = await session.current_user()
    guilds = await session.guilds()

    # Return one JSON payload so the OAuth result is easy to inspect.
    data = dict(me.data)
    data["guilds"] = [guild.data for guild in guilds]
    return Response(data)


app = Litestar(route_handlers=[callback], debug=True)
