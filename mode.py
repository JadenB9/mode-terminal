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
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from project_manager import ProjectManager
from file_navigator import FileNavigator
from help_system import HelpSystem
from bookmark_manager import BookmarkManager
from menu_input import show_menu


MAIN_MENU_OPTIONS = [
    {
        'name': '\U0001f4c1 Current Directory',
        'value': 'normal',
        'description': 'Return to home directory and exit',
    },
    {
        'name': '\u2601\ufe0f  iCloud Directory',
        'value': 'filesystem',
        'description': 'Navigate to iCloud Drive',
    },
    {
        'name': '\U0001f517 SSH John',
        'value': 'john',
        'description': 'SSH to butler@john',
    },
    {
        'name': '\U0001f916 Claude Usage',
        'value': 'claude_usage',
        'description': 'Open Claude AI usage in browser',
    },
    {
        'name': '\U0001f4e6 Projects',
        'value': 'projects',
        'description': 'Manage projects, repos, and environments',
    },
    {
        'name': '\U0001f516 Bookmarks',
        'value': 'bookmarks',
        'description': 'Manage directory bookmarks',
    },
    {
        'name': '\U0001f4bb Source Code',
        'value': 'thecode',
        'description': 'Open Mode Terminal source directory',
    },
    {
        'name': '\u2753 Help',
        'value': 'help',
        'description': 'Help system and documentation',
    },
]


class ModeApp:
    def __init__(self):
        self.console = Console()
        self.config_path = Path.home() / '.mode' / 'config.json'
        self.config = self.load_config()

        # Initialize modules
        self.project_manager = ProjectManager(self.config, self.console)
        self.file_navigator = FileNavigator(self.config, self.console)
        self.help_system = HelpSystem(self.config, self.console)
        self.bookmark_manager = BookmarkManager(self.config, self.console)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.console.print("[red]Configuration file not found. Please reinstall mode.[/red]")
            sys.exit(1)
        except json.JSONDecodeError:
            self.console.print("[red]Invalid configuration file. Please check config.json[/red]")
            sys.exit(1)

    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def clear_screen(self):
        """Clear the terminal screen"""
        if self.config.get('auto_clear_screen', True):
            os.system('clear')

    def show_header(self):
        """Display the application header with ASCII art"""
        ascii_art = (
            "  __  __  ___  ___  ___ \n"
            " |  \\/  |/ _ \\|   \\| __|\n"
            " | |\\/| | (_) | |) | _| \n"
            " |_|  |_|\\___/|___/|___|"
        )

        header_text = Text(ascii_art, style="bold cyan")
        version_text = Text("v2.0", style="bold green", justify="center")
        subtitle = Text("Navigate your workflow with ease", style="dim italic", justify="center")

        panel = Panel(
            header_text,
            subtitle="v2.0",
            subtitle_align="center",
            border_style="cyan",
            padding=(0, 2),
        )

        self.console.print(panel)
        self.console.print(subtitle, justify="center")
        self.console.print()

    def run_main_menu(self):
        """Run the main menu loop"""
        while True:
            try:
                result = show_menu(
                    self.console,
                    "Mode Terminal - Main Menu",
                    MAIN_MENU_OPTIONS,
                    header_callback=self.show_header,
                )

                if result == 'BACK':
                    return 'exit'
                else:
                    return result

            except KeyboardInterrupt:
                return 'exit'

    def handle_normal_use(self):
        """Handle normal use option"""
        target_dir = self.config['default_directory']
        try:
            os.chdir(target_dir)
            self.clear_screen()
            self.console.print(f"[green]Changed to {target_dir} and returned to normal terminal mode.[/green]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"[red]Error changing to {target_dir}: {e}[/red]")
            self.console.print("[yellow]Returning to normal terminal mode in current directory.[/yellow]")
            sys.exit(0)

    def handle_projects_menu(self):
        """Handle project management menu"""
        return self.project_manager.show_menu()

    def handle_filesystem_menu(self):
        """Handle file system navigation - go directly to iCloud Drive"""
        icloud_path = Path.home() / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'

        try:
            if not icloud_path.exists():
                self.console.print("[red]iCloud Drive not found. Make sure iCloud is set up.[/red]")
                input("Press Enter to continue...")
                return 'continue'

            # Write the target directory to a file that the shell can read
            cd_file = Path.home() / '.mode' / '.mode_cd'
            with open(cd_file, 'w') as f:
                f.write(str(icloud_path))

            # Clear screen
            self.clear_screen()

            self.console.print()

            # Run ls command to show contents
            try:
                result = subprocess.run(['ls', '-la'], capture_output=True, text=True, cwd=icloud_path)
                if result.returncode == 0:
                    self.console.print("[bold blue]Directory Contents:[/bold blue]")
                    self.console.print(result.stdout)
                else:
                    self.console.print("[yellow]Could not list directory contents[/yellow]")
            except Exception as e:
                self.console.print(f"[yellow]Error running ls: {e}[/yellow]")

            # Exit with special code to indicate directory change
            sys.exit(42)

        except Exception as e:
            self.console.print(f"[red]Error navigating to iCloud Drive: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'

    def handle_thecode_menu(self):
        """Handle navigation to Mode Terminal source code"""
        mode_path = Path.home() / '.mode'

        try:
            if not mode_path.exists():
                self.console.print("[red]Mode Terminal source directory not found.[/red]")
                input("Press Enter to continue...")
                return 'continue'

            # Write the target directory to a file that the shell can read
            cd_file = Path.home() / '.mode' / '.mode_cd'
            with open(cd_file, 'w') as f:
                f.write(str(mode_path))

            # Clear screen
            self.clear_screen()

            self.console.print()

            # Run ls command to show contents
            try:
                result = subprocess.run(['ls', '-la'], capture_output=True, text=True, cwd=mode_path)
                if result.returncode == 0:
                    self.console.print("[bold blue]Source Code Directory Contents:[/bold blue]")
                    self.console.print(result.stdout)
                else:
                    self.console.print("[yellow]Could not list directory contents[/yellow]")
            except Exception as e:
                self.console.print(f"[yellow]Error running ls: {e}[/yellow]")

            # Exit with special code to indicate directory change
            sys.exit(42)

        except Exception as e:
            self.console.print(f"[red]Error navigating to source directory: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'

    def handle_john_ssh(self):
        """Handle SSH connection to butler@john"""
        try:
            self.clear_screen()

            self.console.print("[bold blue]Connecting to butler@john...[/bold blue]")
            self.console.print()

            ssh_command = ['ssh', 'butler@john']
            subprocess.run(ssh_command)

            self.console.print()
            self.console.print("[green]SSH session ended. Returning to terminal.[/green]")
            sys.exit(0)

        except Exception as e:
            self.console.print(f"[red]Error connecting to john: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'

    def handle_claude_usage(self):
        """Handle opening Claude AI usage settings in browser"""
        import webbrowser

        try:
            webbrowser.open('https://claude.ai/settings/usage')
            self.console.print("[green]Opened Claude usage settings in browser.[/green]")
            sys.exit(0)

        except Exception as e:
            self.console.print(f"[red]Error opening browser: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'

    def handle_help_menu(self):
        """Handle help and documentation menu"""
        return self.help_system.show_help_menu()

    def run(self):
        """Main application loop"""
        while True:
            try:
                choice = self.run_main_menu()

                if choice == 'exit':
                    break
                elif choice == 'normal':
                    self.handle_normal_use()
                    break
                elif choice == 'filesystem':
                    result = self.handle_filesystem_menu()
                    if result == 'exit':
                        break
                elif choice == 'john':
                    result = self.handle_john_ssh()
                    if result == 'exit':
                        break
                elif choice == 'claude_usage':
                    result = self.handle_claude_usage()
                    if result == 'exit':
                        break
                elif choice == 'thecode':
                    result = self.handle_thecode_menu()
                    if result == 'exit':
                        break
                elif choice == 'projects':
                    result = self.handle_projects_menu()
                    if result == 'exit':
                        break
                elif choice == 'bookmarks':
                    result = self.bookmark_manager.show_menu()
                    if result == 'exit':
                        break
                elif choice == 'help':
                    result = self.handle_help_menu()
                    if result == 'exit':
                        break

            except KeyboardInterrupt:
                break
            except SystemExit:
                # Re-raise SystemExit to allow proper exit codes
                raise
            except Exception as e:
                self.console.print(f"[red]An error occurred: {e}[/red]")
                input("Press Enter to continue...")

        # Save config before exit
        self.save_config()


def main():
    """Main entry point for the application"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Mode Terminal - Interactive development workflow navigator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mode            Launch interactive navigator
  mode --version  Show version information

For more information, visit: https://github.com/JadenB9/mode-terminal
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Mode Terminal v2.0'
    )

    parser.add_argument(
        '--config',
        help='Path to custom configuration file',
        default=None
    )

    args = parser.parse_args()

    try:
        app = ModeApp()
        if args.config:
            import json
            with open(args.config, 'r') as f:
                custom_config = json.load(f)
                app.config.update(custom_config)

        app.run()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        # Re-raise SystemExit to allow proper exit codes (like exit code 42)
        raise
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
