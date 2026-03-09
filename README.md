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

from oauthcord import OAuth2Cord, Scope


async def main() -> None:
    client = OAuth2Cord(
        client_id=123456789012345678,
        client_secret="your-client-secret",
        redirect_uri="http://localhost:8000/callback",
        scopes=[Scope.IDENTIFY, Scope.GUILDS],
        state="optional-csrf-state",
    )

    # 1) Send the user to this URL
    authorize_url = client.oauth2_url()
    print(authorize_url)

    # 2) In your callback, exchange the received ?code=... for a token
    token = await client.get_token("authorization_code_here")

    # 3) Call OAuth-protected endpoints
    me = await client.current_user(token)
    guilds = await client.guilds(token)

    print(me.username, me.id)
    print(f"Guilds: {len(guilds)}")

    # Optional close the client session.
    await client.http.close()


asyncio.run(main())
```

## Typical OAuth flow

1. Build the Discord authorize URL (`client.oauth2_url()`).
2. Redirect the user to Discord.
3. Receive `code` on your redirect URI.
4. Exchange it with `client.get_token(code)`.
5. Use the returned token in API calls.
6. Refresh when needed with `refresh_token(...)`.
7. Revoke when needed with `revoke_token(...)`.

## Scope behavior

Many methods enforce scope requirements before making HTTP calls.

Examples:
- `current_user(...)` requires `Scope.IDENTIFY`
- `guilds(...)` requires `Scope.GUILDS`
- `connections(...)` requires `Scope.CONNECTIONS`

If scopes are missing, the client raises `MissingRequiredScopes`.

## API references

This project tracks Discord behavior as closely as possible using:

- Unofficial docs: https://docs.discord.food/
- Official docs: https://discord.com/developers/docs

## Credits

- Rate-limit bucket design in `src/models/internals/_ratelimiter_.py` and `src/models/internals/http.py` are inspired by `discord.py` by Rapptz

## Status

This is an ongoing project.  Endpoints and models will probably grow as coverage improves.  A partial rewrite or refactor is also likely at the moment.
