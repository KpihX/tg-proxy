# IDEAS — Future Directions for tg-proxy

---

## `do raw` — Generic Telegram Gateway

A generic `do raw` command that lets users execute ANY Telegram operation directly,
even if not covered by existing `do` commands.

### Concept

One command, three protocols, auto-HITL:

```bash
tg-proxy do raw '{
  "method": "messages.sendMessage",
  "params": {"peer": "@user", "message": "Hello"},
  "protocol": "mtproto"
}'
```

### Three Protocol Modes

| Protocol | Value | Mechanism |
|----------|-------|-----------|
| MTProto | `"mtproto"` | `client(functions.some.Request(**params))` with dynamic method resolution |
| Bot API | `"botapi"` | `POST https://api.telegram.org/bot{token}/{method}` with JSON params |
| BotFather | `"bf"` | Send text command to BotFather, return raw response |

### Key Features

- **Auto-HITL** via `@require_approval()` — every raw request is reviewed before sending
- **100% coverage** — any Telegram API method becomes instantly available
- **Protocol auto-detect** — infer protocol from method naming convention
- **Raw response** — returns Telegram's response as-is, no tg-proxy wrapping

### Design Notes

- Single `do` command, no new binary
- HITL catches type mistakes before sending
- Payload can be a file path like other `do` commands
- Perfect for prototyping new features before committing to a proper `do` command

---

## Archive / Done Ideas

*(None yet — this file is new)*
