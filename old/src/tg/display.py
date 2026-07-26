"""Rich display helpers for tg CLI."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text

console = Console()
err_console = Console(stderr=True)


def _ts(unix: int | None) -> str:
    if not unix:
        return "—"
    return datetime.fromtimestamp(unix).strftime("%Y-%m-%d %H:%M")


def print_bots(bots: dict, default_bot: str | None) -> None:
    table = Table(title="🤖 Configured Bots", box=box.ROUNDED, show_header=True)
    table.add_column("Alias", style="bold cyan")
    table.add_column("Bot Name")
    table.add_column("Username")
    table.add_column("ID")
    table.add_column("Default", justify="center")

    for alias, (bot_cfg, me) in bots.items():
        is_default = "★" if alias == default_bot else ""
        table.add_row(
            alias,
            me.get("first_name", "?"),
            f"@{me.get('username', '?')}",
            str(me.get("id", "?")),
            f"[green]{is_default}[/green]" if is_default else "",
        )
    console.print(table)


def print_bot_status(alias: str, me: dict, webhook: dict) -> None:
    wh_url = webhook.get("url") or "[dim]none[/dim]"
    wh_pending = webhook.get("pending_update_count", 0)
    last_err = webhook.get("last_error_message", "")

    panel_content = (
        f"[bold]ID:[/bold]           {me.get('id')}\n"
        f"[bold]Name:[/bold]         {me.get('first_name')}\n"
        f"[bold]Username:[/bold]     @{me.get('username')}\n"
        f"[bold]Can join groups:[/bold]    {me.get('can_join_groups', False)}\n"
        f"[bold]Inline queries:[/bold]    {me.get('supports_inline_queries', False)}\n"
        f"\n[bold]Webhook URL:[/bold]  {wh_url}\n"
        f"[bold]Pending updates:[/bold]   {wh_pending}"
    )
    if last_err:
        panel_content += f"\n[red]Last error:[/red] {last_err}"

    console.print(Panel(panel_content, title=f"🤖 [{alias}]", border_style="cyan"))


def print_updates(alias: str, updates: list[dict]) -> None:
    if not updates:
        console.print(f"[dim]No pending updates for [{alias}][/dim]")
        return

    table = Table(
        title=f"📨 Updates — [{alias}]",
        box=box.SIMPLE_HEAD,
        show_header=True,
    )
    table.add_column("ID", style="dim")
    table.add_column("From")
    table.add_column("Chat")
    table.add_column("Type")
    table.add_column("Text", max_width=60)
    table.add_column("Time")

    for upd in updates:
        msg = upd.get("message") or upd.get("channel_post") or {}
        frm = msg.get("from") or {}
        chat = msg.get("chat") or {}
        sender = frm.get("username") or frm.get("first_name") or "?"
        chat_name = chat.get("title") or chat.get("username") or str(chat.get("id", "?"))
        msg_type = "channel" if upd.get("channel_post") else "message"
        text = (msg.get("text") or msg.get("caption") or "[media]")[:60]
        ts = _ts(msg.get("date"))
        table.add_row(str(upd["update_id"]), sender, chat_name, msg_type, text, ts)

    console.print(table)


def print_chat_info(chat: dict, member_count: int | None = None) -> None:
    lines = []
    for key in ("id", "type", "title", "username", "description", "invite_link"):
        val = chat.get(key)
        if val:
            lines.append(f"[bold]{key.replace('_', ' ').title()}:[/bold] {val}")
    if member_count is not None:
        lines.append(f"[bold]Members:[/bold] {member_count}")
    console.print(Panel("\n".join(lines), title="💬 Chat Info", border_style="blue"))


def print_webhook(alias: str, webhook: dict) -> None:
    url = webhook.get("url") or "[dim]not set[/dim]"
    console.print(f"[bold cyan][{alias}][/bold cyan] Webhook: {url}")
    if webhook.get("pending_update_count"):
        console.print(f"  Pending updates: {webhook['pending_update_count']}")
    if webhook.get("last_error_message"):
        console.print(f"  [red]Last error:[/red] {webhook['last_error_message']}")
    if webhook.get("last_error_date"):
        console.print(f"  [red]At:[/red] {_ts(webhook['last_error_date'])}")


def success(msg: str) -> None:
    console.print(f"[green]✓[/green] {msg}")


def error(msg: str) -> None:
    err_console.print(f"[red]✗[/red] {msg}")
