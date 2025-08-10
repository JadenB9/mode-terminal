#!/bin/bash

# Mode Terminal Navigator Auto-Start Setup
# This script helps set up Mode to run automatically when you open a new terminal

echo "🚀 Setting up Mode Terminal Navigator to run on terminal startup..."
echo

# Check if mode command exists
if ! command -v mode &> /dev/null && ! [ -f ~/.local/bin/mode ]; then
    echo "❌ Mode command not found. Please run the installer first:"
    echo "cd ~/.mode && ./install.sh"
    exit 1
fi

# Determine the correct mode command path
if command -v mode &> /dev/null; then
    MODE_CMD="mode"
else
    MODE_CMD="~/.local/bin/mode"
fi

echo "Found mode command: $MODE_CMD"
echo

# Setup options
echo "Choose how you want Mode to start:"
echo "1. Always run Mode when opening terminal"
echo "2. Run Mode only in new terminal windows (not tabs)"
echo "3. Run Mode with a prompt (ask each time)"
echo "4. Remove auto-start (if already set up)"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "Setting up Mode to always run on terminal startup..."
        
        # Add to .zshrc
        if ! grep -q "# Mode Terminal Navigator Auto-Start" ~/.zshrc; then
            echo "" >> ~/.zshrc
            echo "# Mode Terminal Navigator Auto-Start" >> ~/.zshrc
            echo "$MODE_CMD" >> ~/.zshrc
        else
            echo "Auto-start already configured in ~/.zshrc"
        fi
        
        echo "✅ Mode will now run automatically when you open a new terminal"
        ;;
        
    2)
        echo "Setting up Mode to run only in new terminal windows..."
        
        if ! grep -q "# Mode Terminal Navigator Auto-Start" ~/.zshrc; then
            echo "" >> ~/.zshrc
            echo "# Mode Terminal Navigator Auto-Start (windows only)" >> ~/.zshrc
            echo "if [ -z \"\$TMUX\" ] && [ \"\$TERM_PROGRAM\" != \"vscode\" ]; then" >> ~/.zshrc
            echo "    $MODE_CMD" >> ~/.zshrc
            echo "fi" >> ~/.zshrc
        else
            echo "Auto-start already configured in ~/.zshrc"
        fi
        
        echo "✅ Mode will run in new terminal windows (but not tabs or tmux)"
        ;;
        
    3)
        echo "Setting up Mode with prompt..."
        
        if ! grep -q "# Mode Terminal Navigator Auto-Start" ~/.zshrc; then
            echo "" >> ~/.zshrc
            echo "# Mode Terminal Navigator Auto-Start (with prompt)" >> ~/.zshrc
            echo "echo 'Launch Mode Terminal Navigator? (y/n)'" >> ~/.zshrc
            echo "read -t 3 response" >> ~/.zshrc
            echo "if [[ \$response == 'y' ]] || [[ -z \$response ]]; then" >> ~/.zshrc
            echo "    $MODE_CMD" >> ~/.zshrc
            echo "fi" >> ~/.zshrc
        else
            echo "Auto-start already configured in ~/.zshrc"
        fi
        
        echo "✅ Mode will prompt with 3-second timeout (defaults to yes)"
        ;;
        
    4)
        echo "Removing Mode auto-start..."
        
        # Remove the auto-start section from .zshrc
        if grep -q "# Mode Terminal Navigator Auto-Start" ~/.zshrc; then
            # Create a backup
            cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
            
            # Remove the auto-start section
            sed -i '' '/# Mode Terminal Navigator Auto-Start/,/^$/d' ~/.zshrc
            
            echo "✅ Mode auto-start removed from ~/.zshrc"
            echo "Backup saved as ~/.zshrc.backup.*"
        else
            echo "No Mode auto-start configuration found in ~/.zshrc"
        fi
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo
echo "📝 Note: You'll need to restart your terminal or run 'source ~/.zshrc' for changes to take effect"
echo
echo "🎯 Pro tip: Use 'Normal Use' in Mode to return to regular terminal in your home directory"
echo "🗂️  Pro tip: Use 'File System' in Mode to go straight to iCloud Drive and see contents"