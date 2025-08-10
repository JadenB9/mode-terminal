import os
import sys
from typing import List, Dict, Any, Optional, Callable

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live

class MenuInput:
    def __init__(self, console: Console):
        self.console = console
        self.ai_mode = False
        self.ai_chat_history = []
        self.current_index = 0

    def show_menu_with_navigation(
        self,
        title: str,
        options: List[Dict[str, Any]],
        help_callback: Optional[Callable] = None,
        show_help_hint: bool = True,
        header_callback: Optional[Callable] = None,
        ai_assistant=None,
    ) -> str:
        self.options = options
        self.title = title
        self.help_callback = help_callback
        self.show_help_hint = show_help_hint
        self.header_callback = header_callback
        self.ai_assistant = ai_assistant

        with Live(self._build_layout(), screen=True, redirect_stderr=False) as live:
            while True:
                if self.ai_mode and self.ai_assistant:
                    live.stop()
                    try:
                        ai_input = self.console.input("[bold cyan]You: [/bold cyan]")
                        if ai_input.strip():
                            self.add_chat_message(ai_input, is_user=True)
                            self.ai_assistant.process_input_split_screen(ai_input, self, live)
                        self.ai_mode = False
                    except KeyboardInterrupt:
                        self.ai_mode = False
                    except Exception as e:
                        self.add_chat_message(f"Input error: {e}", False)
                        self.ai_mode = False
                    live.start()
                else:
                    key = self._get_key()
                    if key == 'UP':
                        self.current_index = (self.current_index - 1) % len(self.options)
                        live.update(self._build_layout())
                    elif key == 'DOWN':
                        self.current_index = (self.current_index + 1) % len(self.options)
                        live.update(self._build_layout())
                    elif key == 'ENTER':
                        return self.options[self.current_index]['value']
                    elif key == 'b':
                        return 'BACK'
                    elif key == 'TAB':
                        self.ai_mode = not self.ai_mode
                        live.update(self._build_layout())
                    elif key == 'h':
                        live.stop()
                        if self.help_callback:
                            self.help_callback()
                        else:
                            self._show_default_help(self.title, self.options)
                        live.start()
                        live.update(self._build_layout())
                    elif key in ['CTRL_C', 'q']:
                        raise KeyboardInterrupt

    def _build_layout(self) -> Layout:
        layout = Layout()
        
        # Header section
        header = Layout(name="header", size=15)
        if self.header_callback:
            with self.console.capture() as capture:
                self.header_callback()
            header.update(Text.from_ansi(capture.get()))
        else:
            header.update(Panel(self.title, style="bold blue"))

        # Menu options section (big box on top)
        menu_options = []
        for i, option in enumerate(self.options):
            name = option['name']
            if i == self.current_index and not self.ai_mode:
                menu_options.append(Text(f"> {name}", style="bold cyan"))
            else:
                menu_options.append(Text(f"  {name}", style="white"))

        menu_panel = Panel(
            Text("\n").join(menu_options),
            title="Options",
            border_style="blue"
        )
        
        # AI chat section (small box at bottom)
        ai_panel = self._build_ai_panel()
        
        # Layout: header on top, menu in middle, AI at bottom
        layout.split_column(
            header,
            Layout(menu_panel),
            Layout(ai_panel, size=8)  # Small AI box
        )

        return layout

    def _build_ai_panel(self) -> Panel:
        if not self.ai_chat_history:
            if self.ai_mode:
                chat_history_text = Text("AI Chat Mode Active - Type your message...", style="green")
            else:
                chat_history_text = Text("Press TAB to enter AI chat mode", style="dim")
        else:
            # Show last few messages
            chat_lines = [str(line) for line in self.ai_chat_history[-3:]]
            chat_history_text = Text("\n".join(chat_lines))
            if self.ai_mode:
                chat_history_text.append("\n\nType your message...", style="green")
        
        border_style = "green" if self.ai_mode else "dim"
        title = "AI Assistant" + (" (ACTIVE)" if self.ai_mode else "")
        
        return Panel(
            chat_history_text,
            title=title,
            border_style=border_style,
            subtitle=f"Directory: {os.getcwd()}"
        )

    def add_chat_message(self, message: str, is_user: bool = True):
        if is_user:
            self.ai_chat_history.append(Text(f"You: {message}", style="bold cyan"))
        else:
            self.ai_chat_history.append(Text(f"AI: {message}", style="green"))

    def _get_key(self) -> str:
        """Get single keypress using keyboard library"""
        if KEYBOARD_AVAILABLE:
            try:
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN:
                    if event.name == 'up':
                        return 'UP'
                    elif event.name == 'down':
                        return 'DOWN'
                    elif event.name == 'enter':
                        return 'ENTER'
                    elif event.name == 'tab':
                        return 'TAB'
                    elif event.name == 'ctrl+c':
                        return 'CTRL_C'
                    elif event.name == 'b':
                        return 'b'
                    elif event.name == 'h':
                        return 'h'
                    elif event.name == 'q':
                        return 'q'
                    elif event.name == 'j':
                        return 'DOWN'
                    elif event.name == 'k':
                        return 'UP'
                    else:
                        return event.name.lower()
                return 'UNKNOWN'
            except Exception:
                return 'UNKNOWN'
        else:
            # Fallback if keyboard not available
            return 'UNKNOWN'

    def _show_default_help(self, title: str, options: List[Dict[str, Any]]):
        self.console.clear()
        self.console.print(Panel(f"Help: {title}", style="bold yellow"))
        self.console.print()
        
        from rich.table import Table
        help_table = Table(title="Available Options")
        help_table.add_column("Option", style="cyan", width=40)
        help_table.add_column("Description", style="white", width=60)
        
        for option in options:
            name = option['name']
            description = option.get('description', 'No description available')
            help_table.add_row(name, description)
        
        self.console.print(help_table)
        self.console.print("\n[bold blue]Controls:[/bold blue]")
        self.console.print("• ↑/↓ or j/k: Navigate options")
        self.console.print("• Enter: Select option")
        self.console.print("• Tab: AI chat mode")  
        self.console.print("• b: Go back")
        self.console.print("• h: This help")
        self.console.print("• q: Quit")
        self.console.print("\n[dim]Press any key to continue...[/dim]")
        self._get_key()

def show_menu(console: Console, title: str, options: List[Dict[str, Any]], help_callback: Optional[Callable] = None, header_callback: Optional[Callable] = None, ai_assistant = None) -> str:
    menu_input = MenuInput(console)
    return menu_input.show_menu_with_navigation(title, options, help_callback, True, header_callback, ai_assistant)