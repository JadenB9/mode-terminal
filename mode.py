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

VERSION = "3.1"

MAIN_MENU_OPTIONS = [
    {
        'name': 'Current Directory',
        'value': 'normal',
        'description': 'Return to terminal in current directory',
    },
    {
        'name': 'Project Directory',
        'value': 'project_dir',
        'description': 'Navigate to your Projects directory',
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

    def _handle_project_dir(self):
        projects_path = Path(self.config.get(
            'projects_path',
            Path.home() / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs' / 'Projects',
        ))
        if not projects_path.exists():
            self.console.print(f"[red]Projects directory not found at {projects_path}[/red]")
            input("Press Enter to continue...")
            return 'continue'
        self._change_dir_and_exit(projects_path)

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
            # Auto-update projectmaker to latest version
            self.console.print("[dim]Checking for projectmaker updates...[/dim]", end="")
            subprocess.run(
                ['brew', 'upgrade', 'JadenB9/tap/project'],
                capture_output=True, timeout=30
            )
            self.console.print("\r" + " " * 50 + "\r", end="")
            self._clear()
            subprocess.run(['project'], cwd=str(self.config.get('projects_path', Path.home())))
            sys.exit(0)
        except FileNotFoundError:
            self.console.print("[red]projectmaker not found. Install with: brew install JadenB9/tap/project[/red]")
            input("Press Enter to continue...")
            return 'continue'
        except Exception:
            # If brew update fails, just run project anyway
            self._clear()
            subprocess.run(['project'], cwd=str(self.config.get('projects_path', Path.home())))
            sys.exit(0)

    def _get_customls_order_status(self) -> bool:
        """Read the order_by_color flag from customls config."""
        try:
            cfg_path = Path.home() / '.config' / 'customls' / 'colors.json'
            with open(cfg_path) as f:
                data = json.load(f)
            return data.get('order_by_color', False)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def _handle_customls(self):
        while True:
            order_on = self._get_customls_order_status()
            status = "ON" if order_on else "OFF"
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
                {
                    'name': f'Order Colors [{status}]',
                    'value': 'order',
                    'description': 'Toggle sorting items by color group',
                    'style': 'bold green' if order_on else 'bold red',
                },
            ]

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
                elif result == 'order':
                    self._clear()
                    subprocess.run(['customls', 'order'])
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
                'name': 'Manage Aliases',
                'value': 'manage',
                'description': 'View, edit, or remove your aliases',
            },
        ]

        while True:
            try:
                result = show_menu(self.console, "Alias Manager", options)
                if result in ('BACK', 'back'):
                    return 'continue'
                elif result == 'create':
                    return self._create_alias()
                elif result == 'manage':
                    mgr_result = self._manage_aliases()
                    if mgr_result == 'reload':
                        self._save_config()
                        sys.exit(43)
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

    def _manage_aliases(self):
        from menu_input import prompt_confirm

        while True:
            all_aliases = self.alias_manager.get_all_aliases()
            if not all_aliases:
                self._clear()
                self.console.print("\n  [dim]No custom aliases found in .zshrc.[/dim]\n")
                input("Press Enter to continue...")
                return

            alias_options = []
            for name, command in all_aliases:
                # Truncate long commands for display
                display_cmd = command if len(command) <= 50 else command[:47] + "..."
                alias_options.append({
                    'name': name,
                    'value': name,
                    'description': display_cmd,
                    'style': 'bold color(141)',
                })

            try:
                selected = show_menu(self.console, "Your Aliases", alias_options)
                if selected in ('BACK', 'back'):
                    return
            except KeyboardInterrupt:
                return

            # Find the full command for the selected alias
            selected_cmd = None
            for name, command in all_aliases:
                if name == selected:
                    selected_cmd = command
                    break

            # Show action menu for this alias
            action_options = [
                {
                    'name': 'Edit',
                    'value': 'edit',
                    'description': f'Change the command for "{selected}"',
                    'style': 'bold color(208)',
                },
                {
                    'name': 'Remove',
                    'value': 'remove',
                    'description': f'Delete "{selected}" from .zshrc',
                    'style': 'bold red',
                },
            ]

            try:
                action = show_menu(self.console, f"{selected} = {selected_cmd}", action_options)
                if action in ('BACK', 'back'):
                    continue
            except KeyboardInterrupt:
                continue

            if action == 'edit':
                new_cmd = prompt_text(self.console, "New command", default=selected_cmd)
                if not new_cmd or new_cmd == selected_cmd:
                    continue
                try:
                    self.alias_manager.edit_alias(selected, new_cmd)
                    self._save_config()
                    self.console.print(f"[green]Updated alias '{selected}'.[/green]")
                    return 'reload'
                except ValueError as exc:
                    self.console.print(f"[red]Error: {exc}[/red]")
                    input("Press Enter to continue...")

            elif action == 'remove':
                if prompt_confirm(self.console, f"Remove alias '{selected}'?", default=False):
                    try:
                        self.alias_manager.remove_alias(selected)
                        self._save_config()
                        self.console.print(f"[green]Removed alias '{selected}'.[/green]")
                        return 'reload'
                    except ValueError as exc:
                        self.console.print(f"[red]Error: {exc}[/red]")
                        input("Press Enter to continue...")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    _HANDLERS = {
        'normal':       '_handle_normal_use',
        'project_dir':  '_handle_project_dir',
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
