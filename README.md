# tg — Telegram CLI

Like `gh` for Telegram. Manage your bots and conversations from the terminal.

## Install

```bash
uv tool install --editable ~/Work/tools/tg
```

## Usage

```bash
tg bots                        # list all configured bots
tg status [--bot homelab]      # bot info + webhook
tg send "hello" --to CHAT_ID   # send a message
tg updates [--bot ubuntu]      # get recent updates
tg chat info CHAT_ID           # get chat info
tg webhook get                 # show webhook URL
tg webhook set https://...     # set webhook
tg webhook del                 # delete webhook
tg commands get                # list bot commands
tg commands set start "Start the bot"
```

## Configuration

Bot tokens are auto-discovered from env vars matching `TELEGRAM_*_TOKEN`.

| Env var | Auto alias |
|---------|-----------|
| `TELEGRAM_HOMELAB_TOKEN` | `homelab` |
| `TELEGRAM_UBUNTU_TOKEN` | `ubuntu` |
| `TELEGRAM_N8N_HOMELAB_TOKEN` | `n8n-homelab` |

Optional config file at `~/.config/tg/config.yaml`:

```yaml
default_bot: homelab
default_chat: "YOUR_CHAT_ID"
bots:
  homelab:
    default_chat: "YOUR_CHAT_ID"
```
