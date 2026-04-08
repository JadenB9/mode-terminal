from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Dict, List, Tuple


# Aliases that come from oh-my-zsh or system defaults — skip these
_SYSTEM_ALIASES = {"zshconfig", "ohmyzsh"}


class AliasManager:
    BLOCK_START = "# >>> mode aliases >>>"
    BLOCK_END = "# <<< mode aliases <<<"

    def __init__(self, config: Dict[str, object], config_dir: Path, zshrc_path: Path | None = None):
        self.config = config
        self.config_dir = config_dir
        self.zshrc_path = zshrc_path or (Path.home() / ".zshrc")
        self.reload_path = self.config_dir / ".mode_alias_reload"

    # ------------------------------------------------------------------
    # Parse all aliases from .zshrc
    # ------------------------------------------------------------------

    def get_all_aliases(self) -> List[Tuple[str, str]]:
        """Return all custom aliases from .zshrc as (name, command) pairs."""
        if not self.zshrc_path.exists():
            return []

        content = self.zshrc_path.read_text()
        aliases: List[Tuple[str, str]] = []

        for line in content.splitlines():
            stripped = line.strip()
            if not stripped.startswith("alias "):
                continue
            rest = stripped[6:]  # after "alias "
            eq = rest.find("=")
            if eq == -1:
                continue
            name = rest[:eq].strip()
            value = rest[eq + 1:].strip()
            # Strip surrounding quotes
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            if name in _SYSTEM_ALIASES:
                continue
            aliases.append((name, value))

        return aliases

    # ------------------------------------------------------------------
    # Add alias
    # ------------------------------------------------------------------

    def add_alias(self, alias_name: str, command: str) -> str:
        alias_name = alias_name.strip()
        command = command.strip()

        self.validate_alias_name(alias_name)
        if not command:
            raise ValueError("Alias command cannot be empty.")

        # Check if it already exists outside mode block
        existing = self._find_alias_line(alias_name)
        if existing is not None:
            # Update the existing line instead of adding to mode block
            self._replace_alias_line(alias_name, command)
        else:
            aliases = dict(self.config.get("aliases", {}))
            aliases[alias_name] = command
            self.config["aliases"] = dict(sorted(aliases.items()))
            self._write_alias_block(self.config["aliases"])

        reload_snippet = "\n".join(
            [
                f"unalias {alias_name} 2>/dev/null",
                self._alias_line(alias_name, command),
                "",
            ]
        )
        self.reload_path.write_text(reload_snippet)
        return alias_name

    # ------------------------------------------------------------------
    # Edit alias
    # ------------------------------------------------------------------

    def edit_alias(self, alias_name: str, new_command: str) -> str:
        """Edit an existing alias command."""
        new_command = new_command.strip()
        if not new_command:
            raise ValueError("Alias command cannot be empty.")

        # Check mode-managed aliases first
        mode_aliases = dict(self.config.get("aliases", {}))
        if alias_name in mode_aliases:
            mode_aliases[alias_name] = new_command
            self.config["aliases"] = dict(sorted(mode_aliases.items()))
            self._write_alias_block(self.config["aliases"])
        else:
            self._replace_alias_line(alias_name, new_command)

        reload_snippet = "\n".join(
            [
                f"unalias {alias_name} 2>/dev/null",
                self._alias_line(alias_name, new_command),
                "",
            ]
        )
        self.reload_path.write_text(reload_snippet)
        return alias_name

    # ------------------------------------------------------------------
    # Remove alias
    # ------------------------------------------------------------------

    def remove_alias(self, alias_name: str) -> None:
        """Remove an alias from .zshrc entirely."""
        # Remove from mode config if present
        mode_aliases = dict(self.config.get("aliases", {}))
        if alias_name in mode_aliases:
            del mode_aliases[alias_name]
            self.config["aliases"] = dict(sorted(mode_aliases.items()))
            self._write_alias_block(self.config["aliases"])
        else:
            self._delete_alias_line(alias_name)

        reload_snippet = f"unalias {alias_name} 2>/dev/null\n"
        self.reload_path.write_text(reload_snippet)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_alias_name(self, alias_name: str) -> None:
        if not alias_name:
            raise ValueError("Alias name cannot be empty.")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", alias_name):
            raise ValueError("Alias names must start with a letter or underscore and use only letters, numbers, `_`, or `-`.")

    # ------------------------------------------------------------------
    # Internal: line-level operations on .zshrc
    # ------------------------------------------------------------------

    def _find_alias_line(self, alias_name: str) -> int | None:
        """Return line index of a standalone alias definition, or None."""
        if not self.zshrc_path.exists():
            return None
        lines = self.zshrc_path.read_text().splitlines()
        pattern = re.compile(rf"^\s*alias\s+{re.escape(alias_name)}=")
        for i, line in enumerate(lines):
            if pattern.match(line):
                return i
        return None

    def _replace_alias_line(self, alias_name: str, new_command: str) -> None:
        """Replace an existing alias line in .zshrc with a new command."""
        lines = self.zshrc_path.read_text().splitlines()
        pattern = re.compile(rf"^\s*alias\s+{re.escape(alias_name)}=")
        new_line = self._alias_line(alias_name, new_command)
        found = False
        for i, line in enumerate(lines):
            if pattern.match(line):
                lines[i] = new_line
                found = True
                break
        if not found:
            raise ValueError(f"Alias '{alias_name}' not found in {self.zshrc_path}")
        self.zshrc_path.write_text("\n".join(lines) + "\n")

    def _delete_alias_line(self, alias_name: str) -> None:
        """Delete an alias line from .zshrc."""
        lines = self.zshrc_path.read_text().splitlines()
        pattern = re.compile(rf"^\s*alias\s+{re.escape(alias_name)}=")
        new_lines = [line for line in lines if not pattern.match(line)]
        if len(new_lines) == len(lines):
            raise ValueError(f"Alias '{alias_name}' not found in {self.zshrc_path}")
        self.zshrc_path.write_text("\n".join(new_lines) + "\n")

    # ------------------------------------------------------------------
    # Internal: mode alias block
    # ------------------------------------------------------------------

    def _write_alias_block(self, aliases: Dict[str, str]) -> None:
        self.zshrc_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.zshrc_path.read_text() if self.zshrc_path.exists() else ""

        start_index = content.find(self.BLOCK_START)
        end_index = content.find(self.BLOCK_END)
        if (start_index == -1) != (end_index == -1):
            raise ValueError(f"{self.zshrc_path} has a partial Mode alias block. Refusing to modify it automatically.")

        alias_lines = [self._alias_line(name, command) for name, command in aliases.items()]
        block_lines = [self.BLOCK_START, *alias_lines, self.BLOCK_END, ""]
        block = "\n".join(block_lines)

        if start_index != -1 and end_index != -1:
            end_index += len(self.BLOCK_END)
            new_content = content[:start_index] + block + content[end_index:]
        else:
            separator = ""
            if content and not content.endswith("\n"):
                separator = "\n"
            if content and not content.endswith("\n\n"):
                separator += "\n"
            new_content = f"{content}{separator}{block}"

        self.zshrc_path.write_text(new_content)

    def _alias_line(self, alias_name: str, command: str) -> str:
        return f"alias {alias_name}={shlex.quote(command)}"
