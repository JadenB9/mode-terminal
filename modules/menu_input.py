"""Clean menu input module using questionary and rich."""

import os
from typing import List, Dict, Any, Optional, Callable

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

MENU_STYLE = Style([
    ("qmark", "fg:cyan bold"),
    ("question", "fg:white bold"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:green bold"),
    ("selected", "fg:green"),
    ("answer", "fg:green bold"),
])


def _format_choice(option: Dict[str, Any]) -> questionary.Choice:
    """Format an option dict into a questionary Choice."""
    label = option["name"]
    if option.get("description"):
        label += f"  \033[2m- {option['description']}\033[0m"
    return questionary.Choice(title=label, value=option["value"])


def show_menu(
    console: Console,
    title: str,
    options: List[Dict[str, Any]],
    help_callback: Optional[Callable] = None,
    header_callback: Optional[Callable] = None,
    ai_assistant: Any = None,
) -> str:
    """Display an interactive menu and return the selected value.

    Args:
        console: Rich Console instance.
        title: Menu title string.
        options: List of dicts with keys 'name', 'value', and optional 'description'.
        help_callback: Optional callable to display help info.
        header_callback: Optional callable to render header art.
        ai_assistant: Unused, kept for API compatibility.

    Returns:
        The 'value' of the selected option, or 'BACK' on cancel.
    """
    os.system("clear")

    if header_callback:
        header_callback()

    console.print(
        Panel(
            Text(title, justify="center", style="bold cyan"),
            border_style="cyan",
            padding=(0, 2),
        )
    )
    console.print()

    choices = [_format_choice(opt) for opt in options]
    choices.append(questionary.Choice(title="\033[2m\u2190 Back\033[0m", value="BACK"))

    try:
        result = questionary.select(
            "",
            choices=choices,
            style=MENU_STYLE,
            qmark="\u25b6",
            instruction="",
            use_arrow_keys=True,
            use_shortcuts=False,
        ).ask()
    except KeyboardInterrupt:
        return "BACK"

    if result is None:
        return "BACK"

    if result == "HELP" and help_callback:
        help_callback()
        return show_menu(console, title, options, help_callback, header_callback)

    return result
