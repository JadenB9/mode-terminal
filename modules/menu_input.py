import os
import sys
from typing import List, Dict, Any, Optional, Callable

try:
    # Try to use termios/tty with a different approach
    import termios
    import tty
    TERMIOS_AVAILABLE = True
except ImportError:
    TERMIOS_AVAILABLE = False

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

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

        # Track if we need full redraw
        self.last_index = -1
        self.need_full_redraw = True
        
        while True:
            # Only clear screen when absolutely necessary
            if self.need_full_redraw or (self.current_index != self.last_index and self.current_index >= 0):
                # Try to minimize clearing
                if not self.need_full_redraw:
                    # Just a navigation change - more efficient redraw
                    pass
                self.console.clear()
                self._draw_interface()
                self.last_index = self.current_index
                self.need_full_redraw = False
            
            # Get key press
            key = self._get_single_key()
            
            # Handle fallback mode
            if key == 'FALLBACK':
                try:
                    # Show prompt at bottom
                    cmd = input("\nCommand (↑/j=up, ↓/k=down, enter=select, tab=AI, b=back, h=help, q=quit): ").strip().lower()
                    if cmd in ['up', 'u', 'j']:
                        key = 'UP'
                    elif cmd in ['down', 'd', 'k']:
                        key = 'DOWN' 
                    elif cmd in ['enter', 'e', '']:
                        key = 'ENTER'
                    elif cmd == 'tab':
                        key = 'TAB'
                    elif cmd == 'b':
                        key = 'b'
                    elif cmd == 'h':
                        key = 'h'
                    elif cmd == 'q':
                        key = 'q'
                    else:
                        continue  # Invalid command, redraw
                except (EOFError, KeyboardInterrupt):
                    # Handle EOF gracefully
                    return 'BACK'
            
            # Handle key presses
            if key == 'UP':
                self.current_index = max(0, self.current_index - 1)
            elif key == 'DOWN':
                self.current_index = min(len(self.options) - 1, self.current_index + 1)
            elif key == 'ENTER':
                return self.options[self.current_index]['value']
            elif key == 'TAB':
                if self.ai_assistant:
                    self._handle_ai_mode()
                    self.need_full_redraw = True  # Force redraw after AI mode
            elif key == 'b' or key == 'B':
                return 'BACK'
            elif key == 'h' or key == 'H':
                if self.help_callback:
                    self.console.clear()
                    self.help_callback()
                    input("Press Enter to continue...")
            elif key == 'q' or key == 'Q':
                raise KeyboardInterrupt

    def _draw_interface(self):
        """Draw the complete interface"""
        # Header
        if self.header_callback:
            self.header_callback()
        else:
            self.console.print(Panel(self.title, style="bold blue"))
        
        self.console.print()
        
        # Menu options - big box
        menu_lines = []
        for i, option in enumerate(self.options):
            name = option['name']
            if i == self.current_index:
                menu_lines.append(f"[bold cyan]▶ {name}[/bold cyan]")
            else:
                menu_lines.append(f"  {name}")
        
        menu_content = "\n".join(menu_lines)
        menu_panel = Panel(menu_content, title="Choose an Option", border_style="blue", expand=False)
        self.console.print(menu_panel)
        
        # AI chat box - small box at bottom
        if self.ai_assistant:
            self._draw_ai_box()
        
        # Controls
        self.console.print("\n[dim]↑↓: Navigate  Enter: Select  Tab: AI Chat  b: Back  h: Help  q: Quit[/dim]")
        
        # Chat history below everything
        if self.ai_chat_history:
            self._draw_chat_history()

    def _draw_ai_box(self):
        """Draw the AI chat box - compact input only"""
        if self.ai_mode:
            # Show only current input in AI mode
            current_input = getattr(self, 'ai_input', '')
            ai_thinking = getattr(self, 'ai_thinking', False)
            
            if ai_thinking:
                ai_content = "[dim]> (processing...)[/dim]"
                title = "AI Assistant (Please wait)"
                border_style = "yellow"
            else:
                input_line = f"[bold green]> {current_input}[/bold green]"
                # Calculate needed height based on input length
                input_height = max(1, len(current_input) // 60 + 1)  # Rough wrap calculation
                ai_content = input_line
                title = "AI Assistant (ACTIVE - TAB to exit)"
                border_style = "green"
        else:
            ai_content = "[dim]Press TAB to chat with AI[/dim]"
            title = "AI Assistant"
            border_style = "dim"
        
        # Dynamic height: 2 lines minimum, grows as needed
        if self.ai_mode and not getattr(self, 'ai_thinking', False):
            current_input = getattr(self, 'ai_input', '')
            input_height = max(2, len(current_input) // 60 + 2)
        else:
            input_height = 2
        
        ai_panel = Panel(
            ai_content,
            title=title,
            border_style=border_style,
            subtitle=f"Directory: {os.path.basename(os.getcwd())}",
            height=input_height + 2  # +2 for borders
        )
        self.console.print(ai_panel)

    def _draw_chat_history(self):
        """Draw chat history below everything with grouped conversations - limited height"""
        if not self.ai_chat_history and not getattr(self, 'ai_thinking', False):
            return
            
        self.console.print("\n[bold blue]━━━ Chat History ━━━[/bold blue]")
        
        # Show thinking indicator if AI is processing
        if getattr(self, 'ai_thinking', False):
            from rich.panel import Panel
            thinking_panel = Panel(
                "[yellow]Generating response...[/yellow]", 
                style="dim",
                padding=(0, 1)
            )
            self.console.print(thinking_panel)
            return
        
        # Group messages in conversation pairs - limit to fit screen
        if self.ai_chat_history:
            from rich.panel import Panel
            
            # Calculate available lines for chat history (rough estimate)
            terminal_height = self.console.size.height if hasattr(self.console.size, 'height') else 24
            available_lines = max(6, terminal_height - 20)  # Reserve space for UI
            
            # Show fewer messages to prevent scrolling
            recent = self.ai_chat_history[-4:]  # Limit to last 4 messages
            
            # Group user/AI message pairs
            conversations_to_show = []
            current_conversation = []
            
            for msg in recent:
                msg_text = str(msg)
                if msg_text.startswith("You:"):
                    # Start a new conversation if we have content
                    if current_conversation:
                        conversations_to_show.append(current_conversation)
                        current_conversation = []
                    current_conversation.append(msg_text)
                else:
                    current_conversation.append(msg_text)
            
            # Add the last conversation
            if current_conversation:
                conversations_to_show.append(current_conversation)
            
            # Only show the most recent conversations that fit
            lines_used = 0
            for conversation in reversed(conversations_to_show[-2:]):  # Max 2 conversations
                conversation_text = "\n".join(conversation)
                estimated_lines = len(conversation_text.split('\n')) + 3  # +3 for panel borders
                
                if lines_used + estimated_lines <= available_lines:
                    conversation_panel = Panel(
                        conversation_text,
                        style="dim white on grey11",
                        padding=(0, 1),
                        border_style="dim"
                    )
                    self.console.print(conversation_panel)
                    lines_used += estimated_lines

    def _handle_ai_mode(self):
        """Handle AI chat interaction with live typing in the box"""
        # Always start fresh
        self.ai_mode = True
        self.ai_input = ""  # Current text being typed
        self.ai_thinking = False  # Ensure thinking state is clear
        
        # Track changes to reduce flicker in AI mode
        last_input = ""
        last_thinking_state = False
        
        # Initial draw
        self.console.clear()
        self._draw_interface()
        
        while self.ai_mode:
            # Get key press first to avoid unnecessary redraws
            key = self._get_single_key()
            
            # Track what changed
            current_input = getattr(self, 'ai_input', '')
            current_thinking = getattr(self, 'ai_thinking', False)
            
            input_changed = current_input != last_input
            thinking_changed = current_thinking != last_thinking_state
            
            # Process the key first - this may change input/thinking state
            should_continue = self._process_ai_key(key)
            if not should_continue:
                break
            
            # Check what changed AFTER processing the key
            new_input = getattr(self, 'ai_input', '')
            new_thinking = getattr(self, 'ai_thinking', False)
            
            # Only redraw if something actually changed after processing
            if (new_input != last_input or new_thinking != last_thinking_state):
                self.console.clear()
                self._draw_interface()
                last_input = new_input
                last_thinking_state = new_thinking

    def _process_ai_key(self, key):
        """Process a key press in AI mode. Returns False to exit AI mode."""
        if key == 'TAB':
            # Exit AI mode back to menu
            self.ai_mode = False
            return False
        elif key == 'ENTER':
            # Send message to AI
            if self.ai_input.strip() and self.ai_assistant:
                user_msg = self.ai_input.strip()
                self.add_chat_message(f"You: {user_msg}")
                self.ai_input = ""  # Clear input immediately
                
                # Show thinking state
                self.ai_thinking = True
                
                # Process with actual AI
                try:
                    self.ai_assistant.process_input(user_msg, self)
                except Exception as e:
                    self.add_chat_message(f"AI Error: {str(e)}")
                finally:
                    self.ai_thinking = False
            else:
                self.ai_input = ""
        elif key == '\x7f' or key == '\b':  # Backspace
            if self.ai_input and not getattr(self, 'ai_thinking', False):
                self.ai_input = self.ai_input[:-1]
        elif key == '\x03':  # Ctrl+C
            self.ai_mode = False
            return False
        elif len(key) == 1 and ord(key) >= 32 and not getattr(self, 'ai_thinking', False):  # Printable characters
            self.ai_input += key
        elif key == 'FALLBACK':
            # Fallback for terminals that can't do live input
            self.ai_mode = False  # Exit AI mode immediately
            self.console.print("\n[yellow]Live input not supported in this environment.[/yellow]")
            self.console.print("[dim]Use TAB to try AI chat in a full terminal.[/dim]")
            input("\nPress Enter to continue...")
            return False
        
        return True  # Continue AI mode

    def add_chat_message(self, message: str):
        """Add message to chat history"""
        self.ai_chat_history.append(Text(message, style="white"))
        if len(self.ai_chat_history) > 10:
            self.ai_chat_history = self.ai_chat_history[-10:]

    def _get_single_key(self) -> str:
        """Get a single key press - optimized for reliability"""
        if TERMIOS_AVAILABLE:
            try:
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    # Use cbreak mode instead of raw for better compatibility
                    tty.setcbreak(sys.stdin.fileno())
                    
                    # Read character
                    ch = sys.stdin.read(1)
                    
                    # Handle escape sequences
                    if ch == '\x1b':  # ESC
                        # Read the rest of the arrow key sequence
                        ch2 = sys.stdin.read(1)
                        ch3 = sys.stdin.read(1)
                        seq = ch + ch2 + ch3
                        
                        if seq == '\x1b[A':
                            return 'UP'
                        elif seq == '\x1b[B':
                            return 'DOWN'
                        elif seq == '\x1b[C':
                            return 'RIGHT'
                        elif seq == '\x1b[D':
                            return 'LEFT'
                        else:
                            return 'ESC'
                    
                    # Handle regular keys
                    elif ch == '\r' or ch == '\n':
                        return 'ENTER'
                    elif ch == '\t':
                        return 'TAB'
                    elif ch == '\x03':  # Ctrl+C
                        return 'q'
                    elif ch == 'j':
                        return 'UP'  # Vim-style
                    elif ch == 'k':
                        return 'DOWN'  # Vim-style
                    else:
                        return ch
                        
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    
            except AttributeError:
                # If cbreak not available, try raw mode
                try:
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                        
                        if ch == '\x1b':  # ESC
                            ch += sys.stdin.read(2)
                            if ch == '\x1b[A':
                                return 'UP'
                            elif ch == '\x1b[B':
                                return 'DOWN'
                            return 'ESC'
                        elif ch == '\r' or ch == '\n':
                            return 'ENTER'
                        elif ch == '\t':
                            return 'TAB'
                        elif ch == '\x03':
                            return 'q'
                        elif ch == 'j':
                            return 'UP'
                        elif ch == 'k':
                            return 'DOWN'
                        else:
                            return ch
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except Exception:
                    return 'FALLBACK'
            except Exception:
                return 'FALLBACK'
        else:
            return 'FALLBACK'

def show_menu(console: Console, title: str, options: List[Dict[str, Any]], help_callback: Optional[Callable] = None, header_callback: Optional[Callable] = None, ai_assistant = None) -> str:
    menu_input = MenuInput(console)
    return menu_input.show_menu_with_navigation(title, options, help_callback, True, header_callback, ai_assistant)