#!/bin/bash

# Mode Terminal Navigator Installation Script
# This script installs the mode command globally on macOS

set -e  # Exit on any error

echo "🚀 Installing Mode Terminal Navigator..."
echo

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This installer is designed for macOS only"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    echo "Please install Python 3 from https://python.org or using Homebrew:"
    echo "brew install python"
    exit 1
fi

# Check Python version (requires 3.8+)
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
min_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
    echo "❌ Error: Python 3.8+ is required, but you have Python $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Install required Python packages
echo "📦 Installing Python dependencies..."
pip3 install --user rich inquirer requests psutil > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create mode directory if it doesn't exist
MODE_DIR="$HOME/.mode"
if [ ! -d "$MODE_DIR" ]; then
    mkdir -p "$MODE_DIR"
    echo "📁 Created $MODE_DIR"
fi

# Make the main script executable
chmod +x "$MODE_DIR/mode.py"
echo "✅ Made mode.py executable"

# Create the global mode command
GLOBAL_BIN_DIR="/usr/local/bin"
MODE_COMMAND="$GLOBAL_BIN_DIR/mode"

# Check if we have permission to write to /usr/local/bin
if [ -w "$GLOBAL_BIN_DIR" ]; then
    USE_SUDO=""
else
    USE_SUDO="sudo"
    echo "🔐 Administrator permission required to install globally..."
fi

# Create the mode command script
cat > /tmp/mode_command << 'EOF'
#!/bin/bash
# Mode Terminal Navigator Global Command
python3 "$HOME/.mode/mode.py" "$@"
EOF

# Install the command globally
if $USE_SUDO cp /tmp/mode_command "$MODE_COMMAND" && $USE_SUDO chmod +x "$MODE_COMMAND"; then
    echo "✅ Installed 'mode' command globally"
else
    echo "❌ Failed to install globally. Trying alternative location..."
    
    # Try local bin directory
    LOCAL_BIN_DIR="$HOME/.local/bin"
    mkdir -p "$LOCAL_BIN_DIR"
    
    if cp /tmp/mode_command "$LOCAL_BIN_DIR/mode" && chmod +x "$LOCAL_BIN_DIR/mode"; then
        echo "✅ Installed 'mode' command to $LOCAL_BIN_DIR"
        
        # Check if local bin is in PATH
        if [[ ":$PATH:" != *":$LOCAL_BIN_DIR:"* ]]; then
            echo "⚠️  Note: $LOCAL_BIN_DIR is not in your PATH"
            echo "Add this line to your ~/.zshrc:"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
            echo
            echo "Then run: source ~/.zshrc"
        fi
    else
        echo "❌ Failed to install mode command"
        exit 1
    fi
fi

# Clean up
rm -f /tmp/mode_command

# Verify installation
if command -v mode &> /dev/null; then
    echo
    echo "🎉 Mode Terminal Navigator installed successfully!"
    echo
    echo "Usage:"
    echo "  mode        - Launch the interactive terminal navigator"
    echo "  mode --help - Show help information"
    echo
    echo "Try running 'mode' now!"
else
    echo
    echo "⚠️  Installation complete, but 'mode' command not found in PATH"
    echo "You may need to:"
    echo "1. Restart your terminal"
    echo "2. Add ~/.local/bin to your PATH (if installed locally)"
    echo "3. Run: source ~/.zshrc"
    echo
    echo "You can also run directly: python3 ~/.mode/mode.py"
fi

echo
echo "📁 Installation directory: $MODE_DIR"
echo "⚙️  Configuration file: $MODE_DIR/config.json"
echo
echo "Happy navigating! 🧭"