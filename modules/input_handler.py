import sys


from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def enhanced_menu_input(
    console: Console,
    prompt: str,
    choices: List[str],
    help_text: Optional[str] = None,
    context_help: Optional[Dict[str, str]] = None
) -> str:
    """
    Enhanced menu input that supports 'b' for back, 'h' for help, and arrow navigation
    
    Args:
        console: Rich console instance
        prompt: The prompt text to display
        choices: List of menu choices
        help_text: General help text to show when 'h' is pressed
        context_help: Dict mapping choice text to help descriptions
    
    Returns:
        The selected choice string, or special values:
        - 'BACK' if 'b' was pressed
        - 'HELP' if 'h' was pressed (after showing help)
    """
    current_index = 0
    
    def show_menu():
        console.clear()
        console.print(f"\n{prompt}\n")
        
        for i, choice in enumerate(choices):
            if i == current_index:
                # Highlighted choice
                console.print(f"[bold green]> {choice}[/bold green]")
                # Show context help if available
                if context_help and choice in context_help:
                    console.print(f"  [dim]{context_help[choice]}[/dim]")
            else:
                console.print(f"  {choice}")
        
        console.print("\n[dim]Navigation: ↑↓ to move, Enter to select, 'b' to go back, 'h' for help[/dim]")
    
    def show_help():
        if help_text:
            console.clear()
            console.print(Panel(help_text, title="Help", border_style="yellow"))
            console.print("\n[dim]Press any key to continue...[/dim]")
            get_char()  # Wait for any key
    
    def get_char():
        """Get a single character from stdin"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    while True:
        show_menu()
        
        try:
            char = get_char()
            
            if char == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif char == '\n' or char == '\r':  # Enter
                return choices[current_index]
            elif char.lower() == 'b':  # Back
                return 'BACK'
            elif char.lower() == 'h':  # Help
                show_help()
                continue
            elif char == '\x1b':  # Escape sequence (arrow keys)
                char = get_char()
                if char == '[':
                    char = get_char()
                    if char == 'A':  # Up arrow
                        current_index = (current_index - 1) % len(choices)
                    elif char == 'B':  # Down arrow
                        current_index = (current_index + 1) % len(choices)
            elif char.lower() == 'q':  # Quick quit in some contexts
                raise KeyboardInterrupt
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled[/yellow]")
            raise

def simple_menu_select(
    console: Console,
    title: str,
    options: List[Dict[str, Any]],
    help_text: Optional[str] = None
) -> str:
    """
    Simplified menu selection using the enhanced input handler
    
    Args:
        console: Rich console instance
        title: Menu title
        options: List of option dicts with 'name', 'value', and 'description'
        help_text: Optional help text
    
    Returns:
        The selected option value or 'BACK'
    """
    choices = [opt['name'] for opt in options]
    context_help = {opt['name']: opt['description'] for opt in options}
    
    try:
        # Fall back to inquirer for now since the custom implementation is complex
        # This is where we'd integrate the enhanced handler
        from inquirer import list_input
        
        choice = list_input(
            f"{title} (press 'h' for help, 'b' to go back):",
            choices=choices,
            carousel=True
        )
        
        # Find the selected option value
        selected_option = next(opt for opt in options if opt['name'] == choice)
        return selected_option['value']
        
    except KeyboardInterrupt:
        return 'BACK'