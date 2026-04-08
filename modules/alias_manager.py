from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Dict


class AliasManager:
    BLOCK_START = "# >>> mode aliases >>>"
    BLOCK_END = "# <<< mode aliases <<<"

    def __init__(self, config: Dict[str, object], config_dir: Path, zshrc_path: Path | None = None):
        self.config = config
        self.config_dir = config_dir
        self.zshrc_path = zshrc_path or (Path.home() / ".zshrc")
        self.reload_path = self.config_dir / ".mode_alias_reload"

    def add_alias(self, alias_name: str, command: str) -> str:
        alias_name = alias_name.strip()
        command = command.strip()

        self.validate_alias_name(alias_name)
        if not command:
            raise ValueError("Alias command cannot be empty.")

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

    def validate_alias_name(self, alias_name: str) -> None:
        if not alias_name:
            raise ValueError("Alias name cannot be empty.")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", alias_name):
            raise ValueError("Alias names must start with a letter or underscore and use only letters, numbers, `_`, or `-`.")

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
