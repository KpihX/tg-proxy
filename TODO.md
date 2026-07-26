# TODO

## ✅ DONE (this session)

- [x] Verify `bot-info` works with actual getAdminedBots data
- [x] Test `bot-token` end-to-end with HITL
- [x] Implement HITL for `bot_create`, `bot_delete`, `bot_send`, `bot_send_file`, `folder_delete`
- [x] Add tests for `doc.py` (docstring parsing + schema)
- [x] Test `chat-download` with real media files
- [x] Verify all JSON output formats match the `meta` + `data` contract
- [x] Implement `bot-photo` download command
- [x] Add folder management (folder-list, folder-set, folder-delete, chat-move)
- [x] Add chat-delete, chat-delete-messages
- [x] Fix BotFather confirmation text ("Yes, I am totally sure.")
- [x] Handle BotFather rate limit gracefully
- [x] Add BF_NOTE to all BotFather methods (all output paths)
- [x] Fix all `except Exception:` → specific exceptions (ZERO `# noqa`)
- [x] Document all 22 commands with Parameters sections
- [x] Enrich `chat-list` with `folders` field
- [x] Enrich `bot-info` with `photo_info` field
- [x] Create IDEAS.md with `do raw` concept
- [x] Install git pre-commit hook
- [x] Remove Makefile `||` — pyright now blocks real errors
- [x] Silence 6 Telethon stub false positives with precise `# type: ignore[code]`
- [x] Rename repos: gh + glab → `tg-proxy`
- [x] 13/13 bot tokens stored in `.env`
- [x] Full BotFather protocol proven (create, token, delete, setuserpic)
- [x] **Implement `do raw` generic gateway** (see IDEAS.md — done 2026-07-26 session)
- [x] **Wire `type_hints` into mtproto handler** — client.py:1648-1668 double-try pattern for TLObject params
- [x] **Extract autosave dir to constant** — `TG_PROXY_AUTOSAVE_DIR` in cli.py
- [x] **Fix autosave naming** — `last_` → `{action}_{timestamp}.json` (both usages)
- [x] **Delete dead `autosave_output()`** from display.py (defined but never called)
- [x] **Verified in production:** `help.getNearestDc` ✅ + `account.getPrivacy` with `InputPrivacyKeyStatusTimestamp` ✅

## Remaining

*(All remaining items moved to reference memory — IDEAS.md merged into CHANGELOG + TODO Done. tg-proxy v1.0.0 core stable.)*
