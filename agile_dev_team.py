"""
Agile Software Development Team - Multi-Agent System
===================================================

This system simulates a complete agile development team with specialized agents following
modern software engineering best practices:

Team Members:
- Product Manager: Defines requirements using DDD principles (uses Mistral)
- UI Developer: Creates clean frontend code with Hexagonal Architecture (uses CodeLlama)
- Backend Developer: Implements DDD and Hexagonal Architecture (uses CodeLlama)
- Documentation Agent: Creates comprehensive documentation (uses Mistral)
- QA Tester: Implements TDD and tests architecture compliance (uses Mistral)
- Project Manager: Coordinates team and ensures quality standards (uses Mistral)

Development Guidelines:
- Test Driven Development (TDD): Red-Green-Refactor cycle
- Clean Code: Readable, maintainable, SOLID principles
- Hexagonal Architecture: Ports and Adapters pattern
- Domain Driven Design (DDD): Bounded contexts, domain modeling

Model Assignment Strategy:
- Mistral: Better for general text tasks (requirements, docs, management)
- CodeLlama: Specialized for code generation and programming tasks

GitHub Integration:
- Automatic repository creation with proper structure
- Issue templates and project setup
- Automatic push to GitHub with commit history
- Requires GITHUB_TOKEN environment variable with 'repo' scope
"""

import os
import time
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, TypedDict, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from github import Github
from github.GithubException import GithubException

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
        return True
    return False

# State definition for the development workflow
class GitHubIssue(TypedDict):
    """Represents a GitHub issue/task"""
    id: int
    title: str
    description: str
    labels: List[str]
    priority: str
    story_points: int
    acceptance_criteria: List[str]
    assignee: Optional[str]
    status: str  # 'backlog', 'in_progress', 'completed', 'blocked'

class DevelopmentState(TypedDict):
    project_brief: str
    project_dir: str
    requirements: str
    architecture: Optional[str]
    tasks: List[GitHubIssue]
    current_task: Optional[GitHubIssue]
    completed_tasks: List[GitHubIssue]
    available_agents: List[str]
    ui_code: str
    backend_code: str
    documentation: str
    test_results: str
    project_status: str
    iteration_count: int
    feedback: List[str]
    git_commits: List[str]
    # Quality assurance tracking
    agent_reviews: Dict[str, Dict[str, Any]]  # {agent_name: {self_review: str, peer_reviews: [], issues: [], revisions: []}}
    quality_gates_passed: Dict[str, bool]  # {agent_name: passed}
    revision_requests: List[Dict[str, str]]  # [{from_agent: str, to_agent: str, issue: str, severity: str}]
    max_revisions: int

# Initialize different LLMs for different task types
# Mistral for general tasks (requirements, documentation, management)
general_llm = ChatOllama(
    model="mistral",
    temperature=0.3
)

# CodeLlama for coding tasks (UI and backend development)
code_llm = ChatOllama(
    model="codellama",
    temperature=0.1  # Lower temperature for more precise code generation
)

# =============================================================================
# GIT INTEGRATION UTILITIES
# =============================================================================

class GitManager:
    """Handles all Git operations for the development team"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()  # Use absolute path
        # Don't create directory here - it's handled by caller
    
    def init_repository(self) -> bool:
        """Initialize a new Git repository"""
        try:
            # Ensure project directory exists
            self.project_dir.mkdir(parents=True, exist_ok=True)
            
            # Store current directory and change to project dir
            original_dir = os.getcwd()
            os.chdir(self.project_dir)
            
            # Initialize git repo
            subprocess.run(["git", "init"], check=True, capture_output=True)
            
            # Create .gitignore
            gitignore_content = """
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Dependencies
node_modules/
*.log

# Build
dist/
build/
*.egg-info/
"""
            gitignore_path = self.project_dir / ".gitignore"
            gitignore_path.write_text(gitignore_content.strip(), encoding='utf-8')
            
            print(f"✅ Git repository initialized in {self.project_dir}")
            
            # Return to original directory
            os.chdir(original_dir)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
            # Return to original directory on error
            try:
                os.chdir(original_dir)
            except:
                pass
            return False
        except Exception as e:
            print(f"❌ Error initializing Git: {e}")
            # Return to original directory on error
            try:
                os.chdir(original_dir)
            except:
                pass
            return False
    
    def commit_changes(self, message: str, author: str = "AI Agent") -> bool:
        """Commit all current changes"""
        try:
            # Work from repository root, not project subdirectory
            os.chdir(Path.cwd())
            
            # Add all changes
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            # Check if there are changes to commit
            result = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
            if result.returncode == 0:
                print(f"ℹ️ No changes to commit for: {message}")
                return True
            
            # Commit changes
            subprocess.run(["git", "commit", "-m", message, "--author", f"{author} <ai@devteam.local>"], 
                         check=True, capture_output=True)
            
            print(f"📝 Git commit: {message}")
            
            # Push to existing remote repository
            try:
                subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
                print(f"🚀 Pushed to remote: {message}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Push failed (but commit succeeded): {e}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git commit error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error committing changes: {e}")
            return False
    
    def create_branch(self, branch_name: str) -> bool:
        """Create and switch to a new branch"""
        try:
            os.chdir(self.project_dir)
            subprocess.run(["git", "checkout", "-b", branch_name], check=True, capture_output=True)
            print(f"🌿 Created and switched to branch: {branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Branch creation error: {e}")
            return False
    
    def get_file_content(self, file_path: str) -> str:
        """Read content of a file in the project"""
        try:
            full_path = self.project_dir / file_path
            if full_path.exists():
                return full_path.read_text(encoding='utf-8')
            return ""
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return ""
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to a file in the project"""
        try:
            # If project_dir is different from current dir, use relative path from project_dir
            if str(self.project_dir) != str(Path.cwd()):
                # We're writing to a subdirectory (like src/), make path relative to repo root
                relative_project = self.project_dir.relative_to(Path.cwd())
                full_path = Path.cwd() / relative_project / file_path
            else:
                full_path = self.project_dir / file_path
                
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            # Show path relative to repo root for clarity
            display_path = full_path.relative_to(Path.cwd())
            print(f"📄 Written: {display_path} ({len(content)} chars)")
            return True
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return False

class GitHubManager:
    """Handles GitHub repository creation and management"""
    
    def __init__(self, github_token: Optional[str] = None):
        """Initialize GitHub manager with personal access token"""
        # Load .env file first
        load_env_file()
        
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.github = None
        
        if self.github_token:
            try:
                self.github = Github(self.github_token)
                # Test the connection
                user = self.github.get_user()
                print(f"✅ GitHub connection established for user: {user.login}")
            except GithubException as e:
                print(f"❌ GitHub authentication failed: {e}")
                self.github = None
        else:
            print("⚠️ No GitHub token provided. Set GITHUB_TOKEN environment variable for GitHub integration.")
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> Optional[str]:
        """Create a new GitHub repository"""
        if not self.github:
            print("❌ GitHub not authenticated. Cannot create repository.")
            return None
            
        try:
            user = self.github.get_user()
            
            # Check if repository already exists
            try:
                existing_repo = user.get_repo(repo_name)
                print(f"⚠️ Repository '{repo_name}' already exists: {existing_repo.html_url}")
                return existing_repo.clone_url
            except GithubException:
                # Repository doesn't exist, we can create it
                pass
            
            # Create the repository
            repo = user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=False,  # We'll push our own initial commit
                has_issues=True,
                has_wiki=True,
                has_projects=True
            )
            
            print(f"🎉 GitHub repository created: {repo.html_url}")
            return repo.clone_url
            
        except GithubException as e:
            print(f"❌ Failed to create GitHub repository: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error creating repository: {e}")
            return None
    
    def push_to_github(self, project_dir: Path, repo_url: str, branch: str = "main") -> bool:
        """Push local repository to GitHub"""
        try:
            os.chdir(project_dir)
            
            # Add GitHub as origin remote
            subprocess.run(["git", "remote", "add", "origin", repo_url], 
                         check=True, capture_output=True)
            
            # Push to GitHub
            subprocess.run(["git", "push", "-u", "origin", branch], 
                         check=True, capture_output=True)
            
            print(f"🚀 Successfully pushed to GitHub: {repo_url}")
            return True
            
        except subprocess.CalledProcessError as e:
            # Try to handle case where remote already exists
            try:
                subprocess.run(["git", "remote", "set-url", "origin", repo_url], 
                             check=True, capture_output=True)
                subprocess.run(["git", "push", "-u", "origin", branch], 
                             check=True, capture_output=True)
                print(f"🚀 Successfully pushed to GitHub (updated remote): {repo_url}")
                return True
            except subprocess.CalledProcessError as e2:
                print(f"❌ Failed to push to GitHub: {e2}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error pushing to GitHub: {e}")
            return False
    
    def setup_repository_features(self, repo_name: str, project_dir: Path) -> bool:
        """Set up additional repository features like README, issues templates, etc."""
        if not self.github:
            return False
            
        try:
            user = self.github.get_user()
            repo = user.get_repo(repo_name)
            
            # Create issue templates if they don't exist
            issue_templates_dir = project_dir / ".github" / "ISSUE_TEMPLATE"
            if not (issue_templates_dir / "bug_report.md").exists():
                bug_template = """---
name: Bug report
about: Create a report to help us improve
title: ''
labels: 'bug'
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Additional context**
Add any other context about the problem here.
"""
                (issue_templates_dir / "bug_report.md").write_text(bug_template, encoding='utf-8')
            
            # Create feature request template
            if not (issue_templates_dir / "feature_request.md").exists():
                feature_template = """---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: 'enhancement'
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
"""
                (issue_templates_dir / "feature_request.md").write_text(feature_template, encoding='utf-8')
            
            print(f"✅ Repository features set up for: {repo_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up repository features: {e}")
            return False

# This function is no longer needed - keeping for compatibility
def create_project_structure(project_dir: Path) -> GitManager:
    """Legacy function - now handled inline"""
    return GitManager(project_dir)

# =============================================================================
# TASK MANAGEMENT SYSTEM
# =============================================================================

class TaskManager:
    """Manages task assignment and tracking for the development team"""
    
    def __init__(self, git_manager: GitManager):
        self.git = git_manager
    
    def parse_github_issues(self, issues_md: str) -> List[GitHubIssue]:
        """Parse GitHub issues from markdown format into structured tasks"""
        tasks = []
        current_task = None
        task_id = 1
        
        lines = issues_md.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # New issue detection
            if line.startswith('Issue:') or (line.startswith('1.') and 'Issue:' in line):
                if current_task:
                    tasks.append(current_task)
                
                # Extract title
                title = line.split('Issue:')[-1].strip()
                if '(' in title and ')' in title:
                    priority = title.split('(')[-1].split(')')[0].strip()
                    title = title.split('(')[0].strip()
                else:
                    priority = 'Medium Priority'
                
                current_task = GitHubIssue(
                    id=task_id,
                    title=title,
                    description="",
                    labels=[],
                    priority=priority,
                    story_points=0,
                    acceptance_criteria=[],
                    assignee=None,
                    status='backlog'
                )
                task_id += 1
            
            elif current_task and line.startswith('**Labels:**'):
                labels_text = line.replace('**Labels:**', '').strip()
                current_task['labels'] = [label.strip() for label in labels_text.split(',')]
            
            elif current_task and line.startswith('**Estimate:**'):
                estimate_text = line.replace('**Estimate:**', '').strip()
                try:
                    points = int(estimate_text.split()[0])
                    # Enforce maximum 3 story points per task
                    if points > 3:
                        print(f"⚠️ Task '{current_task['title']}' has {points} points - capping at 3 points max")
                        points = 3
                    current_task['story_points'] = points
                except:
                    current_task['story_points'] = 3
            
            elif current_task and line.startswith('**Description:**'):
                current_task['description'] = line.replace('**Description:**', '').strip()
            
            elif current_task and line.startswith('- [ ]'):
                criteria = line.replace('- [ ]', '').strip()
                current_task['acceptance_criteria'].append(criteria)
        
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def get_available_tasks_for_agent(self, agent_type: str, tasks: List[GitHubIssue]) -> List[GitHubIssue]:
        """Get tasks that are available for a specific agent type"""
        agent_labels = {
            'backend': ['backend', 'api', 'database'],
            'frontend': ['frontend', 'ui', 'ux'],
            'documentation': ['documentation', 'docs'],
            'testing': ['testing', 'qa']
        }
        
        relevant_labels = agent_labels.get(agent_type, [])
        available_tasks = []
        
        for task in tasks:
            if task['status'] == 'backlog':
                # Check if task is relevant for this agent
                task_labels = [label.lower() for label in task['labels']]
                if any(label in task_labels for label in relevant_labels):
                    available_tasks.append(task)
        
        # Sort by priority and story points
        priority_order = {'High Priority': 1, 'Medium Priority': 2, 'Low Priority': 3}
        available_tasks.sort(key=lambda x: (priority_order.get(x['priority'], 2), x['story_points']))
        
        return available_tasks
    
    def assign_task(self, task: GitHubIssue, agent_name: str) -> GitHubIssue:
        """Assign a task to an agent"""
        task['assignee'] = agent_name
        task['status'] = 'in_progress'
        return task
    
    def complete_task(self, task: GitHubIssue) -> GitHubIssue:
        """Mark a task as completed"""
        task['status'] = 'completed'
        return task
    
    def save_task_progress(self, state: DevelopmentState):
        """Save current task progress to file"""
        progress_data = {
            'total_tasks': len(state.get('tasks', [])),
            'completed_tasks': len(state.get('completed_tasks', [])),
            'current_task': state.get('current_task'),
            'task_breakdown': {
                'backend': len([t for t in state.get('tasks', []) if 'backend' in [l.lower() for l in t['labels']]]),
                'frontend': len([t for t in state.get('tasks', []) if 'frontend' in [l.lower() for l in t['labels']]]),
                'documentation': len([t for t in state.get('tasks', []) if 'documentation' in [l.lower() for l in t['labels']]]),
                'testing': len([t for t in state.get('tasks', []) if 'testing' in [l.lower() for l in t['labels']]])
            }
        }
        
        import json
        self.git.write_file("docs/project_management/task_progress.json", json.dumps(progress_data, indent=2))

# =============================================================================
# ARCHITECTURE AGENT
# =============================================================================

class ArchitectAgent:
    """Technical Architecture and Technology Stack Decision Agent"""
    
    def __init__(self, llm, git_manager, qa_manager):
        self.llm = llm
        self.git = git_manager
        self.qa_manager = qa_manager
        self.prompt = ChatPromptTemplate.from_template("""
        You are a Senior Software Architect with 15+ years of experience designing scalable systems.
        
        Project Brief: {project_brief}
        Requirements: {requirements}
        
        Analyze the requirements and make informed decisions about:
        
        1. **Backend Technology Stack:**
           - Programming language (Python, Node.js, Java, Go, etc.)
           - Web framework (FastAPI, Express, Spring Boot, etc.)
           - Database choice (PostgreSQL, MongoDB, SQLite, etc.)
           - Authentication method
           - API design pattern (REST, GraphQL, etc.)
        
        2. **Frontend Technology Stack:**
           - Framework/Library (React, Vue, Angular, or vanilla JS)
           - CSS framework (Tailwind, Bootstrap, Material-UI, etc.)
           - Build tools and bundlers
           - State management approach
        
        3. **Infrastructure & DevOps:**
           - Deployment strategy
           - Database hosting
           - Environment management
           - Testing frameworks
        
        4. **Architecture Patterns:**
           - Overall architecture (Monolith, Microservices, etc.)
           - Code organization pattern (MVC, Hexagonal, Clean Architecture, etc.)
           - Data flow and API design
        
        Provide specific technology choices with clear reasoning. Consider:
        - Project complexity and scale
        - Development team size and expertise
        - Performance requirements
        - Deployment constraints
        - Maintenance and evolution needs
        
        Format your response as a structured technical specification with clear sections for each technology choice.
        """)
    
    def design_architecture(self, state: DevelopmentState) -> DevelopmentState:
        # Check if architecture already exists
        arch_path = self.git.project_dir / "docs" / "architecture" / "tech_stack.md"
        if arch_path.exists():
            print("🏗️ Architect: Architecture specification already exists, skipping...")
            # Read existing architecture
            architecture = self.git.get_file_content("docs/architecture/tech_stack.md")
            state["architecture"] = architecture
            return state
        
        print("🏗️ Architect: Designing technical architecture and selecting tech stack...")
        
        # Get requirements from Product Manager
        requirements = state.get("requirements", "") or self.git.get_file_content("docs/prd/requirements.md")
        
        # Generate architecture specification
        chain = self.prompt | self.llm | StrOutputParser()
        architecture = chain.invoke({
            "project_brief": state["project_brief"],
            "requirements": requirements
        })
        
        # Write architecture documents
        self.git.write_file("docs/architecture/tech_stack.md", architecture)
        
        # Create detailed technology decision records
        self._create_technology_decision_records(architecture)
        
        # Create development guidelines
        self._create_development_guidelines(architecture)
        
        # Self-review the architecture
        print("🔍 Architect: Conducting self-review...")
        self_review = self.qa_manager.conduct_self_review(
            "Architect",
            architecture,
            "Technical Architecture and Technology Decisions", 
            state["project_brief"]
        )
        
        # Store review results
        if "agent_reviews" not in state:
            state["agent_reviews"] = {}
        state["agent_reviews"]["Architect"] = {
            "self_review": self_review,
            "peer_reviews": [],
            "issues": self_review["issues"],
            "revisions": []
        }
        
        # Check if revision is needed
        if not self_review["gate_passed"]:
            print("⚠️ Architect: Self-review identified issues, creating revision...")
            revised_architecture = self._revise_architecture(architecture, self_review["issues"], requirements)
            
            # Write revised architecture
            self.git.write_file("docs/architecture/tech_stack.md", revised_architecture)
            self._create_technology_decision_records(revised_architecture)
            self._create_development_guidelines(revised_architecture)
            
            architecture = revised_architecture
        
        # Commit architecture
        self.git.commit_changes("docs: Add technical architecture and tech stack specification", "Architect")
        
        # Store in state for other agents
        state["architecture"] = architecture
        
        return state
    
    def enhance_tasks_with_technical_details(self, state: DevelopmentState) -> DevelopmentState:
        """Review and enhance tasks with technical implementation details"""
        tasks = state.get('tasks', [])
        architecture = state.get('architecture', '') or self.git.get_file_content("docs/architecture/tech_stack.md")
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        
        if not tasks:
            print("🏗️ Architect: No tasks to enhance")
            return state
        
        print(f"🏗️ Architect: Enhancing {len(tasks)} tasks with technical details...")
        
        enhanced_tasks = []
        
        for task in tasks:
            print(f"   • Enhancing Task #{task['id']}: {task['title']}")
            
            enhancement_prompt = ChatPromptTemplate.from_template("""
            You are a Senior Software Architect reviewing a development task for technical completeness.
            
            ORIGINAL TASK:
            Title: {task_title}
            Description: {task_description}
            Labels: {task_labels}
            Acceptance Criteria: {acceptance_criteria}
            
            PROJECT CONTEXT:
            Architecture: {architecture}
            Requirements: {requirements}
            
            Your job is to enhance this task with precise technical implementation details so a developer can implement it without any ambiguity.
            
            Add technical specifications including:
            1. **Exact file paths** where code should be written
            2. **Specific technology stack** components to use (from architecture)
            3. **API signatures** and data structures
            4. **Database schema** details if applicable
            5. **Import statements** and dependencies needed
            6. **Error handling** requirements
            7. **Testing requirements** specific to this task
            8. **Integration points** with other components
            
            Enhanced Description Format:
            ## Technical Implementation
            
            ### File Structure
            - Create/modify: `exact/file/path.py`
            - Dependencies: list specific imports needed
            
            ### Implementation Details
            - Use the framework specified in the architecture
            - Follow the architectural patterns from the tech stack
            - Implement specific classes and interfaces as needed
            - Include exact method signatures and return types
            
            ### API Specification (if applicable)
            ```
            Exact endpoint definitions, request/response formats
            ```
            
            ### Database Changes (if applicable)
            ```sql
            Exact SQL or schema definitions
            ```
            
            ### Testing Requirements
            - Unit tests for specific functions
            - Integration tests for specific flows
            - Test file locations and naming conventions
            
            ### Acceptance Criteria (Enhanced)
            Make the original acceptance criteria more specific and technical with exact implementation details.
            
            Provide a completely unambiguous technical specification that a developer can follow step-by-step.
            """)
            
            chain = enhancement_prompt | self.llm | StrOutputParser()
            enhanced_description = chain.invoke({
                "task_title": task['title'],
                "task_description": task['description'],
                "task_labels": ', '.join(task['labels']),
                "acceptance_criteria": '\n'.join([f"- {criteria}" for criteria in task['acceptance_criteria']]),
                "architecture": architecture[:1500],  # Truncate for context
                "requirements": requirements[:1000]
            })
            
            # Create enhanced task
            enhanced_task = task.copy()
            enhanced_task['description'] = enhanced_description
            enhanced_task['technical_enhanced'] = True
            
            enhanced_tasks.append(enhanced_task)
        
        # Update state with enhanced tasks
        state['tasks'] = enhanced_tasks
        
        # Save enhanced tasks to file
        enhanced_tasks_content = "# Enhanced Technical Tasks\n\n"
        for task in enhanced_tasks:
            enhanced_tasks_content += f"## Task #{task['id']}: {task['title']}\n"
            enhanced_tasks_content += f"**Labels:** {', '.join(task['labels'])}\n"
            enhanced_tasks_content += f"**Story Points:** {task['story_points']}\n"
            enhanced_tasks_content += f"**Priority:** {task['priority']}\n\n"
            enhanced_tasks_content += task['description'] + "\n\n"
            enhanced_tasks_content += "---\n\n"
        
        self.git.write_file("docs/architecture/enhanced_tasks.md", enhanced_tasks_content)
        
        # Commit enhanced tasks
        self.git.commit_changes("docs: Add technical details to development tasks", "Architect")
        
        print(f"✅ Architect: Enhanced {len(enhanced_tasks)} tasks with technical specifications")
        return state
    
    def _create_technology_decision_records(self, architecture: str):
        """Create ADR (Architecture Decision Records)"""
        adr_content = f"""# Architecture Decision Records (ADR)

## ADR-001: Technology Stack Selection

### Status
Accepted

### Context
{architecture[:500]}...

### Decision
Based on the project requirements and constraints, we have selected the technology stack as outlined in the architecture specification.

### Consequences
- **Positive**: Clear technology direction for development team
- **Positive**: Consistent tooling and patterns across the project  
- **Negative**: Learning curve for team members unfamiliar with chosen technologies
- **Risk**: Technology choices may need revision as requirements evolve

### Compliance
All development agents must follow the technology choices specified in this ADR.
"""
        self.git.write_file("docs/architecture/adr-001-tech-stack.md", adr_content)
    
    def _create_development_guidelines(self, architecture: str):
        """Create development guidelines based on architecture"""
        guidelines_content = f"""# Development Guidelines

## Technology Stack Compliance

All development work must adhere to the architecture specification in `tech_stack.md`.

## Code Organization

Follow the architectural patterns specified in the tech stack document.

## API Design

RESTful API design following OpenAPI 3.0 specification.

## Database Design

Follow the database technology and patterns specified in the architecture.

## Testing Strategy

Implement comprehensive testing following the testing framework choices in the architecture.

## Deployment

Follow the deployment strategy outlined in the architecture specification.
"""
        self.git.write_file("docs/architecture/development_guidelines.md", guidelines_content)
    
    def _revise_architecture(self, original_architecture: str, issues: List[str], requirements: str) -> str:
        """Revise architecture based on self-review issues"""
        revision_prompt = ChatPromptTemplate.from_template("""
        You need to revise this technical architecture based on identified issues:
        
        Original Architecture:
        {original_architecture}
        
        Requirements:
        {requirements}
        
        Issues to Address:
        {issues}
        
        Provide a revised architecture specification that addresses all the issues while maintaining technical coherence.
        """)
        
        chain = revision_prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "original_architecture": original_architecture,
            "requirements": requirements,
            "issues": "\n".join([f"- {issue}" for issue in issues])
        })

# =============================================================================
# QUALITY ASSURANCE SYSTEM
# =============================================================================

class QualityAssuranceManager:
    """Manages quality gates, peer reviews, and iterative improvements"""
    
    def __init__(self, git_manager: GitManager):
        self.git = git_manager
        self.llm = general_llm
    
    def conduct_self_review(self, agent_name: str, work_output: str, work_type: str, requirements: str = "") -> Dict[str, Any]:
        """Agent reviews their own work for quality and compliance"""
        
        self_review_prompt = ChatPromptTemplate.from_template("""
        You are conducting a thorough self-review of your work as a {agent_name}.
        
        Your Work Output:
        {work_output}
        
        Work Type: {work_type}
        Requirements Context: {requirements}
        
        Conduct a comprehensive self-review covering:
        
        1. **Code Quality Assessment**:
           - SOLID principles compliance
           - Clean code practices (naming, functions, structure)
           - Error handling and edge cases
           - Performance considerations
        
        2. **Architecture Compliance**:
           - Hexagonal Architecture implementation
           - Domain Driven Design principles
           - Proper separation of concerns
           - Dependency injection usage
        
        3. **Requirements Traceability**:
           - Does the code implement the requirements?
           - Are all acceptance criteria met?
           - Any missing functionality?
        
        4. **Technical Issues**:
           - Syntax errors or bugs
           - Security vulnerabilities
           - Integration problems
           - Testability issues
        
        5. **Best Practices**:
           - TDD compliance
           - Documentation quality
           - Code maintainability
        
        Format your response as:
        ## Self-Review Results
        
        ### Overall Quality Score: [1-10]
        
        ### ✅ Strengths Found:
        - [List specific strengths]
        
        ### ⚠️ Issues Identified:
        - [List specific issues with severity: LOW/MEDIUM/HIGH/CRITICAL]
        
        ### 🔧 Recommended Improvements:
        - [Specific actionable improvements]
        
        ### 📋 Architecture Compliance: [PASS/FAIL]
        [Explanation]
        
        ### ✅ Requirements Coverage: [PASS/FAIL] 
        [Explanation]
        
        ### 🚦 Quality Gate Status: [PASS/FAIL]
        [Overall assessment - FAIL if any CRITICAL issues or major problems]
        """)
        
        chain = self_review_prompt | self.llm | StrOutputParser()
        review_result = chain.invoke({
            "agent_name": agent_name,
            "work_output": work_output,
            "work_type": work_type,
            "requirements": requirements
        })
        
        # Parse the review to extract key information
        quality_score = self._extract_quality_score(review_result)
        issues = self._extract_issues(review_result)
        gate_status = "PASS" in review_result and "Quality Gate Status: PASS" in review_result
        
        return {
            "review_text": review_result,
            "quality_score": quality_score,
            "issues": issues,
            "gate_passed": gate_status,
            "timestamp": time.time()
        }
    
    def conduct_peer_review(self, reviewer_agent: str, reviewee_agent: str, work_output: str, work_type: str, context: Dict[str, str]) -> Dict[str, Any]:
        """One agent reviews another agent's work"""
        
        peer_review_prompt = ChatPromptTemplate.from_template("""
        You are a {reviewer_agent} conducting a peer review of work by the {reviewee_agent}.
        
        Work Being Reviewed ({work_type}):
        {work_output}
        
        Project Context:
        Requirements: {requirements}
        Frontend Summary: {frontend_summary}
        Backend Summary: {backend_summary}
        
        As a {reviewer_agent}, focus on areas within your expertise:
        
        **If you're the Product Manager reviewing:**
        - Requirements compliance
        - Business logic correctness
        - User story implementation
        - Acceptance criteria fulfillment
        
        **If you're the UI Developer reviewing Backend:**
        - API design and usability
        - Frontend integration compatibility  
        - Data formats and endpoints
        - Error responses
        
        **If you're the Backend Developer reviewing Frontend:**
        - API integration correctness
        - Data handling and validation
        - Security considerations
        - Performance implications
        
        **If you're the QA Tester reviewing:**
        - Testability and test coverage
        - Edge cases and error handling
        - Security vulnerabilities
        - Performance bottlenecks
        
        **If you're the Documentation Agent reviewing:**
        - Code clarity and maintainability
        - Documentation completeness
        - API documentation accuracy
        
        Format your response as:
        ## Peer Review by {reviewer_agent}
        
        ### 🎯 Review Focus Areas:
        [Areas you focused on based on your role]
        
        ### ✅ Positive Observations:
        - [Specific things done well]
        
        ### ⚠️ Issues Found:
        - [Issue description] - Severity: [LOW/MEDIUM/HIGH/CRITICAL]
        
        ### 🔄 Integration Concerns:
        - [How this work integrates with other components]
        
        ### 📝 Recommendations:
        - [Specific actionable recommendations]
        
        ### 🚦 Peer Review Status: [APPROVE/REQUEST_CHANGES/NEEDS_DISCUSSION]
        [Reasoning for the status]
        """)
        
        chain = peer_review_prompt | self.llm | StrOutputParser()
        peer_review = chain.invoke({
            "reviewer_agent": reviewer_agent,
            "reviewee_agent": reviewee_agent,
            "work_output": work_output,
            "work_type": work_type,
            "requirements": context.get("requirements", ""),
            "frontend_summary": context.get("frontend_summary", ""),
            "backend_summary": context.get("backend_summary", "")
        })
        
        # Parse peer review status
        issues = self._extract_issues(peer_review)
        status = "APPROVE"
        if "REQUEST_CHANGES" in peer_review:
            status = "REQUEST_CHANGES"
        elif "NEEDS_DISCUSSION" in peer_review:
            status = "NEEDS_DISCUSSION"
        
        return {
            "reviewer": reviewer_agent,
            "review_text": peer_review,
            "status": status,
            "issues": issues,
            "timestamp": time.time()
        }
    
    def generate_revision_request(self, from_agent: str, to_agent: str, issues: List[str]) -> Dict[str, str]:
        """Generate a structured revision request"""
        
        critical_issues = [issue for issue in issues if "CRITICAL" in issue]
        high_issues = [issue for issue in issues if "HIGH" in issue]
        
        severity = "CRITICAL" if critical_issues else "HIGH" if high_issues else "MEDIUM"
        
        revision_prompt = ChatPromptTemplate.from_template("""
        As the {from_agent}, create a clear revision request for the {to_agent}.
        
        Issues Found:
        {issues_list}
        
        Create a constructive revision request that:
        1. Clearly explains what needs to be fixed
        2. Provides specific examples
        3. Suggests solutions or approaches
        4. Maintains a collaborative tone
        
        Format as:
        ## Revision Request: {from_agent} → {to_agent}
        
        ### Priority: {severity}
        
        ### Issues to Address:
        [Numbered list of specific issues]
        
        ### Recommended Actions:
        [Specific steps to take]
        
        ### Success Criteria:
        [How to know when issues are resolved]
        """)
        
        chain = revision_prompt | self.llm | StrOutputParser()
        request = chain.invoke({
            "from_agent": from_agent,
            "to_agent": to_agent,
            "issues_list": "\n".join(issues),
            "severity": severity
        })
        
        return {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "request_text": request,
            "severity": severity,
            "issues": issues,
            "timestamp": time.time()
        }
    
    def _extract_quality_score(self, review_text: str) -> int:
        """Extract quality score from review text"""
        import re
        match = re.search(r'Quality Score:\s*(\d+)', review_text)
        return int(match.group(1)) if match else 5
    
    def _extract_issues(self, review_text: str) -> List[str]:
        """Extract issues from review text"""
        issues = []
        lines = review_text.split('\n')
        in_issues_section = False
        
        for line in lines:
            if "Issues" in line and ("⚠️" in line or "Found:" in line):
                in_issues_section = True
                continue
            elif line.startswith('###') and in_issues_section:
                in_issues_section = False
            elif in_issues_section and line.strip().startswith('-'):
                issues.append(line.strip())
        
        return issues

# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

class ProductManagerAgent:
    """Defines requirements, user stories, and product specifications"""
    
    def __init__(self, git_manager: GitManager):
        self.llm = general_llm  # Use Mistral for requirements analysis
        self.git = git_manager
        self.qa_manager = QualityAssuranceManager(git_manager)
        self.prompt = ChatPromptTemplate.from_template("""
        You are a Product Manager for an agile software development team.
        
        Project Brief: {project_brief}
        
        Your task is to:
        1. Analyze the project brief
        2. Define clear functional requirements using Domain Driven Design principles
        3. Create user stories in the format "As a [user], I want [goal] so that [benefit]"
        4. Specify acceptance criteria
        5. Identify key features and prioritize them
        6. Define domain boundaries and bounded contexts
        7. Identify domain entities, value objects, and aggregates
        
        Follow these architectural guidelines:
        - Apply Domain Driven Design (DDD) to identify core domains
        - Define clear bounded contexts and domain models
        - Identify ubiquitous language for the domain
        - Structure requirements to support Hexagonal Architecture
        
        Provide a comprehensive requirements document that the development team can use.
        
        Format your response as:
        ## Requirements Document
        
        ### Project Overview
        [Brief overview]
        
        ### User Stories
        [List of user stories]
        
        ### Functional Requirements
        [Detailed requirements]
        
        ### Acceptance Criteria
        [Clear criteria for completion]
        
        ### Priority Features
        [Ranked list of features]
        
        ### Domain Model (DDD)
        [Domain entities, value objects, aggregates, and bounded contexts]
        
        ### Architecture Guidelines
        [Hexagonal Architecture structure and domain boundaries]
        """)
        
    def analyze_project(self, state: DevelopmentState) -> DevelopmentState:
        # Check if PRD already exists
        prd_path = self.git.project_dir / "docs" / "prd" / "requirements.md"
        if prd_path.exists():
            print("📋 Product Manager: PRD already exists, skipping requirements generation...")
            # Read existing requirements
            requirements = self.git.get_file_content("docs/prd/requirements.md")
            state["requirements"] = requirements
            return state
        
        # Work directly on main branch
        print("📋 Product Manager: Generating PRD...")
        
        # Generate requirements
        chain = self.prompt | self.llm | StrOutputParser()
        requirements = chain.invoke({"project_brief": state["project_brief"]})
        
        # Write requirements to files
        self.git.write_file("docs/prd/requirements.md", requirements)
        
        # Create GitHub Issues template
        issues_template = self._create_issues_from_requirements(requirements)
        self.git.write_file("docs/prd/github_issues.md", issues_template)
        
        # Create project roadmap
        roadmap = self._create_project_roadmap(requirements)
        self.git.write_file("docs/prd/roadmap.md", roadmap)
        
        # Self-review the requirements
        print("🔍 Product Manager: Conducting self-review...")
        self_review = self.qa_manager.conduct_self_review(
            "Product Manager", 
            requirements, 
            "Requirements and Product Planning",
            state["project_brief"]
        )
        
        # Store review results
        if "agent_reviews" not in state:
            state["agent_reviews"] = {}
        state["agent_reviews"]["Product Manager"] = {
            "self_review": self_review,
            "peer_reviews": [],
            "issues": self_review["issues"],
            "revisions": []
        }
        
        # Check if revision is needed
        if not self_review["gate_passed"]:
            print("⚠️ Product Manager: Self-review identified issues, creating revision...")
            revised_requirements = self._revise_requirements(requirements, self_review["issues"])
            
            # Write revised requirements
            self.git.write_file("docs/prd/requirements.md", revised_requirements)
            self.git.write_file("docs/prd/github_issues.md", self._create_issues_from_requirements(revised_requirements))
            self.git.write_file("docs/prd/roadmap.md", self._create_project_roadmap(revised_requirements))
            
            requirements = revised_requirements
            state["agent_reviews"]["Product Manager"]["revisions"].append({
                "reason": "Self-review quality gate failed",
                "timestamp": time.time()
            })
        
        # Write self-review to git
        self.git.write_file("docs/reviews/product_manager_self_review.md", self_review["review_text"])
        
        # Parse GitHub issues into structured tasks
        task_manager = TaskManager(self.git)
        issues_content = self.git.get_file_content("docs/prd/github_issues.md")
        tasks = task_manager.parse_github_issues(issues_content)
        
        # Initialize task tracking in state
        state["tasks"] = tasks
        state["completed_tasks"] = []
        state["current_task"] = None
        state["available_agents"] = ["backend", "frontend", "documentation", "testing"]
        
        # Save task progress
        task_manager.save_task_progress(state)
        
        # Validate task sizes
        oversized_tasks = [t for t in tasks if t['story_points'] > 3]
        if oversized_tasks:
            print(f"⚠️ Product Manager: Found {len(oversized_tasks)} oversized tasks (>3 points)")
        
        # Show task statistics
        point_distribution = {}
        for task in tasks:
            points = task['story_points']
            point_distribution[points] = point_distribution.get(points, 0) + 1
        
        print(f"📋 Product Manager: Created {len(tasks)} tasks")
        print(f"   📊 Task distribution: {dict(sorted(point_distribution.items()))}")
        
        # Show first few tasks as examples
        for task in tasks[:3]:  # Show first 3 tasks
            print(f"   • Task #{task['id']}: {task['title']} ({task['priority']}, {task['story_points']} pts)")
        
        # Commit the requirements
        commit_msg = "feat: Add product requirements and roadmap"
        if state["agent_reviews"]["Product Manager"]["revisions"]:
            commit_msg += " (revised after self-review)"
        
        self.git.commit_changes(commit_msg, "Product Manager")
        
        state["requirements"] = requirements
        state["feedback"].append("✓ Product Manager: Requirements defined, self-reviewed, and committed")
        state["git_commits"].append("Requirements and roadmap committed with self-review")
        state["quality_gates_passed"] = {"Product Manager": self_review["gate_passed"]}
        
        print(f"🎯 Product Manager: Requirements completed (Quality Score: {self_review['quality_score']}/10)")
        return state
    
    def _create_issues_from_requirements(self, requirements: str) -> str:
        """Extract actionable tasks from requirements and format as GitHub issues"""
        issue_prompt = ChatPromptTemplate.from_template("""
        Based on these requirements, create small, focused GitHub issues for development tasks:
        
        {requirements}
        
        CRITICAL CONSTRAINTS:
        - Each task must be 2-3 story points maximum (no larger tasks!)
        - Break down complex features into multiple small tasks
        - Each task should be completable in 1-2 hours
        - Tasks should be very specific and actionable
        - Avoid ambiguous or overly broad tasks
        
        Create granular, focused issues such as:
        ✅ Good: "Create User model with validation" (2 pts)
        ✅ Good: "Add POST /api/users endpoint" (2 pts) 
        ✅ Good: "Implement login form component" (3 pts)
        ❌ Bad: "User management system" (8 pts - too big!)
        ❌ Bad: "Complete frontend" (15 pts - way too big!)
        
        Break down into categories:
        1. **Database/Models** - Individual model classes, schemas, migrations
        2. **API Endpoints** - Single endpoints with specific HTTP methods
        3. **Frontend Components** - Individual UI components or forms
        4. **Authentication** - Specific auth features (login, logout, validation)
        5. **Business Logic** - Individual service methods or utilities
        6. **Testing** - Test suites for specific components
        7. **Documentation** - Specific documentation sections
        
        Format each issue as:
        ## Issue: [Very Specific Title]
        **Labels:** feature, [domain]
        **Estimate:** [1-3] story points
        **Description:** [Detailed, specific description]
        **Acceptance Criteria:**
        - [ ] Criterion 1
        - [ ] Criterion 2
        """)
        
        chain = issue_prompt | self.llm | StrOutputParser()
        return chain.invoke({"requirements": requirements})
    
    def _create_project_roadmap(self, requirements: str) -> str:
        """Create a project roadmap based on requirements"""
        roadmap_prompt = ChatPromptTemplate.from_template("""
        Create a development roadmap based on these requirements:
        
        {requirements}
        
        Structure as:
        # Project Roadmap
        
        ## Phase 1: Foundation (Week 1-2)
        - [ ] Task 1
        - [ ] Task 2
        
        ## Phase 2: Core Features (Week 3-4)
        - [ ] Task 1
        - [ ] Task 2
        
        ## Phase 3: Enhancement (Week 5-6)
        - [ ] Task 1
        - [ ] Task 2
        
        Include dependencies, milestones, and delivery dates.
        """)
        
        chain = roadmap_prompt | self.llm | StrOutputParser()
        return chain.invoke({"requirements": requirements})
    
    def _revise_requirements(self, original_requirements: str, issues: List[str]) -> str:
        """Revise requirements based on self-review issues"""
        revision_prompt = ChatPromptTemplate.from_template("""
        You need to revise these product requirements based on identified issues:
        
        Original Requirements:
        {original_requirements}
        
        Issues to Address:
        {issues}
        
        Create improved requirements that:
        1. Address all identified issues
        2. Maintain the original project goals
        3. Add missing details or clarity
        4. Improve structure and completeness
        5. Ensure better Domain Driven Design alignment
        
        Provide the complete revised requirements document.
        """)
        
        chain = revision_prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "original_requirements": original_requirements,
            "issues": "\n".join(issues)
        })

class UICoderAgent:
    """Creates frontend code, UI components, and user interfaces"""
    
    def __init__(self, git_manager: GitManager):
        self.llm = code_llm  # Use CodeLlama for frontend coding
        self.git = git_manager
        self.qa_manager = QualityAssuranceManager(git_manager)
        self.prompt = ChatPromptTemplate.from_template("""
        You are a Frontend/UI Developer specializing in modern web development.
        
        Project Requirements: {requirements}
        Technical Architecture: {architecture}
        Backend API Info: {backend_api_info}
        Existing Frontend Files: {existing_frontend_files}
        
        CRITICAL: You MUST follow the frontend technology stack specified in the architecture document.
        Use ONLY the framework, CSS framework, and tools specified by the Architect.
        
        Your task is to:
        1. Implement frontend using the EXACT technology stack from the architecture
        2. Use the specified frontend framework (React, Vue, Angular, or vanilla JS)
        3. Use the specified CSS framework (Tailwind, Bootstrap, Material-UI, etc.)
        4. Follow the specified build tools and bundlers
        5. Implement state management using the specified approach
        6. Follow the architectural patterns specified for frontend
        7. Integrate with backend APIs using the patterns specified in architecture
        
        Architecture Compliance Requirements:
        - Use the exact frontend framework specified (React/Vue/Angular/Vanilla)
        - Use the exact CSS framework specified
        - Use the specified build tools and bundlers
        - Follow the state management approach specified
        - Implement the architectural patterns specified
        - Follow the code organization patterns specified
        
        Create frontend code that strictly adheres to the architectural decisions.
        
        Create clean, production-ready frontend code.
        
        Format your response as:
        ## Frontend Implementation
        
        ### HTML Structure
        ```html
        [Complete HTML code]
        ```
        
        ### CSS Styling
        ```css
        [Complete CSS code with responsive design]
        ```
        
        ### JavaScript Logic
        ```javascript
        [Complete JavaScript for functionality]
        ```
        
        ### UI/UX Notes
        [Design decisions and user experience considerations]
        """)
        
    def create_ui(self, state: DevelopmentState) -> DevelopmentState:
        """Work on frontend tasks from the backlog"""
        task_manager = TaskManager(self.git)
        
        # Get available frontend tasks
        available_tasks = task_manager.get_available_tasks_for_agent('frontend', state.get('tasks', []))
        
        if not available_tasks:
            print("🎨 UI Developer: No frontend tasks available in backlog")
            return state
        
        # Pick up the highest priority task
        current_task = available_tasks[0]
        current_task = task_manager.assign_task(current_task, "UI Developer")
        state["current_task"] = current_task
        
        print(f"🎨 UI Developer: Picking up task #{current_task['id']}: {current_task['title']}")
        print(f"   Priority: {current_task['priority']}, Story Points: {current_task['story_points']}")
        
        # Read project context
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        architecture = state.get("architecture", "") or self.git.get_file_content("docs/architecture/tech_stack.md")
        
        # Create task-specific prompt
        task_chain = ChatPromptTemplate.from_template("""
        You are a Frontend/UI Developer working on a specific task.
        
        CURRENT TASK: {task_title}
        TASK DESCRIPTION: {task_description}
        ACCEPTANCE CRITERIA:
        {acceptance_criteria}
        
        Project Requirements: {requirements}
        Technical Architecture: {architecture}
        
        CRITICAL: You MUST follow the frontend technology stack specified in the architecture document.
        
        Focus ONLY on this specific task. Implement the minimal code needed to satisfy the acceptance criteria.
        Do not implement features outside this task scope.
        
        Generate code that:
        1. Addresses the specific task requirements
        2. Meets all acceptance criteria
        3. Follows the architecture specification
        4. Is production-ready and responsive
        5. Includes proper error handling and user feedback
        
        Provide implementation details for this specific task only.
        """) | self.llm | StrOutputParser()
        
        # Generate code for this specific task
        task_implementation = task_chain.invoke({
            "task_title": current_task['title'],
            "task_description": current_task['description'],
            "acceptance_criteria": '\n'.join([f"- {criteria}" for criteria in current_task['acceptance_criteria']]),
            "requirements": requirements,
            "architecture": architecture
        })
        
        # Write frontend files for this task
        self._write_frontend_files_for_task(task_implementation, current_task)
        
        # Mark task as completed
        task_manager.complete_task(current_task)
        state["completed_tasks"] = state.get("completed_tasks", []) + [current_task]
        
        # Update task list
        updated_tasks = []
        for task in state.get("tasks", []):
            if task['id'] != current_task['id']:
                updated_tasks.append(task)
            else:
                updated_tasks.append(current_task)
        state["tasks"] = updated_tasks
        
        # Commit this specific task
        commit_msg = f"feat: Implement {current_task['title']} (#{current_task['id']})"
        self.git.commit_changes(commit_msg, "UI Developer")
        
        # Save progress
        task_manager.save_task_progress(state)
        
        print(f"✅ UI Developer: Completed task #{current_task['id']}")
        state["feedback"].append(f"✓ UI Developer: Task #{current_task['id']} completed and committed")
        
        # Clear current task
        state["current_task"] = None
        
        # Create package.json
        self._create_package_json()
        
        # Self-review the frontend code
        print("🔍 UI Developer: Conducting self-review...")
        self_review = self.qa_manager.conduct_self_review(
            "UI Developer",
            ui_code,
            "Frontend Implementation", 
            requirements
        )
        
        # Initialize or update agent reviews
        if "agent_reviews" not in state:
            state["agent_reviews"] = {}
        state["agent_reviews"]["UI Developer"] = {
            "self_review": self_review,
            "peer_reviews": [],
            "issues": self_review["issues"],
            "revisions": []
        }
        
        # Check for revision needs
        revised_code = ui_code
        if not self_review["gate_passed"]:
            print("⚠️ UI Developer: Self-review found issues, revising...")
            revised_code = self._revise_frontend_code(ui_code, self_review["issues"], requirements)
            self._write_frontend_files(revised_code)
            state["agent_reviews"]["UI Developer"]["revisions"].append({
                "reason": "Self-review quality gate failed",
                "timestamp": time.time()
            })
        
        # Conduct peer review from Product Manager perspective
        print("👥 Conducting peer review from Product Manager...")
        pm_review = self.qa_manager.conduct_peer_review(
            "Product Manager",
            "UI Developer", 
            revised_code,
            "Frontend Implementation",
            {
                "requirements": requirements,
                "backend_summary": backend_api_info,
                "frontend_summary": existing_files
            }
        )
        
        state["agent_reviews"]["UI Developer"]["peer_reviews"].append(pm_review)
        
        # Handle peer review feedback
        if pm_review["status"] == "REQUEST_CHANGES":
            print("🔄 UI Developer: Addressing peer review feedback...")
            final_code = self._address_peer_feedback(revised_code, pm_review["issues"], requirements)
            self._write_frontend_files(final_code)
            revised_code = final_code
            
            state["agent_reviews"]["UI Developer"]["revisions"].append({
                "reason": "Product Manager peer review feedback",
                "timestamp": time.time()
            })
        
        # Write review documentation
        self.git.write_file("docs/reviews/ui_developer_self_review.md", self_review["review_text"])
        self.git.write_file("docs/reviews/ui_developer_peer_review_pm.md", pm_review["review_text"])
        
        # Commit the frontend code
        commit_msg = "feat: Implement frontend components and styling"
        if state["agent_reviews"]["UI Developer"]["revisions"]:
            commit_msg += " (revised after reviews)"
            
        self.git.commit_changes(commit_msg, "UI Developer")
        
        # Update quality gates
        if "quality_gates_passed" not in state:
            state["quality_gates_passed"] = {}
        state["quality_gates_passed"]["UI Developer"] = self_review["gate_passed"] and pm_review["status"] == "APPROVE"
        
        state["ui_code"] = revised_code
        state["feedback"].append(f"✓ UI Developer: Frontend code created, reviewed (Score: {self_review['quality_score']}/10), and committed")
        state["git_commits"].append("Frontend implementation with peer review committed")
        print(f"🎨 UI Developer: Frontend completed (Quality: {self_review['quality_score']}/10, Peer Review: {pm_review['status']})")
        return state
    
    def _get_existing_frontend_files(self) -> str:
        """Get summary of existing frontend files"""
        frontend_files = []
        frontend_dir = Path(self.git.project_dir) / "frontend"
        
        if frontend_dir.exists():
            for file_path in frontend_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in [".html", ".css", ".js", ".json"]:
                    rel_path = file_path.relative_to(self.git.project_dir)
                    content = self.git.get_file_content(str(rel_path))
                    frontend_files.append(f"{rel_path}: {len(content)} characters")
        
        return "\n".join(frontend_files) if frontend_files else "No existing frontend files"
    
    def _write_frontend_files(self, ui_code: str):
        """Generate individual frontend files using CodeLlama"""
        print(f"🎨 Generating frontend files with CodeLlama...")
        
        files_created = 0
        
        # HTML Chain
        html_chain = ChatPromptTemplate.from_template(
            "Generate ONLY the HTML code for {file_description}. "
            "Based on these requirements: {requirements}. "
            "Return only clean HTML with no markdown formatting, no explanations."
        ) | self.llm | StrOutputParser()
        
        # CSS Chain  
        css_chain = ChatPromptTemplate.from_template(
            "Generate ONLY the CSS code for {file_description}. "
            "Based on these requirements: {requirements}. "
            "Return only clean CSS with no markdown formatting, no explanations."
        ) | self.llm | StrOutputParser()
        
        # JavaScript Chain
        js_chain = ChatPromptTemplate.from_template(
            "Generate ONLY the JavaScript code for {file_description}. "
            "Based on these requirements: {requirements}. "
            "Return only clean JavaScript with no markdown formatting, no explanations."
        ) | self.llm | StrOutputParser()
        
        # Generate HTML
        try:
            html_code = html_chain.invoke({
                "file_description": "index.html - Complete HTML page for todo app with form inputs, task list, and responsive layout",
                "requirements": ui_code[:1000]
            })
            if html_code and len(html_code.strip()) > 50:
                self.git.write_file("frontend/index.html", html_code.strip())
                files_created += 1
            else:
                print("⚠️ Generated HTML was too short or empty")
        except Exception as e:
            print(f"⚠️ Error generating HTML: {e}")
        
        # Generate CSS
        try:
            css_code = css_chain.invoke({
                "file_description": "src/styles.css - Modern responsive CSS styles for todo app with animations and mobile support",
                "requirements": ui_code[:1000]
            })
            if css_code and len(css_code.strip()) > 50:
                self.git.write_file("frontend/src/styles.css", css_code.strip())
                files_created += 1
            else:
                print("⚠️ Generated CSS was too short or empty")
        except Exception as e:
            print(f"⚠️ Error generating CSS: {e}")
        
        # Generate JavaScript
        try:
            js_code = js_chain.invoke({
                "file_description": "src/app.js - JavaScript for todo app with API calls, DOM manipulation, and event handling",
                "requirements": ui_code[:1000]
            })
            if js_code and len(js_code.strip()) > 50:
                self.git.write_file("frontend/src/app.js", js_code.strip())
                files_created += 1
            else:
                print("⚠️ Generated JavaScript was too short or empty")
        except Exception as e:
            print(f"⚠️ Error generating JavaScript: {e}")
        
        print(f"🎨 Created {files_created} frontend files with CodeLlama")
    
    def _write_frontend_files_for_task(self, task_implementation: str, task: GitHubIssue):
        """Write frontend files for a specific task"""
        print(f"🎨 Implementing frontend task: {task['title']}")
        
        # Determine which files to generate based on task type and labels
        task_labels = [label.lower() for label in task['labels']]
        files_created = 0
        
        # Create focused prompts for specific files based on task
        html_chain = ChatPromptTemplate.from_template(
            "Generate ONLY the HTML code for this specific frontend task: {task_title}. "
            "Task implementation: {task_implementation}. "
            "Return only clean HTML with no markdown formatting, no explanations."
        ) | self.llm | StrOutputParser()
        
        css_chain = ChatPromptTemplate.from_template(
            "Generate ONLY the CSS code for this specific frontend task: {task_title}. "
            "Task implementation: {task_implementation}. "
            "Return only clean CSS with no markdown formatting, no explanations."
        ) | self.llm | StrOutputParser()
        
        js_chain = ChatPromptTemplate.from_template(
            "Generate ONLY the JavaScript code for this specific frontend task: {task_title}. "
            "Task implementation: {task_implementation}. "
            "Return only clean JavaScript with no markdown formatting, no explanations."
        ) | self.llm | StrOutputParser()
        
        # Generate specific files based on task needs
        if 'ui' in task_labels or 'component' in task['title'].lower() or 'form' in task['title'].lower():
            try:
                html_code = html_chain.invoke({
                    "task_title": task['title'],
                    "task_implementation": task_implementation[:1000]
                })
                if html_code and len(html_code.strip()) > 30:
                    # Append to or create HTML file
                    existing_html = ""
                    try:
                        existing_html = self.git.get_file_content("frontend/index.html")
                    except:
                        pass
                    
                    if existing_html:
                        # Insert new component into existing HTML
                        updated_html = existing_html.replace("</body>", f"\n<!-- {task['title']} -->\n{html_code.strip()}\n</body>")
                    else:
                        updated_html = html_code.strip()
                    
                    self.git.write_file("frontend/index.html", updated_html)
                    files_created += 1
            except Exception as e:
                print(f"⚠️ Error generating HTML: {e}")
        
        if 'styling' in task['title'].lower() or 'css' in task_labels:
            try:
                css_code = css_chain.invoke({
                    "task_title": task['title'],
                    "task_implementation": task_implementation[:1000]
                })
                if css_code and len(css_code.strip()) > 30:
                    # Append to existing CSS
                    existing_css = ""
                    try:
                        existing_css = self.git.get_file_content("frontend/src/styles.css")
                    except:
                        pass
                    
                    if existing_css:
                        updated_css = existing_css + f"\n\n/* {task['title']} */\n" + css_code.strip()
                    else:
                        updated_css = css_code.strip()
                    
                    self.git.write_file("frontend/src/styles.css", updated_css)
                    files_created += 1
            except Exception as e:
                print(f"⚠️ Error generating CSS: {e}")
        
        if 'javascript' in task_labels or 'interaction' in task['title'].lower() or 'api' in task['title'].lower():
            try:
                js_code = js_chain.invoke({
                    "task_title": task['title'],
                    "task_implementation": task_implementation[:1000]
                })
                if js_code and len(js_code.strip()) > 30:
                    # Append to existing JavaScript
                    existing_js = ""
                    try:
                        existing_js = self.git.get_file_content("frontend/src/app.js")
                    except:
                        pass
                    
                    if existing_js:
                        updated_js = existing_js + f"\n\n// {task['title']}\n" + js_code.strip()
                    else:
                        updated_js = js_code.strip()
                    
                    self.git.write_file("frontend/src/app.js", updated_js)
                    files_created += 1
            except Exception as e:
                print(f"⚠️ Error generating JavaScript: {e}")
        
        print(f"🎨 Created {files_created} files for task #{task['id']}")
        
        # Ensure complete frontend structure
        self._ensure_complete_frontend_structure()

    def _ensure_complete_frontend_structure(self):
        """Ensure all essential frontend files exist for a production-ready application"""
        frontend_files = {
            "frontend/Dockerfile": """FROM nginx:alpine

COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
""",
            "frontend/nginx.conf": """server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
""",
            "frontend/manifest.json": """{
  "name": "Todo App",
  "short_name": "TodoApp",
  "description": "A complete todo list application",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#007bff",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ]
}
""",
            "frontend/serviceworker.js": """const CACHE_NAME = 'todo-app-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/src/styles.css',
  '/src/app.js'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
"""
        }
        
        # Create frontend files if they don't exist
        for file_path, content in frontend_files.items():
            try:
                existing_content = self.git.get_file_content(file_path)
            except:
                # File doesn't exist, create it
                self.git.write_file(file_path, content)
                print(f"🎨 Created frontend file: {file_path}")
    
    def _create_package_json(self):
        """Create package.json for the frontend"""
        package_json = {
            "name": "frontend",
            "version": "1.0.0",
            "description": "Frontend for AI-generated application",
            "main": "index.html",
            "scripts": {
                "start": "python -m http.server 8000",
                "dev": "python -m http.server 8000",
                "build": "echo 'Build not configured'"
            },
            "dependencies": {},
            "devDependencies": {}
        }
        
        self.git.write_file("frontend/package.json", json.dumps(package_json, indent=2))
    
    def _revise_frontend_code(self, original_code: str, issues: List[str], requirements: str) -> str:
        """Revise frontend code based on self-review issues"""
        revision_prompt = ChatPromptTemplate.from_template("""
        You need to revise this frontend code based on identified issues:
        
        Original Code:
        {original_code}
        
        Requirements:
        {requirements}
        
        Issues to Fix:
        {issues}
        
        Create improved frontend code that:
        1. Fixes all identified issues
        2. Maintains the original functionality
        3. Follows clean code principles
        4. Implements proper Hexagonal Architecture patterns
        5. Ensures accessibility and responsiveness
        
        Provide the complete revised frontend implementation.
        """)
        
        chain = revision_prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "original_code": original_code,
            "requirements": requirements,
            "issues": "\n".join(issues)
        })
    
    def _address_peer_feedback(self, code: str, peer_issues: List[str], requirements: str) -> str:
        """Address peer review feedback"""
        feedback_prompt = ChatPromptTemplate.from_template("""
        Address this peer review feedback for your frontend code:
        
        Current Code:
        {code}
        
        Requirements:
        {requirements}
        
        Peer Review Issues:
        {peer_issues}
        
        Modify the code to address the peer feedback while:
        1. Maintaining existing functionality
        2. Improving integration with backend
        3. Following suggested improvements
        4. Ensuring requirements compliance
        
        Provide the updated frontend code.
        """)
        
        chain = feedback_prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "code": code,
            "requirements": requirements,
            "peer_issues": "\n".join(peer_issues)
        })

class BackendCoderAgent:
    """Creates server-side code, APIs, and database logic"""
    
    def __init__(self, git_manager: GitManager):
        self.llm = code_llm  # Use CodeLlama for backend coding
        self.git = git_manager
        self.qa_manager = QualityAssuranceManager(git_manager)
        self.prompt = ChatPromptTemplate.from_template("""
        You are a Backend Developer specializing in server-side development.
        
        Project Requirements: {requirements}
        Technical Architecture: {architecture}
        Frontend Files Summary: {frontend_summary}
        Existing Backend Structure: {existing_backend}
        
        CRITICAL: You MUST follow the technology stack specified in the architecture document.
        Use ONLY the programming language, framework, and database specified by the Architect.
        
        Your task is to:
        1. Implement backend using the EXACT technology stack from the architecture
        2. Design API endpoints following the architecture's API design patterns
        3. Use the specified web framework (FastAPI, Express, Spring Boot, etc.)
        4. Implement the database technology chosen by the architect
        5. Follow the architectural patterns specified (Hexagonal, MVC, etc.)
        6. Implement authentication using the method specified in architecture
        7. Structure code according to the architecture's code organization patterns
        
        Architecture Compliance Requirements:
        - Use the exact programming language specified
        - Use the exact web framework specified  
        - Use the exact database technology specified
        - Follow the architectural patterns specified
        - Implement the API design pattern specified (REST, GraphQL, etc.)
        - Use the testing framework specified in architecture
        
        Create backend code that strictly adheres to the architectural decisions.
        
        Format your response as:
        ## Backend Implementation
        
        ### API Design
        [List of endpoints with methods and descriptions]
        
        ### Server Code
        ```python
        [Complete server code - FastAPI or Flask]
        ```
        
        ### Database Schema
        ```sql
        [Database table definitions]
        ```
        
        ### Configuration
        ```python
        [Configuration and environment setup]
        ```
        
        ### Security & Validation
        [Security measures and data validation]
        
        ### Hexagonal Architecture Structure
        ```python
        [Domain layer, application layer, and infrastructure adapters]
        ```
        
        ### Domain Model Implementation
        [DDD entities, value objects, aggregates, and domain services]
        """)
        
    def create_backend(self, state: DevelopmentState) -> DevelopmentState:
        """Work on backend tasks from the backlog"""
        task_manager = TaskManager(self.git)
        
        # Get available backend tasks
        available_tasks = task_manager.get_available_tasks_for_agent('backend', state.get('tasks', []))
        
        if not available_tasks:
            print("🔧 Backend Developer: No backend tasks available in backlog")
            return state
        
        # Pick up the highest priority task
        current_task = available_tasks[0]
        current_task = task_manager.assign_task(current_task, "Backend Developer")
        state["current_task"] = current_task
        
        print(f"🔧 Backend Developer: Picking up task #{current_task['id']}: {current_task['title']}")
        print(f"   Priority: {current_task['priority']}, Story Points: {current_task['story_points']}")
        
        # Read project context
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        architecture = state.get("architecture", "") or self.git.get_file_content("docs/architecture/tech_stack.md")
        
        # Create task-specific prompt
        task_chain = ChatPromptTemplate.from_template("""
        You are a Backend Developer working on a specific task.
        
        CURRENT TASK: {task_title}
        TASK DESCRIPTION: {task_description}
        ACCEPTANCE CRITERIA:
        {acceptance_criteria}
        
        Project Requirements: {requirements}
        Technical Architecture: {architecture}
        
        CRITICAL: You MUST follow the technology stack specified in the architecture document.
        
        Focus ONLY on this specific task. Implement the minimal code needed to satisfy the acceptance criteria.
        Do not implement features outside this task scope.
        
        Generate code that:
        1. Addresses the specific task requirements
        2. Meets all acceptance criteria
        3. Follows the architecture specification
        4. Is production-ready and well-tested
        5. Includes proper error handling
        
        Provide implementation details for this specific task only.
        """) | self.llm | StrOutputParser()
        
        # Generate code for this specific task
        task_implementation = task_chain.invoke({
            "task_title": current_task['title'],
            "task_description": current_task['description'],
            "acceptance_criteria": '\n'.join([f"- {criteria}" for criteria in current_task['acceptance_criteria']]),
            "requirements": requirements,
            "architecture": architecture
        })
        
        # Write backend files for this task
        self._write_backend_files_for_task(task_implementation, current_task)
        
        # Mark task as completed
        task_manager.complete_task(current_task)
        state["completed_tasks"] = state.get("completed_tasks", []) + [current_task]
        
        # Update task list
        updated_tasks = []
        for task in state.get("tasks", []):
            if task['id'] != current_task['id']:
                updated_tasks.append(task)
            else:
                updated_tasks.append(current_task)
        state["tasks"] = updated_tasks
        
        # Commit this specific task
        commit_msg = f"feat: Implement {current_task['title']} (#{current_task['id']})"
        self.git.commit_changes(commit_msg, "Backend Developer")
        
        # Save progress
        task_manager.save_task_progress(state)
        
        print(f"✅ Backend Developer: Completed task #{current_task['id']}")
        state["feedback"].append(f"✓ Backend Developer: Task #{current_task['id']} completed and committed")
        
        # Clear current task
        state["current_task"] = None
        state["git_commits"].append("Backend implementation committed")
        print("⚙️ Backend Developer: Server-side implementation completed and committed")
        return state
    
    def _get_frontend_summary(self) -> str:
        """Get summary of frontend implementation"""
        frontend_files = []
        for file_type in ["index.html", "src/styles.css", "src/app.js"]:
            content = self.git.get_file_content(f"frontend/{file_type}")
            if content:
                frontend_files.append(f"{file_type}: {len(content)} chars")
        return "\n".join(frontend_files) if frontend_files else "No frontend files found"
    
    def _get_existing_backend_structure(self) -> str:
        """Get existing backend file structure"""
        backend_files = []
        backend_dir = Path(self.git.project_dir) / "backend"
        
        if backend_dir.exists():
            for file_path in backend_dir.rglob("*.py"):
                rel_path = file_path.relative_to(self.git.project_dir)
                content = self.git.get_file_content(str(rel_path))
                backend_files.append(f"{rel_path}: {len(content)} characters")
        
        return "\n".join(backend_files) if backend_files else "No existing backend files"
    
    def _write_backend_files(self, backend_code: str):
        """Generate individual backend files using CodeLlama"""
        print(f"🔍 Generating backend files with CodeLlama...")
        
        files_created = 0
        chain = ChatPromptTemplate.from_template(
            "Generate ONLY the Python code for {file_description}. "
            "Based on these requirements: {requirements}. "
            "Return only clean Python code with no markdown formatting, no explanations, no comments about the task."
        ) | self.llm | StrOutputParser()
        
        # Generate main.py
        try:
            main_py_code = chain.invoke({
                "file_description": "main.py - FastAPI application with endpoints for todo tasks (GET, POST, PUT, DELETE /tasks)",
                "requirements": backend_code[:1000]  # Truncate for context
            })
            if main_py_code and len(main_py_code.strip()) > 50:
                self.git.write_file("backend/main.py", main_py_code.strip())
                files_created += 1
            else:
                print("⚠️ Generated main.py was too short or empty")
        except Exception as e:
            print(f"⚠️ Error generating main.py: {e}")
        
        # Generate domain models
        try:
            models_code = chain.invoke({
                "file_description": "src/domain/models.py - Pydantic domain models for Task and User entities with business logic",
                "requirements": backend_code[:1000]
            })
            if models_code and len(models_code.strip()) > 50:
                self.git.write_file("backend/src/domain/models.py", models_code.strip())
                files_created += 1
            else:
                print("⚠️ Generated models.py was too short or empty")
        except Exception as e:
            print(f"⚠️ Error generating models.py: {e}")
        
        # Generate services
        try:
            services_code = chain.invoke({
                "file_description": "src/application/services.py - Business logic services for task operations (create, read, update, delete)",
                "requirements": backend_code[:1000]
            })
            if services_code and len(services_code.strip()) > 50:
                self.git.write_file("backend/src/application/services.py", services_code.strip())
                files_created += 1
            else:
                print("⚠️ Generated services.py was too short or empty")
        except Exception as e:
            print(f"⚠️ Error generating services.py: {e}")
        
        # Generate database/repository
        try:
            db_code = chain.invoke({
                "file_description": "src/infrastructure/database.py - Database connection and repository pattern for task persistence",
                "requirements": backend_code[:1000]
            })
            if db_code and len(db_code.strip()) > 50:
                self.git.write_file("backend/src/infrastructure/database.py", db_code.strip())
                files_created += 1
            else:
                print("⚠️ Generated database.py was too short or empty")
        except Exception as e:
            print(f"⚠️ Error generating database.py: {e}")
        
        # Generate SQL schema (using different prompt for SQL)
        try:
            sql_chain = ChatPromptTemplate.from_template(
                "Generate ONLY the SQL schema for {file_description}. "
                "Based on these requirements: {requirements}. "
                "Return only clean SQL with no markdown formatting, no explanations."
            ) | self.llm | StrOutputParser()
            
            schema_sql = sql_chain.invoke({
                "file_description": "todo app database with users and tasks tables, including indexes",
                "requirements": backend_code[:1000]
            })
            if schema_sql and len(schema_sql.strip()) > 50:
                self.git.write_file("backend/schema.sql", schema_sql.strip())
                files_created += 1
            else:
                print("⚠️ Generated schema.sql was too short or empty")
        except Exception as e:
            print(f"⚠️ Error generating schema.sql: {e}")
        
        print(f"📁 Created {files_created} backend files with CodeLlama")
    
    def _write_backend_files_for_task(self, task_implementation: str, task: GitHubIssue):
        """Write backend files for a specific task"""
        print(f"🔍 Implementing backend task: {task['title']}")
        
        # Determine which files to generate based on task type and labels
        task_labels = [label.lower() for label in task['labels']]
        files_created = 0
        
        # Create focused prompts for specific files based on task
        chain = ChatPromptTemplate.from_template(
            "Generate ONLY the {file_type} code for this specific task: {task_title}. "
            "Task implementation: {task_implementation}. "
            "Return only clean code with no markdown formatting, no explanations."
        ) | self.llm | StrOutputParser()
        
        # Generate specific files based on task needs
        if 'api' in task_labels or 'endpoint' in task['title'].lower():
            try:
                api_code = chain.invoke({
                    "file_type": "FastAPI endpoints and routes",
                    "task_title": task['title'],
                    "task_implementation": task_implementation[:1000]
                })
                if api_code and len(api_code.strip()) > 30:
                    existing_main = ""
                    try:
                        existing_main = self.git.get_file_content("backend/main.py")
                    except:
                        pass
                    
                    # Append to existing main.py or create new
                    if existing_main:
                        updated_main = existing_main + "\n\n# " + task['title'] + "\n" + api_code.strip()
                    else:
                        updated_main = api_code.strip()
                    
                    self.git.write_file("backend/main.py", updated_main)
                    files_created += 1
            except Exception as e:
                print(f"⚠️ Error generating API code: {e}")
        
        if 'database' in task_labels or 'schema' in task['title'].lower():
            try:
                db_code = chain.invoke({
                    "file_type": "database models and repository",
                    "task_title": task['title'],
                    "task_implementation": task_implementation[:1000]
                })
                if db_code and len(db_code.strip()) > 30:
                    self.git.write_file(f"backend/src/infrastructure/task_{task['id']}_db.py", db_code.strip())
                    files_created += 1
            except Exception as e:
                print(f"⚠️ Error generating database code: {e}")
        
        if 'auth' in task['title'].lower() or 'user' in task['title'].lower():
            try:
                auth_code = chain.invoke({
                    "file_type": "authentication and user management",
                    "task_title": task['title'],
                    "task_implementation": task_implementation[:1000]
                })
                if auth_code and len(auth_code.strip()) > 30:
                    self.git.write_file(f"backend/src/application/auth_service.py", auth_code.strip())
                    files_created += 1
            except Exception as e:
                print(f"⚠️ Error generating auth code: {e}")
        
        print(f"📁 Created {files_created} files for task #{task['id']}")
        
        # Ensure essential project files exist for a complete application
        self._ensure_complete_project_structure()

    def _ensure_complete_project_structure(self):
        """Ensure all essential files exist for a production-ready application"""
        essential_files = {
            "backend/requirements.txt": """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
sqlalchemy==2.0.23
alembic==1.13.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
""",
            "backend/.env.example": """# Database Configuration
DATABASE_URL=sqlite:///./todo.db

# API Configuration
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
""",
            "backend/Dockerfile": """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
            "frontend/.gitignore": """node_modules/
.env
.env.local
.env.production
dist/
build/
*.log
.DS_Store
""",
            "docker-compose.yml": """version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./todo.db
    volumes:
      - ./backend:/app
      
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
""",
            ".gitignore": """# Dependencies
node_modules/
__pycache__/
*.pyc
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Build outputs
dist/
build/
""",
            "README.md": """# Todo Application

A complete todo list application with modern web technologies.

## Features

- ✅ Create, read, update, delete todos
- ✅ Mark todos as complete/incomplete
- ✅ Filter and search todos
- ✅ Responsive design
- ✅ RESTful API
- ✅ Data persistence

## Quick Start

### Using Docker (Recommended)
```bash
docker-compose up
```

### Manual Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend  
```bash
cd frontend
# Open index.html in browser or serve with local server
python -m http.server 8080
```

## API Documentation

The API will be available at `http://localhost:8000/docs` when running.

## Testing

```bash
cd backend
pytest
```

## Project Structure

```
todo-app/
├── backend/           # FastAPI backend
├── frontend/          # HTML/CSS/JS frontend  
├── docs/             # Documentation
├── tests/            # Test files
└── docker-compose.yml
```
"""
        }
        
        # Create essential files if they don't exist
        for file_path, content in essential_files.items():
            try:
                existing_content = self.git.get_file_content(file_path)
            except:
                # File doesn't exist, create it
                self.git.write_file(file_path, content)
                print(f"📄 Created essential file: {file_path}")

    def _create_api_documentation(self, backend_code: str):
        """Create API documentation from backend code"""
        api_doc_prompt = ChatPromptTemplate.from_template("""
        Based on this backend implementation, create comprehensive API documentation:
        
        {backend_code}
        
        Create documentation with:
        - Base URL and authentication
        - All endpoints with methods, parameters, responses
        - Request/response examples
        - Error codes and handling
        - Rate limiting information
        
        Format as OpenAPI/Swagger style documentation in Markdown.
        """)
        
        chain = api_doc_prompt | self.llm | StrOutputParser()
        api_docs = chain.invoke({"backend_code": backend_code})
        self.git.write_file("docs/api/api_spec.md", api_docs)
    
    def _create_requirements_txt(self):
        """Create Python requirements file"""
        requirements = """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
python-multipart==0.0.6
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.0.1
alembic==1.13.1
pytest==7.4.3
pytest-asyncio==0.21.1"""
        
        self.git.write_file("backend/requirements.txt", requirements)

class DocumentationAgent:
    """Creates comprehensive documentation for the project"""
    
    def __init__(self, git_manager: GitManager):
        self.llm = general_llm  # Use Mistral for documentation
        self.git = git_manager
        self.prompt = ChatPromptTemplate.from_template("""
        You are a Technical Documentation Specialist.
        
        Requirements: {requirements}
        UI Code: {ui_code}
        Backend Code: {backend_code}
        
        Your task is to create comprehensive documentation including:
        1. README.md with setup instructions
        2. API documentation
        3. User guide
        4. Developer guide
        5. Deployment instructions
        6. Architecture overview
        
        Format your response as:
        ## Project Documentation
        
        ### README.md
        ```markdown
        [Complete README with setup, installation, usage]
        ```
        
        ### API Documentation
        [Detailed API endpoints, parameters, responses]
        
        ### User Guide
        [How to use the application from user perspective]
        
        ### Developer Guide
        [How to set up development environment and contribute]
        
        ### Architecture Overview
        [System architecture and design decisions]
        
        ### Deployment Guide
        [How to deploy to production]
        """)
        
    def create_documentation(self, state: DevelopmentState) -> DevelopmentState:
        """Work on documentation tasks from the backlog"""
        task_manager = TaskManager(self.git)
        
        # Get available documentation tasks
        available_tasks = task_manager.get_available_tasks_for_agent('documentation', state.get('tasks', []))
        
        if not available_tasks:
            print("📚 Documentation Agent: No documentation tasks available in backlog")
            return state
        
        # Pick up the highest priority task
        current_task = available_tasks[0]
        current_task = task_manager.assign_task(current_task, "Documentation Agent")
        state["current_task"] = current_task
        
        print(f"📚 Documentation Agent: Picking up task #{current_task['id']}: {current_task['title']}")
        print(f"   Priority: {current_task['priority']}, Story Points: {current_task['story_points']}")
        
        # Read project context
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        project_structure = self._analyze_project_structure()
        
        # Create task-specific documentation
        task_chain = ChatPromptTemplate.from_template("""
        You are a Documentation Agent working on a specific documentation task.
        
        CURRENT TASK: {task_title}
        TASK DESCRIPTION: {task_description}
        ACCEPTANCE CRITERIA:
        {acceptance_criteria}
        
        Project Context: {requirements}
        Project Structure: {project_structure}
        
        Focus ONLY on this specific documentation task. Create the exact documentation needed to satisfy the acceptance criteria.
        
        Provide clear, comprehensive documentation for this specific task only.
        """) | self.llm | StrOutputParser()
        
        documentation = task_chain.invoke({
            "task_title": current_task['title'],
            "task_description": current_task['description'],
            "acceptance_criteria": '\n'.join([f"- {criteria}" for criteria in current_task['acceptance_criteria']]),
            "requirements": requirements,
            "project_structure": project_structure
        })
        
        # Write task-specific documentation
        self._write_documentation_for_task(documentation, current_task)
        
        # Mark task as completed
        task_manager.complete_task(current_task)
        state["completed_tasks"] = state.get("completed_tasks", []) + [current_task]
        
        # Update task list
        updated_tasks = []
        for task in state.get("tasks", []):
            if task['id'] != current_task['id']:
                updated_tasks.append(task)
            else:
                updated_tasks.append(current_task)
        state["tasks"] = updated_tasks
        
        # Commit this specific task
        commit_msg = f"docs: {current_task['title']} (#{current_task['id']})"
        self.git.commit_changes(commit_msg, "Documentation Agent")
        
        # Save progress
        task_manager.save_task_progress(state)
        
        print(f"✅ Documentation Agent: Completed task #{current_task['id']}")
        state["feedback"].append(f"✓ Documentation Agent: Task #{current_task['id']} completed and committed")
        
        # Clear current task
        state["current_task"] = None
        return state
    
    def _write_documentation_for_task(self, documentation: str, task: GitHubIssue):
        """Write documentation files for a specific task"""
        print(f"📚 Writing documentation for task: {task['title']}")
        
        task_title_lower = task['title'].lower()
        
        if 'readme' in task_title_lower:
            self.git.write_file("README.md", documentation)
        elif 'api' in task_title_lower:
            self.git.write_file("docs/api/README.md", documentation)
        elif 'deployment' in task_title_lower:
            self.git.write_file("docs/deployment/README.md", documentation) 
        elif 'architecture' in task_title_lower:
            self.git.write_file("docs/architecture/README.md", documentation)
        elif 'setup' in task_title_lower or 'installation' in task_title_lower:
            self.git.write_file("docs/setup/README.md", documentation)
        else:
            # Generic documentation file
            filename = task['title'].lower().replace(' ', '_').replace('-', '_') + '.md'
            self.git.write_file(f"docs/{filename}", documentation)
        
        print(f"📁 Created documentation file for task #{task['id']}")
    
    def _analyze_project_structure(self) -> str:
        """Analyze the current project file structure"""
        structure = []
        for root, dirs, files in os.walk(self.git.project_dir):
            level = root.replace(str(self.git.project_dir), '').count(os.sep)
            indent = ' ' * 2 * level
            structure.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                structure.append(f"{subindent}{file}")
        return '\n'.join(structure)
    
    def _get_frontend_summary(self) -> str:
        """Get frontend files summary"""
        return self.git.get_file_content("frontend/index.html")[:500] + "..."
    
    def _get_backend_summary(self) -> str:
        """Get backend files summary"""
        return self.git.get_file_content("backend/main.py")[:500] + "..."
    
    def _extract_readme(self, documentation: str) -> str:
        """Extract README content from documentation"""
        readme_match = re.search(r'```markdown\n(.*?)```', documentation, re.DOTALL)
        return readme_match.group(1) if readme_match else documentation
    
    def _extract_architecture_docs(self, documentation: str) -> str:
        """Extract architecture documentation"""
        return "# Architecture Overview\n\nGenerated from full documentation..."
    
    def _extract_deployment_docs(self, documentation: str) -> str:
        """Extract deployment documentation"""
        return "# Deployment Guide\n\nGenerated from full documentation..."

class QATesterAgent:
    """Tests the code and identifies issues"""
    
    def __init__(self, git_manager: GitManager):
        self.llm = general_llm  # Use Mistral for testing analysis
        self.git = git_manager
        self.prompt = ChatPromptTemplate.from_template("""
        You are a QA Engineer and Software Tester.
        
        Requirements: {requirements}
        UI Code: {ui_code}
        Backend Code: {backend_code}
        
        Your task is to:
        1. Review code for bugs, clean code violations, and architectural issues
        2. Create comprehensive test cases following TDD principles
        3. Validate Hexagonal Architecture implementation
        4. Test domain model and business logic separately from infrastructure
        5. Identify potential security vulnerabilities
        6. Check for accessibility issues
        7. Validate that code meets acceptance criteria and architectural guidelines
        8. Create automated test scripts (unit, integration, and domain tests)
        9. Performance and load testing considerations
        
        Follow these testing guidelines:
        - Apply Test Driven Development (TDD) approach: Red-Green-Refactor
        - Write tests for domain logic independent of infrastructure
        - Create unit tests for each domain entity and service
        - Test ports and adapters separately from domain logic
        - Validate clean code principles: readability, maintainability, SOLID principles
        - Ensure proper separation of concerns and dependency inversion
        - Test bounded contexts and domain boundaries
        - Verify that business rules are properly encapsulated in domain layer
        
        Format your response as:
        ## QA Test Report
        
        ### Code Review Issues
        [List of bugs, security issues, code quality problems]
        
        ### Test Cases
        [Detailed test cases for each feature]
        
        ### TDD Test Suite
        ```python
        [Unit tests following TDD Red-Green-Refactor cycle]
        ```
        
        ### Domain Tests
        ```python
        [Tests for domain entities, value objects, and business rules]
        ```
        
        ### Integration Tests
        ```python
        [Tests for ports, adapters, and infrastructure integration]
        ```
        
        ### Architecture Validation
        [Assessment of Hexagonal Architecture and DDD implementation]
        
        ### Clean Code Assessment
        [Evaluation of code quality, readability, and SOLID principles]
        
        ### Accessibility Audit
        [Accessibility compliance and improvements needed]
        
        ### Performance Analysis
        [Performance bottlenecks and optimization suggestions]
        
        ### Security Assessment
        [Security vulnerabilities and mitigation strategies]
        
        ### Overall Quality Score
        [Score out of 10 with justification]
        """)
        
    def test_code(self, state: DevelopmentState) -> DevelopmentState:
        """Work on testing tasks from the backlog"""
        task_manager = TaskManager(self.git)
        
        # Get available testing tasks
        available_tasks = task_manager.get_available_tasks_for_agent('testing', state.get('tasks', []))
        
        if not available_tasks:
            print("🧪 QA Tester: No testing tasks available in backlog")
            return state
        
        # Pick up the highest priority task
        current_task = available_tasks[0]
        current_task = task_manager.assign_task(current_task, "QA Tester")
        state["current_task"] = current_task
        
        print(f"🧪 QA Tester: Picking up task #{current_task['id']}: {current_task['title']}")
        print(f"   Priority: {current_task['priority']}, Story Points: {current_task['story_points']}")
        
        # Read project context
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        backend_files = self._get_all_backend_files()
        frontend_files = self._get_all_frontend_files()
        
        # Create task-specific test
        task_chain = ChatPromptTemplate.from_template("""
        You are a QA Tester working on a specific testing task.
        
        CURRENT TASK: {task_title}
        TASK DESCRIPTION: {task_description}
        ACCEPTANCE CRITERIA:
        {acceptance_criteria}
        
        Project Context: {requirements}
        Backend Files: {backend_files}
        Frontend Files: {frontend_files}
        
        Focus ONLY on this specific testing task. Create the exact tests needed to satisfy the acceptance criteria.
        
        Provide specific test code and test cases for this task only.
        """) | self.llm | StrOutputParser()
        
        test_results = task_chain.invoke({
            "task_title": current_task['title'],
            "task_description": current_task['description'],
            "acceptance_criteria": '\n'.join([f"- {criteria}" for criteria in current_task['acceptance_criteria']]),
            "requirements": requirements,
            "backend_files": backend_files,
            "frontend_files": frontend_files
        })
        
        # Write test files for this specific task
        self._write_test_files_for_task(test_results, current_task)
        
        # Mark task as completed
        task_manager.complete_task(current_task)
        state["completed_tasks"] = state.get("completed_tasks", []) + [current_task]
        
        # Update task list
        updated_tasks = []
        for task in state.get("tasks", []):
            if task['id'] != current_task['id']:
                updated_tasks.append(task)
            else:
                updated_tasks.append(current_task)
        state["tasks"] = updated_tasks
        
        # Commit this specific task
        commit_msg = f"test: {current_task['title']} (#{current_task['id']})"
        self.git.commit_changes(commit_msg, "QA Tester")
        
        # Save progress
        task_manager.save_task_progress(state)
        
        print(f"✅ QA Tester: Completed task #{current_task['id']}")
        state["feedback"].append(f"✓ QA Tester: Task #{current_task['id']} completed and committed")
        
        # Clear current task
        state["current_task"] = None
        return state
    
    def _write_test_files_for_task(self, test_results: str, task: GitHubIssue):
        """Write test files for a specific task"""
        print(f"🧪 Writing tests for task: {task['title']}")
        
        task_title_lower = task['title'].lower()
        
        # Generate test file content
        test_chain = ChatPromptTemplate.from_template(
            "Generate ONLY the test code for: {task_title}. "
            "Test implementation: {test_results}. "
            "Return only clean Python test code with no markdown formatting, no explanations."
        ) | self.llm | StrOutputParser()
        
        try:
            test_code = test_chain.invoke({
                "task_title": task['title'],
                "test_results": test_results[:1000]
            })
            
            if test_code and len(test_code.strip()) > 30:
                if 'backend' in task_title_lower or 'api' in task_title_lower:
                    filename = f"backend/tests/test_{task['id']}_backend.py"
                elif 'frontend' in task_title_lower or 'ui' in task_title_lower:
                    filename = f"frontend/tests/test_{task['id']}_frontend.py"
                elif 'integration' in task_title_lower:
                    filename = f"tests/integration/test_{task['id']}_integration.py"
                else:
                    filename = f"tests/test_{task['id']}.py"
                
                self.git.write_file(filename, test_code.strip())
                print(f"📁 Created test file: {filename}")
            
            # Also create test report
            report_filename = f"docs/qa/test_report_{task['id']}.md"
            self.git.write_file(report_filename, test_results)
            
        except Exception as e:
            print(f"⚠️ Error generating test files: {e}")
    
    def _get_all_backend_files(self) -> str:
        """Get all backend file contents"""
        files = []
        backend_dir = Path(self.git.project_dir) / "backend"
        
        if backend_dir.exists():
            for file_path in backend_dir.rglob("*.py"):
                rel_path = file_path.relative_to(self.git.project_dir)
                content = self.git.get_file_content(str(rel_path))
                files.append(f"=== {rel_path} ===\n{content}\n")
        
        return "\n".join(files) if files else "No backend files found"
    
    def _get_all_frontend_files(self) -> str:
        """Get all frontend file contents"""
        files = []
        frontend_dir = Path(self.git.project_dir) / "frontend"
        
        if frontend_dir.exists():
            for file_path in frontend_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in [".html", ".css", ".js"]:
                    rel_path = file_path.relative_to(self.git.project_dir)
                    content = self.git.get_file_content(str(rel_path))
                    files.append(f"=== {rel_path} ===\n{content}\n")
        
        return "\n".join(files) if files else "No frontend files found"
    
    def _write_test_files(self, test_results: str):
        """Extract and write test files"""
        # Extract Python test code
        test_matches = re.findall(r'```python\n(.*?)```', test_results, re.DOTALL)
        
        for i, test_code in enumerate(test_matches):
            if "test_" in test_code or "def test" in test_code:
                filename = f"test_{i+1}.py" if i > 0 else "test_main.py"
                self.git.write_file(f"backend/tests/unit/{filename}", test_code.strip())

class ProjectManagerAgent:
    """Coordinates the team and manages the development workflow"""
    
    def __init__(self, git_manager: GitManager):
        self.llm = general_llm  # Use Mistral for project management
        self.git = git_manager
        self.prompt = ChatPromptTemplate.from_template("""
        You are a Project Manager overseeing an agile development team.
        
        Current Project Status:
        Requirements: {requirements_status}
        UI Development: {ui_status}
        Backend Development: {backend_status}
        Documentation: {documentation_status}
        Testing: {testing_status}
        
        Team Feedback: {feedback}
        Iteration: {iteration_count}
        
        Your task is to:
        1. Assess overall project status and architectural compliance
        2. Identify blockers and risks
        3. Coordinate next steps
        4. Ensure quality, architectural guidelines, and timeline adherence
        5. Validate adherence to TDD, Clean Code, Hexagonal Architecture, and DDD
        6. Make go/no-go decisions based on code quality and architecture
        7. Plan next iteration if needed
        
        Format your response as:
        ## Project Status Report
        
        ### Current Status
        [Overall project health and progress]
        
        ### Completed Deliverables
        [What has been completed successfully]
        
        ### Issues and Risks
        [Current problems and potential risks]
        
        ### Next Actions
        [Specific next steps for the team]
        
        ### Quality Assessment
        [Code quality, documentation quality, test coverage]
        
        ### Architecture Compliance
        [Hexagonal Architecture and DDD implementation assessment]
        
        ### Development Practices
        [TDD adherence, Clean Code principles, and best practices evaluation]
        
        ### Decision
        [READY FOR RELEASE / NEEDS ANOTHER ITERATION / MAJOR ISSUES]
        """)
        
    def coordinate_team(self, state: DevelopmentState) -> DevelopmentState:
        # All work already on main branch - no merging needed
        
        # Analyze project status from actual files
        project_analysis = self._analyze_project_completion()
        
        chain = self.prompt | self.llm | StrOutputParser()
        project_status = chain.invoke({
            "requirements_status": "✓ Complete" if self.git.get_file_content("docs/prd/requirements.md") else "❌ Pending",
            "ui_status": "✓ Complete" if self.git.get_file_content("frontend/index.html") else "❌ Pending", 
            "backend_status": "✓ Complete" if self.git.get_file_content("backend/main.py") else "❌ Pending",
            "documentation_status": "✓ Complete" if self.git.get_file_content("README.md") else "❌ Pending",
            "testing_status": "✓ Complete" if self.git.get_file_content("backend/tests/unit/test_main.py") else "❌ Pending",
            "feedback": "\n".join(state["feedback"]),
            "iteration_count": state["iteration_count"],
            "git_commits": "\n".join(state["git_commits"]),
            "project_analysis": project_analysis
        })
        
        # Create comprehensive project completion checklist
        completion_checklist = self._create_completion_checklist(state)
        
        # Write final project status and checklist
        self.git.write_file("docs/project_status.md", project_status)
        self.git.write_file("docs/DEPLOYMENT_CHECKLIST.md", completion_checklist)
        self.git.write_file("docs/GETTING_STARTED.md", self._create_getting_started_guide())
        
        # Final commit
        self.git.commit_changes("docs: Final project status, deployment checklist, and getting started guide", "Project Manager")
        
        state["project_status"] = project_status
        state["iteration_count"] += 1
        state["git_commits"].append("Final project status and deployment guide committed")
        
        # Print completion summary
        self._print_completion_summary(state)
        print("👔 Project Manager: Team coordination and final status completed")
        return state
    
    def _create_completion_checklist(self, state: DevelopmentState) -> str:
        """Create a comprehensive deployment checklist"""
        completed_tasks = len(state.get('completed_tasks', []))
        total_tasks = len(state.get('tasks', []))
        
        return f"""# 🚀 Deployment Checklist

## Project Status: {completed_tasks}/{total_tasks} Tasks Completed

### ✅ Core Application
- [ ] Backend API endpoints functional
- [ ] Frontend UI responsive and interactive
- [ ] Database schema implemented
- [ ] Data persistence working
- [ ] CRUD operations complete

### ✅ Quality Assurance
- [ ] Unit tests written and passing
- [ ] Integration tests implemented
- [ ] Error handling comprehensive
- [ ] Input validation working
- [ ] Security measures in place

### ✅ Production Readiness
- [ ] Environment configuration (`.env` files)
- [ ] Docker configuration ready
- [ ] Dependencies documented (`requirements.txt`, `package.json`)
- [ ] Database migration scripts
- [ ] CORS configuration set

### ✅ Documentation
- [ ] README with setup instructions
- [ ] API documentation complete
- [ ] Deployment guide available
- [ ] Architecture documentation
- [ ] User guide/manual

### 🚀 Deployment Commands

#### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
python -m http.server 8080
```

#### Production (Docker)
```bash
docker-compose up --build
```

### 📊 Project Statistics
- **Total Tasks**: {total_tasks}
- **Completed Tasks**: {completed_tasks}
- **Team Iterations**: {state.get('iteration_count', 0)}
- **Git Commits**: {len(state.get('git_commits', []))}

### 🎯 Next Steps
1. Run local tests: `pytest backend/tests/`
2. Test full application flow
3. Deploy to staging environment
4. Perform user acceptance testing
5. Deploy to production

---
*Generated by AI Development Team - Ready for Production* 🎉
"""
    
    def _create_getting_started_guide(self) -> str:
        """Create a user-friendly getting started guide"""
        return """# 🚀 Getting Started with Todo App

## Quick Setup (5 minutes)

### Option 1: Docker (Recommended)
```bash
# Clone and run
git clone <your-repo>
cd todo-app
docker-compose up
```
✅ App running at: http://localhost:3000

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
✅ API running at: http://localhost:8000

#### Frontend Setup
```bash
cd frontend
python -m http.server 8080
```
✅ Frontend at: http://localhost:8080

## 📖 How to Use

1. **Add Todo**: Click "Add Task" and enter details
2. **Complete Todo**: Click the checkbox to mark complete
3. **Edit Todo**: Click on task text to edit
4. **Delete Todo**: Click the delete button
5. **Filter Todos**: Use filter buttons (All/Active/Completed)

## 🔧 Development

### Backend Development
- API docs: http://localhost:8000/docs
- Add new endpoints in `backend/main.py`
- Database models in `backend/src/domain/models.py`

### Frontend Development
- Main logic: `frontend/src/app.js`
- Styling: `frontend/src/styles.css`
- Layout: `frontend/index.html`

### Testing
```bash
cd backend
pytest
```

## 🚀 Deployment

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
```

### Production Build
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 📚 Documentation
- [API Documentation](docs/api/README.md)
- [Architecture Overview](docs/architecture/README.md)
- [Deployment Guide](docs/DEPLOYMENT_CHECKLIST.md)

## 🆘 Troubleshooting

### Common Issues
- **Port already in use**: Change ports in `docker-compose.yml`
- **Database errors**: Check DATABASE_URL in `.env`
- **CORS issues**: Update CORS_ORIGINS in `.env`

### Getting Help
1. Check logs: `docker-compose logs`
2. Review API docs: http://localhost:8000/docs
3. Verify environment: Check `.env` file

---
*Ready to build amazing todos! 🎉*
"""
    
    def _print_completion_summary(self, state: DevelopmentState):
        """Print a comprehensive completion summary"""
        completed_tasks = len(state.get('completed_tasks', []))
        total_tasks = len(state.get('tasks', []))
        
        print("\n" + "="*80)
        print("🎉 PROJECT COMPLETION SUMMARY")
        print("="*80)
        print(f"📊 Tasks: {completed_tasks}/{total_tasks} completed ({(completed_tasks/max(total_tasks,1)*100):.1f}%)")
        print(f"🔄 Iterations: {state.get('iteration_count', 0)}")
        print(f"📝 Git Commits: {len(state.get('git_commits', []))}")
        
        print("\n📁 Generated Files:")
        try:
            for root, dirs, files in os.walk(self.git.project_dir):
                for file in files:
                    if not file.startswith('.') and file.endswith(('.py', '.html', '.css', '.js', '.md', '.json', '.txt')):
                        rel_path = os.path.relpath(os.path.join(root, file), self.git.project_dir)
                        print(f"   ✅ {rel_path}")
        except:
            print("   📂 Multiple files generated in project directory")
            
        print("\n🚀 Ready for:")
        print("   ✅ Local development testing")
        print("   ✅ Docker deployment")
        print("   ✅ Production deployment")
        print("   ✅ User acceptance testing")
        
        print("\n📖 Next Steps:")
        print("   1. Review DEPLOYMENT_CHECKLIST.md")
        print("   2. Test locally: docker-compose up")
        print("   3. Run tests: pytest backend/tests/")
        print("   4. Deploy to production")
        print("="*80)
    
    def _merge_feature_branches(self):
        """No longer needed - all work happens on main branch"""
        print("✓ All work committed directly to main branch")
    
    def _analyze_project_completion(self) -> str:
        """Analyze the completion status of the project"""
        analysis = []
        
        # Check file counts
        file_counts = {
            "Frontend files": len(list((Path(self.git.project_dir) / "frontend").rglob("*.*"))),
            "Backend files": len(list((Path(self.git.project_dir) / "backend").rglob("*.py"))),
            "Documentation files": len(list((Path(self.git.project_dir) / "docs").rglob("*.md"))),
            "Test files": len(list((Path(self.git.project_dir) / "backend" / "tests").rglob("*.py")))
        }
        
        for category, count in file_counts.items():
            analysis.append(f"{category}: {count}")
        
        return "\n".join(analysis)

# =============================================================================
# FILE OUTPUT UTILITIES
# =============================================================================

def extract_code_blocks(text: str) -> Dict[str, str]:
    """Extract code blocks from markdown text"""
    code_blocks = {}
    
    # Pattern to match code blocks with language
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for language, code in matches:
        if language.lower() in ['html', 'css', 'javascript', 'python', 'sql', 'markdown']:
            if language.lower() not in code_blocks:
                code_blocks[language.lower()] = []
            code_blocks[language.lower()].append(code.strip())
    
    return code_blocks

def save_project_files(final_state: DevelopmentState, project_name: str = "generated_project"):
    """Save all generated code and documentation to files"""
    
    # Create project directory
    project_dir = Path(project_name)
    project_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Creating project structure in: {project_dir.absolute()}")
    
    # Create subdirectories
    (project_dir / "frontend").mkdir(exist_ok=True)
    (project_dir / "backend").mkdir(exist_ok=True)
    (project_dir / "docs").mkdir(exist_ok=True)
    (project_dir / "tests").mkdir(exist_ok=True)
    
    saved_files = []
    
    # Save UI code
    if final_state.get("ui_code"):
        ui_blocks = extract_code_blocks(final_state["ui_code"])
        
        if "html" in ui_blocks:
            for i, html in enumerate(ui_blocks["html"]):
                filename = "index.html" if i == 0 else f"page_{i+1}.html"
                file_path = project_dir / "frontend" / filename
                file_path.write_text(html, encoding='utf-8')
                saved_files.append(str(file_path))
        
        if "css" in ui_blocks:
            for i, css in enumerate(ui_blocks["css"]):
                filename = "styles.css" if i == 0 else f"styles_{i+1}.css"
                file_path = project_dir / "frontend" / filename
                file_path.write_text(css, encoding='utf-8')
                saved_files.append(str(file_path))
        
        if "javascript" in ui_blocks:
            for i, js in enumerate(ui_blocks["javascript"]):
                filename = "script.js" if i == 0 else f"script_{i+1}.js"
                file_path = project_dir / "frontend" / filename
                file_path.write_text(js, encoding='utf-8')
                saved_files.append(str(file_path))
    
    # Save Backend code
    if final_state.get("backend_code"):
        backend_blocks = extract_code_blocks(final_state["backend_code"])
        
        if "python" in backend_blocks:
            for i, python_code in enumerate(backend_blocks["python"]):
                filename = "main.py" if i == 0 else f"module_{i+1}.py"
                file_path = project_dir / "backend" / filename
                file_path.write_text(python_code, encoding='utf-8')
                saved_files.append(str(file_path))
        
        if "sql" in backend_blocks:
            for i, sql in enumerate(backend_blocks["sql"]):
                filename = "schema.sql" if i == 0 else f"schema_{i+1}.sql"
                file_path = project_dir / "backend" / filename
                file_path.write_text(sql, encoding='utf-8')
                saved_files.append(str(file_path))
    
    # Save Documentation
    if final_state.get("documentation"):
        doc_blocks = extract_code_blocks(final_state["documentation"])
        
        # Save README
        if "markdown" in doc_blocks:
            readme_content = doc_blocks["markdown"][0] if doc_blocks["markdown"] else final_state["documentation"]
        else:
            readme_content = final_state["documentation"]
        
        readme_path = project_dir / "README.md"
        readme_path.write_text(readme_content, encoding='utf-8')
        saved_files.append(str(readme_path))
        
        # Save full documentation
        docs_path = project_dir / "docs" / "documentation.md"
        docs_path.write_text(final_state["documentation"], encoding='utf-8')
        saved_files.append(str(docs_path))
    
    # Save Requirements
    if final_state.get("requirements"):
        req_path = project_dir / "docs" / "requirements.md"
        req_path.write_text(final_state["requirements"], encoding='utf-8')
        saved_files.append(str(req_path))
    
    # Save Test Results
    if final_state.get("test_results"):
        test_blocks = extract_code_blocks(final_state["test_results"])
        
        if "python" in test_blocks:
            for i, test_code in enumerate(test_blocks["python"]):
                filename = "test_main.py" if i == 0 else f"test_{i+1}.py"
                file_path = project_dir / "tests" / filename
                file_path.write_text(test_code, encoding='utf-8')
                saved_files.append(str(file_path))
        
        # Save full test report
        test_report_path = project_dir / "docs" / "test_report.md"
        test_report_path.write_text(final_state["test_results"], encoding='utf-8')
        saved_files.append(str(test_report_path))
    
    # Save Project Status
    if final_state.get("project_status"):
        status_path = project_dir / "docs" / "project_status.md"
        status_path.write_text(final_state["project_status"], encoding='utf-8')
        saved_files.append(str(status_path))
    
    # Create package.json if we have frontend code
    if final_state.get("ui_code"):
        package_json = {
            "name": project_name.replace("_", "-"),
            "version": "1.0.0",
            "description": "Generated by AI Development Team",
            "main": "frontend/index.html",
            "scripts": {
                "start": "python -m http.server 8000 --directory frontend",
                "dev": "python -m http.server 8000 --directory frontend"
            }
        }
        
        import json
        package_path = project_dir / "package.json"
        package_path.write_text(json.dumps(package_json, indent=2), encoding='utf-8')
        saved_files.append(str(package_path))
    
    # Create requirements.txt for Python dependencies
    if final_state.get("backend_code"):
        requirements_txt = """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
python-multipart==0.0.6
"""
        req_txt_path = project_dir / "requirements.txt"
        req_txt_path.write_text(requirements_txt, encoding='utf-8')
        saved_files.append(str(req_txt_path))
    
    return saved_files, project_dir

# =============================================================================
# WORKFLOW ORCHESTRATION
# =============================================================================

def task_coordinator_routing(state: DevelopmentState) -> str:
    """Routing function for conditional edges - decides which agent should work next"""
    tasks = state.get('tasks', [])
    
    # Check if all tasks are completed
    remaining_tasks = [t for t in tasks if t['status'] != 'completed']
    if not remaining_tasks:
        print("🎉 All tasks completed! Moving to final documentation and QA.")
        return "project_manager"
    
    # Count remaining tasks by type
    task_counts = {'backend': 0, 'frontend': 0, 'documentation': 0, 'testing': 0}
    for task in remaining_tasks:
        task_labels = [label.lower() for label in task['labels']]
        if any(label in ['backend', 'api', 'database'] for label in task_labels):
            task_counts['backend'] += 1
        elif any(label in ['frontend', 'ui', 'ux'] for label in task_labels):
            task_counts['frontend'] += 1
        elif any(label in ['documentation', 'docs'] for label in task_labels):
            task_counts['documentation'] += 1
        elif any(label in ['testing', 'qa'] for label in task_labels):
            task_counts['testing'] += 1
    
    print(f"📊 Task Status - Backend: {task_counts['backend']}, Frontend: {task_counts['frontend']}, Docs: {task_counts['documentation']}, Testing: {task_counts['testing']}")
    
    # Prioritize backend first (API should be built before frontend)
    if task_counts['backend'] > 0:
        return "backend_developer"
    
    # Then frontend tasks  
    if task_counts['frontend'] > 0:
        return "ui_developer"
    
    # Then documentation tasks
    if task_counts['documentation'] > 0:
        return "documentation"
    
    # Finally testing tasks
    if task_counts['testing'] > 0:
        return "qa_tester"
    
    # If no specific tasks, go to project manager
    return "project_manager"

def task_coordinator(state: DevelopmentState) -> DevelopmentState:
    """Node function for task coordination - updates state and passes through"""
    # This function just passes through the state - routing is handled by task_coordinator_routing
    return state

def create_development_workflow(git_manager: GitManager):
    """Creates the task-driven LangGraph workflow for the development team"""
    
    # Initialize QA manager first (needed by architect)
    qa_manager = QualityAssuranceManager(git_manager)
    
    # Initialize agents with Git integration
    pm_agent = ProductManagerAgent(git_manager)
    architect_agent = ArchitectAgent(general_llm, git_manager, qa_manager)  
    ui_agent = UICoderAgent(git_manager)
    backend_agent = BackendCoderAgent(git_manager)
    doc_agent = DocumentationAgent(git_manager)
    qa_agent = QATesterAgent(git_manager)
    proj_mgr = ProjectManagerAgent(git_manager)
    
    # Create workflow graph
    workflow = StateGraph(DevelopmentState)
    
    # Add nodes (agents)
    workflow.add_node("product_manager", pm_agent.analyze_project)
    workflow.add_node("architect", architect_agent.design_architecture)
    workflow.add_node("task_enhancement", architect_agent.enhance_tasks_with_technical_details)
    workflow.add_node("task_coordinator", task_coordinator)
    workflow.add_node("ui_developer", ui_agent.create_ui)
    workflow.add_node("backend_developer", backend_agent.create_backend)
    workflow.add_node("documentation", doc_agent.create_documentation)
    workflow.add_node("qa_tester", qa_agent.test_code)
    workflow.add_node("project_manager", proj_mgr.coordinate_team)
    
    # Define workflow edges for task-driven development
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "architect")          # Architect defines tech stack after requirements
    workflow.add_edge("architect", "task_enhancement")         # Architect enhances tasks with technical details
    workflow.add_edge("task_enhancement", "task_coordinator")  # Start task coordination after enhancement
    
    # Task coordinator decides which agent works next
    workflow.add_conditional_edges(
        "task_coordinator",
        task_coordinator_routing,
        {
            "backend_developer": "backend_developer",
            "ui_developer": "ui_developer", 
            "documentation": "documentation",
            "qa_tester": "qa_tester",
            "project_manager": "project_manager"
        }
    )
    
    # After each agent completes a task, go back to coordinator (except project manager)
    workflow.add_edge("backend_developer", "task_coordinator")
    workflow.add_edge("ui_developer", "task_coordinator")  
    workflow.add_edge("documentation", "task_coordinator")
    workflow.add_edge("qa_tester", "task_coordinator")
    workflow.add_edge("project_manager", END)
    
    # Add memory for state persistence
    memory = MemorySaver()
    
    # Add memory for state persistence
    return workflow.compile(checkpointer=memory)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_development_project(project_brief: str, project_name: str = "src", create_github_repo: bool = True):
    """Run a complete development project with the agile team"""
    
    print("🚀 Starting Agile Development Project")
    print("=" * 60)
    
    # Create project directory within existing Git repository (use absolute path to avoid nesting)
    project_dir = Path.cwd() / project_name
    
    # Create directory structure without initializing new Git repo
    project_dir.mkdir(exist_ok=True)
    
    # Create directory structure
    directories = [
        "docs/prd",
        "docs/architecture", 
        "docs/api",
        "docs/reviews",
        "docs/qa",
        "frontend/src",
        "frontend/assets",
        "backend/src/domain",
        "backend/src/application",
        "backend/src/infrastructure",
        "backend/tests/unit",
        "backend/tests/integration",
        ".github/ISSUE_TEMPLATE"
    ]
    
    for dir_path in directories:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Use existing Git repository instead of creating new one
    git_manager = GitManager(Path.cwd())  # Use parent directory (existing repo)
    git_manager.project_dir = project_dir  # But write files to src subdirectory
    
    print(f"📁 Project created at: {project_dir.absolute()}")
    
    # Working within existing Git repository
    print("📝 Using existing Git repository for commits")
    
    # Check for GPU acceleration
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            gpu_info = result.stdout.strip()
            print(f"🎮 GPU Detected: {gpu_info}")
            print("⚡ GPU acceleration enabled for faster inference!")
        else:
            print("💻 Running on CPU (install NVIDIA drivers for GPU acceleration)")
    except:
        print("💻 Running on CPU mode")
    
    print("=" * 60)
    
    # Initialize state with Git integration and quality assurance
    initial_state = DevelopmentState(
        project_brief=project_brief,
        project_dir=str(project_dir),
        requirements="",
        architecture="",
        tasks=[],
        current_task=None,
        completed_tasks=[],
        available_agents=["backend", "frontend", "documentation", "testing"],
        ui_code="",
        backend_code="",
        documentation="",
        test_results="",
        project_status="",
        iteration_count=0,
        feedback=[],
        git_commits=[],
        agent_reviews={},
        quality_gates_passed={},
        revision_requests=[],
        max_revisions=2
    )
    
    # Create and run workflow with Git manager
    app = create_development_workflow(git_manager)
    
    try:
        # Execute the workflow with timing
        start_time = time.time()
        config = {
            "configurable": {"thread_id": "dev-project-1"},
            "recursion_limit": 100  # Increase limit for iterative task processing
        }
        final_state = app.invoke(initial_state, config)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 PROJECT COMPLETED!")
        print("=" * 60)
        
        # Print summary
        print(f"\n📊 Final Status:")
        print(f"⏱️  Total Execution Time: {execution_time:.1f} seconds")
        print(f"🔄 Iterations: {final_state['iteration_count']}")
        print(f"📝 Team Feedback: {len(final_state['feedback'])} updates")
        print(f"📋 Git Commits: {len(final_state['git_commits'])} commits")
        
        print(f"\n🗂️ Git Repository Structure:")
        for commit in final_state['git_commits']:
            print(f"  📝 {commit}")
        
        # Repository Summary
        print(f"\n📁 Local project completed at: {project_dir.absolute()}")
        if create_github_repo:
            print(f"🔗 GitHub repository: https://github.com/daz2d/todo-app")
            print(f"📂 Project files pushed to: ai_generated_project/ directory")
            
        # Quality Assurance Summary
        print(f"\n🎯 Quality Assurance Summary:")
        for agent_name, reviews in final_state.get('agent_reviews', {}).items():
            quality_score = reviews['self_review']['quality_score']
            revisions_count = len(reviews['revisions'])
            peer_reviews_count = len(reviews['peer_reviews'])
            gate_passed = final_state.get('quality_gates_passed', {}).get(agent_name, False)
            
            status_icon = "✅" if gate_passed else "⚠️"
            print(f"  {status_icon} {agent_name}: Quality {quality_score}/10, {revisions_count} revisions, {peer_reviews_count} peer reviews")
        
        total_revisions = sum(len(reviews['revisions']) for reviews in final_state.get('agent_reviews', {}).values())
        total_reviews = sum(len(reviews['peer_reviews']) for reviews in final_state.get('agent_reviews', {}).values())
        
        print(f"\n📊 Quality Metrics:")
        print(f"  🔄 Total Revisions: {total_revisions}")
        print(f"  👥 Total Peer Reviews: {total_reviews}")
        print(f"  ✅ Quality Gates Passed: {sum(final_state.get('quality_gates_passed', {}).values())}/{len(final_state.get('quality_gates_passed', {}))}")
        print(f"  📋 Review Documentation: Check docs/reviews/ folder")
        
        print(f"\n📋 Deliverables Created:")
        print(f"✓ Requirements Document: {len(final_state['requirements'])} chars")
        print(f"✓ UI Code: {len(final_state['ui_code'])} chars")
        print(f"✓ Backend Code: {len(final_state['backend_code'])} chars")
        print(f"✓ Documentation: {len(final_state['documentation'])} chars")
        print(f"✓ Test Results: {len(final_state['test_results'])} chars")
        
        # Display all the generated content
        print("\n" + "="*80)
        print("📋 PRODUCT MANAGER - REQUIREMENTS")
        print("="*80)
        print(final_state['requirements'])
        
        print("\n" + "="*80)
        print("🎨 UI DEVELOPER - FRONTEND CODE")
        print("="*80)
        print(final_state['ui_code'])
        
        print("\n" + "="*80)
        print("⚙️ BACKEND DEVELOPER - SERVER CODE")
        print("="*80)
        print(final_state['backend_code'])
        
        print("\n" + "="*80)
        print("📚 DOCUMENTATION AGENT - PROJECT DOCS")
        print("="*80)
        print(final_state['documentation'])
        
        print("\n" + "="*80)
        print("🧪 QA TESTER - TEST RESULTS")
        print("="*80)
        print(final_state['test_results'])
        
        print("\n" + "="*80)
        print("👔 PROJECT MANAGER - FINAL STATUS")
        print("="*80)
        print(final_state['project_status'])
        
        # Save all files to project directory
        print("\n" + "="*80)
        print("💾 SAVING PROJECT FILES")
        print("="*80)
        
        saved_files, project_dir = save_project_files(final_state, "generated_project")
        
        print(f"\n💾 Files Saved ({len(saved_files)} files):")
        for file_path in saved_files:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            print(f"  📄 {os.path.basename(file_path)} ({file_size:,} bytes)")
        
        print(f"\n�️ Git Repository: {project_dir.absolute()}")
        print(f"📋 Git History: git log --oneline")
        print(f"🌿 Branches created during development")
        
        print(f"\n🚀 To run the project:")
        print(f"   📁 Navigate: cd {project_dir}")
        print(f"   🎨 Frontend: python -m http.server 8000 --directory frontend")
        print(f"   ⚙️  Backend:  cd backend && pip install -r requirements.txt && python main.py")
        print(f"   📚 Documentation: Check README.md and docs/ folder")
        print(f"   🔍 Git Status: git status && git log --oneline")
        
        return final_state
        
    except Exception as e:
        print(f"❌ Project Error: {e}")
        return None

if __name__ == "__main__":
    # Example project
    project_brief = """
    Create a Task Management Web Application with the following features:
    - User registration and authentication
    - Create, edit, and delete tasks
    - Mark tasks as complete/incomplete
    - Filter tasks by status (all, pending, completed)
    - Due date tracking with notifications
    - Simple, clean UI that works on mobile and desktop
    - RESTful API for all operations
    - Data persistence in a database
    
    Target users are individuals and small teams who need a simple way to track their daily tasks.
    The app should be intuitive and fast to use.
    """
    
    print("Testing connection to Ollama...")
    try:
        # Test both models
        print("Testing Mistral model...")
        test_mistral = ChatOllama(model="mistral", temperature=0)
        mistral_response = test_mistral.invoke("Hello")
        print(f"✓ Mistral connected successfully!")
        
        print("Testing CodeLlama model...")
        test_codellama = ChatOllama(model="codellama", temperature=0)
        codellama_response = test_codellama.invoke("Hello")
        print(f"✓ CodeLlama connected successfully!")
        
        print(f"✓ Both models ready for development team!")
        
        print("\n🏁 Starting Development Project...")
        final_result = run_development_project(project_brief)
        
        if final_result:
            print("\n📁 All project artifacts have been generated!")
            print("Check the output above for complete code, documentation, and test results.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Ollama is installed and running")
        print("2. Pull required models:")
        print("   - ollama pull mistral")
        print("   - ollama pull codellama")
        print("3. Check available models: ollama list")
        print("4. Start Ollama service: ollama serve")
