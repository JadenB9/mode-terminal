#!/bin/bash
# Mode Terminal Navigator - One Line Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/JadenB9/mode-terminal-navigator/main/install_one_line.sh | bash

set -e

echo "🚀 Installing Mode Terminal Navigator..."

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is designed for macOS only."
    exit 1
fi

# Create backup if .mode already exists
if [ -d "$HOME/.mode" ]; then
    echo "📦 Backing up existing .mode directory..."
    mv "$HOME/.mode" "$HOME/.mode_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Clone the repository
echo "📥 Downloading Mode Terminal Navigator..."
cd "$HOME"
git clone https://github.com/JadenB9/mode-terminal-navigator.git .mode

# Navigate to directory
cd "$HOME/.mode"

# Make scripts executable
chmod +x mode.py install.sh setup_autostart.sh setup_python.py

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install --user rich inquirer requests psutil
else
    echo "❌ pip3 not found. Please install Python 3 first."
    exit 1
fi

# Add to PATH if not already there
if ! echo $PATH | grep -q "$HOME/.mode"; then
    echo "🔧 Adding Mode Terminal Navigator to PATH..."
    echo 'export PATH="$HOME/.mode:$PATH"' >> ~/.zshrc
    export PATH="$HOME/.mode:$PATH"
fi

# Check for Ollama (optional)
echo "🤖 Checking for AI assistant setup..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found! AI features will work."
    if ! ollama list | grep -q "dolphin-mistral"; then
        echo "📦 Installing AI model (this may take a few minutes)..."
        ollama pull dolphin-mistral:7b
    fi
else
    echo "⚠️  Ollama not found. AI features will be disabled."
    echo "   To enable AI features later, install Ollama:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   ollama pull dolphin-mistral:7b"
fi

# Success message
echo ""
echo "🎉 Mode Terminal Navigator installed successfully!"
echo ""
echo "📖 Quick Start:"
echo "   1. Restart your terminal or run: source ~/.zshrc"
echo "   2. Run: mode"
echo "   3. Press TAB for AI chat (if Ollama is installed)"
echo ""
echo "📍 Installation location: $HOME/.mode"
echo "🔗 Repository: https://github.com/JadenB9/mode-terminal-navigator"
echo ""
echo "Happy navigating! 🧭"