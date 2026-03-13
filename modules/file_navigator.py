"""File system navigation module using questionary and rich."""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from menu_input import show_menu


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

        choices = [questionary.Choice(title=name, value=str(path)) for name, path in dirs]

        while True:
            os.system('clear')
            self.console.print(Panel("Quick Navigation", style="bold cyan"))
            self.console.print()

            try:
                selected = questionary.select(
                    "Select directory:",
                    choices=choices,
                    use_arrow_keys=True,
                ).ask()
            except KeyboardInterrupt:
                return 'continue'

            if selected is None:
                return 'continue'

            path = Path(selected)
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

            os.system('clear')
            self.show_directory_contents(path)

            try:
                stay = questionary.confirm("Stay in this directory and exit mode?").ask()
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
                os.system('clear')
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
                if current_path != directory:
                    choices.append(questionary.Choice(title=".. (Parent)", value="__parent__"))

                for folder in sorted(folders, key=lambda f: f.name.lower()):
                    choices.append(questionary.Choice(title=folder.name, value=str(folder)))

                choices.append(questionary.Choice(title=f"[Select {current_path.name}]", value="__select__"))
                choices.append(questionary.Choice(title="Back", value="__back__"))

                try:
                    choice = questionary.select(
                        "Navigate:",
                        choices=choices,
                        use_arrow_keys=True,
                    ).ask()
                except KeyboardInterrupt:
                    return 'continue'

                if choice is None or choice == "__back__":
                    return 'continue'
                elif choice == "__parent__":
                    current_path = current_path.parent
                elif choice == "__select__":
                    result = self.navigate_to_directory(current_path)
                    if result == 'exit':
                        return 'exit'
                else:
                    current_path = Path(choice)

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
                    size = self._format_size(stat.st_size) if item.is_file() else "—"
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
    def _format_size(size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
