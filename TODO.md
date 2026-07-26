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

## Remaining

- [ ] Implement `do raw` generic gateway (see IDEAS.md)
- [ ] Add `bot-set-photo` command
- [ ] Add `regex` option to `chat-read`
- [ ] Test `all_media: true` for chat-download batch download
- [ ] Validate `--output-file/-o` behavior for all do commands
- [ ] Add `folder-batch` command (add/remove chats without full replace)
