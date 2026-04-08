"""File system navigation module using Rich and menu_input helpers."""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from menu_input import show_menu, prompt_confirm, prompt_select


class FileNavigator:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console

    def show_menu(self):
        """Show file system navigation menu."""
        options = [
            {
                'name': 'Quick Navigation',
                'value': 'quick_nav',
                'description': 'Desktop, Documents, Downloads, Applications, iCloud Drive',
            },
        ]

        while True:
            try:
                result = show_menu(self.console, "File System", options)

                if result == 'BACK':
                    return 'continue'
                elif result == 'quick_nav':
                    nav_result = self.quick_navigation()
                    if nav_result == 'exit':
                        return 'exit'

            except KeyboardInterrupt:
                return 'continue'

    def quick_navigation(self):
        """Quick navigation to common directories."""
        home = Path.home()

        dirs = [
            ('Desktop', home / 'Desktop'),
            ('Documents', home / 'Documents'),
            ('Downloads', home / 'Downloads'),
            ('Applications', Path('/Applications')),
            ('iCloud Drive', home / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'),
        ]

        labels = [name for name, _ in dirs]
        path_map = {name: path for name, path in dirs}

        while True:
            self.console.clear()
            self.console.print(Panel("Quick Navigation", style="bold cyan"))
            self.console.print()

            try:
                selected = prompt_select(
                    self.console,
                    "Select directory:",
                    labels,
                )
            except KeyboardInterrupt:
                return 'continue'

            if selected is None:
                return 'continue'

            path = path_map[selected]
            if path.name == 'com~apple~CloudDocs':
                result = self.browse_directory(path, "iCloud Drive")
                if result == 'exit':
                    return 'exit'
            else:
                result = self.navigate_to_directory(path)
                if result == 'exit':
                    return 'exit'

    def navigate_to_directory(self, path: Path):
        """Navigate to a specific directory."""
        try:
            if not path.exists():
                self.console.print(f"[red]Directory does not exist: {path}[/red]")
                input("Press Enter to continue...")
                return 'continue'

            self.console.clear()
            self.show_directory_contents(path)

            try:
                stay = prompt_confirm(self.console, "Stay in this directory and exit mode?")
            except KeyboardInterrupt:
                return 'continue'

            if stay:
                cd_file = Path.home() / '.mode' / '.mode_cd'
                with open(cd_file, 'w') as f:
                    f.write(str(path))
                sys.exit(42)
            else:
                return 'continue'

        except SystemExit:
            raise
        except Exception as e:
            self.console.print(f"[red]Error navigating to directory: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'

    def browse_directory(self, directory: Path, title: str):
        """Generic directory browser."""
        current_path = directory

        while True:
            try:
                self.console.clear()
                self.console.print(Panel(f"{title} - {current_path}", style="bold cyan"))
                self.console.print()

                folders = []
                try:
                    for item in current_path.iterdir():
                        if item.is_dir() and not item.name.startswith('.'):
                            folders.append(item)
                except PermissionError:
                    self.console.print("[red]Permission denied.[/red]")
                    input("Press Enter to continue...")
                    return 'continue'

                choices = []
                folder_map = {}

                if current_path != directory:
                    choices.append(".. (Parent)")

                for folder in sorted(folders, key=lambda f: f.name.lower()):
                    choices.append(folder.name)
                    folder_map[folder.name] = folder

                select_label = f"[Select {current_path.name}]"
                choices.append(select_label)
                choices.append("Back")

                try:
                    choice = prompt_select(
                        self.console,
                        "Navigate:",
                        choices,
                    )
                except KeyboardInterrupt:
                    return 'continue'

                if choice is None or choice == "Back":
                    return 'continue'
                elif choice == ".. (Parent)":
                    current_path = current_path.parent
                elif choice == select_label:
                    result = self.navigate_to_directory(current_path)
                    if result == 'exit':
                        return 'exit'
                elif choice in folder_map:
                    current_path = folder_map[choice]

            except KeyboardInterrupt:
                return 'continue'

    def show_directory_contents(self, path: Path):
        """Show directory contents in a rich table."""
        try:
            table = Table(title=f"Contents of {path}")
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Size", style="green")
            table.add_column("Modified", style="yellow")

            items = []
            for item in path.iterdir():
                if not item.name.startswith('.'):
                    stat = item.stat()
                    size = self._format_size(stat.st_size) if item.is_file() else "--"
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    item_type = "Dir" if item.is_dir() else "File"
                    items.append((item_type, item.name, size, modified))

            items.sort(key=lambda x: (x[0] != "Dir", x[1].lower()))

            for item_type, name, size, modified in items[:20]:
                table.add_row(item_type, name, size, modified)

            if len(items) > 20:
                table.add_row("...", f"and {len(items) - 20} more", "", "")

            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Error listing directory: {e}[/red]")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
