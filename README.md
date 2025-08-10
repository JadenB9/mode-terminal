# Mode Terminal Navigator

An interactive terminal application for navigating and managing development workflows on macOS with integrated AI assistant.

## 🚀 Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/JadenB9/mode-terminal-navigator/main/install_one_line.sh | bash
```

**Then run:** `mode`

## Features

### 🤖 AI Assistant (NEW!)
- **Natural Language Commands**: Ask the AI to run commands for you in plain English
- **Live Terminal Integration**: AI executes commands directly and shows results
- **Smart Command Understanding**: "show me the files" → automatically runs `ls -la`
- **Directory-Aware**: AI understands your current location and available files
- **Interactive Chat**: Type directly in a live input box with chat history
- **Powered by Dolphin Mixtral**: Local AI model via Ollama integration

### 🏠 Project & Development Management
- **New Git Project**: Create new projects with Git initialization and GitHub integration
- **Clone Repository**: Clone existing repositories from GitHub  
- **Project Switcher**: Navigate between existing projects with last-modified dates
- **Environment Setup**: Auto-setup for React/Next.js, Node.js, Python, and more

### 🗂️ File System & Organization
- **Quick Navigation**: Fast access to Desktop, Documents, Downloads, Applications
- **iCloud Drive Browser**: Navigate through iCloud Drive folders with file preview
- **Directory Contents**: View file listings with sizes and modification dates

### 🛠️ Development Tools
- **Database Explorer**: Find and examine database configurations in projects
- **Port Scanner**: Scan for active services on common development ports
- **Process Monitor**: View running processes with security checks

### ⚙️ System & Maintenance  
- **Brew Manager**: Update, search, and manage Homebrew packages
- **System Info**: CPU, memory, disk usage with detailed statistics
- **Network Diagnostics**: Connectivity tests, DNS resolution, basic speed tests
- **Security Scan**: Check for suspicious processes and outdated software
- **Backup Status**: Verify Time Machine and iCloud sync status

### 🔧 Utilities
- **Alias Creator**: Create and manage terminal aliases with automatic .zshrc integration
- **Configuration Management**: Persistent settings and preferences

## Installation

### Prerequisites
- macOS 10.14 or later
- Python 3.8 or later
- Terminal or iTerm2
- Ollama (for AI assistant features)

### 🚀 One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/JadenB9/mode-terminal-navigator/main/install_one_line.sh | bash
```

This will:
- Clone the repository to `~/.mode`
- Install Python dependencies
- Add to your PATH
- Set up AI assistant (if Ollama is available)
- Make everything ready to use

**Then just run:** `mode`

---

### Manual Installation

#### 1. Clone the Repository
```bash
# Clone to your home directory
cd ~
git clone https://github.com/JadenB9/mode-terminal-navigator.git .mode

# Navigate to the directory
cd ~/.mode

# Make scripts executable
chmod +x mode.py install.sh
```

#### 2. Install Dependencies
```bash
# Run the installation script (recommended)
./install.sh

# OR install manually:
pip3 install --user rich inquirer requests psutil
```

#### 3. Set Up AI Assistant (Optional but Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the Dolphin Mixtral model
ollama pull dolphin-mistral:7b

# Start Ollama service
ollama serve
```

#### 4. Create Global Command (Optional)
```bash
# Add to your PATH (recommended)
echo 'export PATH="$HOME/.mode:$PATH"' >> ~/.zshrc
source ~/.zshrc

# OR create symbolic link
sudo ln -s ~/.mode/mode.py /usr/local/bin/mode
```

### Quick Install (if you already have the files)
```bash
# Navigate to the mode directory
cd ~/.mode

# Run the installation script
./install.sh

# Set up AI (optional)
ollama pull dolphin-mistral:7b
```

## Usage

### Basic Usage
```bash
# Launch interactive navigator
mode

# Show version
mode --version

# Use custom config file
mode --config /path/to/config.json

# Run directly (if global command not available)
python3 ~/.mode/mode.py
```

### Navigation
- Use **arrow keys** to navigate menus
- Press **Enter** to select options
- Press **Tab** to enter AI chat mode
- Press **Tab again** to exit AI chat mode
- Press **Ctrl+C** to go back or exit
- Press **ESC** in most menus to return to previous level

### AI Assistant Usage
- Press **Tab** from any menu to open AI chat
- Type naturally: "show me the files", "go into Projects folder", "find Python files"
- Press **Enter** to send messages
- AI will automatically execute commands and show results
- Chat history appears below with responses grouped in boxes
- Press **Tab** to return to the main menu

## Configuration

The application stores its configuration in `~/.mode/config.json`:

```json
{
  "github_username": "JadenB9",
  "projects_path": "/Users/jaden/Library/Mobile Documents/com~apple~CloudDocs/Projects",
  "default_directory": "/Users/jaden",
  "terminal_theme": "dark",
  "auto_clear_screen": true,
  "show_help_text": true,
  "common_ports": [3000, 8000, 8080, 5000, 4000, 9000],
  "ai_assistant": {
    "model": "dolphin-mistral:7b",
    "max_command_timeout": 30,
    "require_confirmation": true,
    "allowed_base_path": "/Users/jaden",
    "log_commands": true
  }
}
```

### Configuration Options
- `github_username`: Your GitHub username for repository operations
- `projects_path`: Default location for project files
- `default_directory`: Directory to return to in "Normal Use" mode
- `auto_clear_screen`: Whether to clear screen between menus
- `show_help_text`: Display contextual help for menu options
- `common_ports`: Ports to scan in the port scanner tool
- `ai_assistant`: AI model configuration
  - `model`: Ollama model name to use
  - `max_command_timeout`: Maximum seconds for command execution
  - `require_confirmation`: Whether to confirm potentially dangerous commands
  - `allowed_base_path`: Restrict AI operations to this directory
  - `log_commands`: Whether to log AI command executions

## Project Structure

```
~/.mode/
├── mode.py              # Main application
├── config.json          # Configuration file
├── install.sh           # Installation script
├── README.md           # This file
├── modules/            # Application modules
│   ├── project_manager.py
│   ├── file_navigator.py  
│   ├── dev_tools.py
│   ├── system_utils.py
│   ├── help_system.py
│   ├── ai_assistant.py    # AI integration
│   └── menu_input.py      # Interactive UI system
├── templates/          # Project templates
└── logs/              # Application logs
```

## Keyboard Shortcuts

### Menu Navigation
- **↑↓**: Navigate menu options
- **Enter**: Select option
- **Tab**: Toggle AI chat mode
- **b**: Go back to previous menu
- **h**: Show help
- **q**: Quit application
- **Ctrl+C**: Exit current menu/application

### AI Chat Mode
- **Tab**: Enter/exit AI chat mode
- **Enter**: Send message to AI
- **Backspace**: Edit your message
- **Ctrl+C**: Exit AI mode

## Troubleshooting

### Command not found
If `mode` command is not found after installation:
1. Restart your terminal
2. Check if `~/.local/bin` is in your PATH
3. Add to `~/.zshrc`: `export PATH="$HOME/.local/bin:$PATH"`
4. Run: `source ~/.zshrc`

### Permission errors
If you encounter permission errors:
```bash
# Fix file permissions
chmod +x ~/.mode/mode.py
chmod +x ~/.mode/install.sh

# For global installation
sudo chown $(whoami) /usr/local/bin/mode
```

### Python dependencies
If modules are missing:
```bash
# Reinstall dependencies
pip3 install --user --upgrade rich inquirer requests psutil

# Or use system pip
sudo pip3 install rich inquirer requests psutil
```

### GitHub integration
For GitHub features to work:
1. Install GitHub CLI: `brew install gh`
2. Authenticate: `gh auth login`
3. Configure your username in `~/.mode/config.json`

### AI Assistant Issues
If AI features aren't working:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Check if model is installed
ollama list

# Pull model if missing
ollama pull dolphin-mistral:7b

# Test AI connection
# Press Tab in Mode Terminal Navigator and try: "hello"
```

### Performance
For better AI response times:
1. Use an SSD for model storage
2. Ensure adequate RAM (8GB+ recommended)
3. Close unnecessary applications when using AI features

## Development

### Adding New Modules
1. Create a new Python file in `~/.mode/modules/`
2. Follow the existing module pattern with `show_menu()` method
3. Import and integrate in `mode.py`

### Custom Project Templates
Add templates to `~/.mode/templates/project_templates/` and they'll be available in Environment Setup.

## Version History

- **v1.0.0**: Initial release with full feature set
  - Project management and Git integration
  - File system navigation with iCloud support
  - Development tools (database explorer, port scanner)
  - System maintenance utilities
  - Terminal alias management

## License

This project is for personal use. Modify and distribute as needed.

## Support

For issues, questions, or feature requests, please check:
1. This README for troubleshooting
2. Configuration file for settings
3. Terminal output for error messages

---

**Happy navigating! 🧭**