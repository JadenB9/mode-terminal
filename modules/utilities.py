import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from inquirer import text, confirm
from menu_input import show_menu

class Utilities:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        self.zshrc_path = Path.home() / '.zshrc'
        
    def show_menu(self):
        """Show utilities menu"""
        options = [
            {
                'name': '• Alias Creator - Create new terminal aliases',
                'value': 'alias_creator',
                'description': 'Prompt for alias name and command, add to ~/.zshrc'
            },
            {
                'name': '• Alias Manager - View and manage existing aliases',
                'value': 'alias_manager',
                'description': 'View, edit, or remove existing aliases'
            },
            {
                'name': '• Messenger Integration - Connect to messaging (TODO)',
                'value': 'messenger',
                'description': 'Connect to messaging services - In Development'
            },
            {
                'name': '• Back to Main Menu',
                'value': 'back',
                'description': 'Return to the main menu'
            }
        ]
        
        while True:
            try:
                result = show_menu(
                    self.console,
                    "Utilities",
                    options
                )
                
                if result == 'BACK' or result == 'back':
                    return 'continue'
                elif result == 'alias_creator':
                    self.alias_creator()
                elif result == 'alias_manager':
                    self.alias_manager()
                elif result == 'messenger':
                    self.messenger_integration()
                    
            except KeyboardInterrupt:
                return 'continue'
                
    def alias_creator(self):
        """Create new terminal aliases"""
        try:
            self.console.clear()
            self.console.print(Panel("Alias Creator", style="bold blue"))
            self.console.print()
            
            self.console.print("[blue]Create a new terminal alias[/blue]")
            self.console.print("[dim]Example: alias='ll' command='ls -la'[/dim]")
            self.console.print()
            
            # Get alias name
            alias_name = text("Enter alias name (without 'alias' keyword):")
            if not alias_name:
                return
                
            # Validate alias name
            if not alias_name.replace('_', '').replace('-', '').isalnum():
                self.console.print("[red]❌ Alias name can only contain letters, numbers, hyphens, and underscores[/red]")
                input("Press Enter to continue...")
                return
                
            # Check if alias already exists
            existing_aliases = self.get_existing_aliases()
            if alias_name in existing_aliases:
                self.console.print(f"[yellow]⚠️ Alias '{alias_name}' already exists:[/yellow]")
                self.console.print(f"[dim]{existing_aliases[alias_name]}[/dim]")
                
                if not confirm("Do you want to overwrite it?"):
                    return
                    
            # Get command
            command = text("Enter the full command:")
            if not command:
                return
                
            # Preview the alias
            self.console.print()
            self.console.print(f"[blue]Preview:[/blue]")
            self.console.print(f"[green]alias {alias_name}='{command}'[/green]")
            
            if not confirm("Add this alias?"):
                return
                
            # Add alias to config and .zshrc
            self.add_alias(alias_name, command)
            
            self.console.print(f"[green]✅ Alias '{alias_name}' added successfully![/green]")
            self.console.print("[blue]Restart your terminal or run 'source ~/.zshrc' to use the new alias[/blue]")
            
        except Exception as e:
            self.console.print(f"[red]Error creating alias: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def alias_manager(self):
        """Manage existing aliases"""
        try:
            self.console.clear()
            self.console.print(Panel("Alias Manager", style="bold blue"))
            self.console.print()
            
            aliases = self.get_existing_aliases()
            
            if not aliases:
                self.console.print("[yellow]No custom aliases found in ~/.zshrc[/yellow]")
                input("Press Enter to continue...")
                return
                
            # Display aliases in a table
            table = Table(title="Current Aliases")
            table.add_column("Alias", style="cyan")
            table.add_column("Command", style="white") 
            table.add_column("Source", style="green")
            
            for alias_name, command in aliases.items():
                table.add_row(alias_name, command, "~/.zshrc")
                
            self.console.print(table)
            self.console.print()
            
            # Management options
            mgmt_options = [
                'View alias details',
                'Remove an alias',
                'Edit an alias',
                'Back to Utilities Menu'
            ]
            
            choice = list_input(
                "Select action:",
                choices=mgmt_options,
                carousel=True
            )
            
            if choice == 'View alias details':
                self.view_alias_details(aliases)
            elif choice == 'Remove an alias':
                self.remove_alias(aliases)
            elif choice == 'Edit an alias':
                self.edit_alias(aliases)
                
        except Exception as e:
            self.console.print(f"[red]Error managing aliases: {e}[/red]")
            input("Press Enter to continue...")
            
    def view_alias_details(self, aliases: Dict[str, str]):
        """View details of a specific alias"""
        if not aliases:
            return
            
        alias_choices = list(aliases.keys()) + ['Back']
        choice = list_input(
            "Select alias to view:",
            choices=alias_choices,
            carousel=True
        )
        
        if choice != 'Back' and choice in aliases:
            self.console.print()
            self.console.print(f"[bold cyan]Alias: {choice}[/bold cyan]")
            self.console.print(f"[white]Command: {aliases[choice]}[/white]")
            self.console.print(f"[dim]Usage: {choice}[/dim]")
            
            input("\nPress Enter to continue...")
            
    def remove_alias(self, aliases: Dict[str, str]):
        """Remove an alias"""
        if not aliases:
            return
            
        alias_choices = list(aliases.keys()) + ['Back']
        choice = list_input(
            "Select alias to remove:",
            choices=alias_choices,
            carousel=True
        )
        
        if choice != 'Back' and choice in aliases:
            self.console.print(f"[yellow]Removing alias: {choice} = '{aliases[choice]}'[/yellow]")
            
            if confirm("Are you sure you want to remove this alias?"):
                if self.remove_alias_from_zshrc(choice):
                    # Remove from config
                    if 'aliases' in self.config and choice in self.config['aliases']:
                        del self.config['aliases'][choice]
                        
                    self.console.print(f"[green]✅ Alias '{choice}' removed successfully![/green]")
                    self.console.print("[blue]Restart your terminal or run 'source ~/.zshrc' to apply changes[/blue]")
                else:
                    self.console.print(f"[red]❌ Failed to remove alias '{choice}'[/red]")
                    
                input("Press Enter to continue...")
                
    def edit_alias(self, aliases: Dict[str, str]):
        """Edit an existing alias"""
        if not aliases:
            return
            
        alias_choices = list(aliases.keys()) + ['Back']
        choice = list_input(
            "Select alias to edit:",
            choices=alias_choices,
            carousel=True
        )
        
        if choice != 'Back' and choice in aliases:
            current_command = aliases[choice]
            
            self.console.print(f"[blue]Current command for '{choice}': {current_command}[/blue]")
            new_command = text("Enter new command:", default=current_command)
            
            if new_command and new_command != current_command:
                if confirm(f"Update alias '{choice}' to '{new_command}'?"):
                    # Remove old alias and add new one
                    if self.remove_alias_from_zshrc(choice):
                        self.add_alias(choice, new_command)
                        self.console.print(f"[green]✅ Alias '{choice}' updated successfully![/green]")
                        self.console.print("[blue]Restart your terminal or run 'source ~/.zshrc' to apply changes[/blue]")
                    else:
                        self.console.print(f"[red]❌ Failed to update alias '{choice}'[/red]")
                        
                    input("Press Enter to continue...")
                    
    def get_existing_aliases(self) -> Dict[str, str]:
        """Get existing aliases from .zshrc"""
        aliases = {}
        
        try:
            if self.zshrc_path.exists():
                with open(self.zshrc_path, 'r') as f:
                    content = f.read()
                    
                # Parse aliases
                import re
                alias_pattern = r'alias\s+([^=]+)=(["\']?)([^"\'\n]+)\2'
                matches = re.findall(alias_pattern, content)
                
                for match in matches:
                    alias_name = match[0].strip()
                    command = match[2].strip()
                    aliases[alias_name] = command
                    
        except Exception as e:
            self.console.print(f"[red]Error reading .zshrc: {e}[/red]")
            
        return aliases
        
    def add_alias(self, alias_name: str, command: str):
        """Add alias to .zshrc and config"""
        try:
            # Add to config
            if 'aliases' not in self.config:
                self.config['aliases'] = {}
            self.config['aliases'][alias_name] = command
            
            # Add to .zshrc
            alias_line = f"alias {alias_name}='{command}'\n"
            
            # Check if .zshrc exists, create if not
            if not self.zshrc_path.exists():
                self.zshrc_path.touch()
                
            # Add mode aliases section if it doesn't exist
            with open(self.zshrc_path, 'r') as f:
                content = f.read()
                
            if '# Mode Terminal Navigator Aliases' not in content:
                content += '\n# Mode Terminal Navigator Aliases\n'
                
            content += alias_line
            
            with open(self.zshrc_path, 'w') as f:
                f.write(content)
                
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error adding alias: {e}[/red]")
            return False
            
    def remove_alias_from_zshrc(self, alias_name: str) -> bool:
        """Remove alias from .zshrc"""
        try:
            if not self.zshrc_path.exists():
                return False
                
            with open(self.zshrc_path, 'r') as f:
                lines = f.readlines()
                
            # Filter out the alias line
            import re
            new_lines = []
            alias_pattern = rf'alias\s+{re.escape(alias_name)}\s*='
            
            for line in lines:
                if not re.match(alias_pattern, line.strip()):
                    new_lines.append(line)
                    
            with open(self.zshrc_path, 'w') as f:
                f.writelines(new_lines)
                
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error removing alias: {e}[/red]")
            return False
            
    def messenger_integration(self):
        """Placeholder for messenger integration"""
        self.console.clear()
        self.console.print(Panel("Messenger Integration", style="bold blue"))
        self.console.print()
        
        self.console.print("[yellow]🚧 Messenger Integration is in development[/yellow]")
        self.console.print()
        self.console.print("Planned features:")
        self.console.print("• Slack integration")
        self.console.print("• Discord webhook support")
        self.console.print("• Email notifications")
        self.console.print("• SMS alerts for system events")
        self.console.print()
        self.console.print("[blue]This feature will be available in a future update.[/blue]")
        
        input("Press Enter to continue...")