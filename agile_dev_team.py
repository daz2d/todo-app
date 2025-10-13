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
class DevelopmentState(TypedDict):
    project_brief: str
    project_dir: str
    requirements: str
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
        # Work directly on main branch
        
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
        Based on these requirements, create GitHub issues for development tasks:
        
        {requirements}
        
        Format as GitHub Issues with:
        - Clear, actionable titles
        - Detailed descriptions
        - Acceptance criteria
        - Labels (feature, bug, enhancement, documentation)
        - Estimates (story points)
        
        Create separate issues for:
        1. Frontend development tasks
        2. Backend API development
        3. Database schema
        4. Documentation tasks
        5. Testing tasks
        
        Format each issue as:
        ## Issue: [Title]
        **Labels:** feature, frontend
        **Estimate:** 3 story points
        **Description:** [Detailed description]
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
        
        Requirements from docs/prd/requirements.md: {requirements}
        Backend API Info: {backend_api_info}
        Existing Frontend Files: {existing_frontend_files}
        
        Your task is to:
        1. Create HTML structure with semantic markup
        2. Write CSS for responsive, modern styling
        3. Add JavaScript for interactivity following clean code principles
        4. Ensure accessibility (ARIA labels, semantic HTML)
        5. Make it mobile-responsive
        6. Integrate with backend APIs through adapters (Hexagonal Architecture)
        7. Implement clean, maintainable code with proper separation of concerns
        
        Follow these development guidelines:
        - Write clean, readable code with meaningful names
        - Use small, focused functions with single responsibilities
        - Implement proper error handling and validation
        - Follow Hexagonal Architecture: separate UI from business logic
        - Create adapters for external dependencies (API calls, storage)
        - Keep code DRY but prioritize readability over cleverness
        
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
        # Work directly on main branch
        
        # Read existing project files
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        backend_api_info = self.git.get_file_content("docs/api/api_spec.md")
        
        # Check existing frontend files
        existing_files = self._get_existing_frontend_files()
        
        # Generate UI code based on real project state
        chain = self.prompt | self.llm | StrOutputParser()
        ui_code = chain.invoke({
            "requirements": requirements,
            "backend_api_info": backend_api_info,
            "existing_frontend_files": existing_files
        })
        
        # Extract and write individual files
        self._write_frontend_files(ui_code)
        
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
        """Extract code blocks and write to appropriate files"""
        # Extract HTML
        html_matches = re.findall(r'```html\n(.*?)```', ui_code, re.DOTALL)
        if html_matches:
            self.git.write_file("frontend/index.html", html_matches[0].strip())
        
        # Extract CSS
        css_matches = re.findall(r'```css\n(.*?)```', ui_code, re.DOTALL)
        if css_matches:
            self.git.write_file("frontend/src/styles.css", css_matches[0].strip())
        
        # Extract JavaScript
        js_matches = re.findall(r'```javascript\n(.*?)```', ui_code, re.DOTALL)
        if js_matches:
            self.git.write_file("frontend/src/app.js", js_matches[0].strip())
    
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
        
        Requirements from docs/prd/requirements.md: {requirements}
        Frontend Files Summary: {frontend_summary}
        Existing Backend Structure: {existing_backend}
        
        Your task is to:
        1. Design RESTful API endpoints following Domain Driven Design
        2. Implement Hexagonal Architecture (Ports and Adapters pattern)
        3. Create clean, well-structured server-side logic (Python/FastAPI)
        4. Design database schema aligned with domain model
        5. Implement comprehensive error handling and validation
        6. Add authentication and security best practices
        7. Structure code for testability and maintainability
        
        Follow these architectural guidelines:
        - Implement Hexagonal Architecture with clear ports and adapters
        - Separate domain logic from infrastructure concerns
        - Create domain entities, repositories, and services
        - Use dependency injection for testability
        - Follow clean code principles: meaningful names, small functions, single responsibility
        - Design for Domain Driven Design: bounded contexts, aggregates, domain services
        - Structure code to support Test Driven Development (TDD)
        - Keep business logic independent of frameworks and databases
        
        Create robust, scalable, and maintainable backend code.
        
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
        # Work directly on main branch
        
        # Read project context
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        frontend_summary = self._get_frontend_summary()
        existing_backend = self._get_existing_backend_structure()
        
        # Generate backend code
        chain = self.prompt | self.llm | StrOutputParser()
        backend_code = chain.invoke({
            "requirements": requirements,
            "frontend_summary": frontend_summary,
            "existing_backend": existing_backend
        })
        
        # Write backend files following Hexagonal Architecture
        self._write_backend_files(backend_code)
        
        # Create API documentation
        self._create_api_documentation(backend_code)
        
        # Create requirements.txt
        self._create_requirements_txt()
        
        # Commit backend code
        self.git.commit_changes("feat: Implement backend API with Hexagonal Architecture", "Backend Developer")
        
        state["backend_code"] = backend_code
        state["feedback"].append("✓ Backend Developer: Server code and APIs created and committed")
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
        """Write backend files following Hexagonal Architecture"""
        print(f"🔍 Backend code length: {len(backend_code)} chars")
        
        # Save the full backend code for debugging
        self.git.write_file("backend/generated_code.md", f"# Generated Backend Code\n\n{backend_code}")
        
        # Extract and write different code blocks
        files_created = 0
        
        # Main FastAPI application
        main_py_matches = re.findall(r'```python\n# main\.py\n(.*?)```', backend_code, re.DOTALL)
        if main_py_matches:
            self.git.write_file("backend/main.py", main_py_matches[0].strip())
            files_created += 1
        else:
            print("⚠️ No main.py found in generated code")
        
        # Domain models
        domain_matches = re.findall(r'```python\n# domain.*?\n(.*?)```', backend_code, re.DOTALL)
        if domain_matches:
            self.git.write_file("backend/src/domain/models.py", domain_matches[0].strip())
            files_created += 1
        else:
            print("⚠️ No domain models found in generated code")
        
        # Application services
        service_matches = re.findall(r'```python\n# .*service.*?\n(.*?)```', backend_code, re.DOTALL)
        if service_matches:
            self.git.write_file("backend/src/application/services.py", service_matches[0].strip())
            files_created += 1
        else:
            print("⚠️ No services found in generated code")
        
        # Infrastructure (database, repositories)
        infra_matches = re.findall(r'```python\n# .*infrastructure.*?\n(.*?)```', backend_code, re.DOTALL)
        if infra_matches:
            self.git.write_file("backend/src/infrastructure/database.py", infra_matches[0].strip())
            files_created += 1
        else:
            print("⚠️ No infrastructure code found in generated code")
        
        # SQL schema
        sql_matches = re.findall(r'```sql\n(.*?)```', backend_code, re.DOTALL)
        if sql_matches:
            self.git.write_file("backend/schema.sql", sql_matches[0].strip())
            files_created += 1
        else:
            print("⚠️ No SQL schema found in generated code")
        
        print(f"📁 Created {files_created} backend files")
    
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
        # Work directly on main branch
        
        # Read actual project files
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        api_spec = self.git.get_file_content("docs/api/api_spec.md")
        project_structure = self._analyze_project_structure()
        
        chain = self.prompt | self.llm | StrOutputParser()
        documentation = chain.invoke({
            "requirements": requirements,
            "ui_code": self._get_frontend_summary(),
            "backend_code": self._get_backend_summary()
        })
        
        # Write comprehensive documentation
        self.git.write_file("README.md", self._extract_readme(documentation))
        self.git.write_file("docs/architecture/overview.md", self._extract_architecture_docs(documentation))
        self.git.write_file("docs/deployment/deployment.md", self._extract_deployment_docs(documentation))
        
        # Commit documentation
        self.git.commit_changes("docs: Add comprehensive project documentation", "Documentation Agent")
        
        state["documentation"] = documentation
        state["feedback"].append("✓ Documentation Agent: Comprehensive docs created and committed")
        state["git_commits"].append("Documentation committed")
        print("📚 Documentation Agent: Complete documentation generated and committed")
        return state
    
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
        # Work directly on main branch
        
        # Read actual project files
        requirements = self.git.get_file_content("docs/prd/requirements.md")
        backend_files = self._get_all_backend_files()
        frontend_files = self._get_all_frontend_files()
        
        # Generate test analysis
        chain = self.prompt | self.llm | StrOutputParser()
        test_results = chain.invoke({
            "requirements": requirements,
            "ui_code": frontend_files,
            "backend_code": backend_files
        })
        
        # Write test files
        self._write_test_files(test_results)
        
        # Create test report
        self.git.write_file("docs/qa/test_report.md", test_results)
        
        # Commit tests
        self.git.commit_changes("test: Add comprehensive test suite and QA analysis", "QA Tester")
        
        state["test_results"] = test_results
        state["feedback"].append("✓ QA Tester: Code reviewed, tested, and test files committed")
        state["git_commits"].append("Test suite and QA analysis committed")
        print("🧪 QA Tester: Testing completed and committed")
        return state
    
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
        
        # Write final project status
        self.git.write_file("docs/project_status.md", project_status)
        self.git.commit_changes("docs: Final project status and coordination report", "Project Manager")
        
        state["project_status"] = project_status
        state["iteration_count"] += 1
        state["git_commits"].append("Final project status committed")
        print("👔 Project Manager: Team coordination and final status completed")
        return state
    
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

def create_development_workflow(git_manager: GitManager):
    """Creates the LangGraph workflow for the development team"""
    
    # Initialize agents with Git integration
    pm_agent = ProductManagerAgent(git_manager)
    ui_agent = UICoderAgent(git_manager)
    backend_agent = BackendCoderAgent(git_manager)
    doc_agent = DocumentationAgent(git_manager)
    qa_agent = QATesterAgent(git_manager)
    proj_mgr = ProjectManagerAgent(git_manager)
    
    # Create workflow graph
    workflow = StateGraph(DevelopmentState)
    
    # Add nodes (agents)
    workflow.add_node("product_manager", pm_agent.analyze_project)
    workflow.add_node("ui_developer", ui_agent.create_ui)
    workflow.add_node("backend_developer", backend_agent.create_backend)
    workflow.add_node("documentation", doc_agent.create_documentation)
    workflow.add_node("qa_tester", qa_agent.test_code)
    workflow.add_node("project_manager", proj_mgr.coordinate_team)
    
    # Define workflow edges (dependencies) - Sequential to avoid concurrent updates
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "backend_developer")  # Backend first (provides API)
    workflow.add_edge("backend_developer", "ui_developer")     # UI second (consumes API)
    workflow.add_edge("ui_developer", "documentation")
    workflow.add_edge("documentation", "qa_tester")
    workflow.add_edge("qa_tester", "project_manager")
    workflow.add_edge("project_manager", END)
    
    # Add memory for state persistence
    memory = MemorySaver()
    
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
        config = {"configurable": {"thread_id": "dev-project-1"}}
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
