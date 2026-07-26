"""
Minimal .env config loader for tg-proxy.

Reads ~/.config/tg-proxy/.env and validates TG_API_ID and TG_API_HASH.
"""

import os
from pathlib import Path

from .exceptions import TgProxyError

CONFIG_DIR = Path.home() / ".config" / "tg-proxy"
ENV_PATH = CONFIG_DIR / ".env"


def ensure_env() -> None:
    """Check that ~/.config/tg-proxy/.env exists and has required keys."""
    if not ENV_PATH.exists():
        raise TgProxyError(
            f"Config file not found at {ENV_PATH}. Run 'tg-proxy admin setup' first."
        )
    load_env()
    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    if not api_id or not api_hash:
        raise TgProxyError(
            f"{ENV_PATH} is missing TG_API_ID or TG_API_HASH. "
            "Run 'tg-proxy admin setup' to configure."
        )


def load_env() -> dict[str, str]:
    """Load .env file into os.environ and return as dict."""
    if not ENV_PATH.exists():
        return {}
    result: dict[str, str] = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip()
                os.environ.setdefault(key, val)
                result[key] = val
    return result


def append_env(key: str, value: str) -> None:
    """Append a key=value line to the .env file."""
    with open(ENV_PATH, "a") as f:
        f.write(f"\n{key}={value}\n")


def get_api_credentials() -> tuple[str, str]:
    """Return (api_id, api_hash) from the environment."""
    api_id = os.environ.get("TG_API_ID", "")
    api_hash = os.environ.get("TG_API_HASH", "")
    return api_id, api_hash
