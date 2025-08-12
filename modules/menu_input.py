import os
import sys
import signal
from typing import List, Dict, Any, Optional, Callable

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class MenuInput:
    def __init__(self, console: Console):
        self.console = console
        self.ai_mode = False
        self.ai_chat_history = []
        self.current_index = 0
        self.menu_drawn = False
        self.menu_line_start = 0
        self.terminal_height = 0
        self.terminal_width = 0
        self.last_terminal_size = (0, 0)
        self.chat_only_mode = False
        self._prev_input_lines = 1
        self._resize_flag = False
        
        # Set up signal handler for terminal resize
        signal.signal(signal.SIGWINCH, self._handle_resize)
    
    def _handle_resize(self, signum, frame):
        """Handle terminal resize signal"""
        self._resize_flag = True
    
    def _check_resize(self):
        """Check if terminal was resized and handle it"""
        if self._resize_flag:
            self._resize_flag = False
            old_size = (self.terminal_width, self.terminal_height)
            self._update_terminal_size()
            if (self.terminal_width, self.terminal_height) != old_size:
                # Terminal was actually resized
                if self.chat_only_mode:
                    self.console.clear()
                    self._draw_chat_interface_static()
                else:
                    self.console.clear()
                    self._draw_complete_interface()
                return True
        return False
        
    def _update_terminal_size(self):
        """Update terminal dimensions"""
        try:
            import shutil
            self.terminal_width, self.terminal_height = shutil.get_terminal_size()
        except:
            # Fallback to default sizes
            self.terminal_width, self.terminal_height = 80, 24
    
    def _calculate_header_lines(self):
        """Calculate how many lines the header takes up"""
        if self.header_callback:
            # ASCII art header is typically around 11-17 lines depending on screen
            return min(17, max(11, self.terminal_height // 4))
        else:
            return 3  # Simple panel title
        
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

        # Update terminal size and draw interface
        self._update_terminal_size()
        self.console.clear()
        self._draw_complete_interface()
        self.menu_drawn = True
        
        while True:
            try:
                # Check for terminal resize before processing input
                self._check_resize()
                
                # Get live keypress
                key = self._get_live_key()
                
                if key == 'UP':
                    old_index = self.current_index
                    self.current_index = max(0, self.current_index - 1)
                    if old_index != self.current_index:
                        self._update_menu_selection_in_place(old_index)
                        
                elif key == 'DOWN':
                    old_index = self.current_index
                    self.current_index = min(len(self.options) - 1, self.current_index + 1)
                    if old_index != self.current_index:
                        self._update_menu_selection_in_place(old_index)
                        
                elif key == 'ENTER':
                    return self.options[self.current_index]['value']
                    
                elif key == 'TAB':
                    if self.ai_assistant:
                        if self.chat_only_mode:
                            # Exit chat-only mode back to main menu
                            self.chat_only_mode = False
                            self.ai_mode = False
                            self.console.clear()
                            self._draw_complete_interface()
                        else:
                            # Enter chat-only mode
                            self.chat_only_mode = True
                            result = self._handle_chat_only_mode()
                            if result == 'exit_to_menu':
                                # Clear screen and redraw main interface
                                self.console.clear()
                                self._draw_complete_interface()
                            elif result:
                                return result
                        
                elif key == 'b' or key == 'B':
                    return 'BACK'
                    
                elif key == 'h' or key == 'H':
                    if self.help_callback:
                        self.console.clear()
                        self.help_callback()
                        input("Press Enter to continue...")
                        self.console.clear()
                        self._draw_complete_interface()
                        
                elif key == 'VIEW_MESSAGES':
                    if self.ai_chat_history:
                        self._show_full_messages()
                        self.console.clear()
                        self._draw_complete_interface()
                        
                elif key == 'q' or key == 'Q':
                    raise KeyboardInterrupt
                    
            except KeyboardInterrupt:
                raise

    def _get_live_key(self, ai_mode: bool = False) -> str:
        """Get live keypress with proper terminal handling"""
        try:
            import termios
            import tty
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                
                # Handle escape sequences (arrow keys and special commands)
                if ch == '\x1b':
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        # Arrow keys and function keys
                        ch3 = sys.stdin.read(1)
                        sequence = ch + ch2 + ch3
                        
                        if sequence == '\x1b[A':
                            return 'UP'
                        elif sequence == '\x1b[B':
                            return 'DOWN'
                        elif sequence == '\x1b[C':
                            return 'RIGHT'
                        elif sequence == '\x1b[D':
                            return 'LEFT'
                        return 'ESC'
                    elif ch2 == 'm':
                        # Escape+m for messages
                        return 'VIEW_MESSAGES'
                    else:
                        return 'ESC'
                
                # Handle regular keys
                elif ch == '\r' or ch == '\n':
                    return 'ENTER'
                elif ch == '\t':
                    return 'TAB'
                elif ch == '\x03':  # Ctrl+C
                    return 'q'
                elif ch == 'j' and not ai_mode:
                    return 'DOWN'
                elif ch == 'k' and not ai_mode:
                    return 'UP'
                else:
                    return ch
                    
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
        except Exception as e:
            # If live keys don't work, try a fallback approach
            print(f"\nLive key detection failed: {e}")
            print("Your terminal may not support live key input.")
            print("Press Ctrl+C to exit.")
            raise KeyboardInterrupt

    def _draw_complete_interface(self):
        """Draw the complete interface once"""
        # Store position for cursor calculations
        line_count = 0
        
        # Header
        if self.header_callback:
            self.header_callback()
            line_count += 12  # Approximate ASCII art height
        else:
            self.console.print(Panel(self.title, style="bold blue"))
            line_count += 3
        
        self.console.print()
        line_count += 1
        
        # Store menu start position
        self.menu_line_start = line_count + 2 # +2 for box border
        
        # Draw menu
        self._draw_menu_box()
        line_count += len(self.options) + 3  # options + borders
        
        # AI box - only draw if AI mode has been activated
        if self.ai_assistant and (self.ai_mode or self.ai_chat_history):
            self._draw_ai_box()
            line_count += 5
        
        # Controls
        self.console.print("\n[dim]↑↓: Navigate  Enter: Select  Tab: AI Chat  b: Back  h: Help  q: Quit[/dim]")
        line_count += 2
        
        # Chat history
        if self.ai_chat_history:
            self._draw_chat_history()

    def _draw_menu_box(self):
        """Draw the menu options box"""
        menu_lines = []
        for i, option in enumerate(self.options):
            name = option['name']
            if i == self.current_index:
                menu_lines.append(f"[bold cyan]▶ {name}[/bold cyan]")
            else:
                menu_lines.append(f"  {name}")
        
        menu_content = "\n".join(menu_lines)
        menu_panel = Panel(menu_content, title="Choose an Option", border_style="blue")
        self.console.print(menu_panel)

    def _update_menu_selection_in_place(self, old_index: int):
        """Update menu selection - redraw all if screen resized, otherwise position update"""
        # Update terminal size first
        self._update_terminal_size()
        
        # Check if screen size changed
        current_size = (self.terminal_width, self.terminal_height)
        if current_size != self.last_terminal_size:
            # Screen resized - redraw everything
            self.last_terminal_size = current_size
            # Clear screen completely using ANSI codes
            print("\033[2J\033[H", end="", flush=True)
            self.console.clear()
            self._draw_complete_interface()
        else:
            # Always redraw complete interface to avoid positioning issues
            self.console.clear()
            self._draw_complete_interface()

    def _draw_ai_box(self):
        """Draw the AI chat box"""
        if self.ai_mode:
            current_input = getattr(self, 'ai_input', '')
            ai_thinking = getattr(self, 'ai_thinking', False)
            
            if ai_thinking:
                ai_content = "[dim]> (processing...)[/dim]"
                title = "AI Assistant (Please wait)"
                border_style = "yellow"
            else:
                input_line = f"[bold green]> {current_input}[/bold green]"
                ai_content = input_line
                title = "AI Assistant (ACTIVE - TAB to exit)"
                border_style = "green"
        else:
            ai_content = "[dim]Press TAB to chat with AI[/dim]"
            title = "AI Assistant"
            border_style = "dim"
        
        ai_panel = Panel(
            ai_content,
            title=title,
            border_style=border_style,
            subtitle=f"Directory: {os.path.basename(os.getcwd())}",
            height=4
        )
        self.console.print(ai_panel)

    def _handle_ai_live_typing(self):
        """Handle AI mode with live typing like Claude Code"""
        self.ai_mode = True
        self.ai_input = ""
        self.ai_thinking = False
        
        # Update AI box to active state without redrawing everything
        self._update_ai_box_in_place()
        
        while self.ai_mode:
            try:
                key = self._get_live_key(ai_mode=True)
                
                if key == 'TAB':
                    # Exit AI mode
                    self.ai_mode = False
                    break
                    
                elif key == 'VIEW_MESSAGES':
                    if self.ai_chat_history:
                        self._show_full_messages()
                        self.console.clear()
                        self._draw_complete_interface()
                        
                elif key == 'ENTER':
                    if self.ai_input.strip() and self.ai_assistant:
                        user_msg = self.ai_input.strip()
                        self.add_chat_message(f"You: {user_msg}")
                        self.ai_input = ""
                        
                        # Show thinking state
                        self.ai_thinking = True
                        self._update_ai_box_in_place()
                        
                        try:
                            self.ai_assistant.process_input(user_msg, self)
                        except Exception as e:
                            self.add_chat_message(f"AI Error: {str(e)}")
                        finally:
                            self.ai_thinking = False
                            self._update_ai_box_in_place()
                            # Force complete redraw to show new messages
                            self.console.clear()
                            self._draw_complete_interface()
                    else:
                        self.ai_input = ""
                        self._update_ai_box_in_place()
                        
                elif key == '\x7f' or key == '\b':  # Backspace
                    if self.ai_input and not self.ai_thinking:
                        self.ai_input = self.ai_input[:-1]
                        self._update_ai_box_in_place()
                        
                elif key == '\x03':  # Ctrl+C
                    self.ai_mode = False
                    break
                    
                elif len(key) == 1 and ord(key) >= 32 and not self.ai_thinking:
                    # Regular typing
                    self.ai_input += key
                    self._update_ai_box_in_place()
                    
            except Exception:
                self.ai_mode = False
                break
        
        return None
    
    def _handle_chat_only_mode(self):
        """Handle chat-only mode like Claude Code - smooth live updates"""
        self.ai_mode = True
        self.ai_input = ""
        self.ai_thinking = False
        
        # Draw initial chat interface once
        self.console.clear()
        self._draw_chat_interface_static()
        
        # Hide cursor for clean interface
        print("\033[?25l", end="", flush=True)
        
        while self.chat_only_mode and self.ai_mode:
            try:
                # Check for terminal resize before processing input
                self._check_resize()
                
                key = self._get_live_key(ai_mode=True)
                
                if key == 'TAB' or key == '\t':
                    # Exit chat-only mode immediately - clear screen and return properly
                    self.chat_only_mode = False
                    self.ai_mode = False
                    # Show cursor again before exiting
                    print("\033[?25h", end="", flush=True)
                    # Don't just clear - return a specific signal to redraw main menu
                    return 'exit_to_menu'
                    
                elif key == 'VIEW_MESSAGES':
                    if self.ai_chat_history:
                        # Store current state
                        saved_state = {
                            'input': self.ai_input,
                            'thinking': self.ai_thinking,
                            'chat_mode': self.chat_only_mode,
                            'ai_mode': self.ai_mode
                        }
                        
                        # Show full messages in clean screen
                        self._show_full_messages_clean()
                        
                        # Restore state and redraw interface
                        self.ai_input = saved_state['input']
                        self.ai_thinking = saved_state['thinking']
                        self.chat_only_mode = saved_state['chat_mode']
                        self.ai_mode = saved_state['ai_mode']
                        
                        self.console.clear()
                        self._draw_chat_interface_static()
                        
                elif key == 'ENTER':
                    if self.ai_input.strip() and self.ai_assistant:
                        user_msg = self.ai_input.strip()
                        self.add_chat_message(f"You: {user_msg}")
                        self.ai_input = ""
                        
                        # Update to show user message and thinking state
                        self.ai_thinking = True
                        self.console.clear()
                        self._draw_chat_interface_static()
                        
                        try:
                            self.ai_assistant.process_input(user_msg, self)
                        except Exception as e:
                            self.add_chat_message(f"AI Error: {str(e)}")
                        finally:
                            self.ai_thinking = False
                            self.console.clear()
                            self._draw_chat_interface_static()
                    else:
                        self.ai_input = ""
                        self._update_input_line_only()
                        
                elif key == '\x7f' or key == '\b':  # Backspace
                    if self.ai_input and not self.ai_thinking:
                        self.ai_input = self.ai_input[:-1]
                        self._update_input_line_only()
                        
                elif key == '\x03':  # Ctrl+C
                    self.chat_only_mode = False
                    self.ai_mode = False
                    # Show cursor again before exiting
                    print("\033[?25h", end="", flush=True)
                    return None
                    
                elif len(key) == 1 and ord(key) >= 32 and key != '\t' and not self.ai_thinking:
                    # Live typing like Claude Code (exclude Tab characters)
                    self.ai_input += key
                    self._update_input_line_only()
                    
            except Exception:
                self.chat_only_mode = False
                self.ai_mode = False
                # Show cursor again before exiting
                print("\033[?25h", end="", flush=True)
                return None
        
        return None
    
    def _draw_chat_interface_static(self):
        """Draw the static chat interface like Claude Code with proper resizing"""
        # Always update terminal size first
        old_size = (self.terminal_width, self.terminal_height)
        self._update_terminal_size()
        current_size = (self.terminal_width, self.terminal_height)
        
        # If terminal was resized, force a complete redraw
        if current_size != old_size:
            self.console.clear()
            # Reset input line tracking
            self._prev_input_lines = 1
        
        # Draw chat history if it exists
        if self.ai_chat_history:
            self._draw_chat_history_clean()
        else:
            self._draw_welcome_message()
        
        # Draw the input line at bottom
        self._draw_input_line_at_bottom()
    
    def _draw_chat_history_clean(self):
        """Draw chat history with nice boxes, newest at bottom like normal chat"""
        # Leave space for input at bottom (4 lines)
        available_lines = self.terminal_height - 5
        
        # Calculate how many messages can fit (estimate 3 lines per message with box)
        max_messages = max(1, available_lines // 4)
        
        # Get recent messages in NORMAL order (newest at bottom)
        recent_messages = self.ai_chat_history[-max_messages:]
        
        # Show messages in chronological order (oldest first, newest last)
        for msg in recent_messages:
            msg_text = str(msg)
            
            # Determine message type and styling
            if msg_text.startswith("You:"):
                # User message - right-aligned style
                content = msg_text[4:].strip()  # Remove "You:" prefix
                if len(content) > self.terminal_width - 8:
                    content = content[:self.terminal_width - 12] + "..."
                
                msg_panel = Panel(
                    content,
                    title="You",
                    style="bold blue",
                    border_style="blue",
                    padding=(0, 1),
                    width=min(len(content) + 8, self.terminal_width - 10)
                )
            else:
                # AI message - left-aligned style  
                content = msg_text
                if msg_text.startswith("AI:"):
                    content = msg_text[3:].strip()  # Remove "AI:" prefix
                    
                if len(content) > self.terminal_width - 8:
                    content = content[:self.terminal_width - 12] + "..."
                
                msg_panel = Panel(
                    content,
                    title="AI Assistant",
                    style="dim white",
                    border_style="green",
                    padding=(0, 1)
                )
            
            self.console.print(msg_panel)
        
        # Show truncation hint if there are more messages
        if len(self.ai_chat_history) > len(recent_messages):
            self.console.print("\n[dim]Press Esc+m for full message history[/dim]")
    
    def _draw_input_line_at_bottom(self):
        """Draw Claude Code-style input box at bottom that expands"""
        current_input = getattr(self, 'ai_input', '')
        
        # Calculate how many lines we need for input (with wrapping)
        input_display_width = self.terminal_width - 4  # Account for box borders
        if current_input:
            lines_needed = max(1, (len(current_input) + len("> ")) // input_display_width + 1)
        else:
            lines_needed = 1
        
        # Limit expansion to reasonable size
        lines_needed = min(lines_needed, 5)
        
        # Create input content with proper wrapping
        if self.ai_thinking:
            input_content = "[yellow](processing...)[/yellow]"
        else:
            # Wrap the input text properly
            input_text = f"> {current_input}"
            if len(input_text) > input_display_width:
                wrapped_lines = []
                for i in range(0, len(input_text), input_display_width):
                    wrapped_lines.append(input_text[i:i + input_display_width])
                input_content = "\n".join(wrapped_lines)
            else:
                input_content = input_text
        
        # Create the input panel with dynamic height and color
        if self.ai_thinking:
            border_style = "yellow"
            title = "AI Assistant (Processing...)"
        else:
            border_style = "bright_green"
            title = "AI Assistant"
            if current_input:
                border_style = "bright_cyan"  # Change color when typing
        
        input_panel = Panel(
            input_content,
            title=title,
            border_style=border_style,
            height=lines_needed + 2,  # +2 for borders
            width=self.terminal_width
        )
        
        # Position at bottom and draw
        bottom_start = self.terminal_height - (lines_needed + 2)
        print(f"\033[{bottom_start};1H", end="", flush=True)
        
        # Use Rich to render the panel
        self.console.print(input_panel)
        
        # Hide cursor
        print("\033[?25l", end="", flush=True)
    
    def _update_input_line_only(self):
        """Update only the input box like Claude Code live typing with expansion"""
        try:
            # Check for terminal resize first
            old_size = (self.terminal_width, self.terminal_height)
            self._update_terminal_size()
            current_size = (self.terminal_width, self.terminal_height)
            
            # If terminal resized, do full redraw
            if current_size != old_size:
                self.console.clear()
                self._draw_chat_interface_static()
                return
                
            current_input = getattr(self, 'ai_input', '')
            
            # Calculate current and previous input box size
            input_display_width = self.terminal_width - 4
            if current_input:
                lines_needed = max(1, (len(current_input) + len("> ")) // input_display_width + 1)
            else:
                lines_needed = 1
            lines_needed = min(lines_needed, 5)
            
            # Get previous size (stored in instance variable)
            prev_lines = getattr(self, '_prev_input_lines', 1)
            
            # If input box size changed, redraw the entire interface
            if abs(lines_needed - prev_lines) > 0:
                self.console.clear()
                self._draw_chat_interface_static()
                self._prev_input_lines = lines_needed
                return
            
            # For now, always do full redraw to prevent stacking - optimize later
            self.console.clear()
            self._draw_chat_interface_static()
            
        except Exception:
            # Fallback to full redraw if positioning fails
            self.console.clear()
            self._draw_chat_interface_static()
    
    def _draw_input_box_content_only(self, lines_needed):
        """Draw just the input box content without affecting rest of screen"""
        current_input = getattr(self, 'ai_input', '')
        
        # Create input content with proper wrapping
        input_display_width = self.terminal_width - 4
        if self.ai_thinking:
            input_content = "[yellow](processing...)[/yellow]"
        else:
            input_text = f"> {current_input}"
            if len(input_text) > input_display_width:
                wrapped_lines = []
                for i in range(0, len(input_text), input_display_width):
                    wrapped_lines.append(input_text[i:i + input_display_width])
                input_content = "\n".join(wrapped_lines)
            else:
                input_content = input_text
        
        # Create the input panel with color based on state
        if self.ai_thinking:
            border_style = "yellow"
            title = "AI Assistant (Processing...)"
        else:
            border_style = "bright_green"
            title = "AI Assistant"
            if current_input:
                border_style = "bright_cyan"
        
        input_panel = Panel(
            input_content,
            title=title,
            border_style=border_style,
            height=lines_needed + 2,
            width=self.terminal_width
        )
        
        self.console.print(input_panel)
        
        # Hide cursor
        print("\033[?25l", end="", flush=True)
    
    def _show_full_messages_clean(self):
        """Show full messages in completely clean screen with nice formatting"""
        self.console.clear()
        self.console.print(Panel("Full Message History", style="bold green", border_style="green"))
        self.console.print()
        
        if not self.ai_chat_history:
            self.console.print("[dim]No messages yet[/dim]")
        else:
            # Show ALL messages in chronological order (oldest first, newest last)
            for i, msg in enumerate(self.ai_chat_history, 1):
                msg_text = str(msg)
                
                # Format based on message type
                if msg_text.startswith("You:"):
                    content = msg_text[4:].strip()
                    msg_panel = Panel(
                        content,
                        title=f"Message {i} - You",
                        style="bold blue",
                        border_style="blue",
                        padding=(1, 2)
                    )
                else:
                    content = msg_text
                    if msg_text.startswith("AI:"):
                        content = msg_text[3:].strip()
                    
                    msg_panel = Panel(
                        content,
                        title=f"Message {i} - AI Assistant",
                        style="white",
                        border_style="green",
                        padding=(1, 2)
                    )
                
                self.console.print(msg_panel)
                self.console.print()  # Space between messages
        
        self.console.print("[dim]Press Enter to return to chat...[/dim]")
        input()
    
    def _draw_chat_only_interface(self):
        """Draw chat-only interface with AI box at bottom"""
        self.console.clear()
        
        # Update terminal size and check for changes
        old_size = (self.terminal_width, self.terminal_height)
        self._update_terminal_size()
        
        # If size changed, force a complete redraw
        if (self.terminal_width, self.terminal_height) != old_size:
            # Clear completely and redraw with new dimensions
            print("\033[2J\033[H", end="", flush=True)
            self.console.clear()
        
        # Draw chat history scrolling upward (leave space for AI box at bottom)
        if self.ai_chat_history:
            available_lines = self.terminal_height - 6  # Leave 6 lines for AI box
            self._draw_chat_history_scrolling(available_lines)
        else:
            # Show welcome message in center when no chat history
            self._draw_welcome_message()
        
        # Draw AI box at bottom of terminal
        self._draw_ai_box_at_bottom()
    
    def _draw_welcome_message(self):
        """Draw welcome message in center of screen when no chat history exists"""
        # Always use current terminal size
        self._update_terminal_size()
        
        # Calculate center position accounting for input box at bottom
        available_height = self.terminal_height - 8  # Account for input box height
        center_line = max(5, available_height // 2)
        
        # Position cursor at center
        print(f"\033[{center_line};1H", end="", flush=True)
        
        # Create welcome message
        welcome_text = "Welcome to Mode Terminal AI, how can I assist you?"
        
        # Ensure message fits in terminal width
        if len(welcome_text) > self.terminal_width - 4:
            welcome_text = "Welcome to Mode Terminal AI"
        
        # Center the text horizontally
        padding = max(0, (self.terminal_width - len(welcome_text)) // 2)
        centered_text = " " * padding + welcome_text
        
        # Print in light grey
        print(f"\033[37;2m{centered_text}\033[0m", end="", flush=True)
    
    def _draw_chat_history_scrolling(self, available_lines):
        """Draw chat history that scrolls upward, using available lines"""
        if not self.ai_chat_history:
            return
        
        # Update console size for proper wrapping
        self.console.size = (self.terminal_width, self.terminal_height)
        
        # Calculate dynamic wrapping based on terminal width
        # Account for panel borders (4 chars) and padding (2 chars)
        available_width = max(20, self.terminal_width - 6)
        
        # Estimate lines per message based on text length and wrapping
        has_truncated = False
        messages_to_show = []
        
        # Work backwards through messages to see what fits
        for msg in reversed(self.ai_chat_history):
            msg_text = str(msg)
            
            # Calculate wrapped lines for this message
            if len(msg_text) > available_width:
                wrapped_lines = (len(msg_text) // available_width) + 1
            else:
                wrapped_lines = 1
                
            # Add panel overhead (borders + padding)
            total_lines_needed = wrapped_lines + 3  # +3 for top/bottom border + padding
            
            # Check if we have space
            if len(messages_to_show) * 4 + total_lines_needed <= available_lines:  # Conservative estimate
                # Truncate very long messages but allow wrapping for reasonable ones
                if len(msg_text) > available_width * 5:  # Allow up to 5 wrapped lines
                    msg_text = msg_text[:available_width * 5] + "... [TRUNCATED]"
                    has_truncated = True
                
                messages_to_show.append(msg_text)
            else:
                break
        
        # Reverse to show in chronological order
        messages_to_show.reverse()
        
        # Display messages with proper wrapping
        for msg_text in messages_to_show:
            msg_panel = Panel(
                msg_text,
                style="dim white on grey11",
                padding=(0, 1),
                border_style="dim",
                width=self.terminal_width
            )
            self.console.print(msg_panel)
        
        # Show Esc+m hint if there are truncated messages
        if has_truncated or len(self.ai_chat_history) > len(messages_to_show):
            self.console.print("[dim yellow]Press Esc+m to read full messages[/dim yellow]")
    
    def _draw_ai_box_at_bottom(self):
        """Draw AI box at bottom of terminal with proper sizing"""
        # Update console size for proper rendering
        self.console.size = (self.terminal_width, self.terminal_height)
        
        # Move cursor to bottom area
        bottom_start = self.terminal_height - 5
        print(f"\033[{bottom_start};1H", end="", flush=True)
        
        # Draw AI box with dynamic width
        if self.ai_thinking:
            ai_content = "[dim]> (processing...)[/dim]"
            title = "AI Assistant (Please wait)"
            border_style = "yellow"
        else:
            current_input = getattr(self, 'ai_input', '')
            # Wrap long input text
            if len(current_input) > self.terminal_width - 10:
                wrapped_input = current_input[:self.terminal_width - 15] + "..."
            else:
                wrapped_input = current_input
            ai_content = f"[bold green]> {wrapped_input}[/bold green]"
            title = "AI Assistant (TAB to exit)"
            border_style = "green"
        
        ai_panel = Panel(
            ai_content,
            title=title,
            border_style=border_style,
            subtitle=f"Directory: {os.path.basename(os.getcwd())}",
            height=4,
            width=self.terminal_width
        )
        self.console.print(ai_panel)
    
    def _update_ai_box_only(self):
        """Update only the AI box content without clearing screen or redrawing everything"""
        try:
            # Update terminal size
            self._update_terminal_size()
            
            # Save cursor position
            print("\033[s", end="", flush=True)
            
            # Move to AI box area (bottom of screen)
            bottom_start = self.terminal_height - 5
            print(f"\033[{bottom_start};1H", end="", flush=True)
            
            # Clear the AI box area (5 lines)
            for i in range(5):
                print(f"\033[{bottom_start + i};1H\033[K", end="", flush=True)
            
            # Redraw just the AI box
            print(f"\033[{bottom_start};1H", end="", flush=True)
            self._draw_ai_box_content_only()
            
            # Restore cursor position
            print("\033[u", end="", flush=True)
            
        except Exception:
            # If positioning fails, fall back to full redraw
            self._draw_chat_only_interface()
    
    def _draw_ai_box_content_only(self):
        """Draw only the AI box content without affecting rest of screen"""
        # Update console size for proper rendering
        self.console.size = (self.terminal_width, self.terminal_height)
        
        # Draw AI box with dynamic width
        if self.ai_thinking:
            ai_content = "[dim]> (processing...)[/dim]"
            title = "AI Assistant (Please wait)"
            border_style = "yellow"
        else:
            current_input = getattr(self, 'ai_input', '')
            # Wrap long input text
            if len(current_input) > self.terminal_width - 10:
                wrapped_input = current_input[:self.terminal_width - 15] + "..."
            else:
                wrapped_input = current_input
            ai_content = f"[bold green]> {wrapped_input}[/bold green]"
            title = "AI Assistant (TAB to exit)"
            border_style = "green"
        
        ai_panel = Panel(
            ai_content,
            title=title,
            border_style=border_style,
            subtitle=f"Directory: {os.path.basename(os.getcwd())}",
            height=4,
            width=self.terminal_width
        )
        self.console.print(ai_panel)

    def _update_ai_box_in_place(self):
        """Update AI box by always doing complete redraw to ensure correct positioning"""
        # Always redraw complete interface to avoid positioning issues
        # This ensures the AI box always appears in the right place relative to everything else
        self.console.clear()
        self._draw_complete_interface()

    def _restore_interface_after_ai(self):
        """Restore interface state after AI mode without full redraw"""
        self.ai_mode = False
        self._update_ai_box_in_place()
        # Chat history will be shown when menu redraws

    def _draw_chat_history(self):
        """Draw recent chat history"""
        if not self.ai_chat_history:
            return
            
        self.console.print("\n[bold blue]━━━ Chat History ━━━[/bold blue]")
        
        recent = self.ai_chat_history[-6:]  # Show last 6 messages (3 conversation pairs)
        has_truncated = False
        
        for msg in recent:
            msg_text = str(msg)
            is_truncated = len(msg_text) > 100
            if is_truncated:
                msg_text = msg_text[:100] + "... [TRUNCATED]"
                has_truncated = True
            
            msg_panel = Panel(
                msg_text,
                style="dim white on grey11",
                padding=(0, 1),
                border_style="dim"
            )
            self.console.print(msg_panel)
            
        if has_truncated:
            self.console.print("[dim yellow]Press Esc+m to read full messages[/dim yellow]")
    
    def _show_full_messages(self):
        """Show full messages in a dedicated viewer"""
        self.console.clear()
        self.console.print(Panel("Full Message History", style="bold green"))
        self.console.print()
        
        if not self.ai_chat_history:
            self.console.print("[yellow]No messages to display[/yellow]")
        else:
            # Show ALL messages, not just recent ones, and show them COMPLETELY
            for i, msg in enumerate(self.ai_chat_history, 1):
                msg_text = str(msg)
                # NO truncation - show complete message
                
                # Create panel with FULL message (no length limits)
                msg_panel = Panel(
                    msg_text,
                    title=f"Message {i}",
                    style="white on grey11",
                    padding=(1, 2),
                    border_style="green"
                )
                self.console.print(msg_panel)
                self.console.print()  # Add spacing between messages
        
        self.console.print("[bold blue]Press Enter to return...[/bold blue]")
        input()

    def add_chat_message(self, message: str):
        """Add message to chat history"""
        self.ai_chat_history.append(Text(message, style="white"))
        if len(self.ai_chat_history) > 8:
            self.ai_chat_history = self.ai_chat_history[-8:]

def show_menu(console: Console, title: str, options: List[Dict[str, Any]], help_callback: Optional[Callable] = None, header_callback: Optional[Callable] = None, ai_assistant = None) -> str:
    menu_input = MenuInput(console)
    return menu_input.show_menu_with_navigation(title, options, help_callback, True, header_callback, ai_assistant)
