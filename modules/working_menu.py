import os
import sys
import termios
import tty
from typing import List, Dict, Any, Optional, Callable

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class WorkingMenu:
    def __init__(self, console: Console):
        self.console = console
        self.current_index = 0
        self.ai_mode = False
        self.ai_chat_history = []

    def show_menu(
        self,
        title: str,
        options: List[Dict[str, Any]],
        help_callback: Optional[Callable] = None,
        header_callback: Optional[Callable] = None,
        ai_assistant=None
    ) -> str:
        """Show interactive menu with working controls"""
        self.options = options
        self.title = title
        self.help_callback = help_callback
        self.header_callback = header_callback
        self.ai_assistant = ai_assistant

        while True:
            # Clear and redraw menu
            os.system('clear')
            self._draw_menu()
            
            # Handle AI chat mode
            if self.ai_mode and self.ai_assistant:
                try:
                    user_input = input("\n[AI] Your message: ")
                    if user_input.strip():
                        self.ai_chat_history.append(f"You: {user_input}")
                        self.ai_chat_history.append(f"AI: Response to '{user_input}'")  # Placeholder
                    self.ai_mode = False
                    continue
                except (EOFError, KeyboardInterrupt):
                    self.ai_mode = False
                    continue
            
            # Get key input
            key = self._get_key()
            
            # Handle key presses
            if key == 'UP':
                self.current_index = (self.current_index - 1) % len(options)
            elif key == 'DOWN':
                self.current_index = (self.current_index + 1) % len(options)
            elif key == 'ENTER':
                return options[self.current_index]['value']
            elif key == 'TAB':
                self.ai_mode = True
            elif key == 'b':
                return 'BACK'
            elif key == 'h':
                if self.help_callback:
                    os.system('clear')
                    self.help_callback()
                    input("\nPress Enter to continue...")
            elif key == 'q':
                raise KeyboardInterrupt

    def _draw_menu(self):
        """Draw the menu interface"""
        # Header
        if self.header_callback:
            self.header_callback()
        else:
            self.console.print(Panel(self.title, style="bold blue"))
        
        self.console.print()
        
        # Menu options (left side)
        for i, option in enumerate(self.options):
            name = option['name']
            if i == self.current_index:
                self.console.print(f"[bold cyan]> {name}[/bold cyan]")
            else:
                self.console.print(f"  {name}")
        
        # AI chat area (right side or bottom)
        self.console.print("\n" + "─" * 60)
        if self.ai_mode:
            self.console.print("[bold green]AI Chat Mode Active[/bold green]")
        elif self.ai_chat_history:
            self.console.print("[dim]Recent AI Chat:[/dim]")
            for msg in self.ai_chat_history[-3:]:  # Show last 3 messages
                self.console.print(f"[dim]{msg}[/dim]")
        else:
            self.console.print("[dim]Press TAB for AI chat[/dim]")
        
        # Controls
        self.console.print("\n" + "─" * 60)
        self.console.print("[dim]Controls: ↑↓=Navigate, Enter=Select, Tab=AI, b=Back, h=Help, q=Quit[/dim]")

    def _get_key(self) -> str:
        """Get a single key press"""
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.cbreak(fd)
                ch = sys.stdin.read(1)
                
                # Handle escape sequences for arrow keys
                if ch == '\x1b':  # ESC
                    # Read next character
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        # Read final character
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'A':
                            return 'UP'
                        elif ch3 == 'B':
                            return 'DOWN'
                        elif ch3 == 'C':
                            return 'RIGHT'
                        elif ch3 == 'D':
                            return 'LEFT'
                        else:
                            return 'UNKNOWN'
                    else:
                        return 'ESC'
                
                # Handle regular keys
                elif ch == '\r' or ch == '\n':
                    return 'ENTER'
                elif ch == '\t':
                    return 'TAB'
                elif ch == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                elif ch.lower() == 'b':
                    return 'b'
                elif ch.lower() == 'h':
                    return 'h'
                elif ch.lower() == 'q':
                    return 'q'
                elif ch.lower() == 'j':
                    return 'DOWN'  # Vim-style
                elif ch.lower() == 'k':
                    return 'UP'    # Vim-style
                else:
                    return ch.lower()
                    
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception as e:
            # Fallback to simple input
            print(f"\nTerminal input failed ({e}), using text mode:")
            cmd = input("Command (up/down/enter/tab/b/h/q): ").strip().lower()
            if cmd in ['up', 'u']:
                return 'UP'
            elif cmd in ['down', 'd']:
                return 'DOWN'
            elif cmd in ['enter', 'e', '']:
                return 'ENTER'
            elif cmd == 'tab':
                return 'TAB'
            elif cmd == 'b':
                return 'b'
            elif cmd == 'h':
                return 'h'
            elif cmd == 'q':
                return 'q'
            else:
                return cmd

def show_working_menu(
    console: Console, 
    title: str, 
    options: List[Dict[str, Any]], 
    help_callback: Optional[Callable] = None,
    header_callback: Optional[Callable] = None,
    ai_assistant = None
) -> str:
    """Main function to show working menu"""
    menu = WorkingMenu(console)
    return menu.show_menu(title, options, help_callback, header_callback, ai_assistant)