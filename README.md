# tg-proxy

Telegram administrative proxy — RPC CLI for bot and user management.

## Architecture

Single binary with two namespaces:

```bash
tg-proxy admin setup|status          # Admin operations (always JSON)
tg-proxy do <action> [payload|file]  # RPC actions (JSON default, table via --format)
```

### `tg-proxy admin`

| Command | Description |
|---------|-------------|
| `setup` | First-time auth via HITL web form (creates `~/.config/tg-proxy/.env`) |
| `status` | Your Telegram identity as JSON |

### `tg-proxy do` (RPC) — 22 commands

| Action | Description | HITL | Enriched |
|--------|-------------|:----:|:--------:|
| `bot-list` | List ALL owned bots (getAdminedBots) | ❌ | — |
| `bot-info` | Details for one or more bots | ❌ | **`photo_info`** ✅ |
| `bot-token` | Get token(s) — appends to `.env` | ✅ | — |
| `bot-create` | Create one or more bots (max privacy) | ✅ | — |
| `bot-delete` | Delete one or more bots | ✅ | — |
| `bot-send` | Send message AS a bot (to me) | ✅ | — |
| `bot-send-file` | Send message + files AS a bot | ✅ | — |
| **`bot-photo`** | **Download profile photo from any bot/user** | ❌ | — |
| `chat-list` | List conversations | ❌ | **`folders`** ✅ |
| `chat-read` | Read messages from a chat | ❌ | — |
| `chat-send` | Send message as you to anyone | ✅ | — |
| `chat-send-file` | Send message + files as you | ✅ | — |
| `chat-download` | Download media files by message_id(s) | ❌ | — |
| **`chat-delete`** | **Delete entire conversation** | ❌ | — |
| **`chat-delete-messages`** | **Delete specific messages** | ❌ | — |
| **`folder-list`** | **List Telegram chat folders with chats** | ❌ | — |
| **`folder-set`** | **Create/update folder (UPSERT)** | ❌ | — |
| **`folder-delete`** | **Delete folder by title** | ✅ | — |
| **`chat-move`** | **Move chat between folders** | ❌ | — |
| `updates` | Read bot's inbox | ❌ | — |
| `webhook-get` | Show webhook configuration | ❌ | — |
| `webhook-set` | Set webhook URL | ❌ | — |
| `webhook-del` | Delete webhook | ❌ | — |

### Enriched features

- **`bot-info`** now includes **`photo_info`** (has_photo, photo_id, dc_id, has_video, size) — fetched via Telethon's `get_profile_photos()`
- **`chat-list`** now includes **`folders`** — cross-references Telegram dialog filters (`GetDialogFiltersRequest`) to show which folder each chat belongs to

### BotFather operations

- **`bot-create`** automates `/newbot` + privacy settings
- **`bot-delete`** sends exact confirmation text `"Yes, I am totally sure."`
- **`bot-token`** retrieves and stores tokens in `.env`
- **BF_NOTE** in ALL BotFather methods (success AND error paths)
- Rate limit detection with graceful error handling
- `/setuserpic` flow proven (S25 got Ubuntu's photo via BotFather)
- 13/13 bot tokens now in `.env`

## Config

Single `.env` at `~/.config/tg-proxy/.env`:

```env
TG_API_ID=32750118
TG_API_HASH=df796e5e2c4f045ae51eba5de68335f7
```

Created by `tg-proxy admin setup` (HITL web form).

## HITL

Human-in-the-Loop via local web UI (port 1143). Sensitive operations open a browser page showing the payload for review, editing, and approval/rejection.

## Output format

Every response has a `meta` section:

```json
{
  "meta": {
    "status": "ok",
    "comment": "optional user comment",
    "edited": false
  },
  "data": { ... }
}
```

Use `--format table` or `-f table` for table output.

## Install

### uv tool

```bash
uv tool install .
```

### Development

```bash
uv tool install --editable .
```

### Docker

```bash
make docker-build
docker run --rm kpihx/tg-proxy --help
```

## Development

```bash
make check        # ruff + py_compile + pyright + pytest
make uv-link      # editable install
make git-install-hooks  # pre-commit hook
```

See `Makefile` for full target list.
