import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from inquirer import list_input, confirm
from menu_input import show_menu

class FileNavigator:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        
    def show_menu(self):
        """Show file system navigation menu"""
        options = [
            {
                'name': '• Quick Navigation - Navigate to common directories',
                'value': 'quick_nav',
                'description': 'Quick access to Desktop, Documents, Downloads, Applications, and iCloud Drive'
            },
            {
                'name': '• Back to Main Menu',
                'value': 'back',
                'description': 'Return to the main menu'
            }
        ]
        
        while True:
            self.console.clear()
            self.console.print(Panel("File System & Organization", style="bold cyan"))
            self.console.print()
            
            menu_choices = [opt['name'] for opt in options]
            
            try:
                result = show_menu(
                    self.console,
                    "File System & Organization",
                    options
                )
                
                if result == 'BACK' or result == 'back':
                    return 'continue'
                elif result == 'quick_nav':
                    nav_result = self.quick_navigation()
                    if nav_result == 'exit':
                        return 'exit'
                    
            except KeyboardInterrupt:
                return 'continue'
                
    def quick_navigation(self):
        """Quick navigation to common directories"""
        home_path = Path.home()
        
        # Standard directories
        nav_options = [
            {
                'name': '> Desktop',
                'path': home_path / 'Desktop',
                'description': 'Navigate to Desktop folder'
            },
            {
                'name': '> Documents', 
                'path': home_path / 'Documents',
                'description': 'Navigate to Documents folder'
            },
            {
                'name': '> Downloads',
                'path': home_path / 'Downloads', 
                'description': 'Navigate to Downloads folder'
            },
            {
                'name': '> Applications',
                'path': Path('/Applications'),
                'description': 'Navigate to Applications folder'
            },
            {
                'name': '> iCloud Drive',
                'path': home_path / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs',
                'description': 'Navigate to iCloud Drive with folder browser'
            }
        ]
        
        # Add back option
        nav_options.append({
            'name': '> Back to File System Menu',
            'path': None,
            'description': 'Return to File System & Organization menu'
        })
        
        while True:
            self.console.clear()
            self.console.print(Panel("Quick Navigation", style="bold cyan"))
            self.console.print()
            
            menu_choices = [opt['name'] for opt in nav_options]
            
            try:
                choice = list_input(
                    "Select a directory:",
                    choices=menu_choices,
                    carousel=True
                )
                
                selected_option = next(opt for opt in nav_options if opt['name'] == choice)
                
                if selected_option['path'] is None:  # Back option
                    return 'continue'
                    
                if selected_option['name'] == '> iCloud Drive':
                    result = self.browse_icloud_drive()
                    if result == 'exit':
                        return 'exit'
                else:
                    result = self.navigate_to_directory(selected_option['path'])
                    if result == 'exit':
                        return 'exit'
                        
            except KeyboardInterrupt:
                return 'continue'
                
    def navigate_to_directory(self, path: Path):
        """Navigate to a specific directory"""
        try:
            if not path.exists():
                self.console.print(f"[red]Directory does not exist: {path}[/red]")
                input("Press Enter to continue...")
                return 'continue'
                
            self.console.clear()
            # Removed duplicate navigation message since shell function shows navigation
            
            # Show directory contents
            self.show_directory_contents(path)
            
            # Ask if user wants to stay here or continue browsing
            from inquirer import confirm
            if confirm("Stay in this directory and exit mode?"):
                # Write the target directory to a file that the shell can read
                cd_file = Path.home() / '.mode' / '.mode_cd'
                with open(cd_file, 'w') as f:
                    f.write(str(path))
                
                # Exit with special code to indicate directory change
                import sys
                sys.exit(42)
            else:
                return 'continue'
                
        except SystemExit:
            # Re-raise SystemExit to allow proper exit codes (like exit code 42)
            raise
        except Exception as e:
            self.console.print(f"[red]Error navigating to directory: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'
            
    def browse_icloud_drive(self):
        """Browse iCloud Drive folders"""
        icloud_path = Path.home() / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'
        
        if not icloud_path.exists():
            self.console.print("[red]iCloud Drive not found. Make sure iCloud is set up.[/red]")
            input("Press Enter to continue...")
            return 'continue'
            
        return self.browse_directory(icloud_path, "iCloud Drive")
        
    def browse_directory(self, directory: Path, title: str):
        """Generic directory browser"""
        current_path = directory
        
        while True:
            try:
                self.console.clear()
                self.console.print(Panel(f"{title} - {current_path}", style="bold cyan"))
                self.console.print()
                
                # Get directory contents
                folders = []
                files = []
                
                try:
                    for item in current_path.iterdir():
                        if item.is_dir() and not item.name.startswith('.'):
                            folders.append(item)
                        elif item.is_file() and not item.name.startswith('.'):
                            files.append(item)
                except PermissionError:
                    self.console.print("[red]Permission denied accessing this directory.[/red]")
                    input("Press Enter to continue...")
                    return 'continue'
                    
                # Create menu options
                options = []
                
                # Add parent directory option (if not at root)
                if current_path != directory:
                    options.append({
                        'name': '> .. (Parent Directory)',
                        'type': 'parent',
                        'path': current_path.parent
                    })
                    
                # Add folders
                for folder in sorted(folders):
                    options.append({
                        'name': f'> {folder.name}',
                        'type': 'folder',
                        'path': folder
                    })
                    
                # Add action options
                options.extend([
                    {
                        'name': f'> Select Current Directory ({current_path.name})',
                        'type': 'select',
                        'path': current_path
                    },
                    {
                        'name': '> Back to Quick Navigation',
                        'type': 'back',
                        'path': None
                    }
                ])
                
                menu_choices = [opt['name'] for opt in options]
                
                choice = list_input(
                    "Select an option:",
                    choices=menu_choices,
                    carousel=True
                )
                
                selected_option = next(opt for opt in options if opt['name'] == choice)
                
                if selected_option['type'] == 'back':
                    return 'continue'
                elif selected_option['type'] == 'parent':
                    current_path = selected_option['path']
                elif selected_option['type'] == 'folder':
                    current_path = selected_option['path']
                elif selected_option['type'] == 'select':
                    result = self.navigate_to_directory(selected_option['path'])
                    if result == 'exit':
                        return 'exit'
                    
            except KeyboardInterrupt:
                return 'continue'
                
    def show_directory_contents(self, path: Path):
        """Show directory contents in a table"""
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
                    size = self.format_size(stat.st_size) if item.is_file() else "—"
                    modified = self.format_timestamp(stat.st_mtime)
                    item_type = "> Dir" if item.is_dir() else "> File"
                    
                    items.append((item_type, item.name, size, modified))
                    
            # Sort: directories first, then files, both alphabetically
            items.sort(key=lambda x: (x[0] != "> Dir", x[1].lower()))
            
            for item_type, name, size, modified in items[:20]:  # Show max 20 items
                table.add_row(item_type, name, size, modified)
                
            if len(items) > 20:
                table.add_row("...", f"and {len(items) - 20} more items", "", "")
                
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error listing directory contents: {e}[/red]")
            
    def format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
        
    def format_timestamp(self, timestamp: float) -> str:
        """Format timestamp in human-readable format"""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")