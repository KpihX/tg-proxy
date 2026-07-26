# tg-proxy — Architecture Contract (v2)

> **Status:** ✅ STABLE — Refactoring complete. `tg` (v0.3.0) → `tg-proxy` (single binary, namespaced CLI: `do`/`admin`, MTProto-first, minimal config)

---

## Mantras

- **0 Hardcoding · 100% Flexibility:** No hardcoded tokens, no config.yaml, no per-bot env vars.
- **0 Magic · 100% Transparency:** Every API call is explicit, every secret is loaded from `.env` or retrieved at runtime.
- **0 Trust · 100% Control:** All credentials are in `.env` (gitignored). The user controls what's exposed.

---

## New Design — Single Binary, Namespaced CLI (VALIDATED ✅)

**ONE binary** with TWO sub-command groups (inspired by `ts_proxy`):

```
tg-proxy do <action> [payload|file] [--meta-options]     # RPC style — flat actions, JSON payload (inline or file)
tg-proxy admin <action>                                   # Admin — setup (HITL), status, contacts (ALWAYS JSON)
```

### `tg-proxy admin` — Admin (Telethon, ALWAYS JSON to stdout — hardcoded, no --format)

| Command | Role | Output | HITL | Backend |
|---------|------|--------|------|---------|
| `tg-proxy admin setup` | First-time auth — web form in browser (API ID + Hash + Phone) | Interactive (web) | ✅ HITL | Telethon |
| `tg-proxy admin status` | Your identity (id, name, username, phone, premium) | JSON | ❌ | Telethon |

### `tg-proxy do` — RPC Actions (JSON default, can switch to table via `--format/-f`)

**Meta options (ONLY for `do`, every `--` has its `-`):**
- `--output-file <path>` / `-o <path>` — redirect output (path required)
- `--format json|table` / `-f json|table` — display format (default: json)
- `--help` / `-h` — show help with full docstring + schema
- Payload (positional): inline JSON `'{"key":"val"}'` or file path `./payload.json`

**Output format — EVERY response has a `meta` section:**

```json
{
  "meta": {
    "status": "ok" | "rejected" | "error",
    "comment": "user comment or empty",
    "edited": false
  },
  "data": { ... }  // actual result
}
```

If HITL was involved, `meta.comment` contains the user's comment (empty if none), `meta.edited` is true if the user modified the payload, and `meta.status` is "approved", "rejected", or "ok".

**Pre-check (ALL `do` commands):** `~/.config/tg-proxy/.env` must exist and be valid. Checked **once** at the start of any `do` command. `bot-token` does NOT check (it writes to this file).

**Actions — FLAT, ONE level after `do`. Pure RPC. Ultra-simple.**

| Action | Operation | HITL | Backend | Notes |
|--------|-----------|------|---------|-------|
| `tg-proxy do bot-list [payload]` | List ALL owned bots | ❌ | MTProto | `{"filter":"all"}` optional |
| `tg-proxy do bot-info [payload]` | Details for one or MULTIPLE bots | ❌ | MTProto | `{"bots":["@bot1","@bot2"]}` |
| `tg-proxy do bot-token [payload]` | ⭐ Get token(s) — **NO meta options, writes to .env** | ✅ HITL | Telethon | `{"bots":["@bot1","@bot2"]}` — ONLY accepts `--help/-h`. Rejects `--output-file`/`--format` with error. **Appends** to `~/.config/tg-proxy/.env` in `BOT_USERNAME_UPPER=token` format |
| `tg-proxy do bot-create [payload]` | Create ONE or MULTIPLE bots at once with **MAX PRIVACY** (groups disabled, inline disabled) | ✅ HITL | Telethon | `{"bots":[{"name":"Bot1","username":"bot1"},{"name":"Bot2","username":"bot2"}]}` — BotFather commands automated: `/setjoingroups Disable`, `/setinline Disable` |
| `tg-proxy do bot-delete [payload]` | Delete ONE or MULTIPLE bots | ✅ HITL | Telethon | `{"bots":["@bot1","bot_id2"]}` |
| `tg-proxy do bot-send [payload]` | Send message AS a bot (to ME always) | ✅ HITL | Bot API | `{"bot":"@bot","message":"Hello"}` |
| `tg-proxy do bot-send-file [payload]` | Send message + list of files AS a bot | ✅ HITL | Bot API | `{"bot":"@bot","message":"See","files":["/a.pdf","/b.pdf"]}` |
| `tg-proxy do chat-list [payload]` | List conversations | ❌ | Telethon | `{"type":"user","limit":30}` |
| `tg-proxy do chat-read [payload]` | Read messages from a chat | ❌ | Telethon | `{"chat":93372553,"limit":5}` |
| `tg-proxy do chat-send [payload]` | Send message as YOU to ANYONE (contact, bot, BotFather) | ❌ | Telethon | `{"to":"@KpihX","message":"Hello"}` |
| `tg-proxy do chat-send-file [payload]` | Send message + list of files as YOU to ANYONE | ❌ | Telethon | `{"to":"@KpihX","message":"See","files":["/a.pdf","/b.pdf"]}` |
| `tg-proxy do updates [payload]` | Read bot inbox messages | ❌ | Bot API | `{"bot":"@bot","limit":10}` |
| `tg-proxy do webhook-get [payload]` | Show webhook config | ❌ | Bot API | `{"bot":"@bot"}` |
| `tg-proxy do chat-download [payload]` | Download media files from a chat by message_id(s) | ❌ | Telethon | `{"chat":"@chat","message_ids":[42,43],"out":"/tmp/"}` — downloads each file to the output directory |
| `tg-proxy do webhook-set [payload]` | Set webhook URL | ❌ | Bot API | `{"bot":"@bot","url":"https://..."}` — ⚠️ **Output includes YELLOW WARNING** reminding to filter by `from.id` in the webhook handler |
| `tg-proxy do webhook-del [payload]` | Delete webhook | ❌ | Bot API | `{"bot":"@bot","drop_pending":true}` |

**REMOVED** (not necessary): `cmd-get`, `cmd-set` (handled by BotFather), `status` (bot-info covers it), `me` (admin status covers it), `chat-info`, `chat-admins`, `admin contacts`.

---

## Config — One `.env` at `~/.config/tg-proxy/.env`

Created by `tg-proxy admin setup` (HITL required). Written to `~/.config/tg-proxy/.env`:

```env
TG_API_ID=32750118
TG_API_HASH=df796e5e2c4f045ae51eba5de68335f7
```

**No `config.yaml`.** **No per-bot `TELEGRAM_*_TOKEN`.** **No cache.** **No magic.**

- `TG_API_ID` and `TG_API_HASH` are the ONLY needed secrets.
- Bot tokens are retrieved from BotFather on demand via HITL (not cached).
- `bot-token` writes tokens to a `.env` file via `--output-file/-o` (file MUST end in `.env`).

---

## Architecture

```
tg-proxy
   │
   ├── do <action> [payload|file] [--meta]   # RPC — Bot API + MTProto + Telethon
   └── admin <action>                        # Always JSON — Telethon + MTProto
       │
       ▼
┌──────────────────────────────┐
│  src/tg/                     │
│  ├── cli.py                  │  ONE Typer app: `do` + `admin` sub-typers
│  ├── client.py               │  TgClient — Telethon + MTProto + Bot API
│  ├── models.py               │  Pydantic models (ts_proxy style)
│  ├── display.py              │  Rich output helpers
│  ├── config.py               │  ~/.config/tg-proxy/.env loader
│  ├── logger.py               │  Rotating file logger (ts_proxy)
│  ├── exceptions.py           │  Base exception (ts_proxy)
│  ├── doc.py                  │  Dynamic --help injection (ts_proxy)
│  └── hitl.py                 │  Web UI for HITL (adapted ts_proxy)
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  ~/.config/tg-proxy/.env     │  TG_API_ID + TG_API_HASH
│  ~/.config/tg/user.session   │  Telethon session
└──────────────────────────────┘
```

### Doc system (ts_proxy doc.py equivalent)

Each `TgClient` method has a **structured docstring** with mandatory sections:

```
Description of what this method does.
More detail about behavior, edge cases, and limitations.

Parameters:
    - param_name (type): Description.

Examples:
    - tg-proxy do bot-send '{"bot":"@bot","message":"Hello"}'
    - tg-proxy do bot-send ./payload.json
    - tg-proxy do bot-send '{"bot":"@bot","message":"Hi"}' -o result.json -f table
```

`doc.py` extracts this at import time and injects it into Typer's `command.help` and `command.short_help` via `apply_dynamic_docs()` (ts_proxy pattern). The JSON schema from Pydantic models appears inline in `--help`.

**Result:** `tg-proxy do bot-send --help` shows full docstring + exact payload schema — both **human-readable** and **agent-parseable**.

### Discovery flow (no cache, no magic)

```
1. tg-proxy do bot-list
   └─ client(functions.bots.GetAdminedBotsRequest())
      └─ 13 bots returned (ID, @username, name, photo, version)

2. tg-proxy do bot-token '{"bots":["@bot1","@bot2"]}' -o ~/.config/tg-proxy/.env
   └─ ⚠️ HITL — web UI opens, you approve
      └─ Telethon: send BotFather "/token"
      └─ Telethon: send BotFather "@bot1"
      └─ Parse response → BOT1_TOKEN=xxx
      └─ Repeat for @bot2
      └─ Write to output file (must be .env):
           BOT_USERNAME_UPPER=token
           BOT2_UPPER=token

3. tg-proxy do bot-send '{"bot":"@bot1","message":"Hello"}'
   └─ ⚠️ HITL — web UI shows message, you edit + approve
      └─ Client calls BotFather for token
      └─ Client sends via Bot API
```

---

## Files to Create / Delete (VALIDATED ✅)

### DELETE
| File | Reason |
|------|--------|
| `src/tg/config.py` ❌ | Replaced by new minimal config |
| `src/tg/config.yaml` ❌ | Credentials + bots moved to `.env` and runtime API |
| `src/tg/.env.example` ❌ | Rewritten (only TG_API_ID + TG_API_HASH) |
| `src/tg/api.py` ❌ | Replaced by client.py |
| `src/tg/user.py` ❌ | Integrated into client.py |
| `src/tg/cli.py` ❌ | Rewritten as namespaced single CLI |

### CREATE / REWRITE
| File | Role |
|------|------|
| `src/tg/__init__.py` | Version bump → 1.0.0 |
| `src/tg/cli.py` | **ONE** Typer app with `do` + `admin` sub-typers |
| `src/tg/client.py` | **TgClient** — Telethon + MTProto + Bot API (centralized) |
| `src/tg/models.py` | Pydantic models (ts_proxy style) |
| `src/tg/config.py` | Minimal `.env` loader (dotenv or manual) |
| `src/tg/display.py` | 🟢 Gardé (Rich helpers) |
| `src/tg/logger.py` | 🆕 Rotating file logger (ts_proxy style) |
| `src/tg/exceptions.py` | 🆕 Base exception class (ts_proxy style) |
| `src/tg/doc.py` | 🆕 Dynamic `--help` injection (ts_proxy style) |
| `pyproject.toml` | Single entry point: `tg-proxy = "tg.cli:app"` |
| `.env.example` | Only: `TG_API_ID=`, `TG_API_HASH=` |

### ADD (infrastructure — adapted from ts_proxy)
| File | Source |
|------|--------|
| `Makefile` | ts_proxy |
| `Dockerfile` | ts_proxy |
| `docker-compose.yml` | ts_proxy |
| `.gitlab-ci.yml` | ts_proxy |
| `.gitignore` | ts_proxy |
| `.dockerignore` | ts_proxy |
| `scripts/install.sh` | ts_proxy |
| `scripts/uninstall.sh` | ts_proxy |
| `scripts/audit_infra.py` | ts_proxy |
| `CHANGELOG.md` | Standard |
| `README.md` | Updated |
| `TODO.md` | Pending work |

---

## Makefile Targets (inspired by ts_proxy)

| Target | Action |
|--------|--------|
| `check` | ruff check → ruff format → py_compile → pyright → pytest |
| `uv-install` | `uv tool install . --force` |
| `uv-link` | `uv tool install --editable . --force` |
| `uv-purge` | `uv tool uninstall tg` |
| `uv-build` | `uv build` |
| `uv-publish` | `uv publish` |
| `git-push` | Push to gitlab + github |
| `git-install-hooks` | Pre-commit: `make check` |
| `release` | check → git-push → uv-publish → docker-publish |
| `docker-build` | Build image |
| `docker-publish` | Push image |
| `docker-logs` | Container logs |

---

## HITL Design — 100% Web UI

**Human-in-the-Loop is REQUIRED for sensitive operations.** The HITL system is:

- **100% Web UI** — no TUI fallback, no passphrase, no tmux requirement
- On HITL command, a local web server starts on port 1143
- Browser auto-opens with the review page
- The page shows: action name, payload (editable), comment field
- User can: edit payload, add comment, approve, or reject
- Output file/stream prints the result with `meta` section

**HITL flow:**
```
1. User/Agent runs: tg-proxy do bot-send '{"bot":"@bot","message":"Hello"}'
2. HITL server starts on http://127.0.0.1:1143/review?id=xxx
3. Browser opens (or user clicks URL printed to stdout)
4. Page shows:
   ┌────────────────────────────────┐
   │  tg-proxy — HITL Review        │
   │                                │
   │  Action: bot-send              │
   │                                │
   │  Payload (editable):      │
   │  ┌────────────────────────┐    │
   │  │ {"bot":"@bot",          │    │
   │  │  "message":"Hello"}     │    │
   │  └────────────────────────┘    │
   │                                │
   │  Comment: [______________]     │
   │                                │
   │  [✅ Approve]  [❌ Reject]     │
   └────────────────────────────────┘
5. User edits (if needed), adds comment, approves/rejects
6. Output:
   {
     "meta": {"status":"approved","comment":"LGTM","edited":false},
     "data": {"message_id":42,"chat":"@bot"}
   }
```

**HITL operations:** `admin setup`, `bot-token`, `bot-create`, `bot-delete`, `bot-send`, `bot-send-file`.

**No HITL (read-only):** `bot-list`, `bot-info`, `chat-list`, `chat-read`, `updates`, `webhook-get`, `webhook-set`, `webhook-del`.

**Rationale:** NOT needed anywhere. The web UI comment is optional.

**Exception:** `tg-proxy admin bot create` via BotFather could benefit from a `--confirm` flag, but inline typer prompt is sufficient.

---

## Status

- See `CHANGELOG.md` for version history.
- See `TODO.md` for pending work.
- See `README.md` for user-facing documentation.

*Architecture contract established 2026-07-25 during v2 redesign session.*
