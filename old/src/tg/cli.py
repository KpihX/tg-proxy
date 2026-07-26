"""tg — Telegram CLI, like gh for Telegram.

Bot API commands (use bot tokens from TELEGRAM_*_TOKEN env vars):
  tg bots                                  List all configured bots
  tg status [--bot BOT]                    Bot info + webhook status
  tg send MSG [--to CHAT] [--bot BOT]      Send a message via bot
  tg updates [--bot BOT] [--limit N]       Get recent bot updates
  tg chat info CHAT_ID [--bot BOT]         Get chat/group info
  tg webhook get|set URL|del [--bot BOT]   Manage webhooks
  tg commands get|set CMD DESC [--bot BOT] Manage bot commands

User API commands (Telethon — personal account, full access):
  tg user setup                            First-time auth (phone OTP)
  tg user me                               Your Telegram identity
  tg user chats [--limit N] [--type TYPE]  List your conversations
  tg user read CHAT [--limit N] [--search] Read messages from a chat
  tg user send CHAT MSG [--reply-to ID]    Send as yourself
  tg user edit CHAT MSG_ID NEW_TEXT        Edit a sent message
  tg user delete CHAT MSG_ID               Delete a message
  tg user contacts                         List your contacts
"""

from __future__ import annotations

import sys
from typing import Annotated, Optional

import typer
from rich.console import Console

from tg import __version__
from tg.config import load_config, get_bot
from tg import api
from tg import display

app = typer.Typer(
    name="tg",
    help="Telegram CLI — like gh for Telegram. Manages your Telegram bots.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

webhook_app = typer.Typer(help="Manage bot webhooks.", no_args_is_help=True)
commands_app = typer.Typer(help="Manage bot commands.", no_args_is_help=True)
chat_app = typer.Typer(help="Inspect chats and groups.", no_args_is_help=True)

user_app = typer.Typer(help="User account commands (Telethon — personal Telegram access).", no_args_is_help=True)

app.add_typer(webhook_app, name="webhook")
app.add_typer(commands_app, name="commands")
app.add_typer(chat_app, name="chat")
app.add_typer(user_app, name="user")

console = Console()

BotOpt = Annotated[Optional[str], typer.Option("--bot", "-b", help="Bot alias (e.g. homelab, ubuntu). Default: auto.")]


def _abort(msg: str) -> None:
    display.error(msg)
    raise typer.Exit(1)


# ── tg bots ───────────────────────────────────────────────────────────────────

@app.command()
def bots() -> None:
    """List all configured bots with their Telegram identity."""
    cfg = load_config()
    if not cfg.bots:
        _abort("No bots configured. Set TELEGRAM_*_TOKEN environment variables.")

    resolved: dict[str, tuple] = {}
    for alias, bot_cfg in cfg.bots.items():
        try:
            me = api.get_me(bot_cfg.token)
            resolved[alias] = (bot_cfg, me)
        except Exception as e:
            display.error(f"[{alias}] {e}")

    if resolved:
        display.print_bots(resolved, cfg.default_bot)


# ── tg status ─────────────────────────────────────────────────────────────────

@app.command()
def status(bot: BotOpt = None) -> None:
    """Show bot identity, capabilities, and webhook status."""
    try:
        bot_cfg = get_bot(bot)
    except ValueError as e:
        _abort(str(e))

    try:
        me = api.get_me(bot_cfg.token)
        webhook = api.get_webhook_info(bot_cfg.token)
        display.print_bot_status(bot_cfg.alias, me, webhook)
    except Exception as e:
        _abort(str(e))


# ── tg send ───────────────────────────────────────────────────────────────────

@app.command()
def send(
    message: Annotated[str, typer.Argument(help="Message text (HTML supported).")],
    to: Annotated[Optional[str], typer.Option("--to", "-t", help="Chat ID or @username. Uses CHAT_ID env var if not set.")] = None,
    bot: BotOpt = None,
    reply_to: Annotated[Optional[int], typer.Option("--reply-to", help="Reply to message ID.")] = None,
    plain: Annotated[bool, typer.Option("--plain", help="Disable HTML parse mode.")] = False,
) -> None:
    """Send a message via a bot."""
    try:
        bot_cfg = get_bot(bot)
    except ValueError as e:
        _abort(str(e))

    cfg = load_config()
    chat_id = to or bot_cfg.default_chat or cfg.default_chat
    if not chat_id:
        _abort("No chat ID. Use --to CHAT_ID or set CHAT_ID env var.")

    try:
        result = api.send_message(
            bot_cfg.token,
            chat_id,
            message,
            parse_mode=None if plain else "HTML",
            reply_to=reply_to,
        )
        display.success(f"Sent via [{bot_cfg.alias}] → chat {chat_id} (msg_id: {result['message_id']})")
    except Exception as e:
        _abort(str(e))


# ── tg updates ────────────────────────────────────────────────────────────────

@app.command()
def updates(
    bot: BotOpt = None,
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max updates to fetch.")] = 20,
    download_media: Annotated[Optional[str], typer.Option("--download-media", help="Directory to download media files automatically.")] = None,
) -> None:
    """Fetch recent bot updates (messages received by the bot)."""
    try:
        bot_cfg = get_bot(bot)
    except ValueError as e:
        _abort(str(e))

    try:
        upds = api.get_updates(bot_cfg.token, limit=limit)
        display.print_updates(bot_cfg.alias, upds)
        if download_media and upds:
            from pathlib import Path
            import os
            out_dir = Path(download_media)
            out_dir.mkdir(parents=True, exist_ok=True)
            for raw_upd in upds:
                msg = raw_upd.get("message")
                if msg:
                    file_id = None
                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                    elif "document" in msg:
                        file_id = msg["document"]["file_id"]
                    
                    if file_id:
                        f_info = api.get_file(bot_cfg.token, file_id)
                        if "file_path" in f_info:
                            ext = os.path.splitext(f_info["file_path"])[1] or ".jpg"
                            dest = out_dir / f"{bot_cfg.alias}_{msg['message_id']}{ext}"
                            api.download_file(bot_cfg.token, f_info["file_path"], str(dest))
                            display.success(f"Downloaded media to {dest}")
    except Exception as e:
        _abort(str(e))


# ── tg chat ───────────────────────────────────────────────────────────────────

@chat_app.command("info")
def chat_info(
    chat_id: Annotated[str, typer.Argument(help="Chat ID or @username.")],
    bot: BotOpt = None,
    members: Annotated[bool, typer.Option("--members", help="Show member count.")] = True,
) -> None:
    """Get information about a chat, group, or channel."""
    try:
        bot_cfg = get_bot(bot)
    except ValueError as e:
        _abort(str(e))

    try:
        chat = api.get_chat(bot_cfg.token, chat_id)
        count = None
        if members and chat.get("type") in ("group", "supergroup", "channel"):
            count = api.get_chat_member_count(bot_cfg.token, chat_id)
        display.print_chat_info(chat, count)
    except Exception as e:
        _abort(str(e))


@chat_app.command("admins")
def chat_admins(
    chat_id: Annotated[str, typer.Argument(help="Chat ID or @username.")],
    bot: BotOpt = None,
) -> None:
    """List administrators of a group or channel."""
    try:
        bot_cfg = get_bot(bot)
    except ValueError as e:
        _abort(str(e))

    try:
        admins = api.get_chat_administrators(bot_cfg.token, chat_id)
        for a in admins:
            user = a.get("user", {})
            role = a.get("status", "?")
            name = user.get("username") or user.get("first_name") or "?"
            console.print(f"  [cyan]{role:15}[/cyan] @{name}")
    except Exception as e:
        _abort(str(e))


# ── tg webhook ────────────────────────────────────────────────────────────────

@webhook_app.command("get")
def webhook_get(bot: BotOpt = None) -> None:
    """Show current webhook configuration."""
    try:
        bot_cfg = get_bot(bot)
        wh = api.get_webhook_info(bot_cfg.token)
        display.print_webhook(bot_cfg.alias, wh)
    except Exception as e:
        _abort(str(e))


@webhook_app.command("set")
def webhook_set(
    url: Annotated[str, typer.Argument(help="HTTPS URL for the webhook.")],
    bot: BotOpt = None,
    max_connections: Annotated[int, typer.Option(help="Max simultaneous connections.")] = 40,
) -> None:
    """Set the webhook URL for a bot."""
    try:
        bot_cfg = get_bot(bot)
        api.set_webhook(bot_cfg.token, url, max_connections=max_connections)
        display.success(f"[{bot_cfg.alias}] Webhook set → {url}")
    except Exception as e:
        _abort(str(e))


@webhook_app.command("del")
def webhook_del(
    bot: BotOpt = None,
    drop_pending: Annotated[bool, typer.Option("--drop-pending", help="Drop pending updates.")] = False,
) -> None:
    """Delete the webhook for a bot (switches to polling mode)."""
    try:
        bot_cfg = get_bot(bot)
        api.delete_webhook(bot_cfg.token, drop_pending=drop_pending)
        display.success(f"[{bot_cfg.alias}] Webhook deleted.")
    except Exception as e:
        _abort(str(e))


# ── tg commands ───────────────────────────────────────────────────────────────

@commands_app.command("get")
def commands_get(bot: BotOpt = None) -> None:
    """List the commands registered for a bot."""
    try:
        bot_cfg = get_bot(bot)
        cmds = api.get_my_commands(bot_cfg.token)
        if not cmds:
            console.print(f"[dim]No commands set for [{bot_cfg.alias}][/dim]")
            return
        for cmd in cmds:
            console.print(f"  /{cmd['command']:20} {cmd['description']}")
    except Exception as e:
        _abort(str(e))


@commands_app.command("set")
def commands_set(
    command: Annotated[str, typer.Argument(help="Command name (without /).")],
    description: Annotated[str, typer.Argument(help="Command description.")],
    bot: BotOpt = None,
) -> None:
    """Add or replace a command for a bot (replaces the full command list)."""
    try:
        bot_cfg = get_bot(bot)
        # Merge with existing commands
        existing = api.get_my_commands(bot_cfg.token)
        existing_map = {c["command"]: c["description"] for c in existing}
        existing_map[command.lstrip("/")] = description
        new_list = [{"command": k, "description": v} for k, v in existing_map.items()]
        api.set_my_commands(bot_cfg.token, new_list)
        display.success(f"[{bot_cfg.alias}] /{command} → '{description}'")
    except Exception as e:
        _abort(str(e))


# ── tg user ───────────────────────────────────────────────────────────────────

@user_app.command("setup")
def user_setup(
    api_id: Annotated[int, typer.Option("--api-id", prompt="Telegram API ID (from my.telegram.org)", help="Your API ID.")],
    api_hash: Annotated[str, typer.Option("--api-hash", prompt="Telegram API Hash", help="Your API Hash.")],
    phone: Annotated[str, typer.Option("--phone", prompt="Phone number (e.g. +33600000000)", help="Your phone number.")],
) -> None:
    """First-time setup: store API credentials and authenticate via OTP.

    Get your API credentials at https://my.telegram.org → API development tools.
    """
    from tg import user as u
    try:
        u.setup(api_id, api_hash, phone)
        display.success("User session created. Run 'tg user me' to verify.")
    except Exception as e:
        _abort(str(e))


@user_app.command("me")
def user_me() -> None:
    """Show your Telegram account info."""
    from tg import user as u
    try:
        me = u.get_me()
        console.print(f"[bold cyan]ID:[/bold cyan]         {me['id']}")
        console.print(f"[bold cyan]Name:[/bold cyan]       {me['first_name']} {me.get('last_name') or ''}")
        console.print(f"[bold cyan]Username:[/bold cyan]   @{me.get('username') or '—'}")
        console.print(f"[bold cyan]Phone:[/bold cyan]      +{me.get('phone') or '—'}")
        console.print(f"[bold cyan]Premium:[/bold cyan]    {'✓' if me.get('premium') else '✗'}")
    except RuntimeError as e:
        _abort(str(e))


@user_app.command("chats")
def user_chats(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max dialogs to list.")] = 30,
    type_filter: Annotated[Optional[str], typer.Option("--type", "-t", help="Filter: user, group, channel.")] = None,
) -> None:
    """List your conversations (dialogs)."""
    from tg import user as u
    try:
        dialogs = u.list_dialogs(limit=limit, filter_type=type_filter)
        from rich.table import Table
        from rich import box
        table = Table(title="💬 Your Chats", box=box.SIMPLE_HEAD)
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Type")
        table.add_column("Unread", justify="right")
        table.add_column("Last Message", max_width=50)
        table.add_column("Date")
        for d in dialogs:
            pin = "📌 " if d["pinned"] else ""
            unread = f"[green]{d['unread']}[/green]" if d["unread"] else ""
            table.add_row(str(d["id"]), pin + d["name"], d["type"], unread, d["last_message"], d["date"])
        console.print(table)
    except RuntimeError as e:
        _abort(str(e))


@user_app.command("read")
def user_read(
    chat: Annotated[str, typer.Argument(help="Chat ID, @username, or phone number.")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Number of messages to fetch.")] = 20,
    search: Annotated[Optional[str], typer.Option("--search", "-s", help="Search query in messages.")] = None,
) -> None:
    """Read messages from a conversation."""
    from tg import user as u
    try:
        msgs = u.get_messages(chat, limit=limit, search=search)
        from rich.table import Table
        from rich import box
        title = f"📨 {chat}" + (f" (search: {search})" if search else "")
        table = Table(title=title, box=box.SIMPLE_HEAD, show_header=True)
        table.add_column("ID", style="dim")
        table.add_column("Date")
        table.add_column("From", style="cyan")
        table.add_column("Message", max_width=80)
        for m in reversed(msgs):
            table.add_row(str(m["id"]), m["date"], m["sender"], m["text"])
        console.print(table)
    except RuntimeError as e:
        _abort(str(e))


@user_app.command("send")
def user_send(
    chat: Annotated[str, typer.Argument(help="Chat ID, @username, or phone number.")],
    message: Annotated[Optional[str], typer.Argument(help="Message text/caption (HTML supported).")] = None,
    file: Annotated[Optional[str], typer.Option("--file", "-f", help="File to send.")] = None,
    reply_to: Annotated[Optional[int], typer.Option("--reply-to", help="Reply to message ID.")] = None,
) -> None:
    """Send a message as yourself (user account)."""
    from tg import user as u
    try:
        if file:
            result = u.send_file(chat, file_path=file, caption=message, reply_to=reply_to)
            display.success(f"File sent to {chat} (msg_id: {result['id']})")
        else:
            if not message:
                _abort("Missing message text.")
            result = u.send_message(chat, message, reply_to=reply_to)
            display.success(f"Sent to {chat} (msg_id: {result['id']}) at {result['date']}")
    except RuntimeError as e:
        _abort(str(e))


@user_app.command("edit")
def user_edit(
    chat: Annotated[str, typer.Argument(help="Chat ID or @username.")],
    message_id: Annotated[int, typer.Argument(help="ID of the message to edit.")],
    text: Annotated[str, typer.Argument(help="New message text.")],
) -> None:
    """Edit one of your sent messages."""
    from tg import user as u
    try:
        u.edit_message(chat, message_id, text)
        display.success(f"Message {message_id} edited.")
    except RuntimeError as e:
        _abort(str(e))


@user_app.command("delete")
def user_delete(
    chat: Annotated[str, typer.Argument(help="Chat ID or @username.")],
    message_id: Annotated[int, typer.Argument(help="ID of the message to delete.")],
) -> None:
    """Delete a message."""
    from tg import user as u
    try:
        u.delete_message(chat, message_id)
        display.success(f"Message {message_id} deleted.")
    except RuntimeError as e:
        _abort(str(e))


@user_app.command("delete-chat")
def user_delete_chat(
    chat: Annotated[str, typer.Argument(help="Chat ID or @username.")],
) -> None:
    """Delete a chat, group, or channel."""
    from tg import user as u
    try:
        u.delete_chat(chat)
        display.success(f"Chat {chat} deleted.")
    except RuntimeError as e:
        _abort(str(e))


@user_app.command("contacts")
def user_contacts() -> None:
    """List your Telegram contacts."""
    from tg import user as u
    try:
        contacts = u.list_contacts()
        if not contacts:
            console.print("[dim]No contacts found.[/dim]")
            return
        from rich.table import Table
        from rich import box
        table = Table(title="👥 Contacts", box=box.SIMPLE_HEAD)
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Username")
        table.add_column("Phone")
        for c in contacts:
            table.add_row(str(c["id"]), c["name"], f"@{c['username']}" if c["username"] else "—", c["phone"] or "—")
        console.print(table)
    except RuntimeError as e:
        _abort(str(e))


# ── version ───────────────────────────────────────────────────────────────────

@app.command()
def version() -> None:
    """Show tg version."""
    console.print(f"tg {__version__}")


if __name__ == "__main__":
    app()

@user_app.command("download")
def user_download(
    chat: Annotated[str, typer.Argument(help="Chat ID, @username, or phone number.")],
    message_id: Annotated[int, typer.Argument(help="Message ID.")],
    out: Annotated[str, typer.Option("--out", "-o", help="Output file path or directory.")]
) -> None:
    """Download media from a specific message."""
    from tg import user as u
    try:
        path = u.download_media(chat, message_id, out)
        display.success(f"Downloaded to {path}")
    except RuntimeError as e:
        import sys; sys.exit(f"Error: {e}")

@user_app.command("mark-read")
def user_mark_read(
    chat: Annotated[str, typer.Argument(help="Chat ID, @username, or phone number.")],
    max_id: Annotated[Optional[int], typer.Option("--max-id", help="Message ID up to which to mark as read.")] = None
) -> None:
    """Mark messages in a chat as read to clear phone notifications."""
    from tg import user as u
    try:
        u.mark_read(chat, max_id)
        display.success(f"Marked {chat} as read{(f' up to {max_id}' if max_id else '')}")
    except RuntimeError as e:
        import sys; sys.exit(f"Error: {e}")

@user_app.command("status")
def user_action(
    chat: Annotated[str, typer.Argument(help="Chat ID, @username, or phone number.")],
    action: Annotated[str, typer.Argument(help="Action type (typing, document, photo, etc).")] = "typing"
) -> None:
    """Send a chat action (typing, etc)."""
    from tg import user as u
    try:
        u.send_action(chat, action)
    except RuntimeError as e:
        import sys; sys.exit(f"Error: {e}")

@user_app.command("cleanup")
def user_cleanup(
    path: Annotated[str, typer.Option("--path", "-p", help="Directory to clean up.")] = "~/Downloads/tg/",
    force: Annotated[bool, typer.Option("--force", "-f", help="Force without confirmation")] = False
) -> None:
    """Clean up downloaded media files."""
    import os, shutil
    from pathlib import Path
    import typer
    
    target = Path(path).expanduser()
    if not target.exists():
        display.warning(f"Path does not exist: {target}")
        return
    if not target.is_dir():
        import sys; sys.exit(f"Error: {target} is not a directory.")
        
    if not force:
        confirm = typer.confirm(f"Are you sure you want to wipe contents of {target}?")
        if not confirm:
            display.info("Aborted.")
            return

    for item in target.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            display.error(f"Failed to delete {item}. Reason: {e}")
            
    display.success(f"Cleaned up media directory: {target}")

@user_app.command("cleanup")
def user_cleanup(
    path: Annotated[str, typer.Option("--path", "-p", help="Directory to clean up.")] = "~/Downloads/tg/",
    force: Annotated[bool, typer.Option("--force", "-f", help="Force without confirmation")] = False
) -> None:
    """Clean up downloaded media files."""
    import os, shutil
    from pathlib import Path
    import typer
    
    target = Path(path).expanduser()
    if not target.exists():
        display.warning(f"Path does not exist: {target}")
        return
    if not target.is_dir():
        import sys; sys.exit(f"Error: {target} is not a directory.")
        
    if not force:
        confirm = typer.confirm(f"Are you sure you want to wipe contents of {target}?")
        if not confirm:
            display.info("Aborted.")
            return

    for item in target.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            display.error(f"Failed to delete {item}. Reason: {e}")
            
    display.success(f"Cleaned up media directory: {target}")

@app.command("bot-action")
def bot_action(
    bot: BotOpt = None,
    to: Annotated[Optional[str], typer.Option("--to", "-t", help="Recipient Chat ID.")] = None,
    action: Annotated[str, typer.Argument(help="Action type (typing, upload_document, etc).")] = "typing"
) -> None:
    """Send a chat action as a bot (typing, uploading)."""
    try:
        bot_cfg = get_bot(bot)
        cfg = load_config()
        chat_id = to or bot_cfg.default_chat or cfg.default_chat
        
        if not chat_id:
            _abort("No chat ID. Use --to CHAT_ID or set default_chat.")
            
        api.send_chat_action(bot_cfg.token, chat_id, action)
        display.success(f"[{bot_cfg.alias}] Sent action '{action}' to {chat_id}")
    except Exception as e:
        import sys; sys.exit(f"Error: {e}")
