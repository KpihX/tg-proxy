"""
tg-proxy: Telegram administrative proxy — RPC CLI for bot and user management.

Config: ~/.config/tg-proxy/.env (TG_API_ID, TG_API_HASH, *BOT_TOKENS)
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("tg-proxy")
except PackageNotFoundError:
    __version__ = "0.0.0"
