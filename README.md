> [!WARNING]
> This library is under active development. Public APIs and internal structures may change without notice.
>
> Expect breaking changes. Do not treat the current API as production-stable.

# oauthcord.py

`oauthcord.py` is an async Python wrapper for the Discord OAuth2 API.

It is designed for applications that need to send users through Discord OAuth, exchange authorization codes for tokens, and call Discord endpoints with typed models instead of raw JSON payloads.

This is not a gateway or bot framework. If you need bot events, shards, or gateway state, use a bot SDK such as [`discord.py`](https://github.com/Rapptz/discord.py).

## Why use it

- Async client built on `aiohttp`
- Typed models for OAuth2 and related Discord REST resources
- Coverage for user, guild, connection, DM, relationship, lobby, application, entitlement, and store routes
- Strict typing with Pyright

## Installation

### Requirements

- Python `3.13+`


Install directly from GitHub:

```bash
python -m pip install "oauthcord.py @ git+https://github.com/Soheab/oauthcord.py"
```

Or with `uv`:

```bash
uv add "oauthcord.py @ git+https://github.com/Soheab/oauthcord.py"
```

## OAuth flow

The library centers around two objects:

- `Client` creates the authorization URL and exchanges an OAuth code for tokens.
- `AuthorisedSession` uses the resulting token to call Discord on behalf of the user.

Typical flow:

1. Create a `Client` with your application ID, client secret, redirect URI, and requested scopes.
2. Send the user to `client.get_authorization_url()`.
3. Receive `code` on your redirect URI.
4. Exchange it with `await client.exchange_token(code)`.
5. Use the returned `AuthorisedSession` to call Discord endpoints.
6. Refresh with `await session.refresh()` when needed.
7. Revoke with `await session.revoke()` if needed.

## Session management

`Client` can keep an in-memory registry of `AuthorisedSession` instances for applications that need to look up a user's OAuth session after the callback has finished.

Session storage is opt-in. Pass `store_session=True` to automatically store sessions created by `exchange_token()`, and pass `session_identifier` when you want a stable key such as your own user ID instead of a generated UUID lookup key. If storage is enabled globally but one specific session should not be added to the registry, pass `session_identifier=None` for that exchange.

```python
client = Client(
    client_id=123456789012345678,
    client_secret="your-client-secret",
    redirect_uri="http://127.0.0.1:8000/callback",
    scopes=[Scope.IDENTIFY, Scope.GUILDS],
    store_session=True,  # enabling
)

session = await client.exchange_token(
    code,
    session_identifier="internal-user-id",
)

same_session = client.get_session("internal-user-id")

temporary_session = await client.exchange_token(
    another_code,
    session_identifier=None,
)
```

You can also manage sessions manually:

```python
session = AuthorisedSession.from_token(client, token_data)
client.add_session(session, identifier="internal-user-id")

stored = client.get_session("internal-user-id")

client.remove_session("internal-user-id")
client.clear_sessions()

await session.close()
```

Refreshing a session updates its token in place:

```python
await session.refresh(check_expired=True)
```

Closing a session removes it from the client's registry. If the client was created with `revoke_tokens_on_session_close=True`, closing the session also revokes the current access token.

```python
await session.close()
```

The registry is process-local and in-memory only. Persist `session.to_dict()` yourself if sessions must survive restarts, then recreate them later with `AuthorisedSession.from_token(client, token_data, identifier="internal-user-id")` while `store_session=True` is enabled on the client.

## Quick start

```python
import asyncio

from oauthcord import Client, Scope


async def main() -> None:
    client = Client(
        client_id=123456789012345678,
        client_secret="your-client-secret",
        redirect_uri="http://127.0.0.1:8000/callback",
        scopes=[Scope.IDENTIFY, Scope.GUILDS],
        state="optional-csrf-state",
    )

    authorize_url = client.get_authorization_url()
    print(f"Send the user here: {authorize_url}")

    code = "authorization_code_from_your_callback"
    session = await client.exchange_token(code)

    try:
        me = await session.current_user()
        guilds = await session.guilds()

        print(me.id, me.username)
        print(f"Guild count: {len(guilds)}")
    finally:
        await client.http.close()


asyncio.run(main())
```

## Web callback examples

Minimal end-to-end callback examples are included in [`examples/app_aiohttp.py`](./examples/app_aiohttp.py) and [`examples/app_litestar.py`](./examples/app_litestar.py).

## Model data access

All returned models expose a `.data` attribute containing the raw payload from Discord.
Use this when you want the original API data directly instead of typed attributes.

```python
me = await session.current_user()

# typed model attribute 
username = me.username
print("Username", username)

# raw Discord payload
raw = me.data
print(raw)
username = raw["username"]
print("Username:", username)
```


## API coverage

The wrapper currently includes typed support for these route groups:

- OAuth2 token exchange, refresh, revoke, and current authorization info
- Current user, account edits, and harvest exports
- User guilds, guild member lookup, and guild join flows
- Connections and linked connections
- DM channels, DM messages, channel-linked accounts, and call endpoints
- Relationships and game relationships
- Invite acceptance
- Lobbies and lobby messages
- Application attachments, partial application data, quick links, and role connections
- Application entitlements
- Store SKUs, listings, assets, and plans

For the current concrete route list implemented by the wrapper:

<details>
<summary>Implemented endpoints</summary>

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
  - `POST /users/@me/relationships`
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

</details>

## Reference docs

This project tracks Discord behavior against:

- Unofficial docs: https://docs.discord.food/
- Official docs: https://docs.discord.com/


## Credits

- Rate-limit bucket design in `src/oauthcord/internals/_ratelimiter.py` and `src/oauthcord/internals/http.py` is inspired by `discord.py` by Rapptz
