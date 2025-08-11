import os
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from inquirer import text, list_input, confirm
from menu_input import show_menu

class ProjectManager:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        self.projects_path = Path(config['projects_path'])
        
    def show_menu(self):
        """Show project management menu"""
        options = [
            {
                'name': '• New Git Project - Create new project with Git initialization',
                'value': 'new_project',
                'description': 'Navigate to Projects folder, create new directory, initialize git, link to GitHub'
            },
            {
                'name': '• Environment Setup - Set up development environment',
                'value': 'env_setup',
                'description': 'Choose project type and auto-install dependencies and boilerplate'
            },
            {
                'name': '• Clone Repository - Clone existing repository from GitHub', 
                'value': 'clone_repo',
                'description': 'List repositories from JadenB9 GitHub account and clone selected repo'
            },
            {
                'name': '• Project Switcher - Navigate to existing projects',
                'value': 'switch_project', 
                'description': 'List all directories in Projects folder with last-modified dates'
            }
        ]
        
        while True:
            try:
                result = show_menu(
                    self.console,
                    "Project & Development Management",
                    options
                )
                
                if result == 'BACK' or result == 'back':
                    return 'continue'
                elif result == 'new_project':
                    create_result = self.create_new_project()
                    if create_result == 'exit':
                        return 'exit'
                elif result == 'env_setup':
                    self.setup_environment()
                elif result == 'clone_repo':
                    self.clone_repository()
                elif result == 'switch_project':
                    switch_result = self.switch_project()
                    if switch_result == 'exit':
                        return 'exit'
                    
            except KeyboardInterrupt:
                return 'continue'
                
    def create_new_project(self):
        """Create a new Git project"""
        try:
            # Ensure projects directory exists
            self.projects_path.mkdir(parents=True, exist_ok=True)
            
            # Ask for project name first
            project_name = text("Enter project name:")
            if not project_name:
                return
                
            # Ask for project type
            project_types = [
                'React/Next.js Frontend',
                'Node.js Backend',
                'Python (Flask/Django/FastAPI)', 
                'Full-stack MERN/MEAN',
                'Mobile (React Native/Flutter)',
                'Machine Learning (Python/Jupyter)',
                'Static Site (HTML/CSS/JS)',
                'WordPress/PHP',
                'Rust/Go/C++ project',
                'Docker/DevOps setup',
                'Chrome Extension',
                'Electron Desktop App',
                'Basic (No framework)'
            ]
            
            project_type = list_input(
                "Select project type:",
                choices=project_types,
                carousel=True
            )
            
            project_path = self.projects_path / project_name
            
            if project_path.exists():
                self.console.print(f"[red]Project '{project_name}' already exists![/red]")
                input("Press Enter to continue...")
                return
                
            # Create project directory
            project_path.mkdir()
            os.chdir(project_path)
            
            # Initialize git
            subprocess.run(['git', 'init'], check=True)
            
            # Create basic files
            readme_content = f"# {project_name}\n\nA {project_type} project created with Mode Terminal Navigator.\n"
            with open(project_path / 'README.md', 'w') as f:
                f.write(readme_content)
                
            # Create appropriate .gitignore based on project type
            gitignore_content = self.get_gitignore_for_type(project_type)
            with open(project_path / '.gitignore', 'w') as f:
                f.write(gitignore_content)
                
            # Set up project structure based on type
            self.setup_project_structure(project_path, project_type)
                
            # Initial commit
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Initial commit for {project_type} project'], check=True)
            
            # Try to create GitHub repo (requires gh CLI)
            try:
                create_remote = confirm("Create remote GitHub repository?")
                if create_remote:
                    subprocess.run(['gh', 'repo', 'create', project_name, '--public', '--push'], check=True)
                    self.console.print(f"[green]OK: Created GitHub repository: {self.config['github_username']}/{project_name}[/green]")
            except subprocess.CalledProcessError:
                self.console.print("[yellow]WARNING: GitHub CLI not available. Repository created locally only.[/yellow]")
            except FileNotFoundError:
                self.console.print("[yellow]WARNING: GitHub CLI not found. Repository created locally only.[/yellow]")
                
            # Update recent projects
            self.add_to_recent_projects(str(project_path))
            
            self.console.print(f"[green]OK: Project '{project_name}' created successfully![/green]")
            self.console.print(f"[blue]Location: {project_path}[/blue]")
            
            # Ask if user wants to switch to the project
            if confirm("Switch to the new project directory?"):
                # Write the target directory to a file that the shell can read
                cd_file = Path.home() / '.mode' / '.mode_cd'
                with open(cd_file, 'w') as f:
                    f.write(str(project_path))
                
                self.console.clear()
                self.console.print(f"[green]Switched to project: {project_name}[/green]")
                # Exit with special code to indicate directory change
                import sys
                sys.exit(42)
                
        except SystemExit:
            # Re-raise SystemExit to allow proper exit codes (like exit code 42)
            raise
        except Exception as e:
            self.console.print(f"[red]Error creating project: {e}[/red]")
            
        input("Press Enter to continue...")
        return 'continue'  # Return to project menu
        
    def clone_repository(self):
        """Clone a repository from GitHub"""
        try:
            # This would require GitHub API integration
            self.console.print("[yellow]Clone Repository feature requires GitHub API setup.[/yellow]")
            self.console.print("For now, you can manually clone using:")
            self.console.print(f"[blue]cd {self.projects_path}[/blue]")
            self.console.print(f"[blue]git clone https://github.com/{self.config['github_username']}/REPO_NAME[/blue]")
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            
        input("Press Enter to continue...")
        
    def switch_project(self):
        """Switch to an existing project with enhanced UI"""
        try:
            if not self.projects_path.exists():
                self.console.print(f"[red]Projects directory not found: {self.projects_path}[/red]")
                input("Press Enter to continue...")
                return 'continue'
                
            projects = []
            for item in self.projects_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Get last modified time and size info
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    
                    # Count files in project (quick way to see if it's active)
                    try:
                        file_count = len([f for f in item.iterdir() if f.is_file() and not f.name.startswith('.')])
                    except:
                        file_count = 0
                        
                    projects.append({
                        'name': item.name,
                        'path': str(item),
                        'modified': mtime.strftime("%Y-%m-%d %H:%M"),
                        'file_count': file_count,
                        'value': f"project_{item.name}"
                    })
                    
            if not projects:
                self.console.print("[yellow]No projects found in Projects directory.[/yellow]")
                input("Press Enter to continue...")
                return 'continue'
                
            # Sort by modification time (most recent first)
            projects.sort(key=lambda x: x['modified'], reverse=True)
            
            # Create enhanced project options
            project_options = []
            
            # Add recent projects section
            recent_projects = projects[:5]  # Top 5 most recent
            for i, proj in enumerate(recent_projects):
                status = "Recent" if i < 3 else "Active"
                project_options.append({
                    'name': f"• {proj['name']} - {status} ({proj['file_count']} files)",
                    'value': proj['value'],
                    'description': f"Modified: {proj['modified']} | Path: {proj['path']}"
                })
            
            # Add separator
            if len(projects) > 5:
                project_options.append({
                    'name': '--- Older Projects ---',
                    'value': 'separator',
                    'description': 'Older or less active projects'
                })
                
                # Add older projects
                for proj in projects[5:]:
                    project_options.append({
                        'name': f"• {proj['name']} ({proj['file_count']} files)",
                        'value': proj['value'],
                        'description': f"Modified: {proj['modified']} | Path: {proj['path']}"
                    })
            
            # Remove back option since b key handles it
            
            # Show enhanced project selector
            while True:
                result = show_menu(
                    self.console,
                    "Project Switcher - Choose Your Project",
                    project_options
                )
                
                if result == 'BACK' or result == 'back':
                    return 'continue'
                elif result == 'separator':
                    continue  # Skip separator, show menu again
                elif result.startswith('project_'):
                    # Extract project name from value
                    project_name = result.replace('project_', '')
                    selected_project = next(p for p in projects if p['name'] == project_name)
                    
                    # Show project info before switching
                    self.console.clear()
                    self.console.print(Panel(f"Switching to Project: {project_name}", style="bold green"))
                    self.console.print()
                    
                    # Show project details
                    details_table = Table(title="Project Details")
                    details_table.add_column("Property", style="cyan")
                    details_table.add_column("Value", style="white")
                    
                    details_table.add_row("Name", selected_project['name'])
                    details_table.add_row("Path", selected_project['path'])
                    details_table.add_row("Last Modified", selected_project['modified'])
                    details_table.add_row("Files", str(selected_project['file_count']))
                    
                    self.console.print(details_table)
                    self.console.print()
                    
                    # Write the target directory to a file that the shell can read
                    cd_file = Path.home() / '.mode' / '.mode_cd'
                    with open(cd_file, 'w') as f:
                        f.write(selected_project['path'])
                    
                    self.add_to_recent_projects(selected_project['path'])
                    
                    self.console.print(f"[green]Switched to project: {project_name}[/green]")
                    self.console.print(f"[blue]Directory: {selected_project['path']}[/blue]")
                    self.console.print()
                    
                    # Show directory contents
                    try:
                        import subprocess
                        result = subprocess.run(['ls', '-la'], capture_output=True, text=True, cwd=selected_project['path'])
                        if result.returncode == 0:
                            self.console.print("[bold blue]Project Contents:[/bold blue]")
                            # Show only first 10 lines to avoid clutter
                            lines = result.stdout.split('\n')[:10]
                            for line in lines:
                                if line.strip():
                                    self.console.print(line)
                            if len(result.stdout.split('\n')) > 10:
                                self.console.print("[dim]... and more files[/dim]")
                    except:
                        pass
                    
                    # Exit with special code to indicate directory change
                    import sys
                    sys.exit(42)
            
        except SystemExit:
            # Re-raise SystemExit to allow proper exit codes (like exit code 42)
            raise
        except Exception as e:
            self.console.print(f"[red]Error switching projects: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'
            
    def setup_environment(self):
        """Set up development environment for a project"""
        env_types = [
            'React/Next.js Frontend',
            'Node.js Backend', 
            'Python (Flask/Django/FastAPI)',
            'Full-stack MERN/MEAN',
            'Mobile (React Native/Flutter)',
            'Machine Learning (Python/Jupyter)',
            'Static Site (HTML/CSS/JS)',
            'WordPress/PHP',
            'Rust/Go/C++ project',
            'Docker/DevOps setup',
            'Chrome Extension',
            'Electron Desktop App'
        ]
        
        try:
            env_type = list_input(
                "Select project type:",
                choices=env_types,
                carousel=True
            )
            
            self.console.print(f"[blue]Setting up {env_type} environment...[/blue]")
            
            # Basic setup based on type
            if 'React' in env_type or 'Next.js' in env_type:
                self.setup_react_env()
            elif 'Node.js' in env_type:
                self.setup_nodejs_env()
            elif 'Python' in env_type:
                self.setup_python_env()
            else:
                self.console.print(f"[yellow]Environment setup for {env_type} is not yet implemented.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Error setting up environment: {e}[/red]")
            
        input("Press Enter to continue...")
        
    def setup_react_env(self):
        """Set up React/Next.js environment"""
        try:
            subprocess.run(['npm', 'init', '-y'], check=True)
            subprocess.run(['npm', 'install', 'react', 'react-dom', 'next'], check=True)
            subprocess.run(['npm', 'install', '--save-dev', '@types/react', '@types/node', 'typescript'], check=True)
            self.console.print("[green]OK: React environment set up successfully![/green]")
        except subprocess.CalledProcessError:
            self.console.print("[red]ERROR: Failed to set up React environment. Make sure npm is installed.[/red]")
            
    def setup_nodejs_env(self):
        """Set up Node.js environment"""
        try:
            subprocess.run(['npm', 'init', '-y'], check=True)
            subprocess.run(['npm', 'install', 'express', 'cors', 'dotenv'], check=True)
            subprocess.run(['npm', 'install', '--save-dev', 'nodemon', '@types/node'], check=True)
            self.console.print("[green]OK: Node.js environment set up successfully![/green]")
        except subprocess.CalledProcessError:
            self.console.print("[red]ERROR: Failed to set up Node.js environment. Make sure npm is installed.[/red]")
            
    def setup_python_env(self):
        """Set up Python environment"""
        try:
            subprocess.run(['python3', '-m', 'venv', 'venv'], check=True)
            subprocess.run(['pip', 'install', 'flask', 'requests', 'python-dotenv'], check=True)
            self.console.print("[green]OK: Python environment set up successfully![/green]")
            self.console.print("[blue]Don't forget to activate the virtual environment: source venv/bin/activate[/blue]")
        except subprocess.CalledProcessError:
            self.console.print("[red]ERROR: Failed to set up Python environment. Make sure Python 3 is installed.[/red]")
            
    def get_gitignore_for_type(self, project_type: str) -> str:
        """Get appropriate .gitignore content for project type"""
        base_ignore = """# General
.DS_Store
*.log
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
"""
        
        if 'React' in project_type or 'Node.js' in project_type or 'MERN' in project_type:
            return base_ignore + """
# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next/
out/

# Build outputs
dist/
build/
"""
        elif 'Python' in project_type:
            return base_ignore + """
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Jupyter Notebook
.ipynb_checkpoints
"""
        elif 'WordPress' in project_type or 'PHP' in project_type:
            return base_ignore + """
# WordPress
wp-config.php
wp-content/uploads/
wp-content/cache/

# PHP
vendor/
composer.lock
"""
        else:
            return base_ignore
            
    def setup_project_structure(self, project_path: Path, project_type: str):
        """Set up initial project structure based on type"""
        try:
            if 'React' in project_type:
                # Initialize with create-react-app or create-next-app
                if 'Next.js' in project_type:
                    subprocess.run(['npx', 'create-next-app@latest', '.', '--typescript', '--tailwind', '--eslint', '--app', '--src-dir', '--import-alias', '@/*'], 
                                 check=True, cwd=project_path)
                else:
                    subprocess.run(['npx', 'create-react-app', '.', '--template', 'typescript'], 
                                 check=True, cwd=project_path)
                                 
            elif 'Node.js' in project_type:
                subprocess.run(['npm', 'init', '-y'], check=True, cwd=project_path)
                subprocess.run(['npm', 'install', 'express', 'cors', 'dotenv', 'helmet', 'morgan'], check=True, cwd=project_path)
                subprocess.run(['npm', 'install', '--save-dev', 'nodemon', '@types/node', 'typescript'], check=True, cwd=project_path)
                
                # Create basic server file
                server_content = """const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: 'Hello from your new Node.js server!' });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
"""
                with open(project_path / 'server.js', 'w') as f:
                    f.write(server_content)
                    
            elif 'Python' in project_type:
                subprocess.run(['python3', '-m', 'venv', 'venv'], check=True, cwd=project_path)
                
                if 'Flask' in project_type:
                    # Create basic Flask app
                    app_content = """from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return jsonify({'message': 'Hello from your new Flask server!'})

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', 5000))
"""
                    with open(project_path / 'app.py', 'w') as f:
                        f.write(app_content)
                        
                    # Create requirements.txt
                    requirements = """Flask==2.3.2
Flask-CORS==4.0.0
python-dotenv==1.0.0
"""
                    with open(project_path / 'requirements.txt', 'w') as f:
                        f.write(requirements)
                        
        except subprocess.CalledProcessError as e:
            self.console.print(f"[yellow]Warning: Could not set up full project structure: {e}[/yellow]")
        except Exception as e:
            self.console.print(f"[yellow]Warning: Error setting up project structure: {e}[/yellow]")
            
    def add_to_recent_projects(self, project_path: str):
        """Add project to recent projects list"""
        recent = self.config.get('recent_projects', [])
        
        # Remove if already exists
        recent = [p for p in recent if p != project_path]
        
        # Add to front
        recent.insert(0, project_path)
        
        # Keep only last 10
        recent = recent[:10]
        
        self.config['recent_projects'] = recent