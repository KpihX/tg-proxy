"""
Rich output helpers for tg-proxy.
"""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_json(data: Any):
    """Print data as formatted JSON."""
    console.print_json(data=data)


def print_table(data: list[dict] | dict):
    """Print data as a Rich table."""
    if isinstance(data, dict):
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Key", style="dim")
        table.add_column("Value")
        for k, v in data.items():
            table.add_row(str(k), str(v))
        console.print(table)
    elif isinstance(data, list) and data:
        keys = list(data[0].keys()) if isinstance(data[0], dict) else ["Value"]
        table = Table(show_header=True, header_style="bold cyan")
        for k in keys:
            table.add_column(str(k))
        for item in data:
            if isinstance(item, dict):
                table.add_row(*[str(item.get(k, "")) for k in keys])
            else:
                table.add_row(str(item))
        console.print(table)
    else:
        console.print(data)


def print_warning(message: str):
    """Print a yellow warning."""
    console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")


def print_error(message: str):
    """Print a red error."""
    console.print(f"[bold red]❌ {message}[/bold red]")


def print_success(message: str):
    """Print a green success."""
    console.print(f"[bold green]✅ {message}[/bold green]")


def print_meta(meta: dict):
    """Print the meta section of an output."""
    status = meta.get("status", "ok")
    color = "green" if status in ("ok", "approved") else "red"
    console.print(
        Panel(
            f"[bold {color}]Status:[/] {status}\n"
            f"[bold]Comment:[/] {meta.get('comment', '') or '(empty)'}\n"
            f"[bold]Edited:[/] {'✅ Yes' if meta.get('edited') else '❌ No'}",
            title="[bold blue]Output Meta[/]",
            border_style=color,
        )
    )
