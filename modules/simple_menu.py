import os
import sys
import termios
import tty
import select
from typing import List, Dict, Any, Optional, Callable

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class SimpleMenu:
    def __init__(self, console: Console):
        self.console = console
        self.current_index = 0

    def show_simple_menu(
        self,
        title: str,
        options: List[Dict[str, Any]],
        header_callback: Optional[Callable] = None
    ) -> str:
        self.options = options
        self.title = title
        self.header_callback = header_callback

        while True:
            # Clear screen and show menu
            self.console.clear()
            
            # Show header
            if self.header_callback:
                self.header_callback()
            else:
                self.console.print(Panel(self.title, style="bold blue"))
            
            # Show options
            for i, option in enumerate(options):
                name = option['name']
                if i == self.current_index:
                    self.console.print(f"> [bold cyan]{name}[/bold cyan]")
                else:
                    self.console.print(f"  {name}")
            
            # Show controls
            self.console.print("\n" + "─" * 50)
            self.console.print("[dim]↑↓/jk: Navigate  Enter: Select  b: Back  q: Quit[/dim]")
            
            # Get key
            key = self._get_key()
            
            if key in ['UP', 'k']:
                self.current_index = (self.current_index - 1) % len(options)
            elif key in ['DOWN', 'j']:
                self.current_index = (self.current_index + 1) % len(options)
            elif key in ['ENTER', ' ']:
                return options[self.current_index]['value']
            elif key == 'b':
                return 'BACK'
            elif key == 'TAB':
                # For simple menu, just ignore TAB or treat as navigation
                continue
            elif key in ['CTRL_C', 'q']:
                raise KeyboardInterrupt

    def _get_key(self) -> str:
        """Get single keypress from terminal"""
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                tty.cbreak(fd)
                
                # Read first character
                ch = sys.stdin.read(1)
                
                # Handle escape sequences (arrow keys)
                if ch == '\x1b':  # ESC
                    # Try to read the full escape sequence
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        bracket = sys.stdin.read(1)
                        if bracket == '[':
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                direction = sys.stdin.read(1)
                                if direction == 'A':
                                    return 'UP'
                                elif direction == 'B':
                                    return 'DOWN'
                                elif direction == 'C':
                                    return 'RIGHT'
                                elif direction == 'D':
                                    return 'LEFT'
                    return 'ESC'
                
                # Handle regular keys
                elif ch == '\r' or ch == '\n':
                    return 'ENTER'
                elif ch == '\t':
                    return 'TAB'
                elif ch == ' ':
                    return ' '
                elif ch == '\x03':  # Ctrl+C
                    return 'CTRL_C'
                elif ch.lower() == 'b':
                    return 'b'
                elif ch.lower() == 'q':
                    return 'q'
                elif ch.lower() == 'j':
                    return 'j'
                elif ch.lower() == 'k':
                    return 'k'
                else:
                    return ch.lower()
                    
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
        except Exception as e:
            # Fallback to input()
            print(f"\nTerminal input error: {e}")
            return input("Enter command (j/k/enter/b/q): ").strip().lower()
        
        return 'UNKNOWN'

def show_simple_menu(console: Console, title: str, options: List[Dict[str, Any]], header_callback: Optional[Callable] = None) -> str:
    menu = SimpleMenu(console)
    return menu.show_simple_menu(title, options, header_callback)