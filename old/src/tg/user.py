"""Telethon user-account layer — read/write personal Telegram conversations.

Session is stored at ~/.config/tg/user.session (Telethon SQLite).
API credentials (api_id + api_hash) come from:
  1. ~/.config/tg/config.yaml  → user.api_id / user.api_hash
  2. Env vars: TG_API_ID, TG_API_HASH
  3. Interactive prompt on first use (stored in config.yaml).

How to get API credentials:
  1. Go to https://my.telegram.org
  2. Log in → API development tools
  3. Create an app → copy api_id (integer) and api_hash (string)
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

SESSION_PATH = Path.home() / ".config" / "tg" / "user.session"
CONFIG_PATH = Path.home() / ".config" / "tg" / "config.yaml"


def _load_api_credentials() -> tuple[int, str]:
    """Load api_id and api_hash from config or env. Raises if missing."""
    # 1. env vars
    api_id_env = os.environ.get("TG_API_ID")
    api_hash_env = os.environ.get("TG_API_HASH")

    # 2. config file
    api_id_cfg = None
    api_hash_cfg = None
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f) or {}
        user_cfg = data.get("user", {})
        api_id_cfg = user_cfg.get("api_id")
        api_hash_cfg = user_cfg.get("api_hash")

    api_id = int(api_id_env or api_id_cfg or 0)
    api_hash = api_hash_env or api_hash_cfg or ""

    if not api_id or not api_hash:
        raise RuntimeError(
            "Telegram API credentials not found.\n"
            "Get them at https://my.telegram.org → API development tools\n"
            "Then run: tg user setup"
        )
    return api_id, api_hash


def _save_api_credentials(api_id: int, api_hash: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f) or {}
    data.setdefault("user", {})
    data["user"]["api_id"] = api_id
    data["user"]["api_hash"] = api_hash
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def _get_client():
    """Return a configured (not connected) Telethon client."""
    from telethon import TelegramClient  # lazy import
    api_id, api_hash = _load_api_credentials()
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    return TelegramClient(str(SESSION_PATH), api_id, api_hash)


def run(coro):
    """Run a coroutine synchronously (Telethon is async-native)."""
    return asyncio.run(coro)


# ── Setup / Login ─────────────────────────────────────────────────────────────

async def _interactive_setup(api_id: int, api_hash: str, phone: str) -> None:
    from telethon import TelegramClient
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(str(SESSION_PATH), api_id, api_hash)
    await client.start(phone=phone)
    me = await client.get_me()
    print(f"✓ Logged in as {me.first_name} (@{me.username})")
    await client.disconnect()


def setup(api_id: int, api_hash: str, phone: str) -> None:
    """First-time setup: store credentials and authenticate."""
    _save_api_credentials(api_id, api_hash)
    run(_interactive_setup(api_id, api_hash, phone))


# ── Me ────────────────────────────────────────────────────────────────────────

async def _get_me() -> dict:
    client = _get_client()
    async with client:
        me = await client.get_me()
        return {
            "id": me.id,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "username": me.username,
            "phone": me.phone,
            "verified": me.verified,
            "premium": getattr(me, "premium", False),
            "bot": me.bot,
        }


def get_me() -> dict:
    return run(_get_me())


# ── Chats / Dialogs ───────────────────────────────────────────────────────────

async def _list_dialogs(limit: int = 30, filter_type: Optional[str] = None) -> list[dict]:
    from telethon.tl.types import User, Chat, Channel
    client = _get_client()
    results = []
    async with client:
        async for dialog in client.iter_dialogs(limit=limit):
            entity = dialog.entity
            kind = "user" if isinstance(entity, User) else (
                "group" if isinstance(entity, Chat) else "channel"
            )
            if filter_type and kind != filter_type:
                continue
            results.append({
                "id": dialog.id,
                "name": dialog.name,
                "type": kind,
                "unread": dialog.unread_count,
                "pinned": dialog.pinned,
                "last_message": dialog.message.message[:60] if dialog.message and dialog.message.message else "",
                "date": dialog.date.strftime("%Y-%m-%d %H:%M") if dialog.date else "",
            })
    return results


def list_dialogs(limit: int = 30, filter_type: Optional[str] = None) -> list[dict]:
    return run(_list_dialogs(limit, filter_type))


# ── Messages ──────────────────────────────────────────────────────────────────

async def _resolve_entity(client, chat: str | int):
    """Resolve a chat to a Telethon entity, handling numeric IDs via dialog cache."""
    # Convert numeric strings to int
    if isinstance(chat, str) and chat.lstrip("-").isdigit():
        chat = int(chat)
    try:
        return await client.get_input_entity(chat)
    except ValueError:
        # Entity not in cache — populate cache by fetching dialogs then retry
        await client.get_dialogs()
        return await client.get_input_entity(chat)


async def _get_messages(chat: str | int, limit: int = 20, search: Optional[str] = None) -> list[dict]:
    client = _get_client()
    results = []
    async with client:
        entity = await _resolve_entity(client, chat)
        kwargs = {"limit": limit}
        if search:
            kwargs["search"] = search
        async for msg in client.iter_messages(entity, **kwargs):
            sender = ""
            if msg.sender:
                sender = getattr(msg.sender, "username", None) or getattr(msg.sender, "first_name", "?") or "?"
            results.append({
                "id": msg.id,
                "date": msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "",
                "sender": sender,
                "text": (msg.message or "") if msg.message else f"[{msg.media.__class__.__name__}]" if msg.media else "[empty]",
                "reply_to": msg.reply_to_msg_id,
                "pinned": msg.pinned if hasattr(msg, "pinned") else False,
            })
    return results


def get_messages(chat: str | int, limit: int = 20, search: Optional[str] = None) -> list[dict]:
    return run(_get_messages(chat, limit, search))


# ── Send ──────────────────────────────────────────────────────────────────────

async def _send_message(chat: str | int, text: str, reply_to: Optional[int] = None) -> dict:
    client = _get_client()
    async with client:
        entity = await _resolve_entity(client, chat)
        msg = await client.send_message(entity, text, reply_to=reply_to, parse_mode="html")
        return {"id": msg.id, "date": msg.date.strftime("%Y-%m-%d %H:%M")}


def send_message(chat: str | int, text: str, reply_to: Optional[int] = None) -> dict:
    return run(_send_message(chat, text, reply_to))


# ── Delete / Edit ─────────────────────────────────────────────────────────────

async def _delete_message(chat: str | int, message_id: int) -> None:
    client = _get_client()
    async with client:
        entity = await _resolve_entity(client, chat)
        await client.delete_messages(entity, [message_id])


def delete_message(chat: str | int, message_id: int) -> None:
    run(_delete_message(chat, message_id))


async def _delete_chat(chat: str | int) -> None:
    from telethon.tl.functions.channels import DeleteChannelRequest
    from telethon.tl.functions.messages import DeleteChatRequest
    from telethon.tl.types import Channel, Chat
    client = _get_client()
    async with client:
        entity = await client.get_entity(chat)
        if isinstance(entity, Channel):
            await client(DeleteChannelRequest(channel=entity))
        elif isinstance(entity, Chat):
            await client(DeleteChatRequest(chat_id=entity.id))
        else:
            # For users/DMs, there's no "delete chat" in the same way, but we can delete history
            await client.delete_dialog(entity)


def delete_chat(chat: str | int) -> None:
    run(_delete_chat(chat))


async def _edit_message(chat: str | int, message_id: int, text: str) -> None:
    client = _get_client()
    async with client:
        entity = await _resolve_entity(client, chat)
        await client.edit_message(entity, message_id, text, parse_mode="html")


def edit_message(chat: str | int, message_id: int, text: str) -> None:
    run(_edit_message(chat, message_id, text))


# ── Contacts ──────────────────────────────────────────────────────────────────

async def _list_contacts() -> list[dict]:
    from telethon.tl.functions.contacts import GetContactsRequest
    client = _get_client()
    async with client:
        result = await client(GetContactsRequest(hash=0))
        contacts = []
        for u in result.users:
            contacts.append({
                "id": u.id,
                "name": f"{u.first_name or ''} {u.last_name or ''}".strip(),
                "username": u.username or "",
                "phone": u.phone or "",
            })
        return contacts


def list_contacts() -> list[dict]:
    return run(_list_contacts())

# ── Extension: Download / Media / Read ────────────────────────────────────────

async def _download_media(chat: str | int, message_id: int, out: str) -> str:
    client = _get_client()
    async with client:
        entity = await _resolve_entity(client, chat)
        msg = await client.get_messages(entity, ids=message_id)
        if not msg or not msg.media:
            raise RuntimeError(f"Message {message_id} in {chat} contains no media.")
        path = await client.download_media(msg, file=out)
        if not path:
            raise RuntimeError("Download failed or aborted.")
        return path

def download_media(chat: str | int, message_id: int, out: str) -> str:
    return run(_download_media(chat, message_id, out))


async def _send_file(chat: str | int, file_path: str, caption: str | None = None, reply_to: int | None = None) -> dict:
    client = _get_client()
    async with client:
        entity = await _resolve_entity(client, chat)
        msg = await client.send_file(entity, file_path, caption=caption, reply_to=reply_to)
        return _format_message(msg)

def send_file(chat: str | int, file_path: str, caption: str | None = None, reply_to: int | None = None) -> dict:
    return run(_send_file(chat, file_path, caption, reply_to))


async def _mark_read(chat: str | int, max_id: int | None = None) -> None:
    client = _get_client()
    async with client:
        entity = await _resolve_entity(client, chat)
        await client.send_read_acknowledge(entity, max_id=max_id)

def mark_read(chat: str | int, max_id: int | None = None) -> None:
    run(_mark_read(chat, max_id))


async def _action(chat: str | int, action: str) -> None:
    client = _get_client()
    async with client:
        entity = await _resolve_entity(client, chat)
        async with client.action(entity, action):
            import asyncio
            await asyncio.sleep(0.5)

def send_action(chat: str | int, action: str) -> None:
    run(_action(chat, action))


def _format_message(msg) -> dict:
    return {
        "id": msg.id,
        "date": msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "",
    }


