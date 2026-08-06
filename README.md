> [!WARNING]
> This library is under active development. Public APIs and internal structures may change without notice.
>
> Expect breaking changes. Do not treat the current API as production-stable.
>
> PRs are welcome, but since I'm actively working on this and may redesign things, please open an issue or contact me before working on anything beyond a fix or critical bug.

## Contact

Feel free to contact me on Discord @`soheab_` (ID `150665783268212746`). DMing or mentioning me in any server is fine to me.

You can also open an issue for anything, whether it's a question, a bug, or a feature idea.

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
session = await AuthorisedSession.from_dict(client, token_data)
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

The registry is process-local and in-memory only. Persist `session.to_dict()` yourself if sessions must survive restarts, then recreate them later with `await AuthorisedSession.from_dict(client, token_data, identifier="internal-user-id")` while `store_session=True` is enabled on the client.

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

Models also support `instance["key"]` item access: it first looks for a typed attribute named `key`, falling back to `instance.data["key"]` if there isn't one.

```python
username = me["username"]  # same as me.username
raw_value = me["some_raw_field"]  # falls back to me.data["some_raw_field"]
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

<details>
<summary>Development tracking: missing models and model method candidates</summary>

<details>
<summary>Missing model tracking</summary>

### Missing Model Tracking

Raw `dict[...]` fields, raw nested payload attributes, or overly generic
`TypedDict` fields that likely need dedicated models or more specific payload
types. Ordinary maps such as localization dictionaries, metadata maps, price
maps, caches, headers, and serializer scratch dictionaries are intentionally
excluded.

#### `models/attachment.py`

- [ ] `Attachment.application`
  - Payload-only gap right now: `internals/_types/message.py` has
    `AttachmentResponse.application`, but `models/attachment.py` currently uses
    `internals/_types/attachment.py.Attachment`, which does not include
    `application` or `application_id`.

#### `models/components.py`

- [X] `UnfurledMediaItem.content_scan_metadata`
  - Uses `ContentScanMetadata`.
- [ ] `ContentInventoryEntryComponent.content_inventory_entry`
  - Currently stores `ContentInventoryEntryDataResponse` directly.
- [ ] `CheckpointCard.checkpoint_data`
  - Currently stores `CheckpointDataResponse` directly.

#### `models/embeds.py`

- [X] `EmbedMedia.content_scan_metadata`
  - Uses `ContentScanMetadata`.
- [X] `Embed.provider`
  - Uses `EmbedProvider`.

#### `models/entitlement.py`

- [X] `QuestRewardsMetadata.reward_code`
- [X] `Entitlement.sku`
- [X] `Entitlement.subscription_plan`

#### `models/invite.py`

- [ ] `Invite.profile`
- [ ] `Invite.roles`
- [ ] `Invite.stage_instance`
- [ ] `Invite.guild_scheduled_event`
- [ ] `Invite.guild_join_request`

#### `models/member.py`

- [ ] `ThreadMember.mute_config`

#### `models/store.py`

- [ ] `StoreListing.guild`
- [ ] `StorefrontCollection.tenant_metadata`

#### `internals/_types/channels.py`

- [ ] `ThreadMemberResponse.mute_config`
  - Undocumented.

#### `internals/_types/components.py`

- [X] `UnfurledMediaItemResponse.content_scan_metadata`
  - Uses `ContentScanMetadataResponse`.
- [ ] `ContentInventoryEntryDataResponse.traits`
- [ ] `ContentInventoryEntryDataResponse.extra`
- [ ] `ContentInventoryEntryDataResponse.signature`
- [ ] `CheckpointDataResponse.top_guild`
- [ ] `CheckpointDataResponse.top_emoji`
- [ ] `CheckpointDataResponse.top_game`

#### `internals/_types/entitlement.py`

- [X] `QuestRewardsMetadataResponse.reward_code`
- [X] `EntitlementResponse.sku`
- [X] `EntitlementResponse.subscription_plan`

#### `internals/_types/invite.py`

- [ ] `InviteResponse.profile`
- [ ] `InviteResponse.roles`
- [ ] `InviteResponse.stage_instance`
- [ ] `InviteResponse.guild_scheduled_event`
- [ ] `InviteResponse.guild_join_request`

#### `internals/_types/lobby.py`

- [X] `CreateLobbyMessageRequest.poll`
  - Reuses `PollCreateRequest`.
- [X] `CreateLobbyMessageRequest.shared_client_theme`
  - Reuses `SharedClientThemeRequest`.
- [ ] `CreateLobbyMessageRequest.metadata`
  - Likely intentionally generic metadata, but still tracked because it is a
    request payload field using `dict[str, object]`.

#### `internals/_types/message.py`

- [ ] `AttachmentResponse.application`
- [X] `EmbedMediaResponse.content_scan_metadata`
  - Uses `ContentScanMetadataResponse`.
- [ ] `MessageReferenceRequest.forward_only`
- [ ] `MessageReferenceResponse.forward_only`
- [ ] `MessageInteractionResponse.triggering_interaction_metadata`
- [ ] `MessagePurchaseNotificationResponse.guild_product_purchase`
- [ ] `MessageGiftInfoResponse.sound`
- [X] `MessageSnapshotResponse.message`
  - Reuses `MessageResponse`.
- [ ] `MessageResponse.activity`
- [ ] `MessageResponse.application`
- [X] `MessageResponse.referenced_message`
  - Reuses `MessageResponse | None`.
- [ ] `MessageResponse.interaction`
- [ ] `MessageResponse.resolved`
- [ ] `MessageResponse.sticker_items`
- [ ] `MessageResponse.stickers`
- [ ] `MessageResponse.soundboard_sounds`
- [ ] `MessageResponse.potions`
- [ ] `CreateDMMessageRequest.metadata`
  - Likely intentionally generic metadata, but still tracked because it is a
    request payload field using `dict[str, object]`.

#### `internals/_types/store.py`

- [ ] `StoreListingResponse.guild`
- [ ] `StorefrontCollectionResponse.tenant_metadata`

#### Completed Reuse Candidates

- [X] `CreateLobbyMessageRequest.poll` uses `PollCreateRequest`.
- [X] `CreateLobbyMessageRequest.shared_client_theme` uses
  `SharedClientThemeRequest`.
- [X] `MessageSnapshotResponse.message` and
  `MessageResponse.referenced_message` use recursive `MessageResponse` payloads.

</details>

<details>
<summary>Model method candidates</summary>

### Model Method Candidates

This tracks places where a model instance already has the identifiers needed to
call a session/client method directly, similar to `DMChannel.get_call_eligibility()`.

#### Audit Scope

Audited endpoint/client/model files:

- `internals/endpoints`: `application`, `channel`, `connection`, `current_auth`,
  `guild`, `invite`, `lobby`, `member`, `message`, `relationship`, `store`,
  `token`, and `user`.
- `client`: `_application`, `_channel`, `_connection`, `_guild`, `_invite`,
  `_lobby`, `_message`, `_oauth2`, `_relationship`, `_store`, and `_user`.
- Session-backed models: `CurrentApplication`, `CurrentInformation`, `Guild`,
  `GuildMember`, `ThreadMember`, `Lobby`, `PartialMessage`, `Message`,
  `PartialApplication`, `Entitlement`, `PartialUser`, `CurrentUser`, channels,
  relationships, and store models that inherit `BaseModelWithSession`.

#### `AccessToken`

- [X] `refresh(check_expired=...)`
  - Existing token model method.
- [X] `revoke()`
  - Existing token model method.

#### `CurrentApplication`

- [X] `get_partial()`
  - Forwards `get_partial_application(application_id=self.id)`.
- [ ] `skus(...)`
  - Can forward `get_application_skus(application_id=self.id, ...)`.
- [ ] `create_sku(...)`
  - Can forward `create_sku(application_id=self.id, ...)`.
- [ ] `store_assets()`
  - Can forward `get_application_store_assets(application_id=self.id)`.
- [ ] `create_store_asset(file=...)`
  - Can forward `create_application_store_asset(application_id=self.id, file=file)`.
- [ ] `bulk_identities(user_ids=...)`
  - Can forward `get_bulk_application_identities(user_ids=...)`.
  - This is current-application scoped and only correct for the application
    authorized by the session.
- [ ] `entitlements(...)`
  - Can forward `get_application_entitlements(application_id=self.id, ...)`.
- [ ] `get_entitlement(entitlement_id=...)`
  - Can forward `get_application_entitlement(application_id=self.id, entitlement_id=...)`.

##### Added But Not Implemented

These are already declared on `CurrentApplication` in
`src/oauthcord/models/current_auth.py`, but currently only contain `pass`.

- [ ] `get_global_application_commands()`
  - Likely needs `GET /applications/{application.id}/commands`.
  - Needs command HTTP/client mixins, then command model construction.
- [ ] `get_global_application_command(command_id)`
  - Likely needs `GET /applications/{application.id}/commands/{command.id}`.
- [ ] `create_global_application_command(data)`
  - Likely needs `POST /applications/{application.id}/commands`.
  - Should accept typed command request payloads/builders, not `Any`.
- [ ] `edit_global_application_command(command_id, data)`
  - Likely needs `PATCH /applications/{application.id}/commands/{command.id}`.
- [ ] `delete_global_application_command(command_id)`
  - Likely needs `DELETE /applications/{application.id}/commands/{command.id}`.
- [ ] `bulk_overwrite_global_application_commands(data)`
  - Likely needs `PUT /applications/{application.id}/commands`.
  - Should return command models if the endpoint response is modeled.
- [ ] `get_guild_application_commands(guild_id)`
  - Likely needs `GET /applications/{application.id}/guilds/{guild.id}/commands`.
- [ ] `get_guild_application_command(guild_id, command_id)`
  - Likely needs `GET /applications/{application.id}/guilds/{guild.id}/commands/{command.id}`.
- [ ] `edit_guild_application_command(guild_id, command_id, data)`
  - Likely needs `PATCH /applications/{application.id}/guilds/{guild.id}/commands/{command.id}`.
  - Should accept typed command request payloads/builders.
- [ ] `delete_guild_application_command(guild_id, command_id)`
  - Likely needs `DELETE /applications/{application.id}/guilds/{guild.id}/commands/{command.id}`.
- [ ] `bulk_overwrite_guild_application_commands(guild_id, data)`
  - Likely needs `PUT /applications/{application.id}/guilds/{guild.id}/commands`.
  - Should return command models if the endpoint response is modeled.
- [ ] `get_guild_application_command_permissions(guild_id)`
  - Likely needs `GET /applications/{application.id}/guilds/{guild.id}/commands/permissions`.
  - Model type likely `GuildApplicationCommandPermissions`.
- [ ] `get_application_command_permissions(guild_id, command_id)`
  - Likely needs `GET /applications/{application.id}/guilds/{guild.id}/commands/{command.id}/permissions`.
  - Model type likely `GuildApplicationCommandPermissions`.
- [ ] `edit_application_command_permissions(guild_id, command_id, data)`
  - Likely needs `PUT /applications/{application.id}/guilds/{guild.id}/commands/{command.id}/permissions`.
  - Should accept typed permission payloads, not `Any`.

#### `CurrentUser`

- [ ] `edit_account(global_name=...)`
  - Can forward `edit_current_user_account(global_name=...)`.
  - The session method returns `PartialUser`.
- [ ] `harvest()`
  - HTTP endpoint exists as `get_user_harvest()`, but there is no public
    client/session wrapper yet.
- [ ] `create_harvest()`
  - HTTP endpoint exists as `create_user_harvest()`, but there is no public
    client/session wrapper yet.

#### `DMChannel`

- [X] `get_call_eligibility()`
  - Existing reference pattern.
  - Forwards `get_call_eligibility(channel_id=self.id)`.
- [ ] `messages(limit=...)`
  - Can forward `get_dm_messages(user_id=..., limit=...)`.
  - The API takes the recipient user ID, not the channel ID. Only safe for
    one-to-one DMs via `self.recipients[0].id`.
- [ ] `send(...)` or `create_message(...)`
  - Can forward `create_dm_message(user_id=..., ...)`.
  - Same one-to-one DM caveat as `messages`.

#### `Entitlement`

- [ ] `consume()`
  - Can forward `consume_application_entitlement(application_id=self.application_id, entitlement_id=self.id)`.
- [ ] `delete()`
  - Can forward `delete_application_entitlement(application_id=self.application_id, entitlement_id=self.id)`.

#### `GameRelationship`

- [ ] `delete()`
  - Can forward `delete_game_relationship(user_id=self.user_id)`.

#### `GroupDMChannel`

- [X] `get_linked_accounts(user_ids=...)`
  - Existing convenience method.
  - Forwards `get_channel_linked_accounts(channel_id=self.id, ...)`.

#### `Guild`

- [X] `channels(...)`
  - Existing convenience method.
  - Forwards `get_guild_channels(guild_id=self.id, ...)`.
- [ ] `current_member()`
  - Can forward `get_current_guild_member(guild_id=self.id)`.
- [ ] `add_current_user(...)`
  - Can forward `add_current_user_to_guild(guild_id=self.id, ...)`.
  - Requires `bot_token` and may need explicit `user_id` when the session lacks
    `identify`.

#### `Lobby`

- [ ] `leave(user_id=...)`
  - Can forward `leave_lobby(lobby_id=self.id, user_id=...)`.
  - Could also offer a current-user shortcut if the session can reliably expose
    the current user ID.
- [ ] `create_invite_for_current_user()`
  - Can forward `create_lobby_invite_for_current_user(lobby_id=self.id)`.
- [ ] `edit_linked_channel(channel_id=...)`
  - Can forward `edit_lobby_linked_channel(lobby_id=self.id, channel_id=...)`.
  - Prefer `edit_*` naming to match repo conventions.
- [ ] `messages(limit=...)`
  - Can forward `get_lobby_messages(lobby_id=self.id, limit=...)`.
- [ ] `send(...)` or `create_message(...)`
  - Can forward `create_lobby_message(lobby_id=self.id, ...)`.
  - Should mirror `create_lobby_message` parameters closely.

#### `Message` / `PartialMessage`

- [ ] `edit(content=...)`
  - Can forward `edit_dm_message(user_id=..., message_id=self.id, ...)`.
  - Needs reliable recipient/user context. Current message models expose
    `channel_id`, `lobby_id`, and sometimes `recipient_id`, but the DM message
    endpoint wants `user_id`.
- [ ] `delete()`
  - Can forward `delete_dm_message(user_id=..., message_id=self.id)`.
  - Same recipient context issue as `edit`.

#### `PartialApplication`

- [X] `create_attachment(file)`
  - Existing convenience method.
  - Forwards `create_application_attachment(application_id=self.id, file=file)`.
- [X] `get_user_role_connection()`
  - Existing method, but the session method derives the application from current
    authorization rather than from `self.id`.
- [X] `edit_user_role_connection(...)`
  - Same current-authorization caveat as `get_user_role_connection`.
- [X] `create_quick_link(...)`
  - Same current-authorization caveat; the lower-level HTTP endpoint takes
    `application_id`.
- [ ] `skus(...)`
  - Can forward `get_application_skus(application_id=self.id, ...)`.
- [ ] `create_sku(...)`
  - Can forward `create_sku(application_id=self.id, ...)`.
- [ ] `store_assets()`
  - Can forward `get_application_store_assets(application_id=self.id)`.
- [ ] `create_store_asset(file=...)`
  - Can forward `create_application_store_asset(application_id=self.id, file=file)`.
- [ ] `bulk_identities(user_ids=...)`
  - Can forward `get_bulk_application_identities(user_ids=...)`.
  - This is current-application scoped and only correct when `self.id` matches
    the session's authorized application.
- [ ] `entitlements(...)`
  - Can forward `get_application_entitlements(application_id=self.id, ...)`.
- [ ] `get_entitlement(entitlement_id=...)`
  - Can forward `get_application_entitlement(application_id=self.id, entitlement_id=...)`.

#### `PartialUser`

- [X] `dm_channel()`
  - Existing convenience method.
  - Forwards `get_dm_channel(user_id=self.id)`.

#### `PrivateChannel`

- [X] `ring(...)`
  - Existing convenience method.
  - Forwards `ring_channel_recipients(channel_id=self.id, ...)`.
- [X] `stop_ringing(...)`
  - Existing convenience method.
  - Forwards `stop_ringing_channel_recipients(channel_id=self.id, ...)`.

#### `Relationship`

- [ ] `delete()`
  - Can forward `delete_relationship(user_id=self.user.id)`.
- [ ] `accept()`
  - Possibly forwards `create_relationship(user_id=self.user.id, ...)` if that is
    the right action for pending requests.

#### `SKU`

- [ ] `refresh(country_code=..., localize=...)`
  - Can forward `get_sku(sku_id=self.id, ...)`.
- [ ] `edit(...)`
  - Can forward `modify_sku(sku_id=self.id, ...)`.
  - Method body can mirror `modify_sku` minus `sku_id`.
- [ ] `store_listings(country_code=..., localize=...)`
  - Can forward `get_sku_store_listings(sku_id=self.id, ...)`.
- [ ] `subscription_plans()`
  - Can forward `get_subscription_plans(sku_id=self.id)`.

#### `StoreListing`

- [ ] `refresh(country_code=..., localize=...)`
  - Can forward `get_store_listing(listing_id=self.id, ...)`.
- [ ] `edit(...)`
  - Can forward `modify_store_listing(listing_id=self.id, ...)`.
  - Method body can mirror `modify_store_listing` minus `listing_id`.
- [ ] `delete()`
  - Can forward `delete_store_listing(listing_id=self.id)`.

#### Deferred Or Ambiguous

- `StoreAsset.delete()`
  - The delete endpoint needs both `application_id` and `asset_id`, but
    `StoreAsset` currently only carries `id`. This becomes straightforward if
    store assets retain their parent application ID when constructed.
- `DMChannel` message helpers on `PrivateChannel`
  - Group DMs also inherit `PrivateChannel`, but message history/send endpoints
    use a user ID route. Keep those helpers on `DMChannel` unless group-DM
    endpoint semantics are added.
- `Invite.accept()`
  - `accept_invite()` returns an `Invite`; accepting an invite from an already
    accepted `Invite` object is less useful unless invite fetch support is added
    first.
- `Connection` list endpoints
  - `get_current_user_connections()` and `get_current_user_linked_connections()`
    are current-user collection fetches. They do not fit a specific
    `Connection` instance.
- `send_friend_request(username=...)`
  - Username-based creation has no existing model carrying the required username
    target in a useful way.
- Token exchange/client close/OAuth URL helpers
  - These are client/session lifecycle helpers rather than model instance
    actions.

</details>

</details>

## Reference docs

This project tracks Discord behavior against:

- Unofficial docs: https://docs.discord.food/
- Official docs: https://docs.discord.com/

## Credits

- Rate-limit bucket design in `src/oauthcord/internals/_ratelimiter.py` and `src/oauthcord/internals/http.py` is inspired by `discord.py` by Rapptz
