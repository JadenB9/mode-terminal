import os
import socket
import subprocess
import psutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.text import Text
from inquirer import text, list_input, confirm
from menu_input import show_menu

class DevTools:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        
    def show_menu(self):
        """Show development tools menu"""
        options = [
            {
                'name': '• Database Explorer - Connect to project databases',
                'value': 'db_explorer',
                'description': 'Search for database connections in j4den-cybersec and other projects'
            },
            {
                'name': '• Port Scanner - Scan local ports for active services',
                'value': 'port_scanner', 
                'description': 'Comprehensive port scanning with detailed process information'
            },
            {
                'name': '• API Endpoint Scanner - Find API endpoints',
                'value': 'api_scanner',
                'description': 'Scan project files for API endpoints and routes'
            },
            {
                'name': '• Environment Variables - View project env files',
                'value': 'env_viewer',
                'description': 'Browse and analyze environment variable files'
            },
            {
                'name': '• Connection Tester - Test database connections',
                'value': 'connection_tester',
                'description': 'Test connectivity to found database configurations'
            },
            {
                'name': '• Alias Creator - Create new terminal aliases',
                'value': 'alias_creator',
                'description': 'Create terminal aliases with automatic .zshrc integration'
            },
            {
                'name': '• Alias Manager - View and manage existing aliases',
                'value': 'alias_manager',
                'description': 'View, edit, or remove existing terminal aliases'
            },
            {
                'name': '• Brew Manager - Manage Homebrew packages',
                'value': 'brew_manager',
                'description': 'Update, search, cleanup Homebrew packages and dependencies'
            },
            {
                'name': '• Network Diagnostics - Test connectivity and speed',
                'value': 'network_diag',
                'description': 'Run connectivity tests, DNS resolution, and speed tests'
            },
            {
                'name': '• School Integration - Academic workflow tools',
                'value': 'school_integration',
                'description': 'Study management and academic tools (Coming Soon)'
            },
            {
                'name': '• Messenger Integration - Connect to messaging services',
                'value': 'messenger',
                'description': 'Slack, Discord, email notifications (In Development)'
            }
        ]
        
        while True:
            self.console.clear()
            self.console.print(Panel("Development Tools", style="bold magenta"))
            self.console.print()
            
            menu_choices = [opt['name'] for opt in options]
            
            try:
                result = show_menu(
                    self.console,
                    "Development Tools",
                    options
                )
                
                if result == 'BACK' or result == 'back':
                    return 'continue'
                elif result == 'db_explorer':
                    self.database_explorer()
                elif result == 'port_scanner':
                    self.port_scanner()
                elif result == 'api_scanner':
                    self.api_endpoint_scanner()
                elif result == 'env_viewer':
                    self.environment_viewer()
                elif result == 'connection_tester':
                    self.connection_tester()
                elif result == 'alias_creator':
                    self.alias_creator()
                elif result == 'alias_manager':
                    self.alias_manager()
                elif result == 'brew_manager':
                    self.brew_manager()
                elif result == 'network_diag':
                    self.network_diagnostics()
                elif result == 'school_integration':
                    self.school_integration()
                elif result == 'messenger':
                    self.messenger_integration()
                    
            except KeyboardInterrupt:
                return 'continue'
                
    def database_explorer(self):
        """Search for and display database connections"""
        try:
            self.console.clear()
            self.console.print(Panel("Database Explorer", style="bold magenta"))
            self.console.print()
            
            # Search for j4den-cybersec project in multiple locations
            projects_path = Path(self.config['projects_path'])
            
            # Try multiple possible locations
            possible_locations = [
                projects_path / 'j4den-cyber',
                projects_path / 'j4den-cybersec', 
                projects_path / 'website' / 'j4den-cybersec',
                projects_path / 'Website' / 'j4den-cybersec'
            ]
            
            j4den_project = None
            for location in possible_locations:
                if location.exists():
                    j4den_project = location
                    break
            
            if not j4den_project:
                self.console.print("[yellow]j4den-cybersec project not found in any expected locations.[/yellow]")
                self.console.print("[blue]Searched locations:[/blue]")
                for loc in possible_locations:
                    self.console.print(f"  • {loc}")
                
                # Ask user to specify location
                custom_location = input("\nEnter custom project path (or press Enter to skip): ").strip()
                if custom_location and Path(custom_location).exists():
                    j4den_project = Path(custom_location)
                else:
                    input("Press Enter to continue...")
                    return
                
            # Search for database configuration files
            db_configs = self.find_database_configs(j4den_project)
            
            if not db_configs:
                self.console.print("[yellow]No database configuration files found.[/yellow]")
                self.console.print("Searched for: .env, config.json, database.json, wrangler.toml")
                input("Press Enter to continue...")
                return
                
            # Display found configurations
            table = Table(title="Database Configurations Found")
            table.add_column("File", style="cyan")
            table.add_column("Type", style="green") 
            table.add_column("Location", style="yellow")
            table.add_column("Status", style="white")
            
            for config in db_configs:
                table.add_row(
                    config['file'],
                    config['type'],
                    str(config['path'].relative_to(j4den_project)),
                    config['status']
                )
                
            self.console.print(table)
            
            # Show configuration details if requested
            if db_configs:
                show_details = input("\nShow configuration details? (y/n): ").lower() == 'y'
                if show_details:
                    self.show_database_details(db_configs)
                    
        except Exception as e:
            self.console.print(f"[red]Error exploring databases: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def find_database_configs(self, project_path: Path) -> List[Dict[str, Any]]:
        """Find database configuration files in the project"""
        configs = []
        
        # Search patterns
        search_patterns = [
            ('.env', 'Environment Variables'),
            ('config.json', 'JSON Configuration'),
            ('database.json', 'Database Configuration'),
            ('wrangler.toml', 'Cloudflare Wrangler'),
            ('.env.local', 'Local Environment'),
            ('.env.production', 'Production Environment'),
            ('package.json', 'Package Configuration')
        ]
        
        for pattern, config_type in search_patterns:
            for config_file in project_path.rglob(pattern):
                if config_file.is_file():
                    status = "Found"
                    try:
                        # Try to read and validate the file
                        with open(config_file, 'r') as f:
                            content = f.read()
                            if any(db_keyword in content.lower() for db_keyword in 
                                  ['database', 'db_', 'postgresql', 'mysql', 'mongodb', 'cloudflare']):
                                status = "Contains DB Config"
                    except:
                        status = "Cannot Read"
                        
                    configs.append({
                        'file': config_file.name,
                        'type': config_type,
                        'path': config_file,
                        'status': status
                    })
                    
        return configs
        
    def show_database_details(self, configs: List[Dict[str, Any]]):
        """Show detailed database configuration information"""
        for i, config in enumerate(configs, 1):
            try:
                self.console.print(f"\n[bold cyan]{i}. {config['file']} ({config['type']})[/bold cyan]")
                
                with open(config['path'], 'r') as f:
                    content = f.read()
                    
                # Extract database-related lines (safely)
                db_lines = []
                for line in content.split('\n')[:50]:  # Limit to first 50 lines
                    if any(keyword in line.lower() for keyword in 
                          ['database', 'db_', 'postgresql', 'mysql', 'mongodb', 'cloudflare', 'connection']):
                        # Mask sensitive information
                        masked_line = self.mask_sensitive_data(line)
                        db_lines.append(masked_line)
                        
                if db_lines:
                    for line in db_lines[:10]:  # Show max 10 lines
                        self.console.print(f"  {line}")
                else:
                    self.console.print("  [yellow]No database configuration found in this file[/yellow]")
                    
            except Exception as e:
                self.console.print(f"  [red]Error reading file: {e}[/red]")
                
    def mask_sensitive_data(self, line: str) -> str:
        """Mask sensitive information in configuration lines"""
        import re
        
        # Mask passwords, keys, secrets
        patterns = [
            (r'(password\s*[:=]\s*)([^\s\n]+)', r'\1****'),
            (r'(secret\s*[:=]\s*)([^\s\n]+)', r'\1****'),
            (r'(key\s*[:=]\s*)([^\s\n]+)', r'\1****'),
            (r'(token\s*[:=]\s*)([^\s\n]+)', r'\1****'),
        ]
        
        masked_line = line
        for pattern, replacement in patterns:
            masked_line = re.sub(pattern, replacement, masked_line, flags=re.IGNORECASE)
            
        return masked_line
        
    def port_scanner(self):
        """Enhanced port scanner with options"""
        try:
            self.console.clear()
            self.console.print(Panel("Enhanced Port Scanner", style="bold magenta"))
            self.console.print()
            
            # Port scanner options
            scan_options = [
                'Quick Scan - Development ports only',
                'Full Scan - Common system and dev ports', 
                'Custom Range - Specify port range',
                'Specific Ports - Enter specific ports',
                'Back to Development Tools'
            ]
            
            choice = list_input(
                "Select scan type:",
                choices=scan_options,
                carousel=True
            )
            
            if choice == 'Back to Development Tools':
                return
            elif choice == 'Quick Scan - Development ports only':
                ports_to_scan = self.config.get('common_ports', [3000, 8000, 8080, 5000, 4000, 9000, 3001, 8001])
            elif choice == 'Full Scan - Common system and dev ports':
                dev_ports = self.config.get('common_ports', [3000, 8000, 8080, 5000, 4000, 9000, 3001, 8001])
                system_ports = [22, 80, 443, 25, 53, 110, 143, 993, 995, 21, 23, 135, 139, 445, 993, 995]
                ports_to_scan = sorted(list(set(dev_ports + system_ports)))
            elif choice == 'Custom Range - Specify port range':
                try:
                    start_port = int(input("Enter start port (1-65535): "))
                    end_port = int(input("Enter end port (1-65535): "))
                    if 1 <= start_port <= end_port <= 65535:
                        ports_to_scan = list(range(start_port, end_port + 1))
                    else:
                        self.console.print("[red]Invalid port range![/red]")
                        input("Press Enter to continue...")
                        return
                except ValueError:
                    self.console.print("[red]Invalid port numbers![/red]")
                    input("Press Enter to continue...")
                    return
            elif choice == 'Specific Ports - Enter specific ports':
                try:
                    port_input = input("Enter ports separated by commas (e.g., 80,443,3000): ")
                    ports_to_scan = [int(p.strip()) for p in port_input.split(',') if p.strip().isdigit()]
                    if not ports_to_scan:
                        self.console.print("[red]No valid ports entered![/red]")
                        input("Press Enter to continue...")
                        return
                except ValueError:
                    self.console.print("[red]Invalid port format![/red]")
                    input("Press Enter to continue...")
                    return
            
            all_ports = sorted(ports_to_scan)
            
            self.console.print(f"Scanning {len(all_ports)} ports...")
            self.console.print()
            
            active_ports = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Scanning ports...", total=len(all_ports))
                
                for port in all_ports:
                    progress.update(task, description=f"Scanning port {port}...")
                    
                    if self.is_port_open('127.0.0.1', port):
                        process_info = self.get_process_on_port(port)
                        active_ports.append({
                            'port': port,
                            'process': process_info
                        })
                        
                    progress.advance(task)
                    
            # Display results
            if active_ports:
                table = Table(title="Active Ports Found")
                table.add_column("Port", style="cyan")
                table.add_column("Process Name", style="green")
                table.add_column("PID", style="yellow") 
                table.add_column("Status", style="white")
                table.add_column("Security Note", style="red")
                
                for port_info in active_ports:
                    port = port_info['port']
                    process = port_info['process']
                    
                    process_name = process.get('name', 'Unknown') if process else 'Unknown'
                    pid = str(process.get('pid', 'N/A')) if process else 'N/A'
                    
                    # Determine status and security notes
                    status = "Active"
                    security_note = ""
                    
                    if port in [3000, 8000, 8080, 5000, 4000, 9000]:
                        status = "Development"
                        security_note = "OK for dev"
                    elif port in [22, 80, 443]:
                        status = "System Service"
                        security_note = "Standard"
                    elif process_name == 'Unknown':
                        status = "Unknown Process"
                        security_note = "Investigate"
                        
                    table.add_row(
                        str(port),
                        process_name,
                        pid,
                        status,
                        security_note
                    )
                    
                self.console.print(table)
                
                # Security summary
                suspicious_ports = [p for p in active_ports 
                                  if p['process'] is None or p['process'].get('name') == 'Unknown']
                
                if suspicious_ports:
                    self.console.print(f"\n[yellow]WARNING: Found {len(suspicious_ports)} ports with unknown processes[/yellow]")
                    self.console.print("[yellow]Consider investigating these ports for security[/yellow]")
                else:
                    self.console.print("\n[green]OK: All active ports have known processes[/green]")
                    
            else:
                self.console.print("[green]No active ports found on the scanned range.[/green]")
                
        except Exception as e:
            self.console.print(f"[red]Error during port scan: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def is_port_open(self, host: str, port: int, timeout: float = 0.5) -> bool:
        """Check if a port is open"""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, socket.error, OSError):
            return False
            
    def get_process_on_port(self, port: int) -> Optional[Dict[str, Any]]:
        """Get information about the process using a specific port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    connections = proc.info['connections']
                    if connections:
                        for conn in connections:
                            if conn.laddr.port == port:
                                return {
                                    'pid': proc.info['pid'],
                                    'name': proc.info['name']
                                }
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    continue
                    
        except Exception:
            pass
            
        return None
            
    def connection_tester(self):
        """Test database connections"""
        try:
            self.console.clear()
            self.console.print(Panel("Database Connection Tester", style="bold magenta"))
            self.console.print()
            
            self.console.print("[blue]This feature tests connectivity to database configurations found in projects.[/blue]")
            self.console.print("[yellow]WARNING: Connection testing is not yet implemented.[/yellow]")
            self.console.print()
            
            self.console.print("Planned features:")
            self.console.print("• Test PostgreSQL connections")
            self.console.print("• Test MySQL/MariaDB connections") 
            self.console.print("• Test MongoDB connections")
            self.console.print("• Test Redis connections")
            self.console.print("• Test Cloudflare D1 connections")
            self.console.print("• Connection latency testing")
            
        except Exception as e:
            self.console.print(f"[red]Error in connection tester: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def environment_viewer(self):
        """View and analyze environment files"""
        try:
            self.console.clear()
            self.console.print(Panel("Environment Variables Viewer", style="bold magenta"))
            self.console.print()
            
            # Find all .env files in projects
            projects_path = Path(self.config['projects_path'])
            env_files = []
            
            # Search for .env files
            for env_file in projects_path.rglob('.env*'):
                if env_file.is_file() and not env_file.name.startswith('.env.example'):
                    env_files.append(env_file)
            
            if not env_files:
                self.console.print("[yellow]No environment files found in projects directory.[/yellow]")
                input("Press Enter to continue...")
                return
            
            table = Table(title="Environment Files Found")
            table.add_column("File", style="cyan")
            table.add_column("Project", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Modified", style="white")
            
            for env_file in env_files[:10]:  # Limit to 10 files
                relative_path = env_file.relative_to(projects_path)
                project_name = str(relative_path).split('/')[0] if '/' in str(relative_path) else 'Root'
                file_size = f"{env_file.stat().st_size} bytes"
                from datetime import datetime
                modified = datetime.fromtimestamp(env_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                
                table.add_row(env_file.name, project_name, file_size, modified)
            
            self.console.print(table)
            
            if len(env_files) > 10:
                self.console.print(f"\n[dim]... and {len(env_files) - 10} more files[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]Error viewing environment files: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def api_endpoint_scanner(self):
        """Scan for API endpoints in project files"""
        try:
            self.console.clear()
            self.console.print(Panel("API Endpoint Scanner", style="bold magenta"))
            self.console.print()
            
            # Show progress indicator
            self.console.print("[dim]Initializing API endpoint scan...[/dim]")
            
            projects_path = Path(self.config['projects_path'])
            
            # Search for common API patterns
            api_patterns = [
                r'app\.get\(["\']([^"\']+)["\']',  # Express.js GET routes
                r'app\.post\(["\']([^"\']+)["\']', # Express.js POST routes
                r'app\.put\(["\']([^"\']+)["\']',  # Express.js PUT routes
                r'app\.delete\(["\']([^"\']+)["\']', # Express.js DELETE routes
                r'@app\.route\(["\']([^"\']+)["\']', # Flask routes
                r'@api\.route\(["\']([^"\']+)["\']', # Flask-RESTful routes
                r'Route::[a-z]+\(["\']([^"\']+)["\']', # Laravel routes
            ]
            
            endpoints_found = []
            
            # Get all JavaScript files first for progress tracking
            js_files = list(projects_path.rglob('*.js'))
            
            if not js_files:
                self.console.print("[yellow]No JavaScript files found in projects directory.[/yellow]")
                input("\nPress Enter to continue...")
                return
            
            # Clear the progress line and show scanning progress
            self.console.print("\033[A\033[K", end="")  # Move up and clear line
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                scan_task = progress.add_task("[dim]Scanning JavaScript files for API endpoints...[/dim]", total=len(js_files))
                
                for file_path in js_files:
                    if file_path.is_file():
                        progress.update(scan_task, description=f"[dim]Scanning {file_path.name}...[/dim]")
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            import re
                            for pattern in api_patterns:
                                matches = re.findall(pattern, content)
                                for match in matches:
                                    endpoints_found.append({
                                        'endpoint': match,
                                        'file': file_path.name,
                                        'project': str(file_path.relative_to(projects_path)).split('/')[0]
                                    })
                        except:
                            continue
                        
                        progress.advance(scan_task)
            
            # Clear screen and show results
            self.console.clear()
            self.console.print(Panel("API Endpoint Scanner - Results", style="bold magenta"))
            self.console.print()
            
            if endpoints_found:
                table = Table(title=f"API Endpoints Found ({len(endpoints_found)} total)")
                table.add_column("Endpoint", style="cyan")
                table.add_column("File", style="green")
                table.add_column("Project", style="yellow")
                
                for endpoint in endpoints_found[:15]:  # Show max 15
                    table.add_row(endpoint['endpoint'], endpoint['file'], endpoint['project'])
                
                self.console.print(table)
                
                if len(endpoints_found) > 15:
                    self.console.print(f"\n[dim]... and {len(endpoints_found) - 15} more endpoints[/dim]")
            else:
                self.console.print("[yellow]No API endpoints found in project files.[/yellow]")
                self.console.print("[blue]Searched for Express.js, Flask, and Laravel route patterns.[/blue]")
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Scan cancelled by user.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error scanning for API endpoints: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def alias_creator(self):
        """Create new terminal aliases"""
        try:
            self.console.clear()
            self.console.print(Panel("Alias Creator", style="bold magenta"))
            self.console.print()
            
            alias_name = text("Enter alias name (e.g., 'gst'):")
            if not alias_name:
                return
                
            alias_command = text("Enter command for alias (e.g., 'git status'):")
            if not alias_command:
                return
                
            # Create alias string
            alias_string = f'alias {alias_name}="{alias_command}"'
            
            self.console.print(f"\n[blue]Alias to be added: {alias_string}[/blue]")
            
            if confirm("Add this alias to your .zshrc?"):
                # Backup .zshrc
                zshrc_path = Path.home() / '.zshrc'
                backup_path = Path.home() / '.zshrc.backup'
                
                import shutil
                shutil.copy2(zshrc_path, backup_path)
                
                # Add alias to .zshrc
                with open(zshrc_path, 'a') as f:
                    f.write(f'\n{alias_string}\n')
                    
                self.console.print(f"[green]OK: Alias '{alias_name}' added successfully![/green]")
                self.console.print("[yellow]Run 'source ~/.zshrc' or restart terminal to use the new alias.[/yellow]")
                
                # Update config
                if 'aliases' not in self.config:
                    self.config['aliases'] = {}
                self.config['aliases'][alias_name] = alias_command
            
        except Exception as e:
            self.console.print(f"[red]Error creating alias: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def alias_manager(self):
        """View and manage existing aliases"""
        try:
            self.console.clear()
            self.console.print(Panel("Alias Manager", style="bold magenta"))
            self.console.print()
            
            # Read current aliases from .zshrc
            zshrc_path = Path.home() / '.zshrc'
            aliases = {}
            
            try:
                with open(zshrc_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line.startswith('alias ') and '=' in line:
                            parts = line[6:].split('=', 1)  # Remove 'alias ' prefix
                            if len(parts) == 2:
                                alias_name = parts[0].strip()
                                alias_cmd = parts[1].strip('"\'')
                                aliases[alias_name] = alias_cmd
            except Exception as e:
                self.console.print(f"[red]Error reading .zshrc: {e}[/red]")
                input("Press Enter to continue...")
                return
            
            if not aliases:
                self.console.print("[yellow]No aliases found in .zshrc[/yellow]")
                input("Press Enter to continue...")
                return
                
            # Display aliases table
            table = Table(title="Current Aliases")
            table.add_column("Alias", style="cyan")
            table.add_column("Command", style="white")
            
            for alias_name, command in aliases.items():
                table.add_row(alias_name, command)
                
            self.console.print(table)
            self.console.print(f"\n[blue]Found {len(aliases)} aliases total[/blue]")
            
        except Exception as e:
            self.console.print(f"[red]Error in alias manager: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def brew_manager(self):
        """Manage Homebrew packages"""
        try:
            self.console.clear()
            self.console.print(Panel("Brew Manager", style="bold magenta"))
            self.console.print()
            
            # Check if brew is installed
            try:
                subprocess.run(['brew', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.print("[red]Homebrew is not installed on this system.[/red]")
                self.console.print("[blue]Visit https://brew.sh to install Homebrew[/blue]")
                input("Press Enter to continue...")
                return
            
            brew_options = [
                'Update Homebrew',
                'List installed packages',
                'Search for packages', 
                'Cleanup old packages',
                'Check system health'
            ]
            
            choice = list_input(
                "Select brew action:",
                choices=brew_options,
                carousel=True
            )
            
            self.console.print(f"\n[dim]Running brew {choice.lower()}...[/dim]")
            
            if choice == 'Update Homebrew':
                result = subprocess.run(['brew', 'update'], capture_output=True, text=True)
                self.console.print("\033[A\033[K", end="")  # Clear progress line
                if result.returncode == 0:
                    self.console.print("[green]OK: Homebrew updated successfully[/green]")
                else:
                    self.console.print("[red]ERROR: Error updating Homebrew[/red]")
                    
            elif choice == 'List installed packages':
                result = subprocess.run(['brew', 'list'], capture_output=True, text=True)
                self.console.print("\033[A\033[K", end="")  # Clear progress line
                if result.returncode == 0:
                    packages = result.stdout.strip().split('\n')
                    self.console.print(f"[blue]Found {len(packages)} installed packages:[/blue]")
                    for i, package in enumerate(packages[:20]):
                        self.console.print(f"  • {package}")
                    if len(packages) > 20:
                        self.console.print(f"  ... and {len(packages) - 20} more")
                        
            elif choice == 'Cleanup old packages':
                result = subprocess.run(['brew', 'cleanup'], capture_output=True, text=True)
                self.console.print("\033[A\033[K", end="")  # Clear progress line
                if result.returncode == 0:
                    self.console.print("[green]OK: Cleanup completed[/green]")
                else:
                    self.console.print("[red]ERROR: Error during cleanup[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error in brew manager: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def network_diagnostics(self):
        """Test connectivity and speed"""
        try:
            self.console.clear()
            self.console.print(Panel("Network Diagnostics", style="bold magenta"))
            self.console.print()
            
            # Test basic connectivity
            self.console.print("[dim]Testing basic connectivity...[/dim]")
            
            tests = [
                ('Google DNS', '8.8.8.8'),
                ('Cloudflare DNS', '1.1.1.1'),
                ('GitHub', 'github.com')
            ]
            
            results = []
            for name, target in tests:
                try:
                    result = subprocess.run(['ping', '-c', '3', target], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        # Extract average ping time
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if 'avg' in line:
                                avg_time = line.split('/')[-2] if '/' in line else 'N/A'
                                results.append((name, 'Online', f"{avg_time}ms"))
                                break
                        else:
                            results.append((name, 'Online', 'N/A'))
                    else:
                        results.append((name, 'Offline', 'N/A'))
                except subprocess.TimeoutExpired:
                    results.append((name, 'Timeout', 'N/A'))
                except Exception:
                    results.append((name, 'Error', 'N/A'))
            
            # Clear progress line
            self.console.print("\033[A\033[K", end="")
            
            # Display results
            table = Table(title="Network Connectivity Test")
            table.add_column("Target", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Avg Ping", style="yellow")
            
            for name, status, ping in results:
                status_style = "green" if status == "Online" else "red"
                table.add_row(name, f"[{status_style}]{status}[/{status_style}]", ping)
                
            self.console.print(table)
            
            # DNS test
            self.console.print("\n[blue]DNS Resolution Test:[/blue]")
            try:
                import socket
                ip = socket.gethostbyname('google.com')
                self.console.print(f"[green]OK: google.com resolves to {ip}[/green]")
            except:
                self.console.print("[red]ERROR: DNS resolution failed[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error in network diagnostics: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def school_integration(self):
        """Academic workflow tools"""
        try:
            self.console.clear()
            self.console.print(Panel("School Integration", style="bold magenta"))
            self.console.print()
            
            self.console.print("[blue]Academic workflow tools and study management.[/blue]")
            self.console.print()
            
            self.console.print("[yellow]WARNING: Coming Soon - This feature is in development[/yellow]")
            self.console.print()
            
            self.console.print("Planned features:")
            self.console.print("• > Assignment and homework tracking")
            self.console.print("• > Study session timers with Pomodoro technique") 
            self.console.print("• > Grade calculation and GPA tracking")
            self.console.print("• > Class schedule management")
            self.console.print("• > Note-taking integration")
            self.console.print("• > LMS integration (Canvas, Blackboard, etc.)")
            self.console.print()
            
            self.console.print("[dim]This feature will integrate with your academic workflow to help manage")
            self.console.print("coursework, track assignments, and optimize study time.[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]Error in school integration: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def messenger_integration(self):
        """Connect to messaging services"""
        try:
            self.console.clear()
            self.console.print(Panel("Messenger Integration", style="bold magenta"))
            self.console.print()
            
            self.console.print("[blue]Connect to messaging services and communication platforms.[/blue]")
            self.console.print()
            
            self.console.print("[yellow]WARNING: In Development - Communication integration tools[/yellow]")
            self.console.print()
            
            self.console.print("Planned features:")
            self.console.print("• > Slack workspace integration and notifications")
            self.console.print("• > Discord bot integration and server management") 
            self.console.print("• > Email alerts and automation")
            self.console.print("• > SMS notifications for important events")
            self.console.print("• > Custom webhook integrations")
            self.console.print("• > Message analytics and insights")
            self.console.print()
            
            self.console.print("[dim]This feature will help you stay connected with your team and")
            self.console.print("receive important notifications from your development workflow.[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]Error in messenger integration: {e}[/red]")
            
        input("\nPress Enter to continue...")