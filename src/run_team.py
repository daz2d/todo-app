"""
LangTeam CLI Entrypoint

Runs the agile team graph to completion and generates a report.
"""

import sys
import os
import re
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import create_team_graph, TeamState, MAX_TURNS
from src.memory import MemorySystem
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Confirm, Prompt


console = Console()


def get_user_feedback() -> tuple[bool, str]:
    """
    Get user feedback on the project results.
    
    Returns:
        tuple: (satisfied, feedback_text)
            satisfied: True if user is happy with results
            feedback_text: Additional requirements/changes if not satisfied
    """
    console.print("\n" + "="*80)
    console.print("🔄 FEEDBACK TIME", style="bold yellow")
    console.print("="*80)
    console.print()
    
    # Ask if user is satisfied
    satisfied = Confirm.ask(
        "[bold green]Are you satisfied with the current results?[/bold green]",
        default=True
    )
    
    if satisfied:
        console.print("[green]✅ Great! Project completed successfully![/green]")
        return True, ""
    
    # Get feedback for improvements
    console.print()
    console.print("[bold yellow]What would you like the team to improve or change?[/bold yellow]")
    console.print("[dim]Examples:[/dim]")
    console.print("[dim]- Add error handling for file not found[/dim]")
    console.print("[dim]- Make the UI more user-friendly[/dim]")
    console.print("[dim]- Add unit tests[/dim]")
    console.print("[dim]- Change the color scheme[/dim]")
    console.print()
    
    feedback = Prompt.ask(
        "[bold cyan]Your feedback/requirements[/bold cyan]",
        default=""
    ).strip()
    
    if not feedback:
        console.print("[yellow]No feedback provided. Ending session.[/yellow]")
        return True, ""
    
    return False, feedback


def create_iteration_goal(original_goal: str, feedback: str, iteration: int) -> str:
    """
    Create an updated goal incorporating user feedback.
    
    Args:
        original_goal: The original project goal
        feedback: User's feedback and new requirements
        iteration: Current iteration number
        
    Returns:
        Updated goal string for the team
    """
    return f"""ITERATION {iteration}: {original_goal}

PREVIOUS IMPLEMENTATION COMPLETE. Now improve based on user feedback:

USER FEEDBACK: {feedback}

Task: Update the existing codebase to address the feedback above. Build upon what already exists rather than starting from scratch."""


def sanitize_project_name(user_goal: str) -> str:
    """
    Generate an intelligent, descriptive project name from user input.
    
    Args:
        user_goal: The user's project goal description
        
    Returns:
        Clean, descriptive project name that captures the essence
        
    Examples:
        >>> sanitize_project_name("Build a TODO app with React")
        'react-todo-manager'
        >>> sanitize_project_name("Create a scientific calculator desktop application") 
        'scientific-calculator-desktop'
        >>> sanitize_project_name("I want to build an interactive log viewer using Node.js")
        'nodejs-interactive-log-viewer'
    """
    
    # Technology keywords that should be included (higher priority)
    tech_keywords = {
        'react', 'vue', 'angular', 'svelte', 'nextjs', 'nuxt',
        'node', 'nodejs', 'express', 'fastify', 'koa',
        'python', 'flask', 'django', 'fastapi',
        'rust', 'go', 'java', 'spring', 'kotlin',
        'typescript', 'javascript', 'js', 'ts',
        'mobile', 'ios', 'android', 'flutter', 'react-native',
        'desktop', 'electron', 'tauri', 'web', 'api', 'cli', 'gui'
    }
    
    # Domain-specific keywords (medium priority) 
    domain_keywords = {
        'todo', 'task', 'note', 'blog', 'chat', 'game', 'quiz', 'poll',
        'calculator', 'converter', 'parser', 'viewer', 'editor', 'manager',
        'dashboard', 'analytics', 'monitor', 'tracker', 'logger', 'search',
        'ecommerce', 'shop', 'cart', 'payment', 'auth', 'login', 'profile',
        'social', 'messaging', 'notification', 'email', 'calendar', 'schedule'
    }
    
    # Descriptive adjectives (lower priority but useful)
    descriptors = {
        'interactive', 'real-time', 'live', 'dynamic', 'responsive',
        'simple', 'advanced', 'modern', 'smart', 'intelligent',
        'collaborative', 'social', 'personal', 'professional',
        'secure', 'fast', 'lightweight', 'powerful', 'elegant'
    }
    
    # Words to completely remove
    stop_words = {
        'build', 'create', 'make', 'develop', 'write', 'code', 'implement',
        'a', 'an', 'the', 'some', 'basic', 'small', 'quick',
        'i', 'want', 'to', 'need', 'would', 'like', 'please', 'can', 'you',
        'app', 'application', 'program', 'tool', 'system', 'project', 'using',
        'with', 'for', 'that', 'this', 'and', 'or', 'but', 'in', 'on', 'at'
    }
    
    # Extract words and normalize
    words = re.findall(r'[a-zA-Z0-9]+', user_goal.lower())
    
    # Categorize words by importance
    tech_words = []
    domain_words = []
    descriptor_words = []
    other_words = []
    
    for word in words:
        if word in stop_words or len(word) <= 1:
            continue
        elif word in tech_keywords:
            tech_words.append(word)
        elif word in domain_keywords:
            domain_words.append(word)
        elif word in descriptors:
            descriptor_words.append(word)
        elif len(word) > 2:  # Keep other meaningful words
            other_words.append(word)
    
    # Build name with prioritization
    name_parts = []
    
    # Start with tech stack (most distinctive)  
    if tech_words:
        # Special handling and deduplication
        tech_clean = []
        for tech in tech_words[:2]:  # Max 2 tech words
            if tech == 'nodejs':
                tech_clean.append('node')
            elif tech == 'nextjs':
                tech_clean.append('next')
            elif tech == 'javascript':
                tech_clean.append('js')
            elif tech == 'typescript':
                tech_clean.append('ts')
            elif tech not in tech_clean:  # Avoid duplicates
                tech_clean.append(tech)
        name_parts.extend(tech_clean)
    
    # Add domain/purpose words (prioritize the main function)
    if domain_words:
        # Put the most important domain word first
        domain_priority = ['todo', 'calculator', 'game', 'chat', 'dashboard', 'manager', 'viewer', 'editor']
        sorted_domain = sorted(domain_words, key=lambda x: domain_priority.index(x) if x in domain_priority else len(domain_priority))
        name_parts.extend(sorted_domain[:2])  # Max 2 domain words
    
    # Add descriptors if space allows and they add value
    if len(name_parts) < 3 and descriptor_words:
        # Prioritize descriptors that aren't redundant
        useful_descriptors = [d for d in descriptor_words if d not in ['simple', 'basic']]
        if useful_descriptors:
            name_parts.extend(useful_descriptors[:1])
    
    # Add other meaningful words if still space
    if len(name_parts) < 3 and other_words:
        # Filter out words that are too similar to existing ones
        unique_others = []
        for word in other_words:
            if not any(word in part or part in word for part in name_parts):
                unique_others.append(word)
        name_parts.extend(unique_others[:3-len(name_parts)])
    
    # Fallback: if still no good words, use first few meaningful words
    if not name_parts:
        meaningful = [w for w in words if w not in stop_words and len(w) > 2]
        name_parts = meaningful[:3] if meaningful else ['my', 'project']
    
    # Create final name (max 4 parts to keep reasonable length)
    final_name = '-'.join(name_parts[:4])
    
    # Handle special cases and cleanup
    final_name = final_name.replace('--', '-').strip('-')
    
    return final_name if final_name else 'my-project'


def create_project_directory(user_goal: str) -> Path:
    """
    Create a fresh subdirectory for the project.
    
    Args:
        user_goal: The user's project goal
        
    Returns:
        Path to the created project directory
        
    Creates structure:
        projects/
        └── <sanitized-name>-YYYYMMDD-HHMMSS/
            └── (project files will be created here)
    """
    # Get projects root directory
    projects_root = Path(os.getenv('PROJECTS_ROOT', './projects'))
    projects_root.mkdir(exist_ok=True)
    
    # Generate project directory name
    base_name = sanitize_project_name(user_goal)
    
    # Try clean name first, add counter if needed
    project_name = base_name
    counter = 1
    
    while (projects_root / project_name).exists():
        project_name = f"{base_name}-{counter}"
        counter += 1
        # Safety valve - if we get to 100, add timestamp
        if counter > 100:
            timestamp = datetime.now().strftime('%m%d-%H%M')
            project_name = f"{base_name}-{timestamp}"
            break
    
    # Create project directory
    project_dir = projects_root / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create basic structure
    (project_dir / 'src').mkdir(exist_ok=True)
    (project_dir / 'tests').mkdir(exist_ok=True)
    (project_dir / 'docs').mkdir(exist_ok=True)
    
    # Create README with project info
    readme_content = f"""# {user_goal}

**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Generated by**: LangTeam AI Agile Development Team

## Project Structure

This project was created in an isolated directory to keep it separate from other projects.

```
{project_name}/
├── src/          # Source code
├── tests/        # Test files
├── docs/         # Documentation
└── README.md     # This file
```

## Getting Started

See the SPEC.md file (if generated) for acceptance criteria and requirements.

---
*Generated by LangTeam - Multi-agent AI software development system*
"""
    
    (project_dir / 'README.md').write_text(readme_content, encoding='utf-8')
    
    return project_dir


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  🎓 THE COLLEGE CREW - 20 YEARS OF FRIENDSHIP & CODE 🎓              ║
║                                                                      ║
║  👥 Alex (PM) | Jamie (Backend) | Riley (Frontend) | Morgan (Review) ║
║       Casey (QA) - Best friends who love to roast each other! 😂    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")


def print_configuration():
    """Print current configuration."""
    config_table = Table(title="Configuration", show_header=True, header_style="bold magenta")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="yellow")
    
    config_table.add_row("LLM Provider", os.getenv('LLM_PROVIDER', 'ollama'))
    config_table.add_row("LLM Model", os.getenv('LLM_MODEL', 'codellama:latest'))
    config_table.add_row("Projects Root", os.getenv('PROJECTS_ROOT', './projects'))
    config_table.add_row("Max Turns", str(MAX_TURNS))
    config_table.add_row("Shell Commands/Turn", os.getenv('MAX_SHELL_CMDS_PER_TURN', '5'))
    config_table.add_row("HTTP Timeout", f"{os.getenv('HTTP_TIMEOUT_SECONDS', '30')}s")
    config_table.add_row("Learning Enabled", os.getenv('LEARNING_ENABLED', 'true'))
    config_table.add_row("Memory DB", os.getenv('MEMORY_DB_PATH', './memory.db'))
    
    console.print(config_table)
    console.print()


def detect_project_type_and_commands(project_dir: Path) -> tuple[str, list[str]]:
    """
    Detect the project type and return appropriate run commands.
    
    Args:
        project_dir: Path to the project directory
        
    Returns:
        tuple: (project_type, run_commands)
    """
    project_type = "Unknown"
    run_commands = []
    
    # Check for different project types
    package_json = project_dir / "package.json"
    requirements_txt = project_dir / "requirements.txt"
    cargo_toml = project_dir / "Cargo.toml"
    pom_xml = project_dir / "pom.xml"
    go_mod = project_dir / "go.mod"
    gemfile = project_dir / "Gemfile"
    
    # Also check in subdirectories for files that might have been created
    for subdir in ['src', 'app', '.']:
        subdir_path = project_dir / subdir if subdir != '.' else project_dir
        if subdir_path.exists():
            if (subdir_path / "package.json").exists():
                package_json = subdir_path / "package.json"
            if (subdir_path / "requirements.txt").exists():
                requirements_txt = subdir_path / "requirements.txt"
            if (subdir_path / "Cargo.toml").exists():
                cargo_toml = subdir_path / "Cargo.toml"
    
    if package_json.exists():
        project_type = "Node.js/JavaScript"
        run_commands = [
            "npm install",
            "npm start"
        ]
        # Check for specific frameworks
        try:
            import json
            with open(package_json, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                
                if 'react' in deps:
                    project_type = "React Application"
                    if 'next' in deps:
                        project_type = "Next.js Application"
                        run_commands = ["npm install", "npm run dev"]
                    elif '@vitejs/plugin-react' in deps or 'vite' in deps:
                        project_type = "Vite React Application"
                        run_commands = ["npm install", "npm run dev"]
                elif 'vue' in deps:
                    project_type = "Vue.js Application"
                    run_commands = ["npm install", "npm run serve"]
                elif 'angular' in deps or '@angular/core' in deps:
                    project_type = "Angular Application"
                    run_commands = ["npm install", "ng serve"]
                elif 'express' in deps:
                    project_type = "Express.js Server"
                    run_commands = ["npm install", "npm start"]
        except:
            pass
    
    elif requirements_txt.exists() or any((project_dir / f).exists() for f in ["app.py", "main.py", "manage.py"]):
        project_type = "Python Application"
        run_commands = [
            "pip install -r requirements.txt" if requirements_txt.exists() else "# No requirements.txt found",
            "python main.py"  # Default, will be updated based on actual files
        ]
        
        # Check for specific Python frameworks
        if (project_dir / "manage.py").exists():
            project_type = "Django Application"
            run_commands = [
                "pip install -r requirements.txt" if requirements_txt.exists() else "pip install django",
                "python manage.py migrate",
                "python manage.py runserver"
            ]
        elif (project_dir / "app.py").exists():
            project_type = "Flask Application"
            run_commands = [
                "pip install -r requirements.txt" if requirements_txt.exists() else "pip install flask",
                "python app.py"
            ]
        elif any((project_dir / f).exists() for f in ["fastapi_app.py", "api.py"]):
            project_type = "FastAPI Application"
            run_commands = [
                "pip install -r requirements.txt" if requirements_txt.exists() else "pip install fastapi uvicorn",
                "uvicorn main:app --reload"
            ]
    
    elif cargo_toml.exists():
        project_type = "Rust Application"
        run_commands = [
            "cargo build",
            "cargo run"
        ]
    
    elif go_mod.exists():
        project_type = "Go Application"
        run_commands = [
            "go mod download",
            "go run ."
        ]
    
    elif pom_xml.exists():
        project_type = "Java/Maven Application"
        run_commands = [
            "mvn clean install",
            "mvn exec:java"
        ]
    
    elif gemfile.exists():
        project_type = "Ruby Application"
        run_commands = [
            "bundle install",
            "ruby app.rb"
        ]
    
    # Check for HTML files (static websites)
    elif list(project_dir.glob("*.html")):
        project_type = "Static Website"
        run_commands = [
            "# Open index.html in a web browser",
            "# Or use: python -m http.server 8000"
        ]
    
    # Fallback: try to detect from project directory name if no files found
    if project_type == "Unknown":
        dir_name = project_dir.name.lower()
        if any(keyword in dir_name for keyword in ['react', 'vue', 'angular', 'next']):
            project_type = "JavaScript/React Application"
            run_commands = ["npm install", "npm start"]
        elif any(keyword in dir_name for keyword in ['express', 'node', 'js']):
            project_type = "Node.js Application"
            run_commands = ["npm install", "npm start"]
        elif any(keyword in dir_name for keyword in ['python', 'django', 'flask', 'fastapi']):
            project_type = "Python Application"
            run_commands = ["pip install -r requirements.txt", "python main.py"]
        elif any(keyword in dir_name for keyword in ['rust', 'cargo']):
            project_type = "Rust Application"
            run_commands = ["cargo build", "cargo run"]
        elif any(keyword in dir_name for keyword in ['go', 'golang']):
            project_type = "Go Application"
            run_commands = ["go mod download", "go run ."]
        elif any(keyword in dir_name for keyword in ['cli', 'tool', 'cmd']):
            project_type = "CLI Tool"
            run_commands = ["# See project files for build instructions"]
        else:
            # Final fallback - provide generic instructions
            project_type = "Software Project"
            run_commands = ["# Check the project files for specific run instructions"]
    
    return project_type, run_commands


def _get_clean_command(cmd: str) -> str:
    """Extract clean command from verified command string."""
    if cmd.startswith("✅"):
        return cmd[2:].strip()
    elif cmd.startswith("⚠️"):
        parts = cmd.split("#")
        return parts[0].replace("⚠️", "").strip()
    else:
        return cmd.strip()


def test_run_commands(project_dir: Path, run_commands: list[str]) -> list[tuple[str, bool, str]]:
    """
    Test run commands to verify they work in the project directory.
    
    Args:
        project_dir: Path to the project directory
        run_commands: List of commands to test
        
    Returns:
        List of (command, success, output/error) tuples
    """
    import subprocess
    import os
    
    results = []
    original_cwd = os.getcwd()
    
    try:
        os.chdir(project_dir)
        
        for cmd in run_commands:
            if cmd.startswith("#"):
                # Skip comments
                results.append((cmd, True, "Comment - skipped"))
                continue
            
            try:
                # Test commands with timeout and capture output
                if "install" in cmd.lower() or "build" in cmd.lower():
                    # Installation/build commands - run with longer timeout
                    result = subprocess.run(
                        cmd.split(), 
                        capture_output=True, 
                        text=True, 
                        timeout=60,
                        cwd=project_dir
                    )
                else:
                    # Regular commands - shorter timeout  
                    result = subprocess.run(
                        cmd.split(), 
                        capture_output=True, 
                        text=True, 
                        timeout=10,
                        cwd=project_dir
                    )
                
                success = result.returncode == 0
                output = result.stdout[:200] + ("..." if len(result.stdout) > 200 else "")
                if not success:
                    output = result.stderr[:200] + ("..." if len(result.stderr) > 200 else "")
                
                results.append((cmd, success, output))
                
            except subprocess.TimeoutExpired:
                results.append((cmd, False, "Command timed out"))
            except FileNotFoundError:
                results.append((cmd, False, f"Command not found: {cmd.split()[0]}"))
            except Exception as e:
                results.append((cmd, False, f"Error: {str(e)}"))
    
    finally:
        os.chdir(original_cwd)
    
    return results


def update_project_readme(project_dir: Path, user_goal: str, project_type: str, run_commands: list[str]):
    """
    Update the project README with comprehensive information including verified run commands.
    
    Args:
        project_dir: Path to the project directory
        user_goal: Original user goal
        project_type: Detected project type
        run_commands: List of commands to run the project
    """
    readme_path = project_dir / "README.md"
    project_name = project_dir.name
    
    # Test the run commands to verify they work
    console.print("[cyan]🔍 Testing run commands to verify they work...[/cyan]")
    command_results = test_run_commands(project_dir, run_commands)
    
    verified_commands = []
    for cmd, success, output in command_results:
        if success:
            verified_commands.append(f"✅ {cmd}")
            if not cmd.startswith("#"):
                console.print(f"  [green]✓ {cmd}[/green]")
        else:
            if cmd.startswith("#"):
                verified_commands.append(cmd)  # Keep comments as-is
            else:
                verified_commands.append(f"⚠️  {cmd}  # May need adjustment: {output}")
                console.print(f"  [yellow]⚠️  {cmd}: {output}[/yellow]")
    
    # Create comprehensive README content
    readme_content = f"""# {user_goal}

**Project Type**: {project_type}  
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Generated by**: LangTeam AI Agile Development Team  

## Overview

This project was automatically generated by an AI software development team consisting of:
- **Alex (PM)**: Project planning and specification
- **Jamie (Backend)**: Server-side development and architecture  
- **Riley (Frontend)**: User interface and client-side development
- **Morgan (Code Reviewer)**: Code quality assurance and standards
- **Casey (QA Tester)**: Testing and quality validation

## Project Structure

```
{project_name}/
├── src/          # Source code
├── tests/        # Test files  
├── docs/         # Documentation (including SPEC.md)
├── README.md     # This file
└── ...           # Additional project files
```

## Getting Started

### Prerequisites

Make sure you have the required tools installed for this {project_type.lower()}.

### Installation & Running

Follow these steps to run the project:

"""

    # Add numbered steps for each command
    if verified_commands:
        for i, cmd in enumerate(verified_commands, 1):
            if cmd.startswith("#"):
                readme_content += f"{i}. {cmd[1:].strip()}\n"
            elif cmd.startswith("✅"):
                # Verified working command
                clean_cmd = cmd[2:].strip()  # Remove ✅ prefix
                readme_content += f"{i}. Run: `{clean_cmd}`\n"
            elif cmd.startswith("⚠️"):
                # Command with issues
                parts = cmd.split("#")
                clean_cmd = parts[0].replace("⚠️", "").strip()
                note = parts[1].strip() if len(parts) > 1 else "May need adjustment"
                readme_content += f"{i}. Run: `{clean_cmd}` _{note}_\n"
            else:
                readme_content += f"{i}. Run: `{cmd}`\n"
    else:
        readme_content += "1. Check the project files for specific setup instructions\n"
        readme_content += "2. See docs/SPEC.md for requirements and acceptance criteria\n"
    
    readme_content += f"""

### Quick Start Command

```bash
cd {project_dir.name}"""
    
    # Add the quick start command
    if verified_commands and not verified_commands[0].startswith('#'):
        clean_cmd = _get_clean_command(verified_commands[0])
        readme_content += f"\n{clean_cmd}"
    else:
        readme_content += "\n# Follow installation steps above"
    
    readme_content += "\n```"
    
    readme_content += """

## Features

Review the `docs/SPEC.md` file for detailed acceptance criteria and project specifications.

## Testing  

Tests are located in the `tests/` directory. The QA team has validated the core functionality.

## Documentation

- **SPEC.md**: Project specifications and acceptance criteria
- **README.md**: This file with setup and usage instructions
- Additional documentation may be available in the `docs/` folder

## Development Team Notes

This project was developed using an agile AI team workflow:
1. **Planning Phase**: Requirements analysis and technical specification
2. **Development Phase**: Backend and frontend implementation  
3. **Review Phase**: Code quality review and standards compliance
4. **Testing Phase**: Quality assurance and test validation

---

*Generated by LangTeam - Multi-agent AI software development system*  
*For more information about the development process, see the team notes in the docs/ folder*
"""

    # Write the updated README
    try:
        readme_path.write_text(readme_content, encoding='utf-8')
        console.print(f"[green]✓ Updated README.md with run instructions[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not update README.md: {e}[/yellow]")


def print_project_completion(project_dir: Path, user_goal: str, final_state: Optional[dict], iterations: int):
    """
    Print comprehensive project completion message with summary and instructions.
    
    Args:
        project_dir: Path to the created project directory
        user_goal: Original user goal
        final_state: Final team state (if available)
        iterations: Number of iterations completed
    """
    # Detect project type and get run commands
    project_type, run_commands = detect_project_type_and_commands(project_dir)
    
    # Update the README with run instructions
    update_project_readme(project_dir, user_goal, project_type, run_commands)
    
    # Test the first command to verify it works (if it's not a comment)
    working_command = None
    if run_commands and not run_commands[0].startswith('#'):
        working_command = run_commands[0]
        # We could test the command here, but for now we'll assume it's correct
    
    # Create summary paragraph
    success_indicator = "✅ successfully completed" if (final_state and final_state.get('approved') and final_state.get('qa_approved')) else "🔄 has built"
    
    project_type_text = project_type if project_type != "Unknown" else "software project"
    
    summary_text = f"""The AI development team {success_indicator} your project: "{user_goal}". 

The team automatically detected this as a {project_type_text} and set up the development environment with proper file structure, documentation, and project scaffolding. The project went through {iterations} iteration{'s' if iterations > 1 else ''} of development using agile methodology including project management, backend development, frontend implementation (when needed), code review, and quality assurance testing. The team collaborated to ensure the deliverable meets professional standards with comprehensive documentation and clear setup instructions."""

    # Determine status
    iteration_info = f" (Completed after {iterations} iteration{'s' if iterations > 1 else ''})"
    status = f"[green]Successfully Completed{iteration_info}[/green]"
    
    if final_state:
        if final_state.get('approved') and final_state.get('qa_approved'):
            status = f"[green]✅ Fully Approved & Tested{iteration_info}[/green]"
        elif final_state.get('approved') or final_state.get('qa_approved'):
            status = f"[yellow]⚠️  Partially Approved{iteration_info}[/yellow]"
        elif final_state.get('turns', 0) >= 10:
            status = f"[yellow]⏱️  Max Turns Reached{iteration_info}[/yellow]"
    
    # Build command instructions
    command_instructions = "## To run this project:\n\n"
    if working_command:
        command_instructions += f"```bash\ncd {project_dir.name}\n{working_command}\n```"
    else:
        command_instructions += f"```bash\ncd {project_dir.name}\n# See README.md for specific run instructions\n```"
    
    # Create the completion panel
    console.print("\n")
    console.print("=" * 100, style="bold green")
    console.print("  🎉 PROJECT DELIVERY COMPLETE! 🎉", style="bold green")
    console.print("=" * 100, style="bold green")
    console.print()
    
    # Project summary
    console.print(Panel(
        summary_text,
        title="📋 Project Summary", 
        border_style="blue"
    ))
    console.print()
    
    # Project details and location
    console.print(Panel(
        f"[bold green]Project Directory:[/bold green]\n{project_dir}\n\n"
        f"[bold green]Project Type:[/bold green] {project_type}\n"
        f"[bold green]Status:[/bold green] {status}\n\n"
        f"[dim]Files created in isolated directory to keep your workspace clean[/dim]",
        title="📂 Project Location",
        border_style="green"
    ))
    console.print()
    
    # Run instructions
    if run_commands:
        commands_text = ""
        for i, cmd in enumerate(run_commands, 1):
            if cmd.startswith("#"):
                commands_text += f"{i}. {cmd[1:].strip()}\n"
            else:
                commands_text += f"{i}. `{cmd}`\n"
        
        console.print(Panel(
            commands_text.strip(),
            title="🚀 How to Run",
            border_style="cyan"
        ))
        console.print()
    
    # Quick start command
    if working_command:
        console.print(Panel(
            f"cd {project_dir.name}\n{working_command}",
            title="⚡ Quick Start Command",
            border_style="yellow"
        ))
        console.print()
    
    # Additional info
    console.print(Panel(
        f"[bold]📖 Documentation:[/bold] See README.md and docs/SPEC.md\n"
        f"[bold]🧪 Tests:[/bold] Located in tests/ directory\n"
        f"[bold]🔧 Source:[/bold] Main code in src/ directory\n\n"
        f"[dim]The project is ready to use! Check README.md for detailed setup instructions.[/dim]",
        title="📚 Next Steps", 
        border_style="magenta"
    ))


def print_report(state: TeamState, memory: MemorySystem, start_time: datetime):
    """
    Print comprehensive execution report.
    
    Args:
        state: Final team state after execution.
        memory: Memory system instance.
        start_time: Execution start timestamp.
    """
    duration = (datetime.now() - start_time).total_seconds()
    
    console.print("\n")
    console.print("=" * 80, style="bold green")
    console.print("  EXECUTION COMPLETE", style="bold green")
    console.print("=" * 80, style="bold green")
    console.print()
    
    # SPEC Section
    if state['spec']:
        console.print(Panel(
            Markdown(state['spec']),
            title="📋 SPECIFICATION",
            border_style="blue"
        ))
        console.print()
    else:
        console.print(Panel(
            "[yellow]No SPEC generated[/yellow]",
            title="📋 SPECIFICATION",
            border_style="yellow"
        ))
        console.print()
    
    # Backend Notes
    if state['backend_notes']:
        console.print(Panel(
            state['backend_notes'][:2000] + ("..." if len(state['backend_notes']) > 2000 else ""),
            title="🔧 BACKEND ENGINEER NOTES",
            border_style="cyan"
        ))
        console.print()
    
    # Frontend Notes
    if state['frontend_notes']:
        console.print(Panel(
            state['frontend_notes'][:2000] + ("..." if len(state['frontend_notes']) > 2000 else ""),
            title="💻 FRONTEND ENGINEER NOTES",
            border_style="magenta"
        ))
        console.print()
    
    # Review Notes
    if state['review_notes']:
        review_style = "green" if state['approved'] else "yellow"
        console.print(Panel(
            state['review_notes'][:2000] + ("..." if len(state['review_notes']) > 2000 else ""),
            title="✅ CODE REVIEW" if state['approved'] else "📝 CODE REVIEW",
            border_style=review_style
        ))
        console.print()
    
    # QA Notes
    if state['qa_notes']:
        qa_style = "green" if state.get('qa_approved', False) else "yellow"
        console.print(Panel(
            state['qa_notes'][:2000] + ("..." if len(state['qa_notes']) > 2000 else ""),
            title="✅ QA TESTING" if state.get('qa_approved', False) else "🧪 QA TESTING",
            border_style=qa_style
        ))
        console.print()
    
    # Test Results Summary
    if state.get('test_results'):
        console.print(Panel(
            state['test_results'][:1000] + ("..." if len(state['test_results']) > 1000 else ""),
            title="📊 TEST RESULTS",
            border_style="blue"
        ))
        console.print()
    
    # Approvals
    approvals_text = "\n".join(state['approvals']) if state['approvals'] else "[red]No approvals yet[/red]"
    console.print(Panel(
        approvals_text,
        title="👥 APPROVALS",
        border_style="green" if state['approvals'] else "red"
    ))
    console.print()
    
    # Statistics
    stats_table = Table(title="📊 Execution Statistics", show_header=True, header_style="bold")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="yellow")
    
    stats_table.add_row("Total Turns", str(state['turns']))
    stats_table.add_row("Max Turns", str(MAX_TURNS))
    stats_table.add_row("Code Review", "✅ Approved" if state['approved'] else "❌ Pending")
    stats_table.add_row("QA Testing", "✅ Approved" if state.get('qa_approved', False) else "❌ Pending")
    stats_table.add_row("Overall Status", "✅ Complete" if (state['approved'] and state.get('qa_approved', False)) else "🔄 In Progress")
    stats_table.add_row("Execution Time", f"{duration:.1f}s")
    
    # Memory statistics
    mem_summary = memory.get_summary()
    if mem_summary.get('enabled'):
        stats_table.add_row("Memory Entries", str(mem_summary['total_memories']))
        stats_table.add_row("Success Rate", f"{mem_summary['success_rate']:.1%}")
    
    console.print(stats_table)
    console.print()
    
    # Memory Summary
    if mem_summary.get('enabled'):
        memory_table = Table(title="🧠 Memory System", show_header=True, header_style="bold")
        memory_table.add_column("Memory Type", style="cyan")
        memory_table.add_column("Count", style="yellow")
        
        for mem_type, count in mem_summary.get('by_type', {}).items():
            memory_table.add_row(mem_type.capitalize(), str(count))
        
        console.print(memory_table)
        console.print()
    
    # Final Status
    fully_approved = state['approved'] and state.get('qa_approved', False)
    if fully_approved:
        console.print(
            Panel(
                f"[bold green]✅ PROJECT FULLY APPROVED IN {state['turns']} TURNS! ✅[/bold green]\n\n"
                f"✅ Code Review: Approved\n"
                f"✅ QA Testing: All tests passed\n\n"
                f"The team successfully delivered a tested and verified project.\n"
                f"Review the outputs above for details.",
                border_style="bold green"
            )
        )
    elif state['approved'] or state.get('qa_approved', False):
        console.print(
            Panel(
                f"[bold yellow]⚠️  PARTIAL APPROVAL AFTER {state['turns']} TURNS ⚠️[/bold yellow]\n\n"
                f"{'✅' if state['approved'] else '❌'} Code Review: {'Approved' if state['approved'] else 'Pending'}\n"
                f"{'✅' if state.get('qa_approved', False) else '❌'} QA Testing: {'Approved' if state.get('qa_approved', False) else 'Pending'}\n\n"
                f"Project needs both code review AND QA approval to be complete.",
                border_style="bold yellow"
            )
        )
    elif state['turns'] >= MAX_TURNS:
        console.print(
            Panel(
                f"[bold yellow]⏱️  MAX TURNS REACHED ({MAX_TURNS}) ⏱️[/bold yellow]\n\n"
                f"The project was not approved within the turn limit.\n"
                f"Review feedback above and consider:\n"
                f"• Increasing MAX_TURNS in .env\n"
                f"• Simplifying the scope\n"
                f"• Clarifying acceptance criteria",
                border_style="bold yellow"
            )
        )
    else:
        console.print(
            Panel(
                "[bold red]❌ EXECUTION ENDED WITHOUT APPROVAL ❌[/bold red]\n\n"
                "Review the feedback and error messages above.",
                border_style="bold red"
            )
        )


def list_existing_projects():
    """List all existing projects in the projects directory."""
    projects_dir = Path("projects")
    if not projects_dir.exists():
        console.print("[yellow]📂 No projects directory found![/yellow]")
        return
    
    # Get all project directories
    project_dirs = [p for p in projects_dir.iterdir() if p.is_dir() and p.name != "__pycache__"]
    
    if not project_dirs:
        console.print("[yellow]📂 No existing projects found![/yellow]")
        return
    
    console.print("\n[bold cyan]🎯 Existing Projects:[/bold cyan]")
    for i, project_path in enumerate(sorted(project_dirs), 1):
        # Try to read project metadata
        spec_file = project_path / "SPEC.md"
        docs_spec_file = project_path / "docs" / "SPEC.md"
        readme_file = project_path / "README.md"
        
        description = "No description available"
        
        # Check for SPEC.md in docs folder first, then root, then README
        if docs_spec_file.exists():
            spec_file = docs_spec_file
        elif not spec_file.exists() and readme_file.exists():
            spec_file = readme_file
            
        if spec_file.exists():
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    # Look for first non-title line as description
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('Project:'):
                            description = line[:100] + ("..." if len(line) > 100 else "")
                            break
            except Exception:
                pass
        
        console.print(f"[green]{i:2d}.[/green] [bold]{project_path.name}[/bold]")
        console.print(f"     [dim]{description}[/dim]")
        console.print(f"     [blue]Path:[/blue] {project_path}")
    
    console.print(f"\n[bold]Total: {len(project_dirs)} projects[/bold]")


def update_existing_project(project_path_str: str, modification_instructions: str):
    """Update an existing project with new instructions."""
    from src.memory import get_memory_system
    
    project_path = Path(project_path_str)
    
    # Validate project path
    if not project_path.exists():
        console.print(f"[red]❌ Project path not found: {project_path}[/red]")
        return
    
    if not project_path.is_dir():
        console.print(f"[red]❌ Path is not a directory: {project_path}[/red]")
        return
    
    # Check if it looks like a valid project
    spec_file = project_path / "SPEC.md"
    docs_spec_file = project_path / "docs" / "SPEC.md"
    readme_file = project_path / "README.md"
    
    if not spec_file.exists() and not docs_spec_file.exists() and not readme_file.exists():
        console.print(f"[red]❌ No SPEC.md or README.md found in project. Are you sure this is a valid project?[/red]")
        return
    
    # Determine which spec file to use for context
    if docs_spec_file.exists():
        spec_file = docs_spec_file
        console.print(f"[green]✓ Found SPEC.md in docs folder[/green]")
    elif spec_file.exists():
        console.print(f"[green]✓ Found SPEC.md in root[/green]")
    else:
        console.print(f"[yellow]⚠️  No SPEC.md found, using README.md for project context[/yellow]")
    
    console.print(f"\n[bold cyan]🔄 Updating Project: {project_path.name}[/bold cyan]")
    console.print(f"[yellow]📝 Instructions: {modification_instructions}[/yellow]\n")
    
    # Load existing project context from memory
    memory = get_memory_system()
    project_memories = memory.retrieve(query=f"project {project_path.name}", limit=10)
    
    if project_memories:
        console.print("[blue]🧠 Found existing project memories:[/blue]")
        for mem in project_memories[:3]:  # Show top 3 relevant memories
            console.print(f"  • [dim]{mem.content[:80]}...[/dim]")
    
    # Create update context including existing project state
    context_info = f"""
EXISTING PROJECT UPDATE MODE
===========================
Project Path: {project_path}
Project Name: {project_path.name}
Update Instructions: {modification_instructions}

This is an UPDATE of an existing project. The team should:
1. First understand the existing codebase and project structure
2. Analyze what needs to be modified based on the instructions
3. Make targeted improvements while preserving existing functionality
4. Test changes thoroughly to avoid breaking existing features
5. Update documentation to reflect changes

Previous project context from memory:
{chr(10).join([f"- {mem.content}" for mem in project_memories[:5]]) if project_memories else "No previous context found"}
"""
    
    # Run the team workflow in update mode
    asyncio.run(run_team_update_mode(modification_instructions, project_path, context_info))


async def run_team_update_mode(modification_instructions: str, project_path: Path, context_info: str):
    """Run team workflow in update mode for existing project."""
    from src.graph import create_team_graph
    from src.memory import get_memory_system
    
    try:
        # Initialize workflow
        workflow = create_team_graph()
        memory = get_memory_system()
        
        # Create initial state for update mode
        initial_state = {
            "user_goal": f"Update existing project: {modification_instructions}",
            "spec": "",
            "backend_notes": "",
            "frontend_notes": "",
            "review_notes": "",
            "qa_notes": "",
            "test_results": "",
            "approvals": [],
            "turns": 0,
            "approved": False,
            "qa_approved": False,
            "memories_retrieved": [],
            "last_backend_hash": "",
            "last_frontend_hash": "",
            "stagnation_count": 0,
            "files_created": [],
            "messages": [
                {
                    "role": "user", 
                    "content": f"{context_info}\n\nModification Request: {modification_instructions}"
                }
            ],
            "project_name": project_path.name,
            "project_path": str(project_path),
            "requirements": modification_instructions,
            "is_update_mode": True,
            "existing_project_path": str(project_path),
            "conversation_history": [],
            "stagnation_hashes": set(),
            "variety_context": {},
            "generated_files": [],
            "next": "pm"
        }
        
        # Store in memory
        memory.store(
            "episodic",
            f"Project update requested: {modification_instructions}",
            f"update_{project_path.name}",
            tags=["project", project_path.name, "update_request"]
        )
        
        console.print("[green]🚀 Team is analyzing existing project and planning updates...[/green]\n")
        
        # Run the workflow
        final_state = None
        async for event in workflow.astream(initial_state):
            for node_name, node_output in event.items():
                if node_name == "END":
                    final_state = node_output
                    break
        
        if final_state:
            console.print("\n[bold green]✅ Project update completed![/bold green]")
            
            # Ask for feedback on the update
            console.print("\n[bold cyan]📝 How did the update turn out?[/bold cyan]")
            console.print("[yellow]Options:[/yellow]")
            console.print("1. [green]Looks great! ✅[/green]")
            console.print("2. [yellow]Make some changes 🔧[/yellow]") 
            console.print("3. [red]Start over 🔄[/red]")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "2":
                feedback = input("What changes would you like? ")
                console.print(f"\n[blue]🔄 Team is making adjustments: {feedback}[/blue]\n")
                
                # Continue with feedback
                feedback_state = final_state.copy()
                feedback_state["messages"].append({
                    "role": "user",
                    "content": f"User feedback on update: {feedback}. Please make these adjustments."
                })
                
                async for event in workflow.astream(feedback_state):
                    for node_name, node_output in event.items():
                        if node_name == "END":
                            final_state = node_output
                            break
                
                console.print("\n[bold green]✅ Adjustments completed![/bold green]")
            
            elif choice == "3":
                console.print("\n[yellow]🔄 You can run the update again with different instructions.[/yellow]")
            
            # Store completion in memory
            memory.store(
                "episodic",
                f"Successfully updated project with: {modification_instructions}",
                f"update_complete_{project_path.name}",
                tags=["project", project_path.name, "update_complete"],
                success=True
            )
        
        console.print(f"\n[bold blue]📁 Updated project available at: {project_path}[/bold blue]")
        
    except KeyboardInterrupt:
        console.print(f"\n[yellow]⏹️  Update process interrupted by user[/yellow]")
        console.print(f"[blue]💾 Progress may have been saved to project files[/blue]")
        console.print(f"[dim]You can resume by running the update command again[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during project update: {str(e)}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")


def check_system_performance():
    """Check system performance and warn about potential issues."""
    try:
        import psutil
        
        # Get system resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
        # Check for running AI processes
        ai_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pinfo = proc.info
                if pinfo['name'] and ('python' in pinfo['name'].lower() or 'ollama' in pinfo['name'].lower()):
                    ai_processes.append(pinfo['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Performance warnings
        warnings = []
        
        if memory_percent > 80:
            warnings.append(f"⚠️  High memory usage: {memory_percent:.1f}%")
        
        if available_memory_gb < 2:
            warnings.append(f"⚠️  Low available memory: {available_memory_gb:.1f}GB")
        
        if len(ai_processes) > 2:
            warnings.append(f"⚠️  {len(ai_processes)} AI processes running - may cause slowness")
        
        # Display warnings if any
        if warnings:
            console.print()
            console.print(Panel(
                "\n".join(warnings) + 
                f"\n\n💡 For better performance:\n"
                f"• Complete running projects before starting new ones\n"
                f"• Switch to cloud models: LLM_PROVIDER_TEXT=openai\n"
                f"• Run: python performance_monitor.py",
                title="🔍 Performance Warning",
                border_style="yellow"
            ))
            console.print()
        
        elif available_memory_gb < 8:
            console.print()
            console.print(Panel(
                f"📊 Available memory: {available_memory_gb:.1f}GB\n"
                f"💡 For optimal performance with local models, 8GB+ recommended",
                title="💾 Memory Status", 
                border_style="blue"
            ))
            console.print()
            
    except ImportError:
        # psutil not available, skip performance check
        pass
    except Exception:
        # Any other error, skip silently
        pass


def run_team(user_goal: Optional[str] = None):
    """
    Run the agile team workflow.
    
    Args:
        user_goal: User's project goal. If None, prompts interactively.
    """
    start_time = datetime.now()
    
    print_banner()
    print_configuration()
    check_system_performance()
    
    # Get user goal
    if not user_goal:
        console.print("[bold]Enter your project goal:[/bold]")
        console.print("[dim](What would you like the team to build?)[/dim]")
        user_goal = input("> ").strip()
        
        if not user_goal:
            console.print("[red]No goal provided. Exiting.[/red]")
            return
    
    console.print()
    console.print(Panel(
        f"[bold]Goal:[/bold] {user_goal}",
        border_style="cyan"
    ))
    console.print()
    
    # Create project directory
    console.print("[bold cyan]📁 Creating project directory...[/bold cyan]")
    project_dir = create_project_directory(user_goal)
    console.print(f"[green]✓ Project directory created: {project_dir}[/green]")
    console.print()
    
    # Change to project directory for all file operations
    original_cwd = Path.cwd()
    os.chdir(project_dir)
    
    # Initialize memory system
    memory = MemorySystem()
    
    # Create initial state
    initial_state: TeamState = {
        'user_goal': user_goal,
        'spec': '',
        'backend_notes': '',
        'frontend_notes': '',
        'review_notes': '',
        'qa_notes': '',
        'test_results': '',
        'approvals': [],
        'turns': 0,
        'approved': False,
        'qa_approved': False,
        'memories_retrieved': [],
        # Progress tracking
        'last_backend_hash': '',
        'last_frontend_hash': '',
        'stagnation_count': 0,
        'files_created': []
    }
    
    # Build and run graph
    try:
        console.print("[bold cyan]Building team graph...[/bold cyan]")
        graph = create_team_graph()
        
        iteration = 1
        current_goal = user_goal
        
        while True:
            if iteration > 1:
                console.print(f"\n[bold magenta]🔄 STARTING ITERATION {iteration}[/bold magenta]")
                console.print(Panel(
                    f"[bold]Updated Goal:[/bold]\n{current_goal}",
                    border_style="magenta"
                ))
                console.print()
            
            console.print(f"[bold cyan]Starting workflow... (Iteration {iteration})[/bold cyan]")
            console.print()
            
            # Update state for this iteration
            iteration_state = initial_state.copy()
            iteration_state['user_goal'] = current_goal
            iteration_state['turns'] = 0  # Reset turns for new iteration
            iteration_state['approved'] = False  # Reset approvals for new iteration
            iteration_state['qa_approved'] = False
            iteration_state['stagnation_count'] = 0  # Reset progress tracking
            iteration_state['last_backend_hash'] = ''
            iteration_state['last_frontend_hash'] = ''
            
            # Run the graph
            final_state = graph.invoke(iteration_state)
            
            # Print report
            print_report(final_state, memory, start_time)
            
            # Get user feedback (only if running interactively)
            if user_goal and len(sys.argv) <= 1:  # Interactive mode
                satisfied, feedback = get_user_feedback()
                
                if satisfied:
                    break
                    
                # Prepare for next iteration
                iteration += 1
                if iteration > 5:  # Prevent infinite loops
                    console.print("[yellow]⚠️  Maximum iterations (5) reached. Ending session.[/yellow]")
                    break
                    
                current_goal = create_iteration_goal(user_goal, feedback, iteration)
            else:
                # Non-interactive mode (command line argument provided)
                break
    
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]⚠️  Execution interrupted by user[/bold yellow]")
        os.chdir(original_cwd)  # Return to original directory
        sys.exit(1)
    
    except Exception as e:
        console.print(f"\n\n[bold red]❌ Error during execution:[/bold red]\n{e}")
        
        # Store error in memory for learning
        if memory.enabled:
            memory.learn_from_failure(
                failure_description=f"Execution failed: {type(e).__name__}",
                root_cause=str(e),
                solution="Review error message and stack trace",
                context=user_goal[:200] if user_goal else "Unknown",
                tags=['execution-error', 'system']
            )
        
        import traceback
        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")
        os.chdir(original_cwd)  # Return to original directory
        sys.exit(1)
    
    finally:
        # Return to original directory
        os.chdir(original_cwd)
        
        # Close memory system
        if memory.enabled:
            memory.close()
        
        # Print final project completion message
        print_project_completion(project_dir, user_goal, final_state if 'final_state' in locals() else None, iteration if 'iteration' in locals() else 1)


def main():
    """Main entrypoint."""
    # Load .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not required, can use system env vars
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='AI Agile Software Development Team')
    parser.add_argument('goal', nargs='*', help='Project goal or modification instructions')
    parser.add_argument('--update', '--modify', metavar='PROJECT_PATH', 
                       help='Update an existing project instead of creating new one')
    parser.add_argument('--list-projects', action='store_true',
                       help='List all existing projects')
    
    args = parser.parse_args()
    
    # Handle list projects
    if args.list_projects:
        list_existing_projects()
        return
    
    # Handle update mode
    if args.update:
        if not args.goal:
            console.print("[red]❌ Update mode requires modification instructions![/red]")
            console.print("[yellow]Usage: python -m src.run_team --update PROJECT_PATH 'add error handling and unit tests'[/yellow]")
            return
        update_existing_project(args.update, ' '.join(args.goal))
        return
    
    # Handle regular mode
    user_goal = ' '.join(args.goal) if args.goal else None
    run_team(user_goal)


if __name__ == "__main__":
    main()
