"""
Ultra-simple docstring helper for tg-proxy CLI.

Returns the docstring of a function with → output examples
auto-wrapped in meta+data for human/agent clarity.
Single source of truth: the docstrings themselves.
"""

import inspect
import json
import re
from collections.abc import Callable


def get_compact_help(func: Callable) -> str:
    """Return the docstring without the Examples section — for group overview."""
    doc = inspect.getdoc(func) or ""
    parts = re.split(r"(?i)^\s*Examples:\s*$", doc, flags=re.MULTILINE, maxsplit=1)
    return parts[0].strip()


def _wrap_output(line: str) -> str:
    """Wrap → {json} with meta+data. Leave text examples as-is."""
    m = re.match(r"^( *→\s*)(.*)", line)
    if not m:
        return line
    arrow = m.group(1)
    content = m.group(2).strip()
    try:
        data = json.loads(content)
        wrapped = json.dumps(
            {"meta": {"status": "ok", "comment": "", "edited": False}, "data": data},
            indent=2,
            default=str,
        )
        return f"{arrow}{wrapped}"
    except (json.JSONDecodeError, ValueError, TypeError):
        return line


def get_full_help(func: Callable) -> str:
    """Return the docstring with → examples wrapped in meta+data."""
    doc = inspect.getdoc(func) or ""
    lines = doc.split("\n")
    new_lines = [_wrap_output(line) for line in lines]
    return "\n".join(new_lines)
