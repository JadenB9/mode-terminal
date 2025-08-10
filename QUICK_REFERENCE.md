# Mode Terminal Navigator - Quick Reference

## Navigation Controls

| Key | Action | Context |
|-----|--------|---------|
| `↑ ↓` | Navigate menu options | All menus |
| `Enter` | Select current option | All menus |
| `b` | Go back one menu level | Most menus |
| `h` | Show context help | Most menus |
| `Ctrl+C` | Exit current operation | Anywhere |
| `ESC` | Cancel current operation | Text inputs |
| `q` | Quick quit | Some contexts |

## Main Menu Options

- **Normal Use** - Return to regular terminal in home directory
- **Project & Development** - Manage code projects and repositories  
- **File System & Organization** - Navigate directories and files
- **Development Tools** - Database explorer, port scanner, utilities
- **System & Maintenance** - System info, Homebrew, security scans
- **Utilities** - Create aliases, manage configurations
- **Help & Documentation** - Complete help system and guides

## Quick Tips

- Most operations return you to the same menu section
- Press `h` in any menu for context-sensitive help
- Use Project Switcher to quickly jump between projects
- Aliases are immediately available after creation
- Configuration changes are saved automatically

## Configuration

Edit `~/.mode/config.json` to customize:
- GitHub username for repository operations
- Default projects path location
- Screen clearing behavior
- Help text display settings
- Port scanner target ports

## Troubleshooting

**Command not found**: Add `~/.local/bin` to PATH in `~/.zshrc`
**Import errors**: Run `~/.mode/setup_python.py`
**Permission issues**: `chmod +x ~/.mode/mode.py`
**GitHub issues**: Install `gh` CLI and authenticate

## More Help

- Run `mode` and select "Help & Documentation" for detailed guides
- Check `~/.mode/README.md` for complete documentation
- Visit troubleshooting section for common issues

---
*Mode Terminal Navigator v1.0.0 - Your development workflow, streamlined*