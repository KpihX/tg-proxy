"""Telegram Bot API wrapper — thin, synchronous, httpx-based."""

from __future__ import annotations

import httpx
from typing import Any, Optional

BASE = "https://api.telegram.org/bot{token}/{method}"
TIMEOUT = 15.0


def _call(token: str, method: str, **params: Any) -> dict:
    """Call a Telegram Bot API method. Raises on error."""
    url = BASE.format(token=token, method=method)
    # Remove None params
    payload = {k: v for k, v in params.items() if v is not None}
    resp = httpx.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', data)}")
    return data["result"]


# ── Bot identity ──────────────────────────────────────────────────────────────

def get_me(token: str) -> dict:
    return _call(token, "getMe")


def get_webhook_info(token: str) -> dict:
    return _call(token, "getWebhookInfo")


def set_webhook(token: str, url: str, **kwargs) -> dict:
    return _call(token, "setWebhook", url=url, **kwargs)


def delete_webhook(token: str, drop_pending: bool = False) -> dict:
    return _call(token, "deleteWebhook", drop_pending_updates=drop_pending)


# ── Messages ──────────────────────────────────────────────────────────────────

def send_message(
    token: str,
    chat_id: str | int,
    text: str,
    parse_mode: Optional[str] = "HTML",
    reply_to: Optional[int] = None,
) -> dict:
    return _call(
        token, "sendMessage",
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        reply_to_message_id=reply_to,
    )


def send_photo(token: str, chat_id: str | int, photo: str, caption: Optional[str] = None) -> dict:
    return _call(token, "sendPhoto", chat_id=chat_id, photo=photo, caption=caption)


def send_document(token: str, chat_id: str | int, document: str, caption: Optional[str] = None) -> dict:
    return _call(token, "sendDocument", chat_id=chat_id, document=document, caption=caption)


def delete_message(token: str, chat_id: str | int, message_id: int) -> dict:
    return _call(token, "deleteMessage", chat_id=chat_id, message_id=message_id)


def pin_message(token: str, chat_id: str | int, message_id: int) -> dict:
    return _call(token, "pinChatMessage", chat_id=chat_id, message_id=message_id)


# ── Updates & chat history ────────────────────────────────────────────────────

def get_updates(token: str, offset: Optional[int] = None, limit: int = 20) -> list[dict]:
    return _call(token, "getUpdates", offset=offset, limit=limit, timeout=0)


def get_chat(token: str, chat_id: str | int) -> dict:
    return _call(token, "getChat", chat_id=chat_id)


def get_chat_member_count(token: str, chat_id: str | int) -> int:
    return _call(token, "getChatMemberCount", chat_id=chat_id)


def get_chat_administrators(token: str, chat_id: str | int) -> list[dict]:
    return _call(token, "getChatAdministrators", chat_id=chat_id)


# ── Bot commands ──────────────────────────────────────────────────────────────

def get_my_commands(token: str) -> list[dict]:
    return _call(token, "getMyCommands")


def set_my_commands(token: str, commands: list[dict]) -> dict:
    return _call(token, "setMyCommands", commands=commands)
