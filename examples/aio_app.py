"""Minimal aiohttp OAuth callback example for oauthcord.

How to run
----------
1. Open https://discord.com/developers/applications and create/select an application.
2. In the Developer Portal, open `OAuth2` and add your callback URL to Redirects
   (example: `http://127.0.0.1:8000/callback`).
3. Copy your Application ID (`client_id`) and Client Secret (`client_secret`).
4. Install dependencies:
   - `python -m pip install aiohttp`
5. Set the constants (example for environment variables):
   - `DISCORD_CLIENT_ID`
   - `DISCORD_CLIENT_SECRET`
   - `DISCORD_REDIRECT_URI` (for example: `http://127.0.0.1:8000/callback`)
   - Optional: `DISCORD_OAUTH_STATE`
6. Start the app:
   - `python examples/aio_app.py`
7. Open the printed authorize URL, approve scopes, and Discord will redirect to `/callback`.
"""

from __future__ import annotations

from aiohttp import web
from aiohttp.web_response import json_response

from oauthcord import OAuth2Cord, Scope

DISCORD_CLIENT_ID = 0
DISCORD_CLIENT_SECRET = ""
DISCORD_REDIRECT_URI = ""
DISCORD_OAUTH_STATE = None


app = web.Application()
routes = web.RouteTableDef()

scopes = [Scope.IDENTIFY, Scope.GUILDS]
client = OAuth2Cord(
    client_id=DISCORD_CLIENT_ID,
    client_secret=DISCORD_CLIENT_SECRET,
    redirect_uri=DISCORD_REDIRECT_URI,
    scopes=scopes,
    state=DISCORD_OAUTH_STATE,
)
authorize_url = client.oauth2_url()
print(f"Open this URL to authorize: {authorize_url}")


@routes.get("/callback")
async def callback(request: web.Request):
    # Discord redirects here with ?code=... after the user approves access.
    code: str = request.query.get("code") or ""
    if not code:
        return json_response(data={"error": "Missing OAuth code"}, status=400)

    # Exchange the temporary authorization code for an access token.
    token = await client.get_token(code)

    # Fetch the current user and the user's guild list with that token.
    me = await client.current_user(token)
    guilds = await client.guilds(token)

    # Return one JSON payload so the OAuth result is easy to inspect.
    data = me.data
    data["guilds"] = [guild.data for guild in guilds]  # type: ignore

    return json_response(data=data)


app.add_routes(routes)
web.run_app(app, port=8000, host="127.0.0.1")
