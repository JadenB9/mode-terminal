import os
from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from menu_input import show_menu

class HelpSystem:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        
    def show_help_menu(self):
        """Show the main help menu"""
        options = [
            {
                'name': '• Quick Start Guide - Get started with Mode',
                'value': 'quick_start',
                'description': 'Essential first steps and basic navigation'
            },
            {
                'name': '• Navigation Controls - Keyboard shortcuts and controls',
                'value': 'navigation',
                'description': 'All keyboard shortcuts and navigation methods'
            },
            {
                'name': '• Feature Overview - Complete feature list',
                'value': 'features',
                'description': 'Detailed breakdown of all available features'
            },
            {
                'name': '• Configuration Guide - Settings and customization',
                'value': 'configuration',
                'description': 'How to customize and configure Mode'
            },
            {
                'name': '• Troubleshooting - Common issues and solutions',
                'value': 'troubleshooting',
                'description': 'Fix common problems and error messages'
            },
            {
                'name': '• Tips & Tricks - Advanced usage patterns',
                'value': 'tips',
                'description': 'Pro tips to get the most out of Mode'
            },
            {
                'name': '• Quick Reference Card - Essential shortcuts and info',
                'value': 'quick_ref',
                'description': 'Compact reference for keyboard shortcuts and features'
            },
            {
                'name': '• Back to Main Menu',
                'value': 'back',
                'description': 'Return to the main Mode menu'
            }
        ]
        
        while True:
            try:
                result = show_menu(
                    self.console,
                    "Mode Terminal Navigator - Help System",
                    options
                )
                
                if result == 'BACK' or result == 'back':
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
                elif result == 'tips':
                    self.show_tips_help()
                elif result == 'quick_ref':
                    self.show_quick_reference()
                    
            except KeyboardInterrupt:
                return 'continue'
                
    def show_quick_start(self):
        """Show quick start guide"""
        self.console.clear()
        self.console.print(Panel("Quick Start Guide", style="bold yellow"))
        self.console.print()
        
        guide_text = """
[bold cyan]Welcome to Mode Terminal Navigator![/bold cyan]

[yellow]🚀 Getting Started:[/yellow]
1. Use ↑↓ arrow keys to navigate menus
2. Press Enter to select an option
3. Press 'b' or Ctrl+C to go back
4. Press 'h' in any menu for help

[yellow]🏠 First Steps:[/yellow]
• Try "Normal Use" to return to regular terminal
• Explore "Project & Development" to manage code projects
• Use "File System & Organization" for quick navigation
• Check "System & Maintenance" for system health

[yellow]⚡ Pro Tips:[/yellow]
• Most operations return you to the same menu section
• Configuration is saved automatically
• Create aliases in Utilities for frequently used commands
• Use Project Switcher to quickly jump between projects

[yellow]❓ Need More Help?:[/yellow]
• Press 'h' in any menu for context-sensitive help
• Check the full Feature Overview for detailed explanations
• Visit Configuration Guide to customize your experience
        """
        
        self.console.print(Panel(guide_text, border_style="yellow"))
        
        input("\nPress Enter to continue...")
        
    def show_navigation_help(self):
        """Show navigation controls help"""
        self.console.clear()
        self.console.print(Panel("Navigation Controls & Keyboard Shortcuts", style="bold yellow"))
        self.console.print()
        
        # Create navigation table
        nav_table = Table(title="Keyboard Controls", show_header=True)
        nav_table.add_column("Key(s)", style="cyan", width=15)
        nav_table.add_column("Action", style="white", width=30)
        nav_table.add_column("Context", style="green", width=20)
        
        nav_table.add_row("↑ ↓", "Navigate menu options", "All menus")
        nav_table.add_row("Enter", "Select current option", "All menus") 
        nav_table.add_row("b", "Go back one menu level", "Most menus")
        nav_table.add_row("Ctrl+C", "Exit current operation/menu", "Anywhere")
        nav_table.add_row("h", "Show context help", "Most menus")
        nav_table.add_row("ESC", "Cancel current operation", "Text inputs")
        nav_table.add_row("Tab", "Auto-complete", "Text inputs")
        nav_table.add_row("q", "Quick quit", "Some contexts")
        
        self.console.print(nav_table)
        self.console.print()
        
        flow_text = """
[bold cyan]Menu Flow:[/bold cyan]

[yellow]Standard Navigation Pattern:[/yellow]
Main Menu → Sub Menu → Action → [bold green]Back to Sub Menu[/bold green]

[yellow]Special Cases:[/yellow]
• "Normal Use" exits Mode completely
• Project operations may change directories and exit
• File navigation may exit to selected directory

[yellow]Help Access:[/yellow]
• Press 'h' in any menu for contextual help
• Help is always available without losing your place
• Context-sensitive tips show relevant information
        """
        
        self.console.print(Panel(flow_text, border_style="cyan"))
        
        input("\nPress Enter to continue...")
        
    def show_features_help(self):
        """Show comprehensive features overview"""
        self.console.clear()
        self.console.print(Panel("Complete Feature Overview", style="bold yellow"))
        self.console.print()
        
        # Project Management Features
        proj_table = Table(title="🏠 Project & Development Management", show_header=True)
        proj_table.add_column("Feature", style="cyan", width=20)
        proj_table.add_column("Description", style="white", width=50)
        
        proj_table.add_row("New Git Project", "Create project directory, initialize Git, link to GitHub")
        proj_table.add_row("Clone Repository", "Clone repos from your GitHub account") 
        proj_table.add_row("Project Switcher", "Navigate between projects with modification dates")
        proj_table.add_row("Environment Setup", "Auto-setup for React, Node.js, Python, and more")
        
        self.console.print(proj_table)
        self.console.print()
        
        # File System Features  
        file_table = Table(title="🗂️ File System & Organization", show_header=True)
        file_table.add_column("Feature", style="cyan", width=20)
        file_table.add_column("Description", style="white", width=50)
        
        file_table.add_row("Quick Navigation", "Fast access to Desktop, Documents, Downloads, Apps")
        file_table.add_row("iCloud Drive Browser", "Navigate iCloud folders with file preview")
        file_table.add_row("Directory Contents", "View files with sizes, dates, and types")
        file_table.add_row("Path Selection", "Choose directories to navigate to")
        
        self.console.print(file_table)
        self.console.print()
        
        # Development Tools
        dev_table = Table(title="🛠️ Development Tools", show_header=True)
        dev_table.add_column("Feature", style="cyan", width=20)
        dev_table.add_column("Description", style="white", width=50)
        
        dev_table.add_row("Database Explorer", "Find and examine database configurations")
        dev_table.add_row("Port Scanner", "Scan for active services on dev ports")
        dev_table.add_row("Process Monitor", "View running processes with security checks")
        dev_table.add_row("Service Detection", "Identify development servers and services")
        
        self.console.print(dev_table)
        self.console.print()
        
        # System & Maintenance
        sys_table = Table(title="⚙️ System & Maintenance", show_header=True)
        sys_table.add_column("Feature", style="cyan", width=20)
        sys_table.add_column("Description", style="white", width=50)
        
        sys_table.add_row("Brew Manager", "Update, search, cleanup Homebrew packages")
        sys_table.add_row("System Info", "CPU, memory, disk usage with statistics")
        sys_table.add_row("Network Diagnostics", "Connectivity, DNS, speed tests")
        sys_table.add_row("Security Scan", "Check for suspicious processes")
        sys_table.add_row("Backup Status", "Verify Time Machine and iCloud sync")
        
        self.console.print(sys_table)
        self.console.print()
        
        # Utilities
        util_table = Table(title="🔧 Utilities", show_header=True)
        util_table.add_column("Feature", style="cyan", width=20)
        util_table.add_column("Description", style="white", width=50)
        
        util_table.add_row("Alias Creator", "Create terminal aliases with .zshrc integration")
        util_table.add_row("Alias Manager", "View, edit, remove existing aliases")
        util_table.add_row("Config Management", "Persistent settings and preferences")
        util_table.add_row("Shell Integration", "Automatic shell configuration updates")
        
        self.console.print(util_table)
        
        input("\nPress Enter to continue...")
        
    def show_configuration_help(self):
        """Show configuration help"""
        self.console.clear()
        self.console.print(Panel("Configuration Guide", style="bold yellow"))
        self.console.print()
        
        config_text = f"""
[bold cyan]Configuration File Location:[/bold cyan]
~/.mode/config.json

[bold cyan]Current Settings:[/bold cyan]
• GitHub Username: [green]{self.config.get('github_username', 'Not set')}[/green]
• Projects Path: [green]{self.config.get('projects_path', 'Not set')}[/green]
• Default Directory: [green]{self.config.get('default_directory', 'Not set')}[/green]
• Auto Clear Screen: [green]{self.config.get('auto_clear_screen', True)}[/green]
• Show Help Text: [green]{self.config.get('show_help_text', True)}[/green]

[yellow]📝 Editable Settings:[/yellow]

[bold]github_username[/bold] - Your GitHub username for repo operations
[bold]projects_path[/bold] - Default location for project files  
[bold]default_directory[/bold] - Directory for "Normal Use" mode
[bold]auto_clear_screen[/bold] - Whether to clear screen between menus
[bold]show_help_text[/bold] - Display contextual help for options
[bold]common_ports[/bold] - Ports to scan in port scanner tool

[yellow]🔧 How to Edit:[/yellow]
1. Edit ~/.mode/config.json directly with any text editor
2. Changes are loaded automatically on next Mode launch
3. Invalid JSON will show an error message
4. Backup your config before making major changes

[yellow]🔄 Reset Configuration:[/yellow]
Delete ~/.mode/config.json and restart Mode to restore defaults
        """
        
        self.console.print(Panel(config_text, border_style="yellow"))
        
        input("\nPress Enter to continue...")
        
    def show_troubleshooting_help(self):
        """Show troubleshooting help"""
        self.console.clear()
        self.console.print(Panel("Troubleshooting Guide", style="bold yellow"))
        self.console.print()
        
        trouble_text = """
[bold red]🚨 Common Issues & Solutions:[/bold red]

[yellow]Issue: "mode" command not found[/yellow]
• Restart your terminal
• Check if ~/.local/bin is in PATH: echo $PATH
• Add to ~/.zshrc: export PATH="$HOME/.local/bin:$PATH"
• Run: source ~/.zshrc

[yellow]Issue: Python import errors[/yellow]
• Run: ~/.mode/setup_python.py
• Manually install: pip3 install --break-system-packages rich inquirer requests psutil
• Use virtual environment if system packages fail

[yellow]Issue: Permission errors[/yellow]
• Fix permissions: chmod +x ~/.mode/mode.py
• For global install: sudo chown $(whoami) /usr/local/bin/mode

[yellow]Issue: GitHub features not working[/yellow]
• Install GitHub CLI: brew install gh
• Authenticate: gh auth login
• Set username in ~/.mode/config.json

[yellow]Issue: Configuration file errors[/yellow]
• Check JSON syntax in ~/.mode/config.json
• Delete config file to restore defaults
• Backup before making changes

[yellow]Issue: Menu navigation problems[/yellow]
• Use arrow keys (↑↓) not WASD
• Press Enter to select, not Space
• Use 'b' or Ctrl+C to go back

[yellow]Issue: Performance problems[/yellow]
• Check available memory with System Info
• Close other terminal applications
• Restart Mode if it becomes slow

[bold green]✅ Getting Help:[/bold green]
• Press 'h' in any menu for context help
• Check ~/.mode/README.md for detailed docs
• Review ~/.mode/config.json for settings
        """
        
        self.console.print(Panel(trouble_text, border_style="red"))
        
        input("\nPress Enter to continue...")
        
    def show_tips_help(self):
        """Show tips and tricks"""
        self.console.clear()
        self.console.print(Panel("Tips & Tricks for Power Users", style="bold yellow"))
        self.console.print()
        
        tips_text = """
[bold green]💡 Pro Tips:[/bold green]

[yellow]🚀 Productivity Shortcuts:[/yellow]
• Use Project Switcher to quickly jump between recent projects
• Create aliases for frequently used directory paths
• Set up environment templates for new project types
• Use Port Scanner to check what services are running

[yellow]⚡ Advanced Navigation:[/yellow]
• Press 'b' in any menu to go back quickly
• Use Ctrl+C for instant exit from any operation
• Operations return you to the same section for efficiency
• Help ('h') is context-aware and shows relevant info

[yellow]🎯 Workflow Optimization:[/yellow]
• Keep your Projects folder organized by type
• Use descriptive project names for easy switching  
• Regularly clean up with Brew Manager
• Monitor system health with System Info

[yellow]🔧 Customization Tricks:[/yellow]
• Edit ~/.mode/config.json for personalized settings
• Add custom ports to common_ports for your stack
• Disable auto_clear_screen if you prefer persistent output
• Set show_help_text to false once you know the features

[yellow]🛡️ Security Best Practices:[/yellow]
• Run Security Scan periodically
• Check Port Scanner results for unknown services
• Keep Homebrew packages updated
• Monitor backup status regularly

[yellow]📂 Project Management:[/yellow]
• Use consistent naming conventions for projects
• Initialize Git from the start with New Git Project
• Link projects to GitHub early in development
• Use Environment Setup for quick project scaffolding

[yellow]🔍 Debugging & Development:[/yellow]
• Use Database Explorer to find connection configs
• Port Scanner helps debug service conflicts
• System Info shows resource usage during development
• Network Diagnostics troubleshoots connectivity issues

[bold cyan]🎉 Hidden Features:[/bold cyan]
• Press 'q' in some contexts for quick quit
• Tab completion works in text inputs
• Recent projects are automatically tracked
• Aliases are immediately available after creation
        """
        
        self.console.print(Panel(tips_text, border_style="green"))
        
        input("\nPress Enter to continue...")
        
    def show_quick_reference(self):
        """Show quick reference card"""
        self.console.clear()
        self.console.print(Panel("Quick Reference Card", style="bold yellow"))
        self.console.print()
        
        # Navigation Controls Table
        nav_table = Table(title="🎮 Navigation Controls", show_header=True)
        nav_table.add_column("Key", style="cyan", width=8)
        nav_table.add_column("Action", style="white", width=25)
        nav_table.add_column("Context", style="green", width=15)
        
        nav_table.add_row("↑ ↓", "Navigate menu options", "All menus")
        nav_table.add_row("Enter", "Select current option", "All menus")
        nav_table.add_row("b", "Go back one menu", "Most menus")
        nav_table.add_row("h", "Show context help", "Most menus")
        nav_table.add_row("Ctrl+C", "Exit operation", "Anywhere")
        
        self.console.print(nav_table)
        self.console.print()
        
        # Main Features
        features_text = """
[bold cyan]🏠 Main Features:[/bold cyan]
• [yellow]Normal Use[/yellow] - Return to terminal
• [yellow]Projects[/yellow] - Git repos, environment setup
• [yellow]File System[/yellow] - Navigate directories, iCloud
• [yellow]Dev Tools[/yellow] - Port scanner, database explorer
• [yellow]System[/yellow] - Homebrew, system info, security
• [yellow]Utilities[/yellow] - Aliases, configuration

[bold cyan]⚡ Pro Tips:[/bold cyan]
• Operations return to same menu section
• Press 'h' for context-sensitive help
• Configuration auto-saves changes
• Use Project Switcher for quick jumping

[bold cyan]🔧 Files:[/bold cyan]
• Config: [green]~/.mode/config.json[/green]
• Docs: [green]~/.mode/README.md[/green]
• Setup: [green]~/.mode/setup_python.py[/green]
        """
        
        self.console.print(Panel(features_text, border_style="cyan"))
        
        input("\nPress Enter to continue...")