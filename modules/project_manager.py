import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from menu_input import show_menu

MENU_STYLE = Style([
    ("qmark", "fg:cyan bold"),
    ("question", "fg:white bold"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:green bold"),
    ("selected", "fg:green"),
    ("answer", "fg:green bold"),
])


class ProjectManager:
    def __init__(self, config: Dict[str, Any], console: Console):
        self.config = config
        self.console = console
        self.projects_path = Path(config['projects_path'])

    # ------------------------------------------------------------------
    # Main menu
    # ------------------------------------------------------------------
    def show_menu(self):
        """Show project management menu."""
        options = [
            {
                'name': 'New Git Project - Create new project with Git init',
                'value': 'new_project',
                'description': 'Create directory, init git, optional GitHub remote'
            },
            {
                'name': 'Environment Setup - Install deps & boilerplate',
                'value': 'env_setup',
                'description': 'Choose project type and auto-install dependencies'
            },
            {
                'name': 'Clone Repository - Clone from your GitHub',
                'value': 'clone_repo',
                'description': 'Browse your GitHub repos and clone one locally'
            },
            {
                'name': 'Project Switcher - Jump to a project',
                'value': 'switch_project',
                'description': 'Rich table view with git status for every project'
            }
        ]

        while True:
            try:
                result = show_menu(
                    self.console,
                    "Project & Development Management",
                    options
                )

                if result in ('BACK', 'back'):
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

    # ------------------------------------------------------------------
    # Helpers: git info for a directory
    # ------------------------------------------------------------------
    @staticmethod
    def _git_info(project_path: Path) -> Dict[str, str]:
        """Return branch name and status indicator for a project directory.

        Returns dict with keys 'branch' and 'status'.
        Status symbols:
            (checkmark)  - clean working tree
            (pencil)     - modified tracked files
            ?            - untracked files present
            --           - not a git repo
        """
        git_dir = project_path / '.git'
        if not git_dir.exists():
            return {'branch': '--', 'status': '--'}

        try:
            branch = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, cwd=project_path, timeout=5
            )
            branch_name = branch.stdout.strip() if branch.returncode == 0 else '??'
        except Exception:
            branch_name = '??'

        try:
            porcelain = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=project_path, timeout=5
            )
            if porcelain.returncode != 0:
                status_icon = '??'
            else:
                lines = [l for l in porcelain.stdout.splitlines() if l.strip()]
                if not lines:
                    status_icon = '\u2713'  # checkmark - clean
                else:
                    has_modified = any(not l.startswith('?') for l in lines)
                    has_untracked = any(l.startswith('?') for l in lines)
                    if has_modified and has_untracked:
                        status_icon = '\u270e ?'
                    elif has_modified:
                        status_icon = '\u270e'   # pencil - modified
                    else:
                        status_icon = '?'        # untracked only
        except Exception:
            status_icon = '??'

        return {'branch': branch_name, 'status': status_icon}

    # ------------------------------------------------------------------
    # CLAUDE.md generation
    # ------------------------------------------------------------------
    @staticmethod
    def _generate_claude_md(project_name: str, project_type: str) -> str:
        """Generate a CLAUDE.md file tailored to the project type."""

        type_lower = project_type.lower()

        # Determine tech stack
        if 'next.js' in type_lower or 'react' in type_lower and 'native' not in type_lower:
            tech = "- React / Next.js\n- TypeScript\n- Tailwind CSS"
            run_cmd = "npm run dev"
            test_cmd = "npm test"
            build_cmd = "npm run build"
            structure = (
                "src/           - Application source code\n"
                "public/        - Static assets\n"
                "package.json   - Dependencies & scripts"
            )
        elif 'node.js' in type_lower:
            tech = "- Node.js / Express\n- JavaScript"
            run_cmd = "npm start  (or: npx nodemon server.js)"
            test_cmd = "npm test"
            build_cmd = "N/A"
            structure = (
                "server.js      - Entry point\n"
                ".env           - Environment variables\n"
                "package.json   - Dependencies & scripts"
            )
        elif 'python' in type_lower:
            tech = "- Python 3\n- Flask / Django / FastAPI\n- venv"
            run_cmd = "python app.py  (or: flask run)"
            test_cmd = "pytest"
            build_cmd = "pip install -r requirements.txt"
            structure = (
                "app.py              - Entry point\n"
                "requirements.txt    - Dependencies\n"
                "venv/               - Virtual environment"
            )
        elif 'mern' in type_lower or 'mean' in type_lower:
            tech = "- MongoDB / Express / React / Node.js"
            run_cmd = "npm run dev"
            test_cmd = "npm test"
            build_cmd = "npm run build"
            structure = (
                "client/        - React frontend\n"
                "server/        - Express backend\n"
                "package.json   - Root scripts"
            )
        elif 'mobile' in type_lower or 'react native' in type_lower or 'flutter' in type_lower:
            tech = "- React Native / Flutter"
            run_cmd = "npx expo start  (or: flutter run)"
            test_cmd = "npm test  (or: flutter test)"
            build_cmd = "eas build  (or: flutter build)"
            structure = (
                "app/           - Screens & components\n"
                "assets/        - Images & fonts"
            )
        elif 'machine learning' in type_lower or 'jupyter' in type_lower:
            tech = "- Python 3\n- Jupyter Notebook\n- NumPy / Pandas / scikit-learn"
            run_cmd = "jupyter notebook"
            test_cmd = "pytest"
            build_cmd = "pip install -r requirements.txt"
            structure = (
                "notebooks/     - Jupyter notebooks\n"
                "data/          - Datasets\n"
                "models/        - Saved models"
            )
        elif 'static' in type_lower or 'html' in type_lower:
            tech = "- HTML / CSS / JavaScript"
            run_cmd = "open index.html  (or: npx live-server)"
            test_cmd = "N/A"
            build_cmd = "N/A"
            structure = (
                "index.html     - Main page\n"
                "css/           - Stylesheets\n"
                "js/            - Scripts"
            )
        elif 'wordpress' in type_lower or 'php' in type_lower:
            tech = "- PHP\n- WordPress"
            run_cmd = "php -S localhost:8000"
            test_cmd = "phpunit"
            build_cmd = "composer install"
            structure = (
                "wp-content/themes/   - Custom themes\n"
                "wp-content/plugins/  - Custom plugins"
            )
        elif 'rust' in type_lower:
            tech = "- Rust / Cargo"
            run_cmd = "cargo run"
            test_cmd = "cargo test"
            build_cmd = "cargo build --release"
            structure = (
                "src/           - Source code\n"
                "Cargo.toml     - Dependencies"
            )
        elif 'go' in type_lower:
            tech = "- Go"
            run_cmd = "go run ."
            test_cmd = "go test ./..."
            build_cmd = "go build"
            structure = (
                "main.go        - Entry point\n"
                "go.mod         - Module definition"
            )
        elif 'docker' in type_lower or 'devops' in type_lower:
            tech = "- Docker / Docker Compose"
            run_cmd = "docker compose up"
            test_cmd = "docker compose run test"
            build_cmd = "docker compose build"
            structure = (
                "Dockerfile         - Container definition\n"
                "docker-compose.yml - Service orchestration"
            )
        elif 'chrome extension' in type_lower:
            tech = "- JavaScript / Chrome Extensions API"
            run_cmd = "Load unpacked in chrome://extensions"
            test_cmd = "N/A"
            build_cmd = "N/A"
            structure = (
                "manifest.json  - Extension manifest\n"
                "popup/         - Popup UI\n"
                "background.js  - Service worker"
            )
        elif 'electron' in type_lower:
            tech = "- Electron\n- Node.js\n- HTML/CSS/JS or React"
            run_cmd = "npm start"
            test_cmd = "npm test"
            build_cmd = "npm run build"
            structure = (
                "main.js        - Electron main process\n"
                "renderer/      - UI code\n"
                "package.json   - Dependencies & scripts"
            )
        else:
            tech = "- (custom stack)"
            run_cmd = "N/A"
            test_cmd = "N/A"
            build_cmd = "N/A"
            structure = "."

        return f"""# Project: {project_name}

## Overview
{project_type} project created with Mode Terminal.

## Tech Stack
{tech}

## Development
- Run: `{run_cmd}`
- Test: `{test_cmd}`
- Build: `{build_cmd}`

## Structure
{structure}
"""

    # ------------------------------------------------------------------
    # Create new project
    # ------------------------------------------------------------------
    def create_new_project(self):
        """Create a new Git project with CLAUDE.md auto-generation."""
        try:
            self.projects_path.mkdir(parents=True, exist_ok=True)

            project_name = questionary.text(
                "Enter project name:",
                style=MENU_STYLE
            ).ask()
            if not project_name:
                return 'continue'

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

            project_type = questionary.select(
                "Select project type:",
                choices=project_types,
                style=MENU_STYLE
            ).ask()
            if not project_type:
                return 'continue'

            project_path = self.projects_path / project_name

            if project_path.exists():
                self.console.print(f"[red]Project '{project_name}' already exists![/red]")
                input("Press Enter to continue...")
                return 'continue'

            # Create project directory
            project_path.mkdir()
            os.chdir(project_path)

            # Initialize git
            subprocess.run(['git', 'init'], check=True, capture_output=True)

            # Create README
            readme_content = f"# {project_name}\n\nA {project_type} project created with Mode Terminal.\n"
            with open(project_path / 'README.md', 'w') as f:
                f.write(readme_content)

            # Create .gitignore
            gitignore_content = self.get_gitignore_for_type(project_type)
            with open(project_path / '.gitignore', 'w') as f:
                f.write(gitignore_content)

            # Generate CLAUDE.md
            claude_md = self._generate_claude_md(project_name, project_type)
            with open(project_path / 'CLAUDE.md', 'w') as f:
                f.write(claude_md)
            self.console.print("[green]Generated CLAUDE.md[/green]")

            # Set up project structure based on type
            self.setup_project_structure(project_path, project_type)

            # Initial commit
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            subprocess.run(
                ['git', 'commit', '-m', f'Initial commit for {project_type} project'],
                check=True, capture_output=True
            )

            # Offer to create remote GitHub repo
            try:
                create_remote = questionary.confirm(
                    "Create remote GitHub repository?",
                    default=False,
                    style=MENU_STYLE
                ).ask()
                if create_remote:
                    vis = questionary.select(
                        "Repository visibility:",
                        choices=['public', 'private'],
                        style=MENU_STYLE
                    ).ask()
                    flag = '--public' if vis == 'public' else '--private'
                    subprocess.run(
                        ['gh', 'repo', 'create', project_name, flag, '--source=.', '--push'],
                        check=True
                    )
                    self.console.print(
                        f"[green]Created GitHub repository: "
                        f"{self.config.get('github_username', 'you')}/{project_name}[/green]"
                    )
            except subprocess.CalledProcessError:
                self.console.print("[yellow]GitHub CLI error. Repo created locally only.[/yellow]")
            except FileNotFoundError:
                self.console.print("[yellow]GitHub CLI not found. Repo created locally only.[/yellow]")

            self.add_to_recent_projects(str(project_path))

            self.console.print(f"[green]Project '{project_name}' created![/green]")
            self.console.print(f"[blue]Location: {project_path}[/blue]")

            switch_now = questionary.confirm(
                "Switch to the new project directory?",
                default=True,
                style=MENU_STYLE
            ).ask()
            if switch_now:
                cd_file = Path.home() / '.mode' / '.mode_cd'
                cd_file.parent.mkdir(parents=True, exist_ok=True)
                with open(cd_file, 'w') as f:
                    f.write(str(project_path))
                self.console.clear()
                self.console.print(f"[green]Switched to project: {project_name}[/green]")
                sys.exit(42)

        except SystemExit:
            raise
        except Exception as e:
            self.console.print(f"[red]Error creating project: {e}[/red]")

        input("Press Enter to continue...")
        return 'continue'

    # ------------------------------------------------------------------
    # Clone repository (real implementation via gh CLI)
    # ------------------------------------------------------------------
    def clone_repository(self):
        """Clone a repository from your GitHub account using gh CLI."""
        try:
            self.console.print("[cyan]Fetching your repositories...[/cyan]")

            result = subprocess.run(
                ['gh', 'repo', 'list', '--limit', '50', '--json', 'name,description,updatedAt,isPrivate'],
                capture_output=True, text=True, timeout=15
            )

            if result.returncode != 0:
                self.console.print("[red]Failed to list repos. Make sure gh CLI is authenticated.[/red]")
                input("Press Enter to continue...")
                return

            repos = json.loads(result.stdout)
            if not repos:
                self.console.print("[yellow]No repositories found.[/yellow]")
                input("Press Enter to continue...")
                return

            # Sort by most recently updated
            repos.sort(key=lambda r: r.get('updatedAt', ''), reverse=True)

            choices = []
            for repo in repos:
                lock = "\U0001f512" if repo.get('isPrivate') else "\U0001f310"
                desc = repo.get('description') or ''
                if len(desc) > 50:
                    desc = desc[:47] + '...'
                label = f"{lock} {repo['name']}"
                if desc:
                    label += f"  \033[2m- {desc}\033[0m"
                choices.append(questionary.Choice(title=label, value=repo['name']))

            choices.append(questionary.Choice(title="\033[2m\u2190 Back\033[0m", value="BACK"))

            selected = questionary.select(
                "Select repository to clone:",
                choices=choices,
                style=MENU_STYLE,
                qmark="\u25b6",
                instruction="",
            ).ask()

            if not selected or selected == 'BACK':
                return

            self.projects_path.mkdir(parents=True, exist_ok=True)
            clone_target = self.projects_path / selected

            if clone_target.exists():
                self.console.print(f"[yellow]Directory already exists: {clone_target}[/yellow]")
                overwrite = questionary.confirm(
                    "Clone anyway (will fail if non-empty)?",
                    default=False,
                    style=MENU_STYLE
                ).ask()
                if not overwrite:
                    input("Press Enter to continue...")
                    return

            self.console.print(f"[cyan]Cloning {selected}...[/cyan]")
            username = self.config.get('github_username', '')
            clone_url = f"https://github.com/{username}/{selected}.git" if username else selected

            clone_result = subprocess.run(
                ['git', 'clone', clone_url, str(clone_target)],
                capture_output=True, text=True
            )

            if clone_result.returncode == 0:
                self.add_to_recent_projects(str(clone_target))
                self.console.print(f"[green]Cloned to {clone_target}[/green]")

                switch_now = questionary.confirm(
                    "Switch to the cloned project?",
                    default=True,
                    style=MENU_STYLE
                ).ask()
                if switch_now:
                    cd_file = Path.home() / '.mode' / '.mode_cd'
                    cd_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(cd_file, 'w') as f:
                        f.write(str(clone_target))
                    self.console.clear()
                    self.console.print(f"[green]Switched to project: {selected}[/green]")
                    sys.exit(42)
            else:
                self.console.print(f"[red]Clone failed: {clone_result.stderr.strip()}[/red]")

        except FileNotFoundError:
            self.console.print("[red]gh CLI not found. Install it: https://cli.github.com[/red]")
        except subprocess.TimeoutExpired:
            self.console.print("[red]Timed out talking to GitHub. Check your connection.[/red]")
        except SystemExit:
            raise
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        input("Press Enter to continue...")

    # ------------------------------------------------------------------
    # Project switcher (rich table with git status)
    # ------------------------------------------------------------------
    def switch_project(self):
        """Switch to an existing project with rich table and git status."""
        try:
            if not self.projects_path.exists():
                self.console.print(f"[red]Projects directory not found: {self.projects_path}[/red]")
                input("Press Enter to continue...")
                return 'continue'

            projects = []
            for item in self.projects_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    try:
                        file_count = len([
                            f for f in item.iterdir()
                            if f.is_file() and not f.name.startswith('.')
                        ])
                    except Exception:
                        file_count = 0

                    git = self._git_info(item)

                    projects.append({
                        'name': item.name,
                        'path': str(item),
                        'modified': mtime.strftime("%Y-%m-%d %H:%M"),
                        'mtime': mtime,
                        'file_count': file_count,
                        'branch': git['branch'],
                        'status': git['status'],
                    })

            if not projects:
                self.console.print("[yellow]No projects found.[/yellow]")
                input("Press Enter to continue...")
                return 'continue'

            # Sort by most recently modified
            projects.sort(key=lambda x: x['mtime'], reverse=True)

            # Display the rich table
            os.system("clear")
            table = Table(title="Projects", border_style="cyan", expand=True)
            table.add_column("#", style="dim", width=3, justify="right")
            table.add_column("Name", style="bold white", min_width=15)
            table.add_column("Branch", style="magenta", min_width=8)
            table.add_column("Status", justify="center", min_width=6)
            table.add_column("Modified", style="dim", min_width=14)
            table.add_column("Files", justify="right", style="cyan", min_width=5)

            for i, proj in enumerate(projects, 1):
                # Color the status indicator
                s = proj['status']
                if s == '\u2713':
                    status_str = "[green]\u2713[/green]"
                elif '\u270e' in s and '?' in s:
                    status_str = "[yellow]\u270e[/yellow] [red]?[/red]"
                elif '\u270e' in s:
                    status_str = "[yellow]\u270e[/yellow]"
                elif s == '?':
                    status_str = "[red]?[/red]"
                else:
                    status_str = "[dim]--[/dim]"

                table.add_row(
                    str(i),
                    proj['name'],
                    proj['branch'],
                    status_str,
                    proj['modified'],
                    str(proj['file_count']),
                )

            self.console.print(table)
            self.console.print()

            # Build choices for questionary (same order as table)
            choices = []
            for i, proj in enumerate(projects, 1):
                label = f"{i}. {proj['name']}  [{proj['branch']}]"
                choices.append(questionary.Choice(title=label, value=proj['name']))
            choices.append(questionary.Choice(title="\033[2m\u2190 Back\033[0m", value="BACK"))

            selected = questionary.select(
                "Select a project:",
                choices=choices,
                style=MENU_STYLE,
                qmark="\u25b6",
                instruction="",
            ).ask()

            if not selected or selected == 'BACK':
                return 'continue'

            selected_project = next(p for p in projects if p['name'] == selected)

            # Write target directory for shell wrapper
            cd_file = Path.home() / '.mode' / '.mode_cd'
            cd_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cd_file, 'w') as f:
                f.write(selected_project['path'])

            self.add_to_recent_projects(selected_project['path'])

            self.console.clear()
            self.console.print(f"[green]Switched to project: {selected}[/green]")
            self.console.print(f"[blue]Directory: {selected_project['path']}[/blue]")
            sys.exit(42)

        except SystemExit:
            raise
        except Exception as e:
            self.console.print(f"[red]Error switching projects: {e}[/red]")
            input("Press Enter to continue...")
            return 'continue'

    # ------------------------------------------------------------------
    # Environment setup
    # ------------------------------------------------------------------
    def setup_environment(self):
        """Set up development environment for a project."""
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
            env_type = questionary.select(
                "Select project type:",
                choices=env_types,
                style=MENU_STYLE
            ).ask()
            if not env_type:
                return

            self.console.print(f"[blue]Setting up {env_type} environment...[/blue]")

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
        """Set up React/Next.js environment."""
        try:
            subprocess.run(['npm', 'init', '-y'], check=True)
            subprocess.run(['npm', 'install', 'react', 'react-dom', 'next'], check=True)
            subprocess.run(['npm', 'install', '--save-dev', '@types/react', '@types/node', 'typescript'], check=True)
            self.console.print("[green]React environment set up.[/green]")
        except subprocess.CalledProcessError:
            self.console.print("[red]Failed to set up React environment. Make sure npm is installed.[/red]")

    def setup_nodejs_env(self):
        """Set up Node.js environment."""
        try:
            subprocess.run(['npm', 'init', '-y'], check=True)
            subprocess.run(['npm', 'install', 'express', 'cors', 'dotenv'], check=True)
            subprocess.run(['npm', 'install', '--save-dev', 'nodemon', '@types/node'], check=True)
            self.console.print("[green]Node.js environment set up.[/green]")
        except subprocess.CalledProcessError:
            self.console.print("[red]Failed to set up Node.js environment. Make sure npm is installed.[/red]")

    def setup_python_env(self):
        """Set up Python environment."""
        try:
            subprocess.run(['python3', '-m', 'venv', 'venv'], check=True)
            subprocess.run(['pip', 'install', 'flask', 'requests', 'python-dotenv'], check=True)
            self.console.print("[green]Python environment set up.[/green]")
            self.console.print("[blue]Activate the venv: source venv/bin/activate[/blue]")
        except subprocess.CalledProcessError:
            self.console.print("[red]Failed to set up Python environment. Make sure Python 3 is installed.[/red]")

    # ------------------------------------------------------------------
    # Gitignore templates
    # ------------------------------------------------------------------
    def get_gitignore_for_type(self, project_type: str) -> str:
        """Get appropriate .gitignore content for project type."""
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

    # ------------------------------------------------------------------
    # Project structure scaffolding
    # ------------------------------------------------------------------
    def setup_project_structure(self, project_path: Path, project_type: str):
        """Set up initial project structure based on type."""
        try:
            if 'React' in project_type:
                if 'Next.js' in project_type:
                    subprocess.run(
                        ['npx', 'create-next-app@latest', '.', '--typescript',
                         '--tailwind', '--eslint', '--app', '--src-dir',
                         '--import-alias', '@/*'],
                        check=True, cwd=project_path
                    )
                else:
                    subprocess.run(
                        ['npx', 'create-react-app', '.', '--template', 'typescript'],
                        check=True, cwd=project_path
                    )

            elif 'Node.js' in project_type:
                subprocess.run(['npm', 'init', '-y'], check=True, cwd=project_path)
                subprocess.run(
                    ['npm', 'install', 'express', 'cors', 'dotenv', 'helmet', 'morgan'],
                    check=True, cwd=project_path
                )
                subprocess.run(
                    ['npm', 'install', '--save-dev', 'nodemon', '@types/node', 'typescript'],
                    check=True, cwd=project_path
                )
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

                    requirements = """Flask==2.3.2
Flask-CORS==4.0.0
python-dotenv==1.0.0
"""
                    with open(project_path / 'requirements.txt', 'w') as f:
                        f.write(requirements)

        except subprocess.CalledProcessError as e:
            self.console.print(f"[yellow]Could not set up full project structure: {e}[/yellow]")
        except Exception as e:
            self.console.print(f"[yellow]Error setting up project structure: {e}[/yellow]")

    # ------------------------------------------------------------------
    # Recent projects tracking
    # ------------------------------------------------------------------
    def add_to_recent_projects(self, project_path: str):
        """Add project to recent projects list."""
        recent = self.config.get('recent_projects', [])
        recent = [p for p in recent if p != project_path]
        recent.insert(0, project_path)
        recent = recent[:10]
        self.config['recent_projects'] = recent
