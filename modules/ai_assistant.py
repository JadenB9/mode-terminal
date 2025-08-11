import os
import sys
import json
import subprocess
import requests
import shlex

import tty
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.live import Live


class AIAssistant:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        self.ai_config = config.get('ai_assistant', {
            'model': 'dolphin-mistral:7b',
            'max_command_timeout': 30,
            'require_confirmation': True,
            'allowed_base_path': '/Users/jaden',
            'log_commands': True
        })
        self.ollama_url = "http://localhost:11434"
        self.log_path = Path.home() / '.mode' / 'logs' / 'ai_commands.log'
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.SAFE_COMMANDS = ['ls', 'cat', 'grep', 'find', 'pwd', 'echo', 'which', 'head', 'tail', 'tree', 'wc', 'du', 'df']
        self.CONFIRM_COMMANDS = ['rm', 'mv', 'cp', 'mkdir', 'touch', 'chmod', 'pip', 'npm', 'brew', 'git', 'python3', 'node']
        self.BLOCKED_PATHS = ['/System', '/Library', '/private', '/etc', '/usr', '/bin', '/sbin', '/Applications']

    def process_input(self, user_input: str, menu_input):
        """Simple process input without live screen updates"""
        try:
            if not self._check_ollama_connection():
                menu_input.add_chat_message("AI service not available. Please start Ollama.")
                return

            self._log_interaction(f"USER: {user_input}")
            system_prompt = self._create_system_prompt()
            ai_response = self._get_ollama_response(system_prompt, user_input)

            if ai_response:
                clean_response = self._clean_response(ai_response)
                menu_input.add_chat_message(f"AI: {clean_response}")
                self._log_interaction(f"AI: {clean_response}")
                self._handle_commands_in_response_simple(clean_response, menu_input)
            else:
                menu_input.add_chat_message("Failed to get AI response")

        except Exception as e:
            menu_input.add_chat_message(f"Error: {str(e)}")

    def process_input_split_screen(self, user_input: str, menu_input, live: Live):
        try:
            if not self._check_ollama_connection():
                menu_input.add_chat_message("AI service not available. Please start Ollama.", False)
                live.update(menu_input._build_layout())
                return

            self._log_interaction(f"USER: {user_input}")
            system_prompt = self._create_system_prompt()
            ai_response = self._get_ollama_response(system_prompt, user_input)

            if ai_response:
                clean_response = self._clean_response(ai_response)
                menu_input.add_chat_message(clean_response, False)
                live.update(menu_input._build_layout())
                self._log_interaction(f"AI: {clean_response}")
                self._handle_commands_in_response(clean_response, menu_input, live)
            else:
                menu_input.add_chat_message("Failed to get AI response", False)
                live.update(menu_input._build_layout())

        except Exception as e:
            menu_input.add_chat_message(f"Error: {e}", False)
            live.update(menu_input._build_layout())

    def _check_ollama_connection(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _clean_response(self, response: str) -> str:
        import re
        emoji_pattern = re.compile("["
                                   "\U0001F600-\U0001F64F"  # emoticons
                                   "\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   "\U0001F680-\U0001F6FF"  # transport & map symbols
                                   "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "\U00002702-\U000027B0"
                                   "\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        clean_response = emoji_pattern.sub('', response)
        clean_response = ' '.join(clean_response.split())
        return clean_response.strip()

    def _create_system_prompt(self) -> str:
        current_dir = os.getcwd()
        try:
            file_list = "\n".join(os.listdir(current_dir))
        except:
            file_list = "(unable to list files)"
            
        return f"""You are a terminal assistant that ALWAYS EXECUTES commands for the user. Never suggest - always DO.

CURRENT CONTEXT:
- Working directory: {current_dir}
- Files and folders here:
{file_list}

CRITICAL RULES - MUST FOLLOW:
1. EXECUTE EVERY COMMAND IMMEDIATELY - never just suggest or explain
2. Use `command` format to run commands automatically
3. For ANY user request that involves files/directories/system actions: RUN THE COMMAND
4. If user says "show files" → IMMEDIATELY run `ls -la`
5. If user says "go to folder" → IMMEDIATELY run `cd path`
6. If user asks about something → IMMEDIATELY investigate with commands
7. Always act, never just talk

EXECUTION EXAMPLES:
- "show files" → `ls -la` (run immediately)
- "go to Projects" → `cd "{current_dir}/Projects"` (run immediately)  
- "what's in there" → `ls foldername` (run immediately)
- "create file" → `touch filename` (run immediately)
- "check status" → `git status` (run immediately)

Base path: {self.ai_config['allowed_base_path']}/
PRIORITY: Execute first, explain second. Be action-oriented, not conversational."""

    def _get_ollama_response(self, system_prompt: str, user_input: str) -> Optional[str]:
        try:
            payload = {
                "model": self.ai_config['model'],
                "prompt": f"System: {system_prompt}\n\nUser: {user_input}\n\nAssistant:",
                "stream": False
            }
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return None
        except requests.exceptions.Timeout:
            self.console.print("[red]ERROR: Request timed out[/red]")
            return None
        except Exception as e:
            self.console.print(f"[red]ERROR: API Error: {e}[/red]")
            return None

    def _handle_commands_in_response_simple(self, response: str, menu_input):
        """Handle commands without live updates"""
        import re
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('$ '):
                command = line[2:]
                self._execute_command_simple(command, menu_input)
                continue
            backtick_match = re.search(r'`([^`]+)`', line)
            if backtick_match:
                command = backtick_match.group(1)
                if any(cmd in command.split()[0] if command.split() else '' for cmd in self.SAFE_COMMANDS + self.CONFIRM_COMMANDS):
                    self._execute_command_simple(command, menu_input)
                continue
            words = line.split()
            if words and words[0] in self.SAFE_COMMANDS + self.CONFIRM_COMMANDS:
                self._execute_command_simple(line, menu_input)

    def _handle_commands_in_response(self, response: str, menu_input, live: Live):
        import re
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('$ '):
                command = line[2:]
                self._execute_command_split_screen(command, menu_input, live)
                continue
            backtick_match = re.search(r'`([^`]+)`', line)
            if backtick_match:
                command = backtick_match.group(1)
                if any(cmd in command.split()[0] if command.split() else '' for cmd in self.SAFE_COMMANDS + self.CONFIRM_COMMANDS):
                    self._execute_command_split_screen(command, menu_input, live)
                continue
            words = line.split()
            if words and words[0] in self.SAFE_COMMANDS + self.CONFIRM_COMMANDS:
                self._execute_command_split_screen(line, menu_input, live)

    def _execute_command_simple(self, command: str, menu_input):
        """Execute command without live updates"""
        try:
            parts = shlex.split(command)
            if not parts:
                return
            cmd = parts[0]
            if not self._is_command_safe(command):
                menu_input.add_chat_message(f"Command blocked: {command}")
                return
            if cmd in self.CONFIRM_COMMANDS:
                menu_input.add_chat_message(f"Would execute: {command} (confirmation required)")
                return
            self._log_command(command)
            try:
                original_dir = os.getcwd()
                if not original_dir.startswith(self.ai_config['allowed_base_path']):
                    os.chdir(self.ai_config['allowed_base_path'])
                result = subprocess.run(
                    parts,
                    capture_output=True,
                    text=True,
                    timeout=self.ai_config['max_command_timeout'],
                    cwd=os.getcwd()
                )
                if original_dir.startswith(self.ai_config['allowed_base_path']):
                    os.chdir(original_dir)
                if result.stdout:
                    menu_input.add_chat_message(f"Output: {result.stdout.strip()}")
                if result.stderr:
                    menu_input.add_chat_message(f"Error: {result.stderr.strip()}")
                if result.returncode != 0:
                    menu_input.add_chat_message(f"Command failed with code: {result.returncode}")
            except subprocess.TimeoutExpired:
                menu_input.add_chat_message(f"Command timed out: {command}")
            except FileNotFoundError:
                menu_input.add_chat_message(f"Command not found: {cmd}")
            except Exception as e:
                menu_input.add_chat_message(f"Execution error: {e}")
        except Exception as e:
            menu_input.add_chat_message(f"Command parsing error: {e}")

    def _execute_command_split_screen(self, command: str, menu_input, live: Live):
        try:
            parts = shlex.split(command)
            if not parts:
                return
            cmd = parts[0]
            if not self._is_command_safe(command):
                menu_input.add_chat_message(f"Command blocked: {command}", False)
                live.update(menu_input._build_layout())
                return
            if cmd in self.CONFIRM_COMMANDS:
                menu_input.add_chat_message(f"Would execute: {command} (confirmation required)", False)
                live.update(menu_input._build_layout())
                return
            self._log_command(command)
            try:
                original_dir = os.getcwd()
                if not original_dir.startswith(self.ai_config['allowed_base_path']):
                    os.chdir(self.ai_config['allowed_base_path'])
                result = subprocess.run(
                    parts,
                    capture_output=True,
                    text=True,
                    timeout=self.ai_config['max_command_timeout'],
                    cwd=os.getcwd()
                )
                if original_dir.startswith(self.ai_config['allowed_base_path']):
                    os.chdir(original_dir)
                if result.stdout:
                    menu_input.add_chat_message(f"Output: {result.stdout.strip()}", False)
                if result.stderr:
                    menu_input.add_chat_message(f"Error: {result.stderr.strip()}", False)
                if result.returncode != 0:
                    menu_input.add_chat_message(f"Command failed with code: {result.returncode}", False)
                live.update(menu_input._build_layout())
            except subprocess.TimeoutExpired:
                menu_input.add_chat_message(f"Command timed out: {command}", False)
                live.update(menu_input._build_layout())
            except FileNotFoundError:
                menu_input.add_chat_message(f"Command not found: {cmd}", False)
                live.update(menu_input._build_layout())
            except Exception as e:
                menu_input.add_chat_message(f"Execution error: {e}", False)
                live.update(menu_input._build_layout())
        except Exception as e:
            menu_input.add_chat_message(f"Command parsing error: {e}", False)
            live.update(menu_input._build_layout())

    def _is_command_safe(self, command: str) -> bool:
        parts = shlex.split(command)
        if not parts:
            return False
        cmd = parts[0]
        for part in parts[1:]:
            if any(blocked in part for blocked in self.BLOCKED_PATHS):
                return False
        if cmd in self.SAFE_COMMANDS:
            return True
        if cmd in self.CONFIRM_COMMANDS:
            return True
        return False

    def _log_interaction(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open(self.log_path, 'a') as f:
                f.write(log_entry)
        except Exception:
            pass

    def _log_command(self, command: str):
        if self.ai_config.get('log_commands', True):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] COMMAND: {command}\n"
            try:
                with open(self.log_path, 'a') as f:
                    f.write(log_entry)
            except Exception:
                pass
