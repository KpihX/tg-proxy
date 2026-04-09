# CHANGELOG — tg

## [0.2.0] — 2026-04-09

### Added
- [x] **Media & File Support** — download and send files via user or bot API
  - [x] `tg user download` — download media from a chat natively
  - [x] `tg user send --file` — attach a local file to messages
  - [x] `tg updates --download-media` — fetch bot updates and auto-download attachments
- [x] **Read & Actions** — interact with read receipts and chat actions
  - [x] `tg user mark-read` — mark all messages or individual chats as read
  - [x] `tg user status / tg bot-action` — broadcast typing/uploading states

## [0.1.0] — 2026-03-22

### Added
- [x] **Bot API layer** — auto-discovers all `TELEGRAM_*_TOKEN` bots from env
  - [x] `tg bots` — list configured bots with live Telegram identity
  - [x] `tg status` — bot info, capabilities, webhook status
  - [x] `tg send` — send message via bot (HTML supported)
  - [x] `tg updates` — fetch recent updates received by the bot
  - [x] `tg chat info/admins` — inspect chats and groups
  - [x] `tg webhook get/set/del` — manage bot webhooks
  - [x] `tg commands get/set` — manage bot command list
- [x] **User API layer** (Telethon MTProto — personal account, full access)
  - [x] `tg user setup` — first-time OTP auth, stores session
  - [x] `tg user me` — show account identity
  - [x] `tg user chats` — list all conversations with filter support
  - [x] `tg user read` — read messages from any chat/channel
  - [x] `tg user send` — send as yourself
  - [x] `tg user edit` / `delete` — message management
  - [x] `tg user contacts` — list contacts
- [x] Entity resolution for numeric chat IDs (Telethon `access_hash` cache fallback)
- [x] Rich terminal output (tables, panels, colors)
- [x] Editable install via `uv tool install --editable .`
