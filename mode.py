#!/usr/bin/env python3

# Mode Terminal v2.0 - Interactive terminal navigator
# https://github.com/JadenB9/mode-terminal

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

from rich.console import Console
from rich.text import Text

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from alias_manager import AliasManager
from project_manager import ProjectManager
from file_navigator import FileNavigator
from help_system import HelpSystem
from bookmark_manager import BookmarkManager
from ollama_manager import OllamaManager
from menu_input import show_menu, prompt_text

VERSION = "3.0"

MAIN_MENU_OPTIONS = [
    {
        'name': 'Current Directory',
        'value': 'normal',
        'description': 'Return to terminal in current directory',
    },
    {
        'name': 'iCloud Drive',
        'value': 'filesystem',
        'description': 'Navigate to iCloud Drive',
    },
    {
        'name': 'SSH John',
        'value': 'john',
        'description': 'Connect to butler@john via SSH',
        'style': 'bold red',
    },
    {
        'name': 'SSH Windows',
        'value': 'windows',
        'description': 'Connect to jaden@windows via SSH',
        'style': 'bold red',
    },
    {
        'name': 'SSH Ubuntu',
        'value': 'ubuntu',
        'description': 'SSH into Windows then into Ubuntu (WSL2)',
        'style': 'bold red',
    },
    {
        'name': 'Projects',
        'value': 'projects',
        'description': 'Create new projects with projectmaker',
        'style': 'bold cyan',
    },
    {
        'name': 'Bookmarks',
        'value': 'bookmarks',
        'description': 'Manage directory bookmarks',
        'style': 'bold cyan',
    },
    {
        'name': 'Alias',
        'value': 'alias',
        'description': 'Create or view persistent shell aliases',
        'style': 'bold cyan',
    },
    {
        'name': 'Custom LS',
        'value': 'customls',
        'description': 'Set or view custom directory colors',
        'style': 'bold cyan',
    },
    {
        'name': 'Claude Usage',
        'value': 'claude_usage',
        'description': 'Open Claude AI usage in browser',
        'style': 'bold color(208)',
    },
    {
        'name': 'Claude Prep',
        'value': 'prepare',
        'description': 'Add CLAUDE.md and optimize dir for Claude Code',
        'style': 'bold color(208)',
    },
    {
        'name': 'Ollama',
        'value': 'ollama',
        'description': 'Chat with local LLM models via Ollama',
        'style': 'bold white',
    },
    {
        'name': 'Source Code',
        'value': 'thecode',
        'description': 'Open Mode Terminal source directory',
        'style': 'color(245)',
    },
    {
        'name': 'Help',
        'value': 'help',
        'description': 'Help system and documentation',
        'style': 'color(245)',
    },
]


class ModeApp:
    def __init__(self):
        self.console = Console()
        self.config_path = Path.home() / '.mode' / 'config.json'
        self.cd_file = Path.home() / '.mode' / '.mode_cd'
        self.config = self._load_config()

        self.project_manager = ProjectManager(self.config, self.console)
        self.file_navigator = FileNavigator(self.config, self.console)
        self.help_system = HelpSystem(self.config, self.console)
        self.bookmark_manager = BookmarkManager(self.config, self.console)
        self.alias_manager = AliasManager(self.config, self.config_path.parent)
        self.ollama_manager = OllamaManager(self.config, self.console)

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.console.print("[red]Configuration file not found. Please reinstall mode.[/red]")
            sys.exit(1)
        except json.JSONDecodeError:
            self.console.print("[red]Invalid configuration file. Please check config.json[/red]")
            sys.exit(1)

    def _save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _clear(self):
        if self.config.get('auto_clear_screen', True):
            os.system('clear')

    def _show_header(self):
        art = (
            " __  __  ___  ___  ___ \n"
            "|  \\/  |/ _ \\|   \\| __|\n"
            "| |\\/| | (_) | |) | _| \n"
            "|_|  |_|\\___/|___/|___|\n"
        )
        self.console.print(Text(art, style="bold color(141)"), end="")
        self.console.print(Text("──────────────────────", style="color(242)"))
        self.console.print(Text(f"  v{VERSION}", style="dim"))

    def _change_dir_and_exit(self, target: Path):
        """Write target to .mode_cd and exit with code 42."""
        with open(self.cd_file, 'w') as f:
            f.write(str(target))
        sys.exit(42)

    # ------------------------------------------------------------------
    # Menu / routing
    # ------------------------------------------------------------------

    def _run_main_menu(self) -> str:
        """Show the main menu. Returns a value string or 'exit'."""
        while True:
            try:
                result = show_menu(
                    self.console,
                    "",
                    MAIN_MENU_OPTIONS,
                    header_callback=self._show_header,
                )
                if result == 'BACK':
                    return 'exit'
                return result
            except KeyboardInterrupt:
                return 'exit'

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_normal_use(self):
        self._change_dir_and_exit(Path.cwd())

    def _handle_filesystem(self):
        icloud = Path.home() / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'
        if not icloud.exists():
            self.console.print("[red]iCloud Drive not found. Make sure iCloud is set up.[/red]")
            input("Press Enter to continue...")
            return 'continue'
        self._change_dir_and_exit(icloud)

    def _handle_thecode(self):
        mode_path = Path.home() / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs' / 'Projects' / 'mode'
        if not mode_path.exists():
            self.console.print("[red]Mode Terminal source directory not found.[/red]")
            input("Press Enter to continue...")
            return 'continue'
        self._change_dir_and_exit(mode_path)

    def _handle_john_ssh(self):
        try:
            self._clear()
            self.console.print("[bold]Connecting to butler@john...[/bold]")
            self.console.print()
            subprocess.run(['ssh', 'butler@john'])
            self.console.print()
            self.console.print("[green]SSH session ended.[/green]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"[red]Error connecting to john: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'

    def _handle_windows_ssh(self):
        try:
            self._clear()
            self.console.print('[bold]Connecting to jaden@windows...[/bold]')
            self.console.print()
            subprocess.run(['ssh', 'windows'])
            self.console.print()
            self.console.print('[green]SSH session ended.[/green]')
            sys.exit(0)
        except Exception as e:
            self.console.print(f'[red]Error connecting to windows: {e}[/red]')
            input('Press Enter to continue...')
            return 'continue'

    def _handle_ubuntu_ssh(self):
        try:
            self._clear()
            self.console.print('[bold]Connecting to Windows, then Ubuntu (WSL2)...[/bold]')
            self.console.print()
            subprocess.run(['ssh', '-t', 'windows', 'ssh', 'ubuntu'])
            self.console.print()
            self.console.print('[green]SSH session ended.[/green]')
            sys.exit(0)
        except Exception as e:
            self.console.print(f'[red]Error connecting to ubuntu: {e}[/red]')
            input('Press Enter to continue...')
            return 'continue'

    def _handle_claude_usage(self):
        import webbrowser
        try:
            webbrowser.open('https://claude.ai/settings/usage')
            self.console.print("[green]Opened Claude usage in browser.[/green]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"[red]Error opening browser: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'

    def _handle_projects(self):
        try:
            self._clear()
            subprocess.run(['projectmaker'], cwd=str(self.config.get('projects_path', Path.home())))
            sys.exit(0)
        except FileNotFoundError:
            self.console.print("[red]projectmaker not found. Install it to ~/.local/bin/[/red]")
            input("Press Enter to continue...")
            return 'continue'

    def _handle_customls(self):
        options = [
            {
                'name': 'Set Colors',
                'value': 'set',
                'description': 'Assign colors to files and directories',
            },
            {
                'name': 'View Colors',
                'value': 'colors',
                'description': 'Show current custom color assignments',
            },
        ]

        while True:
            try:
                result = show_menu(self.console, "Custom LS", options)
                if result in ('BACK', 'back'):
                    return 'continue'
                elif result == 'set':
                    self._clear()
                    subprocess.run(['customls', 'set'])
                    input("\nPress Enter to continue...")
                elif result == 'colors':
                    self._clear()
                    subprocess.run(['customls', 'colors'])
                    input("\nPress Enter to continue...")
            except FileNotFoundError:
                self.console.print("[red]customls not found. Install it to ~/.local/bin/[/red]")
                input("Press Enter to continue...")
                return 'continue'
            except KeyboardInterrupt:
                return 'continue'

    def _handle_bookmarks(self):
        return self.bookmark_manager.show_menu()

    def _handle_help(self):
        return self.help_system.show_help_menu()

    def _handle_prepare(self):
        self.project_manager.prepare_for_claude()
        return 'continue'

    def _handle_ollama(self):
        return self.ollama_manager.show_menu()

    def _handle_alias(self):
        options = [
            {
                'name': 'Create Alias',
                'value': 'create',
                'description': 'Create a new persistent shell alias',
            },
            {
                'name': 'View Aliases',
                'value': 'view',
                'description': 'Show all custom aliases you have added',
            },
        ]

        while True:
            try:
                result = show_menu(self.console, "Alias Manager", options)
                if result in ('BACK', 'back'):
                    return 'continue'
                elif result == 'create':
                    return self._create_alias()
                elif result == 'view':
                    self._view_aliases()
            except KeyboardInterrupt:
                return 'continue'

    def _create_alias(self):
        try:
            alias_name = prompt_text(self.console, "Alias name")
            if not alias_name:
                return 'continue'
            command = prompt_text(self.console, "Command")
            if not command:
                return 'continue'
            alias_name = self.alias_manager.add_alias(alias_name, command)
        except ValueError as exc:
            self.console.print(f"[red]Alias error: {exc}[/red]")
            input("Press Enter to continue...")
            return 'continue'

        self._save_config()
        self.console.print(f"[green]Loaded alias '{alias_name}' into the current shell.[/green]")
        sys.exit(43)

    def _view_aliases(self):
        from rich.table import Table
        self._clear()
        aliases = self.config.get('aliases', {})
        if not aliases:
            self.console.print("\n  [dim]No custom aliases set. Use 'Create Alias' to add one.[/dim]\n")
            input("Press Enter to continue...")
            return

        table = Table(title="Custom Aliases", border_style="cyan", expand=True)
        table.add_column("Alias", style="bold color(141)", min_width=12)
        table.add_column("Command", style="white", min_width=20)

        for name, command in sorted(aliases.items()):
            table.add_row(name, command)

        self.console.print()
        self.console.print(table)
        self.console.print()
        input("Press Enter to continue...")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    _HANDLERS = {
        'normal':       '_handle_normal_use',
        'filesystem':   '_handle_filesystem',
        'john':         '_handle_john_ssh',
        'windows':      '_handle_windows_ssh',
        'ubuntu':       '_handle_ubuntu_ssh',
        'claude_usage': '_handle_claude_usage',
        'projects':       '_handle_projects',
        'customls':       '_handle_customls',
        'bookmarks':      '_handle_bookmarks',
        'prepare':        '_handle_prepare',
        'alias':          '_handle_alias',
        'ollama':         '_handle_ollama',
        'thecode':      '_handle_thecode',
        'help':         '_handle_help',
    }

    def run(self):
        while True:
            try:
                choice = self._run_main_menu()
                if choice == 'exit':
                    break

                handler_name = self._HANDLERS.get(choice)
                if handler_name is None:
                    continue

                result = getattr(self, handler_name)()
                if result == 'exit':
                    break

            except KeyboardInterrupt:
                break
            except SystemExit:
                raise
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                input("Press Enter to continue...")

        self._save_config()


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Mode Terminal - Interactive development workflow navigator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  mode            Launch interactive navigator\n"
            "  mode --version  Show version information\n"
            "\n"
            "https://github.com/JadenB9/mode-terminal"
        ),
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'Mode Terminal v{VERSION}',
    )

    parser.add_argument(
        '--config',
        help='Path to custom configuration file',
        default=None,
    )

    args = parser.parse_args()

    try:
        app = ModeApp()
        if args.config:
            with open(args.config, 'r') as f:
                app.config.update(json.load(f))
        app.run()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
