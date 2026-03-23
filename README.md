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
        state="optional-csrf-state", # optional
    )

    # 1) Send the user to this URL
    authorize_url = client.get_authorization_url()
    print(authorize_url)

    # 2) In your callback, exchange the received ?code=... for an authorized session
    session = await client.exchange_token("authorization_code_here")

    # 3) Call OAuth-protected endpoints
    me = await session.current_user()
    guilds = await session.guilds()

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


## API references

This project tracks Discord behavior as closely as possible using:

- Unofficial docs: https://docs.discord.food/
- Official docs: https://docs.discord.com/

## Documentation

Build the Sphinx docs with Furo:

```bash
cd docs
uv run --group docs sphinx-build -b html . _build/html
```

## Credits

- Rate-limit bucket design in `src/models/internals/_ratelimiter_.py` and `src/models/internals/http.py` are inspired by `discord.py` by Rapptz

