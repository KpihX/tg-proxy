# Changelog

## 1.1.0 (2026-07-26)

### Production hardening: type_hints, autosave refactor, dead code removal

- **`raw` command — type_hints now functional:** Wire `payload.type_hints` into mtproto handler (client.py:1648-1668) — wraps string params in Telethon TLObject types before passing to request constructor. Double-try pattern handles both value-arg types (`InputUser(id=123)`) and marker types (`InputPrivacyKeyStatusTimestamp()`).
- **Autosave dir extracted to constant:** `TG_PROXY_AUTOSAVE_DIR` at top of cli.py — both usages (execute + _write_and_display) now reference the constant.
- **Autosave naming `last_` removed:** Files now `{action}_{timestamp}.json` instead of `last_{action}.json` (both paths).
- **Dead code purged:** `autosave_output()` removed from display.py — was defined but never called, used old `last_` format.
- **Verified in production:** `help.getNearestDc` ✅ + `account.getPrivacy` with `InputPrivacyKeyStatusTimestamp` ✅ — 2 real tmux+HITL executions, both passed.
- **Cleaner imports:** `from datetime import datetime` moved to global imports (top of cli.py).

## 1.0.0 (2026-07-25)

### Major refactoring — complete rewrite as tg-proxy

- **Architecture:** Single binary with `do` (RPC) + `admin` namespaces (inspired by ts_proxy)
- **Config:** Single `.env` at `~/.config/tg-proxy/.env` — no more `config.yaml`, no more per-bot tokens
- **HITL:** 100% web UI for 7 methods: admin-setup, bot-token, bot-create, bot-delete, bot-send, bot-send-file, chat-send-file, **folder-delete**
- **Bot discovery:** `getAdminedBots` — list ALL owned bots without any token
- **RPC:** Pure JSON-RPC style with payload as inline JSON or file path
- **Output:** Unified `meta + data` format — JSON default, table via `--format/-f`
- **Doc system:** `doc.py` with structured docstrings + Pydantic schema injection into `--help`
- **Maximum privacy:** `bot-create` auto-disables groups and inline mode
- **All 22 commands docstrings have Parameters sections**
- **`folder-list` docstring now has Parameters** (was missing)

### Session 2026-07-26 — 15+ bugs fixed, 22 commands

#### New commands
- **`chat-delete`** — delete entire conversation via `client.delete_dialog()`
- **`chat-delete-messages`** — delete specific messages via `client.delete_messages()`
- **`bot-photo`** — download profile photo from any bot/user via Telethon
- **`folder-list`** — list Telegram chat folders with chats
- **`folder-set`** — create/update folders (UPSERT)
- **`folder-delete`** — delete folder by title (HITL)
- **`chat-move`** — move chat between folders

#### Enriched features
- **`chat-list` now shows `folders`** — cross-references Telegram dialog filters
- **`bot-info` now shows `photo_info`** — photo_id, dc_id, has_video, size

#### BotFather protocol
- **BF_NOTE** — mandatory note in ALL BotFather methods, ALL output paths (success, error, exception)
- **bot-delete fix:** `"Yes, delete it"` → `"Yes, I am totally sure."` — BotFather requires exact text
- **BotFather rate limit** — detected and handled gracefully ("too many attempts")
- **`/setuserpic` flow proven** — S25 bot got Ubuntu's profile photo via BotFather conversation

#### Folder management patterns
- `_title_str()` helper for `TextWithEntities` conversion
- `_peer_id()` helper for peer ID extraction
- `DialogFilterDefault` checks (system filters without `.id`)
- `DialogFilters.filters` property (5 occurrences)

#### Quality
- **All `except Exception:` → specific exceptions** — ZERO `# noqa`
- **6 pyright errors silenced with precise `# type: ignore[code]`** — only Telethon stub false positives
- **Makefile `||` removed** — real pyright errors now block pre-commit hook
- **`make check`:** 0 ruff, 0 pyright errors, 25/25 tests
- **git pre-commit hook installed** — runs `make check`
- **IDEAS.md created** — `do raw` generic gateway concept

#### Repositories renamed
- GitHub: `KpihX/tg` → `KpihX/tg-proxy`
- GitLab: `kpihx/tg` → `kpihx/tg-proxy`

### Major refactoring — complete rewrite as tg-proxy

- **Architecture:** Single binary with `do` (RPC) + `admin` namespaces (inspired by ts_proxy)
- **Config:** Single `.env` at `~/.config/tg-proxy/.env` — no more `config.yaml`, no more per-bot tokens
- **HITL:** 100% web UI for sensitive operations (bot-token, bot-create, bot-delete, bot-send, admin-setup)
- **Bot discovery:** `getAdminedBots` — list ALL owned bots without any token
- **RPC:** Pure JSON-RPC style with payload as inline JSON or file path
- **Output:** Unified `meta + data` format — JSON default, table via `--format/-f`
- **Doc system:** `doc.py` with structured docstrings + Pydantic schema injection into `--help`
- **Maximum privacy:** `bot-create` auto-disables groups and inline mode

### Removed / discontinued

- All `TELEGRAM_*_TOKEN` env vars — tokens retrieved from BotFather on demand (HITL)
- `config.yaml`, `config.py` — replaced by minimal `.env` loader
- Separate `cli.py` → unified single-app CLI
- `cmd-get/set`, `status`, `me`, `chat-info`, `chat-admins`, `admin contacts`
- Agent-specific files: COPILOT.md, GEMINI.md, CLAUDE.md, VIBE.md
- `.agent/` subfolder — AGENTS.md lives directly in the project root

### Old code

Previous `tg` (v0.3.0, uv-tool) source is preserved at `old/src/`.
