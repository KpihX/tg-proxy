# tg — Telegram CLI

> Like `gh` for Telegram. Manage bots and personal conversations from the terminal.

```
┌─────────────────────────────────────────────────────────────────┐
│                         tg CLI                                  │
│                                                                 │
│   ┌─────────────────────┐    ┌─────────────────────────────┐   │
│   │    Bot API Layer     │    │    User API Layer (Telethon) │   │
│   │  (httpx, stateless) │    │  (MTProto, session-based)   │   │
│   │                     │    │                             │   │
│   │  TELEGRAM_*_TOKEN   │    │  TG_API_ID + TG_API_HASH    │   │
│   │  auto-discovered    │    │  OTP auth once, persisted   │   │
│   │  from env vars      │    │  at ~/.config/tg/user.sess  │   │
│   └──────────┬──────────┘    └──────────────┬──────────────┘   │
│              │                              │                   │
│    tg bots   │  tg status                   │  tg user me       │
│    tg send   │  tg updates                  │  tg user chats    │
│    tg webhook│  tg commands                 │  tg user read     │
│    tg chat   │                              │  tg user send     │
└─────────────────────────────────────────────────────────────────┘
```

## Why

Managing Telegram bots and reading conversations requires juggling the Telegram web app, BotFather, and curl commands. `tg` unifies all of this in a single CLI with Rich terminal output, following the **0 Magic — 100% Transparency** philosophy.

- **Bot API**: stateless, uses existing bot tokens, no auth needed
- **User API**: full MTProto access — read *any* conversation, send as yourself, manage contacts

## Install

```bash
# Clone
git clone git@github.com:KpihX/tg.git ~/Work/tools/tg
cd ~/Work/tools/tg

# Install (editable — live source, no reinstall on changes)
uv tool install --editable .

# Verify
tg --version
```

## Configuration

### Secrets (via bw-env / environment)

`tg` auto-discovers bots from `TELEGRAM_*_TOKEN` env vars — no config file needed for basic use.

```bash
# These are injected by bw-env from Bitwarden:
TELEGRAM_HOMELAB_TOKEN=...     # → alias "homelab"
TELEGRAM_UBUNTU_TOKEN=...      # → alias "ubuntu"
TELEGRAM_N8N_HOMELAB_TOKEN=... # → alias "n8n-homelab"
CHAT_ID=...                    # default recipient for tg send

# For tg user (Telethon):
TG_API_ID=12345                # from https://my.telegram.org
TG_API_HASH=abc123...          # from https://my.telegram.org
```

See `src/tg/.env.example` for the full template.

### Config file (optional)

```yaml
# ~/.config/tg/config.yaml
default_bot: homelab
default_chat: "YOUR_CHAT_ID"

bots:
  homelab:
    default_chat: "YOUR_CHAT_ID"
```

## Usage

### Bot API

```bash
# List all configured bots (live Telegram identity)
tg bots

# Bot status + webhook info
tg status
tg status --bot n8n-homelab

# Send a message (HTML supported)
tg send "Hello <b>world</b>"
tg send "Alert!" --to CHAT_ID --bot ubuntu

# Recent updates received by a bot
tg updates --limit 20
tg updates --bot homelab

# Chat / group info
tg chat info @mychannel
tg chat info -1001234567890 --bot homelab
tg chat admins @mygroup

# Webhook management
tg webhook get
tg webhook set https://example.com/webhook --bot n8n-homelab
tg webhook del --drop-pending

# Bot command list
tg commands get
tg commands set start "Start the bot"
```

### User API (Telethon — personal account)

```bash
# First-time setup (OTP — once only)
tg user setup
# → prompts for API ID, API Hash, phone number
# → sends OTP to your Telegram app

# Your identity
tg user me

# List conversations
tg user chats --limit 30
tg user chats --type group
tg user chats --type channel

# Read messages
tg user read @KpihX --limit 20
tg user read -1001234567890 --limit 50
tg user read @mychat --search "keyword"

# Send as yourself
tg user send @username "Hello!"
tg user send -1001234567890 "Group message" --reply-to 4242

# Edit / delete
tg user edit @username 4242 "Corrected text"
tg user delete @username 4242

# Contacts
tg user contacts
```

## Architecture

```
~/Work/tools/tg/
├── src/tg/
│   ├── cli.py          # Typer app — all commands
│   ├── config.py       # Config loading (env + YAML, @lru_cache)
│   ├── api.py          # Telegram Bot API wrapper (httpx, stateless)
│   ├── user.py         # Telethon user API (MTProto, async→sync bridge)
│   ├── display.py      # Rich display helpers
│   ├── config.yaml     # Bundled defaults (non-sensitive)
│   └── .env.example    # Secret template
├── tests/
├── pyproject.toml      # uv_build, Python 3.12+
├── CHANGELOG.md
└── TODO.md
```

## Security

- Bot tokens and API credentials **never hardcoded** — always injected via `bw-env` from Bitwarden
- Telethon session stored at `~/.config/tg/user.session` (SQLite, local only)
- Session file is covered by `backup_workstation.sh` (under `/home/kpihx/.config/`)
- `.env` files excluded from git via `.gitignore`

## License

MIT
