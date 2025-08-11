#!/usr/bin/env python3

import sys
import subprocess
import os
from pathlib import Path

def check_and_install_dependencies():
    """Check and install required Python packages"""
    required_packages = ['rich', 'inquirer', 'requests', 'psutil']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"OK: {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"ERROR: {package} is missing")
    
    if missing_packages:
        print(f"\n> Installing missing packages: {', '.join(missing_packages)}")
        
        # Try different installation methods
        install_methods = [
            # Method 1: pip3 with --break-system-packages
            ['pip3', 'install', '--break-system-packages'] + missing_packages,
            # Method 2: python3 -m pip with --break-system-packages  
            [sys.executable, '-m', 'pip', 'install', '--break-system-packages'] + missing_packages,
            # Method 3: pip3 with --user
            ['pip3', 'install', '--user'] + missing_packages,
            # Method 4: python3 -m pip with --user
            [sys.executable, '-m', 'pip', 'install', '--user'] + missing_packages,
        ]
        
        for method in install_methods:
            try:
                print(f"Trying: {' '.join(method)}")
                result = subprocess.run(method, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("OK: Installation successful!")
                    
                    # Verify installation
                    all_installed = True
                    for package in missing_packages:
                        try:
                            __import__(package)
                        except ImportError:
                            all_installed = False
                            break
                    
                    if all_installed:
                        print("OK: All packages verified successfully!")
                        return True
                    else:
                        print("WARNING: Some packages still not available, trying next method...")
                        continue
                        
                else:
                    print(f"ERROR: {result.stderr}")
                    continue
                    
            except subprocess.TimeoutExpired:
                print("ERROR: Installation timed out")
                continue
            except Exception as e:
                print(f"ERROR: {e}")
                continue
        
        print("ERROR: All installation methods failed")
        return False
    
    print("OK: All required packages are available!")
    return True

def create_venv_if_needed():
    """Create a virtual environment for mode if system packages can't be installed"""
    mode_dir = Path.home() / '.mode'
    venv_dir = mode_dir / 'venv'
    
    if venv_dir.exists():
        print("OK: Virtual environment already exists")
        return str(venv_dir)
    
    print("> Creating virtual environment for Mode...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)
        
        # Install packages in the virtual environment
        pip_path = venv_dir / 'bin' / 'pip3'
        subprocess.run([str(pip_path), 'install', 'rich', 'inquirer', 'requests', 'psutil'], check=True)
        
        print("OK: Virtual environment created and packages installed")
        return str(venv_dir)
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to create virtual environment: {e}")
        return None

def update_mode_script_for_venv(venv_path):
    """Update the mode script to use the virtual environment"""
    mode_script = Path.home() / '.local' / 'bin' / 'mode'
    
    if not mode_script.exists():
        return False
    
    venv_python = Path(venv_path) / 'bin' / 'python3'
    
    content = f"""#!/bin/bash
# Mode Terminal Navigator Global Command (with virtual environment)
{venv_python} "$HOME/.mode/mode.py" "$@"
"""
    
    try:
        with open(mode_script, 'w') as f:
            f.write(content)
        
        # Make executable
        mode_script.chmod(0o755)
        print(f"OK: Updated mode script to use virtual environment")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update mode script: {e}")
        return False

def main():
    print("> Setting up Python environment for Mode Terminal Navigator...")
    print()
    
    # First try to install packages normally
    if check_and_install_dependencies():
        print("> Setup complete! You can now use 'mode' command.")
        return True
    
    # If that fails, create a virtual environment
    print("\n> System package installation failed, creating virtual environment...")
    venv_path = create_venv_if_needed()
    
    if venv_path:
        # Update the mode command to use the virtual environment
        if update_mode_script_for_venv(venv_path):
            print("> Setup complete with virtual environment! You can now use 'mode' command.")
            return True
    
    print("ERROR: Setup failed. You can still run mode directly:")
    print("python3 ~/.mode/mode.py")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)