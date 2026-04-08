"""Ollama model manager — list, chat, and manage local LLM models."""

import subprocess
import webbrowser
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from menu_input import show_menu, prompt_select, prompt_confirm

OLLAMA_URL = "https://ollama.com/download"


class OllamaManager:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ollama_installed(self) -> bool:
        try:
            subprocess.run(
                ["ollama", "--version"],
                capture_output=True, timeout=5,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _ollama_running(self) -> bool:
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _list_models(self) -> List[Dict[str, str]]:
        """Return list of dicts with name, size, and modified info."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return []

            models = []
            lines = result.stdout.strip().split("\n")
            if len(lines) < 2:
                return []

            for line in lines[1:]:
                parts = line.split()
                if not parts:
                    continue
                name = parts[0]
                # Parse size — typically column 3 (after ID)
                size = ""
                modified = ""
                # The output format: NAME  ID  SIZE  MODIFIED
                if len(parts) >= 3:
                    # Find the size value (looks like "4.1 GB" or "900 MB")
                    for i, p in enumerate(parts[1:], 1):
                        if p in ("KB", "MB", "GB", "TB") and i > 1:
                            size = f"{parts[i-1]} {p}"
                            # Everything after size is the modified date
                            modified = " ".join(parts[i+1:])
                            break
                models.append({
                    "name": name,
                    "size": size,
                    "modified": modified,
                })
            return models
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    def _show_model_info(self, model_name: str):
        """Show detailed info about a model."""
        try:
            result = subprocess.run(
                ["ollama", "show", model_name],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                self.console.print()
                self.console.print(Panel(
                    result.stdout.strip(),
                    title=f"[bold color(141)]{model_name}[/]",
                    border_style="color(242)",
                ))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _chat_with_model(self, model_name: str):
        """Launch an interactive Ollama chat session."""
        self.console.print()
        self.console.print(f"[bold color(141)]Starting chat with {model_name}...[/]")
        self.console.print("[dim]Type /bye to exit the chat.[/dim]")
        self.console.print()
        try:
            subprocess.run(["ollama", "run", model_name])
        except KeyboardInterrupt:
            pass
        self.console.print()
        self.console.print("[green]Chat session ended.[/green]")
        input("Press Enter to continue...")

    def _pull_model(self):
        """Pull a new model from the Ollama library."""
        from menu_input import prompt_text
        model_name = prompt_text(self.console, "Model name to pull (e.g. llama3, mistral)")
        if not model_name:
            return
        self.console.print(f"\n[bold]Pulling {model_name}...[/bold]")
        try:
            subprocess.run(["ollama", "pull", model_name])
            self.console.print(f"\n[green]Successfully pulled {model_name}.[/green]")
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Pull cancelled.[/yellow]")
        input("Press Enter to continue...")

    def _delete_model(self):
        """Delete a local model."""
        models = self._list_models()
        if not models:
            self.console.print("[yellow]No models to delete.[/yellow]")
            input("Press Enter to continue...")
            return

        names = [m["name"] for m in models]
        choice = prompt_select(self.console, "Select model to delete", names)
        if not choice:
            return

        if prompt_confirm(self.console, f"Delete {choice}?", default=False):
            try:
                result = subprocess.run(
                    ["ollama", "rm", choice],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode == 0:
                    self.console.print(f"[green]Deleted {choice}.[/green]")
                else:
                    self.console.print(f"[red]Error: {result.stderr.strip()}[/red]")
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                self.console.print(f"[red]Error: {e}[/red]")
            input("Press Enter to continue...")

    def _open_ollama_website(self):
        """Open the Ollama download/install page."""
        try:
            webbrowser.open(OLLAMA_URL)
            self.console.print(f"[green]Opened {OLLAMA_URL} in browser.[/green]")
        except Exception as e:
            self.console.print(f"[red]Could not open browser: {e}[/red]")
            self.console.print(f"[dim]Visit: {OLLAMA_URL}[/dim]")
        input("Press Enter to continue...")

    # ------------------------------------------------------------------
    # Model detail submenu
    # ------------------------------------------------------------------

    def _model_detail_menu(self, model: Dict[str, str]):
        """Show options for a specific model."""
        options = [
            {"name": "Chat", "value": "chat", "description": f"Start a chat session with {model['name']}"},
            {"name": "Model Info", "value": "info", "description": "View model details and parameters"},
            {"name": "Back", "value": "back", "description": "Return to model list"},
        ]

        while True:
            result = show_menu(
                self.console,
                model["name"],
                options,
                header_callback=lambda: self._model_header(model),
            )

            if result in ("BACK", "back"):
                return
            elif result == "chat":
                self._chat_with_model(model["name"])
            elif result == "info":
                self._show_model_info(model["name"])
                input("Press Enter to continue...")

    def _model_header(self, model: Dict[str, str]):
        title = Text("OLLAMA", style="bold color(141)")
        title.append("  ", style="default")
        title.append(model["name"], style="bold white")
        if model.get("size"):
            title.append(f"  ({model['size']})", style="dim")
        self.console.print(title)
        self.console.print()

    # ------------------------------------------------------------------
    # Main menu
    # ------------------------------------------------------------------

    def _ollama_header(self):
        title = Text("OLLAMA", style="bold color(141)")
        title.append("  ", style="default")
        title.append("Local LLM Manager", style="dim")
        self.console.print(title)

        models = self._list_models()
        model_count = len(models)
        total_size = sum(self._parse_size_mb(m.get("size", "")) for m in models)
        if total_size >= 1024:
            size_str = f"{total_size / 1024:.1f} GB"
        else:
            size_str = f"{total_size:.0f} MB"

        info = Text(f"{model_count} model{'s' if model_count != 1 else ''} installed", style="dim")
        info.append(f"  •  {size_str} total", style="dim")
        self.console.print(info)
        self.console.print()

    @staticmethod
    def _parse_size_mb(size_str: str) -> float:
        """Parse a size string like '4.1 GB' into MB."""
        if not size_str:
            return 0
        parts = size_str.split()
        if len(parts) != 2:
            return 0
        try:
            val = float(parts[0])
        except ValueError:
            return 0
        unit = parts[1].upper()
        if unit == "GB":
            return val * 1024
        elif unit == "MB":
            return val
        elif unit == "TB":
            return val * 1024 * 1024
        return 0

    def _start_ollama(self) -> bool:
        """Attempt to start the Ollama server. Returns True if started."""
        import platform
        try:
            if platform.system() == "Darwin":
                subprocess.Popen(
                    ["open", "-a", "Ollama"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            self.console.print("[dim]Starting Ollama...[/dim]")
            import time
            for _ in range(10):
                time.sleep(1)
                if self._ollama_running():
                    self.console.print("[green]Ollama is running.[/green]")
                    return True
            self.console.print("[yellow]Ollama didn't start in time. Try starting it manually.[/yellow]")
            input("Press Enter to continue...")
            return False
        except Exception as e:
            self.console.print(f"[red]Could not start Ollama: {e}[/red]")
            input("Press Enter to continue...")
            return False

    def _stop_ollama(self):
        """Stop the Ollama server."""
        if prompt_confirm(self.console, "Stop Ollama?", default=False):
            try:
                subprocess.run(
                    ["pkill", "-f", "ollama"],
                    capture_output=True, timeout=5,
                )
                import time
                time.sleep(1)
                if not self._ollama_running():
                    self.console.print("[green]Ollama stopped.[/green]")
                else:
                    self.console.print("[yellow]Ollama may still be running.[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error stopping Ollama: {e}[/red]")
            input("Press Enter to continue...")

    def show_menu(self):
        """Main Ollama menu."""
        if not self._ollama_installed():
            self.console.print()
            self.console.print(Panel(
                f"[yellow]Ollama is not installed.[/yellow]\n\n"
                f"Install it from: [bold color(141)]{OLLAMA_URL}[/bold color(141)]",
                title="[bold]Ollama[/bold]",
                border_style="color(242)",
            ))
            self.console.print()
            if prompt_confirm(self.console, "Open Ollama download page?"):
                self._open_ollama_website()
                return "continue"
            input("Press Enter to continue...")
            return "continue"

        if not self._ollama_running():
            self.console.print()
            self.console.print("[yellow]Ollama is installed but not running.[/yellow]")
            if prompt_confirm(self.console, "Start Ollama now?", default=True):
                if not self._start_ollama():
                    return "continue"
            else:
                return "continue"

        while True:
            models = self._list_models()

            # Build menu options: each model + management actions
            options = []
            for m in models:
                desc = m.get("size", "")
                if m.get("modified"):
                    desc += f"  {m['modified']}" if desc else m["modified"]
                options.append({
                    "name": m["name"],
                    "value": f"model:{m['name']}",
                    "description": desc,
                })

            if not options:
                options.append({
                    "name": "(no models installed)",
                    "value": "none",
                    "description": "Pull a model to get started",
                })

            options.append({"name": "───────────────", "value": "sep", "description": ""})
            options.append({"name": "Pull Model", "value": "pull", "description": "Download a new model"})
            options.append({"name": "Delete Model", "value": "delete", "description": "Remove a local model"})
            options.append({"name": "Stop Ollama", "value": "stop", "description": "Shut down the Ollama server", "style": "bold red"})
            options.append({"name": "Ollama Website", "value": "website", "description": OLLAMA_URL})
            options.append({"name": "Back", "value": "back", "description": "Return to main menu"})

            result = show_menu(
                self.console,
                "Ollama Models",
                options,
                header_callback=self._ollama_header,
            )

            if result in ("BACK", "back"):
                return "continue"
            elif result == "sep" or result == "none":
                continue
            elif result.startswith("model:"):
                model_name = result[6:]
                model = next((m for m in models if m["name"] == model_name), None)
                if model:
                    self._model_detail_menu(model)
            elif result == "pull":
                self._pull_model()
            elif result == "stop":
                self._stop_ollama()
                return "continue"
            elif result == "delete":
                self._delete_model()
            elif result == "website":
                self._open_ollama_website()
