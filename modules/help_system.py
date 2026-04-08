"""Help system module for Mode Terminal v2.0."""

from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from menu_input import show_menu


class HelpSystem:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console

    def show_help_menu(self):
        """Show the main help menu."""
        options = [
            {
                'name': 'Quick Start Guide',
                'value': 'quick_start',
                'description': 'Essential first steps and basic navigation',
            },
            {
                'name': 'Navigation Controls',
                'value': 'navigation',
                'description': 'Keyboard shortcuts and controls',
            },
            {
                'name': 'Feature Overview',
                'value': 'features',
                'description': 'Complete feature list',
            },
            {
                'name': 'Configuration Guide',
                'value': 'configuration',
                'description': 'Settings and customization',
            },
            {
                'name': 'Troubleshooting',
                'value': 'troubleshooting',
                'description': 'Common issues and solutions',
            },
            {
                'name': 'Quick Reference Card',
                'value': 'quick_ref',
                'description': 'Compact reference for shortcuts and features',
            },
        ]

        while True:
            try:
                result = show_menu(self.console, "Help System", options)

                if result == 'BACK':
                    return 'continue'
                elif result == 'quick_start':
                    self.show_quick_start()
                elif result == 'navigation':
                    self.show_navigation_help()
                elif result == 'features':
                    self.show_features_help()
                elif result == 'configuration':
                    self.show_configuration_help()
                elif result == 'troubleshooting':
                    self.show_troubleshooting_help()
                elif result == 'quick_ref':
                    self.show_quick_reference()

            except KeyboardInterrupt:
                return 'continue'

    def show_quick_start(self):
        """Show quick start guide."""
        self.console.clear()
        guide = """
[bold cyan]Welcome to Mode Terminal v2.0[/bold cyan]

[yellow]Getting Started:[/yellow]
  1. Use arrow keys to navigate menus
  2. Press Enter to select an option
  3. Select "Back" or press Ctrl+C to go back

[yellow]Main Features:[/yellow]
  - [green]Projects[/green] — Create, clone, and switch between projects
  - [green]Bookmarks[/green] — Save and jump to directories instantly
  - [green]iCloud Drive[/green] — Browse your iCloud files
  - [green]SSH[/green] — Quick SSH connections

[yellow]Tips:[/yellow]
  - New projects auto-generate CLAUDE.md for Claude Code
  - Bookmarks sync with the 'temp' shell command
  - Configuration saves automatically
"""
        self.console.print(Panel(guide, title="Quick Start Guide", border_style="yellow"))
        input("\nPress Enter to continue...")

    def show_navigation_help(self):
        """Show navigation controls."""
        self.console.clear()

        table = Table(title="Keyboard Controls")
        table.add_column("Key", style="cyan", width=12)
        table.add_column("Action", style="white", width=30)
        table.add_column("Context", style="green", width=15)

        table.add_row("Up/Down", "Navigate menu options", "All menus")
        table.add_row("Enter", "Select option", "All menus")
        table.add_row("Ctrl+C", "Go back / cancel", "Anywhere")

        self.console.print(table)
        self.console.print()

        flow = """
[bold cyan]Navigation Flow:[/bold cyan]
  Main Menu -> Sub Menu -> Action -> Back to Sub Menu

[bold cyan]Special Cases:[/bold cyan]
  - "Current Directory" exits Mode to your home dir
  - Project/Bookmark navigation exits Mode and cd's to the target
  - These use exit code 42 to signal the shell wrapper
"""
        self.console.print(Panel(flow, border_style="cyan"))
        input("\nPress Enter to continue...")

    def show_features_help(self):
        """Show feature overview."""
        self.console.clear()
        self.console.print(Panel("Feature Overview", style="bold yellow"))
        self.console.print()

        # Projects
        proj = Table(title="Project Management")
        proj.add_column("Feature", style="cyan", width=20)
        proj.add_column("Description", style="white", width=50)
        proj.add_row("New Git Project", "Create directory, init git, generate CLAUDE.md, link GitHub")
        proj.add_row("Clone Repository", "List and clone repos from your GitHub account")
        proj.add_row("Project Switcher", "Navigate projects with git status indicators")
        proj.add_row("Environment Setup", "Auto-setup for React, Node.js, Python, and more")
        self.console.print(proj)
        self.console.print()

        # Bookmarks
        bm = Table(title="Bookmarks")
        bm.add_column("Feature", style="cyan", width=20)
        bm.add_column("Description", style="white", width=50)
        bm.add_row("Navigate", "Jump to any saved bookmark directory")
        bm.add_row("Save", "Bookmark current directory (named or as 'temp')")
        bm.add_row("List", "View all bookmarks with path status")
        bm.add_row("Delete", "Remove saved bookmarks")
        bm.add_row("Shell Sync", "Shares bookmarks with the 'temp' CLI command")
        self.console.print(bm)
        self.console.print()

        # Navigation
        nav = Table(title="Navigation & Utilities")
        nav.add_column("Feature", style="cyan", width=20)
        nav.add_column("Description", style="white", width=50)
        nav.add_row("iCloud Drive", "Browse and navigate iCloud folders")
        nav.add_row("Quick Navigation", "Fast access to Desktop, Documents, Downloads")
        nav.add_row("SSH Connections", "Quick SSH to configured hosts")
        nav.add_row("Claude Usage", "Open Claude AI usage in browser")
        self.console.print(nav)

        input("\nPress Enter to continue...")

    def show_configuration_help(self):
        """Show configuration help."""
        self.console.clear()

        config_text = f"""
[bold cyan]Config File:[/bold cyan] ~/.mode/config.json

[bold cyan]Current Settings:[/bold cyan]
  GitHub Username: [green]{self.config.get('github_username', 'Not set')}[/green]
  Projects Path:   [green]{self.config.get('projects_path', 'Not set')}[/green]
  Default Dir:     [green]{self.config.get('default_directory', 'Not set')}[/green]

[yellow]Editable Fields:[/yellow]
  [bold]github_username[/bold]    — Your GitHub username
  [bold]projects_path[/bold]      — Default location for projects
  [bold]default_directory[/bold]  — Home directory for "Current Directory" option
  [bold]auto_clear_screen[/bold]  — Clear screen between menus (true/false)

[yellow]How to Edit:[/yellow]
  1. Edit ~/.mode/config.json with any text editor
  2. Changes load automatically on next launch
"""
        self.console.print(Panel(config_text, title="Configuration Guide", border_style="yellow"))
        input("\nPress Enter to continue...")

    def show_troubleshooting_help(self):
        """Show troubleshooting help."""
        self.console.clear()

        trouble = """
[yellow]"mode" command not found[/yellow]
  - Restart terminal
  - Check PATH includes ~/.mode
  - Run: source ~/.zshrc

[yellow]Python import errors[/yellow]
  - Install deps: pip3 install --break-system-packages rich
  - Or use: ~/.mode/setup_python.py

[yellow]Permission errors[/yellow]
  - Fix: chmod +x ~/.mode/mode.py

[yellow]GitHub features not working[/yellow]
  - Install: brew install gh
  - Auth: gh auth login
  - Set username in config.json

[yellow]Menu not displaying correctly[/yellow]
  - Ensure terminal supports ANSI colors
  - Try resizing terminal window
  - Update Rich: pip3 install -U rich
"""
        self.console.print(Panel(trouble, title="Troubleshooting", border_style="red"))
        input("\nPress Enter to continue...")

    def show_quick_reference(self):
        """Show quick reference card."""
        self.console.clear()

        table = Table(title="Quick Reference")
        table.add_column("Key", style="cyan", width=10)
        table.add_column("Action", style="white", width=25)

        table.add_row("Up/Down", "Navigate menus")
        table.add_row("Enter", "Select option")
        table.add_row("Ctrl+C", "Go back")

        self.console.print(table)
        self.console.print()

        ref = """
[bold cyan]Main Menu:[/bold cyan]
  Current Dir / iCloud / SSH / Claude / Projects / Bookmarks / Source / Help

[bold cyan]Key Files:[/bold cyan]
  Config:    [green]~/.mode/config.json[/green]
  Bookmarks: [green]~/.temp_dirs[/green]

[bold cyan]Shell Commands:[/bold cyan]
  [green]mode[/green]         — Launch Mode Terminal
  [green]modebackup[/green]   — Launch backup version
  [green]temp[/green]         — Quick bookmark (CLI)
  [green]temp .[/green]       — Save current dir as 'temp'
  [green]temp . name[/green]  — Save current dir as 'name'
"""
        self.console.print(Panel(ref, border_style="cyan"))
        input("\nPress Enter to continue...")
