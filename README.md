> [!WARNING]
> This library is under active development. APIs and internal structures may change or be rewritten at any time. Expect breaking changes and limited stability.
> 
> Use at your own risk. Not recommended for production use yet.


# oauthcord.py

`oauthcord.py` is an async Discord OAuth2 wrapper.

## What this library is for

Use this when you need to:
- send users through Discord OAuth2
- exchange an authorization code for tokens
- call Discord endpoints with bearer tokens
- work with typed models instead of raw JSON

This is **not** a bot gateway framework. For bot/gateway work, use a bot SDK such as `discord.py`.

## Highlights

- Async client powered by `aiohttp`
- Typed response models for common OAuth2-related endpoints
- Scope guards on client methods (raises `MissingRequiredScopes` early)
- Helpers for messages, channels, relationships, lobbies, entitlements, and more
- Strict static typing with Pyright

## Requirements

- Python `3.14+`

## Installation

Clone the repository:

```bash
git clone https://github.com/Soheab/oauthcord.py.git
cd oauthcord.py
```

Install the library:

```bash
python -m pip install "oauthcord.py @ git+https://github.com/Soheab/oauthcord.py"
```

## Quick start

```python
import asyncio

from oauthcord import Client, Scope


async def main() -> None:
    client = Client(
        client_id=123456789012345678,
        client_secret="your-client-secret",
        redirect_uri="http://localhost:8000/callback",
        scopes=[Scope.IDENTIFY, Scope.GUILDS],
        state="optional-csrf-state",  # optional
    )

    # 1) Send the user to this URL
    authorize_url = client.get_authorization_url()
    print(authorize_url)

    # 2) In your callback, exchange the received ?code=... for an authorized session
    session = await client.exchange_token("authorization_code_here")

    # 3) Call OAuth-protected endpoints
    me = await session.get_current_user()
    guilds = await session.get_current_user_guilds()

    print(me.username, me.id)
    print(f"Guilds: {len(guilds)}")

    # Optional close the client session.
    await client.http.close()


asyncio.run(main())
```

For complete web callback examples (Aiohttp and Litestar), see [examples/](./examples/).

## Typical OAuth flow

1. Build the Discord authorize URL (`client.get_authorization_url()`).
2. Redirect the user to the URL and have them authorize your app.
3. Receive `code` on your redirect URI.
4. Exchange it with `client.exchange_token(code)`.
5. Use the returned authorized session to make API calls.
6. Refresh when needed with `session.refresh()`.
7. Revoke when needed with `session.revoke()`.

## Implemented endpoints

The wrapper currently implements these Discord API routes (including their matching
typed models and request payloads). Most routes use Discord API v10, plus OAuth2
token/revoke endpoints.

- OAuth2
    - `POST /oauth2/token` (authorization code exchange)
    - `POST /oauth2/token` (refresh token)
    - `POST /oauth2/token/revoke`
    - `GET /oauth2/@me`
- Users and profile
    - `GET /users/@me`
    - `PATCH /users/@me/account`
    - `GET /users/@me/harvest`
    - `POST /users/@me/harvest`
- Guilds and members
    - `GET /users/@me/guilds`
    - `GET /users/@me/guilds/{guild_id}/member`
    - `PUT /guilds/{guild_id}/members/{user_id}`
    - `GET /guilds/{guild_id}/channels`
- Connections
    - `GET /users/@me/connections`
    - `GET /users/@me/linked-connections`
- Channels and calls
    - `GET /users/@me/dms/{user_id}`
    - `POST /users/@me/channels`
    - `GET /channels/{channel_id}/call`
    - `POST /channels/{channel_id}/call/ring`
    - `POST /channels/{channel_id}/call/stop-ringing`
    - `GET /channels/{channel_id}/linked-accounts`
- Direct messages
    - `GET /users/{user_id}/messages`
    - `POST /users/{user_id}/messages`
    - `PATCH /users/{user_id}/messages/{message_id}`
    - `DELETE /users/{user_id}/messages/{message_id}`
- Relationships
    - `GET /users/@me/relationships`
    - `POST /users/@me/relationships` (friend request)
    - `PUT /users/@me/relationships/{user_id}`
    - `DELETE /users/@me/relationships/{user_id}`
    - `GET /users/@me/game-relationships`
    - `PUT /users/@me/game-relationships/{user_id}`
    - `DELETE /users/@me/game-relationships/{user_id}`
- Invites
    - `POST /invites/{code}`
- Lobbies
    - `PUT /lobbies`
    - `DELETE /lobbies/{lobby_id}/members/{user_id}`
    - `POST /lobbies/{lobby_id}/members/@me/invites`
    - `PATCH /lobbies/{lobby_id}/channel-linking`
    - `GET /lobbies/{lobby_id}/messages`
    - `POST /lobbies/{lobby_id}/messages`
- Applications
    - `POST /applications/{application_id}/attachment`
    - `GET /applications/{application_id}/partial`
    - `GET /users/@me/applications/{application_id}/role-connection`
    - `PUT /users/@me/applications/{application_id}/role-connection`
    - `POST /applications/{application_id}/quick-links/`
    - `POST /application-identities`
    - `GET /applications/{application_id}/entitlements`
    - `GET /applications/{application_id}/entitlements/{entitlement_id}`
    - `POST /applications/{application_id}/entitlements/{entitlement_id}/consume`
    - `DELETE /applications/{application_id}/entitlements/{entitlement_id}`
- Store and SKUs
    - `GET /applications/{application_id}/skus`
    - `POST /store/skus`
    - `GET /store/skus/{sku_id}`
    - `PATCH /store/skus/{sku_id}`
    - `GET /store/skus/{sku_id}/listings`
    - `POST /store/listings`
    - `GET /store/listings/{listing_id}`
    - `PATCH /store/listings/{listing_id}`
    - `DELETE /store/listings/{listing_id}`
    - `GET /store/skus/{sku_id}/plans`
    - `GET /store/applications/{application_id}/assets`
    - `POST /store/applications/{application_id}/assets`
    - `DELETE /store/applications/{application_id}/assets/{asset_id}`

## API references

This project tracks Discord behavior as closely as possible using:

- Unofficial docs: https://docs.discord.food/
- Official docs: https://docs.discord.com/


## Credits

- Rate-limit bucket design in `src/models/internals/_ratelimiter_.py` and `src/models/internals/http.py` are inspired by `discord.py` by Rapptz

