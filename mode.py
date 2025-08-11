#!/Library/Frameworks/Python.framework/Versions/3.12/bin/python3

# Mode Terminal v1.0 - Interactive terminal navigator with AI assistant
# https://github.com/JadenB9/mode-terminal

import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages')
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from inquirer import list_input, text, confirm

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from project_manager import ProjectManager
from file_navigator import FileNavigator  
from dev_tools import DevTools
from system_utils import SystemUtils
from help_system import HelpSystem
from ai_assistant import AIAssistant
from menu_input import show_menu

class ModeApp:
    def __init__(self):
        self.console = Console()
        self.config_path = Path.home() / '.mode' / 'config.json'
        self.config = self.load_config()
        
        # Initialize modules
        self.project_manager = ProjectManager(self.config, self.console)
        self.file_navigator = FileNavigator(self.config, self.console)
        self.dev_tools = DevTools(self.config, self.console)
        self.system_utils = SystemUtils(self.config, self.console)
        self.help_system = HelpSystem(self.config, self.console)
        self.ai_assistant = AIAssistant(self.config, self.console)
        
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
        ascii_art = """[bold blue]
███╗   ███╗ ██████╗ ██████╗ ███████╗
████╗ ████║██╔═══██╗██╔══██╗██╔════╝
██╔████╔██║██║   ██║██║  ██║█████╗  
██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  
██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗
╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝

████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║     
   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║     
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝[/bold blue]"""
        
        subtitle = Text("Navigate your development workflow with ease", style="dim italic")
        
        self.console.print(ascii_art)
        self.console.print()
        self.console.print(subtitle, justify="center")
        self.console.print()
        
    def get_main_menu_options(self):
        """Get main menu options with descriptions"""
        return [
            {
                'name': '• Normal Use - Continue in current directory like normal',
                'value': 'normal',
                'description': 'Change to home directory, clear screen, exit cleanly'
            },
            {
                'name': '• iCloud Directory',
                'value': 'filesystem',
                'description': 'Navigate to iCloud Drive and continue working there'
            },
            {
                'name': '• Project & Development Management',
                'value': 'projects',
                'description': 'Manage projects, repositories, and development environments'
            },
            {
                'name': '• Development Tools',
                'value': 'devtools', 
                'description': 'Complete development toolkit: databases, ports, APIs, aliases, and utilities'
            },
            {
                'name': '• System & Maintenance',
                'value': 'system',
                'description': 'System info, security scans, and backup status'
            },
            {
                'name': '• The Code',
                'value': 'thecode',
                'description': 'Navigate to the Mode Terminal source code directory'
            },
            {
                'name': '• Help',
                'value': 'help',
                'description': 'Complete help system, guides, and troubleshooting'
            }
        ]
        
    def show_help_text(self, description: str):
        """Show contextual help text for the highlighted option"""
        if self.config.get('show_help_text', True):
            help_panel = Panel(
                description,
                title="Info",
                border_style="dim",
                padding=(0, 1)
            )
            self.console.print(help_panel)
            
    def run_main_menu(self):
        """Run the main menu loop"""
        options = self.get_main_menu_options()
        
        def show_main_help():
            self.console.clear()
            self.console.print(Panel("Mode Terminal - Main Menu Help", style="bold yellow"))
            self.console.print()
            
            help_table = Table(title="Available Options")
            help_table.add_column("Option", style="cyan", width=30)
            help_table.add_column("Description", style="white", width=50)
            
            for opt in options:
                help_table.add_row(opt['name'], opt['description'])
            
            self.console.print(help_table)
            self.console.print()
            self.console.print("[dim]Press any key to continue...[/dim]")
            
            
        
        while True:
            try:
                result = show_menu(
                    self.console,
                    "Mode Terminal - Main Menu", 
                    options,
                    show_main_help,
                    self.show_header,
                    self.ai_assistant
                )
                
                if result == 'BACK':
                    return 'exit'  # At main menu, back means exit
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
            # Exit the program so the user continues in the normal terminal
            import sys
            sys.exit(0)
        except Exception as e:
            self.console.print(f"[red]Error changing to {target_dir}: {e}[/red]")
            self.console.print("[yellow]Returning to normal terminal mode in current directory.[/yellow]")
            import sys
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
            
            # Show current location - removed duplicate message since shell function shows navigation
            self.console.print()
            
            # Run ls command to show contents
            try:
                result = subprocess.run(['ls', '-la'], capture_output=True, text=True, cwd=icloud_path)
                if result.returncode == 0:
                    # Display ls output with nice formatting
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
            
            # Show current location - removed duplicate message since shell function shows navigation
            self.console.print()
            
            # Run ls command to show contents
            try:
                result = subprocess.run(['ls', '-la'], capture_output=True, text=True, cwd=mode_path)
                if result.returncode == 0:
                    # Display ls output with nice formatting
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
        
    def handle_devtools_menu(self):
        """Handle development tools menu"""
        return self.dev_tools.show_menu()
        
    def handle_system_menu(self):
        """Handle system and maintenance menu"""
        return self.system_utils.show_menu()
        
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
                elif choice == 'thecode':
                    result = self.handle_thecode_menu()
                    if result == 'exit':
                        break
                elif choice == 'projects':
                    result = self.handle_projects_menu()
                    if result == 'exit':
                        break
                elif choice == 'devtools':
                    result = self.handle_devtools_menu()
                    if result == 'exit':
                        break
                elif choice == 'system':
                    result = self.handle_system_menu()
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
  
For more information, visit: https://github.com/JadenB9/mode-terminal-navigator
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='Mode Terminal v1.0.0'
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
            # Load custom config if provided
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