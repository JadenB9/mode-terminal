"""Bookmark manager - TUI version of the temp() shell function."""

import os
import sys
from pathlib import Path
from typing import Dict, Any

from rich.console import Console
from rich.table import Table
from menu_input import show_menu, prompt_text, prompt_select


class BookmarkManager:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        self.bookmarks_file = Path.home() / '.temp_dirs'

    def _load_bookmarks(self) -> Dict[str, str]:
        """Load bookmarks from ~/.temp_dirs (same file as the temp shell function)."""
        bookmarks = {}
        if self.bookmarks_file.exists():
            with open(self.bookmarks_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        name, path = line.split(':', 1)
                        bookmarks[name] = path
        return bookmarks

    def _save_bookmarks(self, bookmarks: Dict[str, str]):
        """Save bookmarks to ~/.temp_dirs."""
        with open(self.bookmarks_file, 'w') as f:
            for name, path in bookmarks.items():
                f.write(f"{name}:{path}\n")

    def show_menu(self):
        """Show bookmark management menu."""
        options = [
            {
                'name': 'Navigate to Bookmark',
                'value': 'navigate',
                'description': 'Jump to a saved bookmark directory',
            },
            {
                'name': 'Save Current Directory',
                'value': 'save',
                'description': 'Bookmark the current working directory',
            },
            {
                'name': 'List All Bookmarks',
                'value': 'list',
                'description': 'View all saved bookmarks',
            },
            {
                'name': 'Delete Bookmark',
                'value': 'delete',
                'description': 'Remove a saved bookmark',
            },
        ]

        while True:
            try:
                result = show_menu(
                    self.console,
                    "Bookmarks",
                    options,
                )

                if result == 'BACK':
                    return 'continue'
                elif result == 'navigate':
                    nav_result = self.navigate_to_bookmark()
                    if nav_result == 'exit':
                        return 'exit'
                elif result == 'save':
                    self.save_bookmark()
                elif result == 'list':
                    self.list_bookmarks()
                elif result == 'delete':
                    self.delete_bookmark()

            except KeyboardInterrupt:
                return 'continue'

    def navigate_to_bookmark(self):
        """Show bookmark list and navigate to selected one."""
        bookmarks = self._load_bookmarks()

        if not bookmarks:
            self.console.print("[yellow]No bookmarks saved yet.[/yellow]")
            self.console.print("[dim]Use 'Save Current Directory' to create one.[/dim]")
            input("\nPress Enter to continue...")
            return 'continue'

        # Build choices as "name  ->  path" strings, filtering out missing paths
        choices = []
        valid_names = []
        for name, path in bookmarks.items():
            if Path(path).exists():
                choices.append(f"{name}  ->  {path}")
                valid_names.append(name)

        if not choices:
            self.console.print("[yellow]All bookmarked paths are missing.[/yellow]")
            input("\nPress Enter to continue...")
            return 'continue'

        try:
            selected = prompt_select(
                self.console,
                "Select bookmark to navigate to:",
                choices,
            )
        except KeyboardInterrupt:
            return 'continue'

        if selected is None:
            return 'continue'

        # Extract name from "name  ->  path" format
        name = selected.split("  ->  ")[0]
        target_path = bookmarks[name]

        # Write the target directory for the shell wrapper to cd into
        cd_file = Path.home() / '.mode' / '.mode_cd'
        with open(cd_file, 'w') as f:
            f.write(target_path)

        self.console.print(f"[green]Navigating to bookmark '{name}': {target_path}[/green]")
        sys.exit(42)

    def save_bookmark(self):
        """Save current directory as a bookmark."""
        cwd = os.getcwd()
        bookmarks = self._load_bookmarks()

        name = prompt_text(self.console, "Bookmark name", default="temp")

        if not name:
            return

        bookmarks[name] = cwd
        self._save_bookmarks(bookmarks)
        self.console.print(f"[green]Saved '{name}' -> {cwd}[/green]")
        input("\nPress Enter to continue...")

    def list_bookmarks(self):
        """Display all bookmarks in a rich table."""
        self.console.clear()
        bookmarks = self._load_bookmarks()

        if not bookmarks:
            self.console.print("[yellow]No bookmarks saved yet.[/yellow]")
            input("\nPress Enter to continue...")
            return

        table = Table(title="Saved Bookmarks")
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="white")
        table.add_column("Status", style="green")

        for name, path in bookmarks.items():
            exists = "exists" if Path(path).exists() else "missing"
            style = "green" if Path(path).exists() else "red"
            table.add_row(name, path, f"[{style}]{exists}[/{style}]")

        self.console.print(table)
        self.console.print(f"\n[dim]{len(bookmarks)} bookmark(s) total[/dim]")
        input("\nPress Enter to continue...")

    def delete_bookmark(self):
        """Delete a bookmark."""
        bookmarks = self._load_bookmarks()

        if not bookmarks:
            self.console.print("[yellow]No bookmarks to delete.[/yellow]")
            input("\nPress Enter to continue...")
            return

        choices = [f"{name}  ->  {path}" for name, path in bookmarks.items()]

        try:
            selected = prompt_select(
                self.console,
                "Select bookmark to delete:",
                choices,
            )
        except KeyboardInterrupt:
            return

        if selected is None:
            return

        # Extract name from "name  ->  path" format
        name = selected.split("  ->  ")[0]

        if name in bookmarks:
            del bookmarks[name]
            self._save_bookmarks(bookmarks)
            self.console.print(f"[green]Deleted bookmark '{name}'[/green]")

        input("\nPress Enter to continue...")
