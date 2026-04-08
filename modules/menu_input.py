"""Professional menu system using Rich rendering and raw terminal input.

Replaces questionary with a clean arrow-key TUI that renders correctly
in all terminals without ANSI escape code artifacts.
"""

import os
import sys
import select
import termios
import tty
from typing import Any, Callable, Dict, List

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text


# ---------------------------------------------------------------------------
# Low-level key reading
# ---------------------------------------------------------------------------

def _read_key(timeout: float | None = None) -> str:
    """Read a single keypress from stdin."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        if timeout is not None:
            ready, _, _ = select.select([fd], [], [], timeout)
            if not ready:
                return "NO_INPUT"
        ch = os.read(fd, 1).decode(errors="ignore")
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == "\x1b":
            parts: list[str] = []
            while True:
                r, _, _ = select.select([fd], [], [], 0.05)
                if not r:
                    break
                c = os.read(fd, 1).decode(errors="ignore")
                if not c:
                    break
                parts.append(c)
                if c.isalpha() or c == "~":
                    break
            seq = "".join(parts)
            if seq in ("[A", "OA"):
                return "UP"
            if seq in ("[B", "OB"):
                return "DOWN"
            return "BACK"
        if ch in ("k", "K"):
            return "UP"
        if ch in ("j", "J"):
            return "DOWN"
        if ch in ("b", "B"):
            return "BACK"
        if ch in ("q", "Q"):
            return "QUIT"
        return "UNKNOWN"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _term_size() -> tuple[int, int]:
    """Return (columns, lines)."""
    sz = os.get_terminal_size()
    return sz.columns, sz.lines


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

BRAND = "bold white on color(236)"
ACCENT = "bold color(141)"
BORDER = "color(242)"
SELECTED = "bold white on color(238)"
HINT_STYLE = "dim"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def show_menu(
    console: Console,
    title: str,
    options: List[Dict[str, Any]],
    help_callback: Callable | None = None,
    header_callback: Callable | None = None,
    ai_assistant: Any = None,
) -> str:
    """Arrow-key menu. Returns selected ``value`` or ``"BACK"``."""
    idx = 0
    prev_size: tuple[int, int] | None = None
    first_draw = True

    while True:
        size = _term_size()
        if size != prev_size:
            _draw(console, title, options, idx, size, header_callback, first_draw=first_draw)
            first_draw = False
            prev_size = size

        key = _read_key(timeout=0.1)
        if key == "NO_INPUT":
            if _term_size() != prev_size:
                prev_size = None
            continue

        if key == "UP":
            idx = (idx - 1) % len(options)
            prev_size = None
        elif key == "DOWN":
            idx = (idx + 1) % len(options)
            prev_size = None
        elif key == "ENTER":
            return options[idx]["value"]
        elif key in ("BACK", "QUIT"):
            return "BACK"


def _draw(
    console: Console,
    title: str,
    options: List[Dict[str, Any]],
    idx: int,
    size: tuple[int, int],
    header_callback: Callable | None,
    *,
    first_draw: bool = False,
) -> None:
    if first_draw:
        console.clear()
    else:
        # Move cursor to top-left without clearing — avoids flicker
        sys.stdout.write("\033[H")
        sys.stdout.flush()

    if header_callback:
        header_callback()

    # Title bar (skip if empty)
    if title:
        console.print(Text(f" {title} ", style=BRAND))
        console.print()

    width = size[0]
    compact = width < 60

    tbl = Table(
        box=box.SIMPLE_HEAVY,
        border_style=BORDER,
        expand=True,
        show_header=False,
        padding=(0, 1),
    )
    tbl.add_column("", width=3, justify="right")
    tbl.add_column("", min_width=16)
    if not compact:
        tbl.add_column("", ratio=2, style="dim")

    for i, opt in enumerate(options):
        sel = i == idx
        marker = ">" if sel else " "
        name = opt["name"]
        opt_style = opt.get("style")
        if opt_style and not sel:
            name = Text(name, style=opt_style)
        row: list[Any] = [marker, name]
        if not compact:
            row.append(opt.get("description", ""))
        tbl.add_row(*row)
        if sel:
            tbl.rows[-1].style = SELECTED

    console.print(tbl)
    console.print(Text("Up/Down: navigate   Enter: select   Esc/b: back", style=HINT_STYLE))
    # Erase any leftover lines below the new content
    sys.stdout.write("\033[J")
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Input helpers (replace questionary.text / confirm / select)
# ---------------------------------------------------------------------------

def prompt_text(console: Console, label: str, default: str | None = None) -> str | None:
    """Prompt for a text value. Returns None on cancel."""
    prompt = f"[bold color(141)]{label}[/]"
    if default:
        prompt += f" [dim]({default})[/dim]"
    prompt += ": "
    try:
        value = console.input(prompt).strip()
        return value if value else default
    except (KeyboardInterrupt, EOFError):
        return None


def prompt_confirm(console: Console, label: str, default: bool = True) -> bool:
    """Yes/no prompt. Returns bool."""
    hint = "[Y/n]" if default else "[y/N]"
    try:
        raw = console.input(f"[bold]{label}[/bold] {hint}: ").strip().lower()
        if not raw:
            return default
        return raw in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        return False


def prompt_select(
    console: Console,
    label: str,
    choices: List[str],
) -> str | None:
    """Arrow-key select from plain string choices. Returns None on cancel."""
    idx = 0
    prev: tuple[int, int] | None = None
    first = True

    while True:
        size = _term_size()
        if size != prev:
            if first:
                console.clear()
                first = False
            else:
                sys.stdout.write("\033[H")
                sys.stdout.flush()
            console.print(Text(f" {label} ", style=BRAND))
            console.print()
            for i, ch in enumerate(choices):
                if i == idx:
                    console.print(f"  [bold white on color(238)] > {ch} [/]")
                else:
                    console.print(f"    {ch}")
            console.print()
            console.print(Text("Up/Down: navigate   Enter: select   Esc: cancel", style=HINT_STYLE))
            sys.stdout.write("\033[J")
            sys.stdout.flush()
            prev = size

        key = _read_key(timeout=0.1)
        if key == "NO_INPUT":
            if _term_size() != prev:
                prev = None
            continue
        if key == "UP":
            idx = (idx - 1) % len(choices)
            prev = None
        elif key == "DOWN":
            idx = (idx + 1) % len(choices)
            prev = None
        elif key == "ENTER":
            return choices[idx]
        elif key in ("BACK", "QUIT"):
            return None
