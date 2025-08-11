import os
import subprocess
import psutil
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from inquirer import confirm
from menu_input import show_menu

class SystemUtils:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        
    def show_menu(self):
        """Show system and maintenance menu"""
        options = [
            {
                'name': '• System Info - View system performance and usage',
                'value': 'system_info',
                'description': 'Display CPU, memory, disk usage with trends'
            },
            {
                'name': '• Security Scan - Check for security issues',
                'value': 'security_scan',
                'description': 'Scan for suspicious processes, check outdated software'
            },
            {
                'name': '• Backup Status - Verify backup systems',
                'value': 'backup_status', 
                'description': 'Check Time Machine status, iCloud sync status'
            }
        ]
        
        while True:
            self.console.clear()
            self.console.print(Panel("System & Maintenance", style="bold red"))
            self.console.print()
            
            menu_choices = [opt['name'] for opt in options]
            
            try:
                result = show_menu(
                    self.console,
                    "System & Maintenance",
                    options
                )
                
                if result == 'BACK' or result == 'back':
                    return 'continue'
                elif result == 'system_info':
                    self.system_info()
                elif result == 'security_scan':
                    self.security_scan()
                elif result == 'backup_status':
                    self.backup_status()
                    
            except KeyboardInterrupt:
                return 'continue'
                
    def system_info(self):
        """Display system information and performance"""
        try:
            self.console.clear()
            self.console.print(Panel("System Information", style="bold red"))
            self.console.print()
            
            # CPU Information
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            cpu_table = Table(title="CPU Information")
            cpu_table.add_column("Metric", style="cyan")
            cpu_table.add_column("Value", style="white")
            
            cpu_table.add_row("Physical Cores", str(cpu_count))
            cpu_table.add_row("Logical Cores", str(cpu_count_logical))
            cpu_table.add_row("Current Usage", f"{cpu_percent}%")
            if cpu_freq:
                cpu_table.add_row("Frequency", f"{cpu_freq.current:.2f} MHz")
                
            self.console.print(cpu_table)
            self.console.print()
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_table = Table(title="Memory Information")
            memory_table.add_column("Type", style="cyan")
            memory_table.add_column("Total", style="green")
            memory_table.add_column("Used", style="yellow")
            memory_table.add_column("Available", style="white")
            memory_table.add_column("Percentage", style="red")
            
            memory_table.add_row(
                "RAM",
                self.format_bytes(memory.total),
                self.format_bytes(memory.used),
                self.format_bytes(memory.available),
                f"{memory.percent}%"
            )
            
            memory_table.add_row(
                "Swap", 
                self.format_bytes(swap.total),
                self.format_bytes(swap.used),
                self.format_bytes(swap.free),
                f"{swap.percent}%"
            )
            
            self.console.print(memory_table)
            self.console.print()
            
            # Disk Information
            disk_table = Table(title="Disk Usage")
            disk_table.add_column("Mountpoint", style="cyan")
            disk_table.add_column("Total", style="green")
            disk_table.add_column("Used", style="yellow") 
            disk_table.add_column("Free", style="white")
            disk_table.add_column("Percentage", style="red")
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_table.add_row(
                        partition.mountpoint,
                        self.format_bytes(usage.total),
                        self.format_bytes(usage.used),
                        self.format_bytes(usage.free),
                        f"{(usage.used / usage.total) * 100:.1f}%"
                    )
                except PermissionError:
                    continue
                    
            self.console.print(disk_table)
            
            # Network Information
            self.console.print()
            network_io = psutil.net_io_counters()
            if network_io:
                network_table = Table(title="Network I/O")
                network_table.add_column("Metric", style="cyan")
                network_table.add_column("Value", style="white")
                
                network_table.add_row("Bytes Sent", self.format_bytes(network_io.bytes_sent))
                network_table.add_row("Bytes Received", self.format_bytes(network_io.bytes_recv))
                network_table.add_row("Packets Sent", str(network_io.packets_sent))
                network_table.add_row("Packets Received", str(network_io.packets_recv))
                
                self.console.print(network_table)
                
        except Exception as e:
            self.console.print(f"[red]Error getting system info: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def security_scan(self):
        """Basic security scan"""
        try:
            self.console.clear()
            self.console.print(Panel("Security Scan", style="bold red"))
            self.console.print()
            
            self.console.print("[blue]Scanning for suspicious processes...[/blue]")
            
            suspicious_processes = []
            high_cpu_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    # Check for suspicious process names
                    name = proc.info['name'].lower()
                    if any(suspicious in name for suspicious in ['miner', 'crypto', 'bot', 'hack']):
                        suspicious_processes.append(proc.info)
                        
                    # Check for high CPU usage (get current CPU usage)
                    try:
                        cpu_percent = proc.cpu_percent()
                        if cpu_percent > 50:
                            proc_info = proc.info.copy()
                            proc_info['cpu_percent'] = cpu_percent
                            high_cpu_processes.append(proc_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            # Display results
            if suspicious_processes:
                self.console.print(f"[red]WARNING: Found {len(suspicious_processes)} suspicious processes[/red]")
                for proc in suspicious_processes:
                    self.console.print(f"  • {proc['name']} (PID: {proc['pid']})")
            else:
                self.console.print("[green]OK: No suspicious processes found[/green]")
                
            if high_cpu_processes:
                self.console.print(f"\n[yellow]High CPU processes:[/yellow]")
                for proc in high_cpu_processes[:5]:  # Show top 5
                    self.console.print(f"  • {proc['name']}: {proc['cpu_percent']}% CPU")
                    
            # Check for outdated system
            self.console.print(f"\n[blue]System Version Check:[/blue]")
            try:
                result = subprocess.run(['sw_vers'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.console.print(result.stdout)
                    
                    # Simple check for very old versions
                    if 'macOS 10' in result.stdout:
                        self.console.print("[yellow]WARNING: Consider updating to a newer macOS version[/yellow]")
                    else:
                        self.console.print("[green]OK: Running recent macOS version[/green]")
                        
            except Exception:
                self.console.print("[yellow]Unable to check system version[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Error during security scan: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def backup_status(self):
        """Check backup status"""
        try:
            self.console.clear()
            self.console.print(Panel("Backup Status", style="bold red"))
            self.console.print()
            
            # Check Time Machine status
            self.console.print("[blue]Checking Time Machine status...[/blue]")
            try:
                tm_result = subprocess.run(['tmutil', 'status'], capture_output=True, text=True)
                if tm_result.returncode == 0:
                    if 'Running = 1' in tm_result.stdout:
                        self.console.print("[green]OK: Time Machine backup in progress[/green]")
                    elif 'Running = 0' in tm_result.stdout:
                        self.console.print("[blue]Time Machine idle[/blue]")
                        
                    # Get last backup date
                    tm_date_result = subprocess.run(['tmutil', 'latestbackup'], capture_output=True, text=True)
                    if tm_date_result.returncode == 0 and tm_date_result.stdout.strip():
                        self.console.print(f"[green]Last backup: {tm_date_result.stdout.strip()}[/green]")
                    else:
                        self.console.print("[yellow]WARNING: No Time Machine backups found[/yellow]")
                else:
                    self.console.print("[red]ERROR: Time Machine not available or not configured[/red]")
                    
            except Exception:
                self.console.print("[yellow]Unable to check Time Machine status[/yellow]")
                
            self.console.print()
            
            # Check iCloud status (basic)
            self.console.print("[blue]Checking iCloud Drive status...[/blue]")
            icloud_path = Path.home() / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'
            
            if icloud_path.exists():
                # Get iCloud Drive size
                total_size = 0
                file_count = 0
                
                try:
                    for item in icloud_path.rglob('*'):
                        if item.is_file():
                            total_size += item.stat().st_size
                            file_count += 1
                            
                    self.console.print(f"[green]OK: iCloud Drive active[/green]")
                    self.console.print(f"[blue]Files: {file_count:,}[/blue]")
                    self.console.print(f"[blue]Total size: {self.format_bytes(total_size)}[/blue]")
                    
                except Exception:
                    self.console.print("[green]OK: iCloud Drive available (unable to calculate size)[/green]")
                    
            else:
                self.console.print("[red]ERROR: iCloud Drive not found or not syncing[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error checking backup status: {e}[/red]")
            
        input("\nPress Enter to continue...")
        
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"