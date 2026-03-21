"""Configuration loader — reads bot tokens from env + optional YAML override."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from functools import lru_cache
from typing import Optional

import yaml

CONFIG_PATH = Path.home() / ".config" / "tg" / "config.yaml"

# Maps env var suffix → friendly alias
# e.g. TELEGRAM_HOMELAB_TOKEN → "homelab"
_SUFFIX_RE = re.compile(r"^TELEGRAM_(.+)_TOKEN$")


@dataclass
class BotConfig:
    alias: str       # e.g. "homelab"
    token: str       # bot token
    default_chat: Optional[str] = None  # optional default chat_id


@dataclass
class TgConfig:
    bots: dict[str, BotConfig] = field(default_factory=dict)
    default_bot: Optional[str] = None
    default_chat: Optional[str] = None  # global CHAT_ID fallback


def _alias_from_var(var_name: str) -> str:
    """TELEGRAM_N8N_HOMELAB_TOKEN → 'n8n-homelab'"""
    m = _SUFFIX_RE.match(var_name)
    if not m:
        return var_name.lower()
    return m.group(1).lower().replace("_", "-")


@lru_cache(maxsize=1)
def load_config() -> TgConfig:
    cfg = TgConfig()

    # 1. Auto-discover bots from environment (TELEGRAM_*_TOKEN)
    for key, val in os.environ.items():
        if _SUFFIX_RE.match(key) and val:
            alias = _alias_from_var(key)
            cfg.bots[alias] = BotConfig(alias=alias, token=val)

    # 2. Global CHAT_ID fallback
    cfg.default_chat = os.environ.get("CHAT_ID")

    # 3. Load YAML override if present
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f) or {}

        cfg.default_bot = data.get("default_bot")
        cfg.default_chat = data.get("default_chat", cfg.default_chat)

        # Explicit bot entries (can override tokens or add extra bots)
        for alias, bot_data in data.get("bots", {}).items():
            token = bot_data.get("token") or os.environ.get(
                f"TELEGRAM_{alias.upper().replace('-', '_')}_TOKEN", ""
            )
            if token:
                cfg.bots[alias] = BotConfig(
                    alias=alias,
                    token=token,
                    default_chat=bot_data.get("default_chat"),
                )
            if bot_data.get("default", False):
                cfg.default_bot = alias

    # 4. Set default bot (first found if not specified)
    if not cfg.default_bot and cfg.bots:
        cfg.default_bot = next(iter(cfg.bots))

    return cfg


def get_bot(alias: Optional[str] = None) -> BotConfig:
    """Resolve bot by alias or return the default bot. Raises if not found."""
    cfg = load_config()
    target = alias or cfg.default_bot
    if not target:
        raise ValueError("No bots configured. Set TELEGRAM_*_TOKEN env vars.")
    if target not in cfg.bots:
        available = ", ".join(cfg.bots.keys()) or "none"
        raise ValueError(f"Bot '{target}' not found. Available: {available}")
    return cfg.bots[target]
