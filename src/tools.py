"""
Agent Tools

Provides HTTP, shell, and git tools with safety constraints.
All tools include guardrails, logging, and error handling.
"""

import os
import re
import subprocess
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool


# Configuration from environment
SANDBOX_DIR = Path(os.getenv('SANDBOX_DIR', './sandbox')).resolve()
MAX_SHELL_CMDS_PER_TURN = int(os.getenv('MAX_SHELL_CMDS_PER_TURN', '5'))
HTTP_TIMEOUT_SECONDS = int(os.getenv('HTTP_TIMEOUT_SECONDS', '30'))
ALLOW_SHELL = os.getenv('ALLOW_SHELL', 'true').lower() == 'true'
ALLOW_HTTP = os.getenv('ALLOW_HTTP', 'true').lower() == 'true'
ALLOW_GIT = os.getenv('ALLOW_GIT', 'true').lower() == 'true'
REDACT_SECRETS = os.getenv('REDACT_SECRETS', 'true').lower() == 'true'

# Blocked shell patterns (safety)
BLOCKED_PATTERNS = [
    r'rm\s+-rf',
    r'sudo\s+',
    r'su\s+',
    r'chmod\s+-R',
    r'chown\s+-R',
    r'dd\s+if=',
    r'mkfs',
    r'>/dev/',
    r':\(\)\{',  # Fork bomb
    r'del\s+/f\s+/s\s+/q',
    r'format\s+',
    r'systemctl',
    r'service\s+',
]

# Secret patterns for redaction
SECRET_PATTERNS = [
    r'(api[_-]?key\s*[=:]\s*["\']?)([a-zA-Z0-9_-]+)',
    r'(token\s*[=:]\s*["\']?)([a-zA-Z0-9_-]+)',
    r'(password\s*[=:]\s*["\']?)([^\s"\']+)',
    r'(secret\s*[=:]\s*["\']?)([a-zA-Z0-9_-]+)',
    r'(bearer\s+)([a-zA-Z0-9_-]+)',
]

# Global state (per turn command counter)
_shell_command_count = 0


def reset_turn_counters():
    """Reset per-turn counters (call at start of each agent turn)."""
    global _shell_command_count
    _shell_command_count = 0


def redact_secrets(text: str) -> str:
    """
    Redact sensitive information from text.
    
    Args:
        text: Input text potentially containing secrets.
    
    Returns:
        Text with secrets replaced by [REDACTED] or partial display.
    """
    if not REDACT_SECRETS:
        return text
    
    result = text
    for pattern in SECRET_PATTERNS:
        result = re.sub(pattern, r'\1[REDACTED]', result, flags=re.IGNORECASE)
    
    return result


def is_command_blocked(command: str) -> tuple[bool, Optional[str]]:
    """
    Check if shell command matches blocked patterns.
    
    Args:
        command: Shell command to validate.
    
    Returns:
        Tuple of (is_blocked, reason). If blocked, reason explains why.
    """
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, f"Blocked pattern detected: '{pattern}'"
    
    return False, None


# HTTP Tools

@tool
def http_get(url: str) -> str:
    """
    Perform HTTP GET request.
    
    Args:
        url: URL to fetch (must start with http:// or https://).
    
    Returns:
        Response content (JSON pretty-printed if applicable, otherwise text).
        Returns error message if request fails.
    
    Examples:
        http_get("https://api.github.com/repos/langchain-ai/langgraph")
        → Returns repo information as formatted JSON
    """
    if not ALLOW_HTTP:
        return "❌ HTTP tools are disabled (ALLOW_HTTP=false in config)"
    
    try:
        if not url.startswith(('http://', 'https://')):
            return f"❌ Invalid URL: '{url}'. Must start with http:// or https://"
        
        headers = {
            'User-Agent': 'LangTeam/1.0',
            'Accept': 'application/json,text/html,*/*'
        }
        
        response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
        
        # Try to parse as JSON
        try:
            data = response.json()
            formatted = json.dumps(data, indent=2)
            
            # Truncate if too large
            if len(formatted) > 50000:
                return formatted[:50000] + "\n\n... (truncated, response too large)"
            
            return redact_secrets(formatted)
        
        except json.JSONDecodeError:
            # Return as text
            text = response.text
            if len(text) > 50000:
                return text[:50000] + "\n\n... (truncated, response too large)"
            
            return redact_secrets(text)
    
    except requests.Timeout:
        return f"❌ Request timed out after {HTTP_TIMEOUT_SECONDS}s"
    
    except requests.RequestException as e:
        return f"❌ HTTP GET failed: {e}"


@tool
def http_post(url: str, json_body: Dict[str, Any]) -> str:
    """
    Perform HTTP POST request with JSON body.
    
    Args:
        url: URL to post to (must start with http:// or https://).
        json_body: Dictionary to send as JSON payload.
    
    Returns:
        Response content (JSON pretty-printed if applicable).
        Returns error message if request fails.
    
    Examples:
        http_post("https://api.example.com/items", {"name": "Item1", "value": 42})
        → Posts data and returns server response
    """
    if not ALLOW_HTTP:
        return "❌ HTTP tools are disabled (ALLOW_HTTP=false in config)"
    
    try:
        if not url.startswith(('http://', 'https://')):
            return f"❌ Invalid URL: '{url}'. Must start with http:// or https://"
        
        headers = {
            'User-Agent': 'LangTeam/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            url,
            json=json_body,
            headers=headers,
            timeout=HTTP_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        
        # Try to parse response as JSON
        try:
            data = response.json()
            formatted = json.dumps(data, indent=2)
            
            if len(formatted) > 50000:
                return formatted[:50000] + "\n\n... (truncated, response too large)"
            
            return redact_secrets(formatted)
        
        except json.JSONDecodeError:
            text = response.text
            if len(text) > 50000:
                return text[:50000] + "\n\n... (truncated, response too large)"
            
            return redact_secrets(text)
    
    except requests.Timeout:
        return f"❌ Request timed out after {HTTP_TIMEOUT_SECONDS}s"
    
    except requests.RequestException as e:
        return f"❌ HTTP POST failed: {e}"


# Shell Tool

@tool
def shell(cmd: str) -> str:
    """
    Execute shell command in current directory (project directory).
    
    Args:
        cmd: Command to execute (runs in current working directory).
    
    Returns:
        Combined stdout and stderr output.
        Returns error message if command is blocked or fails.
    
    Safety:
        - Commands run in current project directory
        - Destructive patterns are blocked (rm -rf, sudo, etc.)
        - Per-turn command limit enforced
        - 30-second timeout per command
    
    Examples:
        shell("python src/main.py")
        → Runs the application
        
        shell("pytest tests/")
        → Runs tests
    """
    global _shell_command_count
    
    if not ALLOW_SHELL:
        return "❌ Shell commands are disabled (ALLOW_SHELL=false in config)"
    
    # Check turn limit
    if _shell_command_count >= MAX_SHELL_CMDS_PER_TURN:
        return (
            f"❌ Shell command limit exceeded ({MAX_SHELL_CMDS_PER_TURN} per turn). "
            f"Increase MAX_SHELL_CMDS_PER_TURN in .env if needed."
        )
    
    # Check blocked patterns
    is_blocked, reason = is_command_blocked(cmd)
    if is_blocked:
        return (
            f"❌ Command blocked for safety: {reason}\n"
            f"Command: {cmd}\n"
            f"Review prompts/policies/safety.md for allowed patterns."
        )
    
    try:
        # Execute in current directory (project directory)
        result = subprocess.run(
            cmd,
            cwd=Path.cwd(),  # Run in current directory, not sandbox
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Increment counter
        _shell_command_count += 1
        
        # Combine stdout and stderr
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += "\n" + result.stderr if output else result.stderr
        
        # Add exit code if non-zero
        if result.returncode != 0:
            output += f"\n\n[Exit code: {result.returncode}]"
        
        # Truncate if too large
        if len(output) > 10000:
            output = output[:10000] + "\n\n... (truncated, output too large)"
        
        return redact_secrets(output) if output else "[Command completed with no output]"
    
    except subprocess.TimeoutExpired:
        _shell_command_count += 1
        return "❌ Command timed out after 30 seconds"
    
    except Exception as e:
        _shell_command_count += 1
        return f"❌ Command execution failed: {e}"


# Git Tool

@tool
def git(message: str) -> str:
    """
    Stage all changes and commit with provided message.
    
    Args:
        message: Commit message (will be prefixed with [LangTeam]).
    
    Returns:
        Success message with commit hash, or error message.
    
    Examples:
        git("Implement core functionality with validation")
        → Returns: "Committed: [LangTeam] Implement core functionality with validation (abc1234)"
    """
    if not ALLOW_GIT:
        return "❌ Git operations are disabled (ALLOW_GIT=false in config)"
    
    if not message or not message.strip():
        return "❌ Commit message cannot be empty"
    
    # Prefix message for traceability
    full_message = f"[LangTeam] {message.strip()}"
    
    try:
        # Check if in git repository
        check_result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if check_result.returncode != 0:
            return (
                "❌ Not a git repository. Initialize with: git init\n"
                f"Working directory: {SANDBOX_DIR}"
            )
        
        # Stage all changes
        add_result = subprocess.run(
            ["git", "add", "-A"],
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if add_result.returncode != 0:
            return f"❌ Git add failed: {add_result.stderr}"
        
        # Commit
        commit_result = subprocess.run(
            ["git", "commit", "-m", full_message],
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if commit_result.returncode != 0:
            # Check if it's "nothing to commit"
            if "nothing to commit" in commit_result.stdout.lower():
                return "ℹ️  No changes to commit (working tree clean)"
            return f"❌ Git commit failed: {commit_result.stderr or commit_result.stdout}"
        
        # Extract commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
        
        return f"✅ Committed: {full_message} ({commit_hash})"
    
    except subprocess.TimeoutExpired:
        return "❌ Git operation timed out"
    
    except Exception as e:
        return f"❌ Git operation failed: {e}"


# File System Tools

@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file (creates directories if needed).
    
    Args:
        file_path: Path to file (relative to current directory, e.g., 'src/main.py')
        content: File content to write
    
    Returns:
        Success message with file path, or error message.
    
    Examples:
        write_file("hello.py", "print('Hello World')")
        → Creates hello.py with the given content
        
        write_file("src/app.py", "def main():\\n    pass")
        → Creates src directory and app.py file
    """
    try:
        # Get current working directory (should be project directory)
        file_path = Path(file_path)
        
        # Security: Prevent path traversal
        resolved = file_path.resolve()
        cwd = Path.cwd().resolve()
        
        if not str(resolved).startswith(str(cwd)):
            return f"❌ Path traversal detected. Files must be in current directory or subdirectories. Got: {file_path}"
        
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        file_path.write_text(content, encoding='utf-8')
        
        return f"✓ File created: {file_path} ({len(content)} bytes)"
    
    except Exception as e:
        return f"❌ Failed to write file: {e}"


@tool
def read_file(file_path: str) -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to file (relative to current directory)
    
    Returns:
        File content, or error message.
    
    Examples:
        read_file("README.md")
        → Returns the content of README.md
    """
    try:
        file_path = Path(file_path)
        
        # Security: Prevent path traversal
        resolved = file_path.resolve()
        cwd = Path.cwd().resolve()
        
        if not str(resolved).startswith(str(cwd)):
            return f"❌ Path traversal detected. Files must be in current directory or subdirectories."
        
        if not file_path.exists():
            return f"❌ File not found: {file_path}"
        
        content = file_path.read_text(encoding='utf-8')
        
        # Truncate very large files
        if len(content) > 50000:
            return content[:50000] + f"\n\n... (truncated, file is {len(content)} bytes)"
        
        return content
    
    except Exception as e:
        return f"❌ Failed to read file: {e}"


@tool
def list_files(directory: str = ".") -> str:
    """
    List files and directories in a directory.
    
    Args:
        directory: Directory path (default: current directory)
    
    Returns:
        List of files and directories, or error message.
    
    Examples:
        list_files(".")
        → Lists files in current directory
        
        list_files("src")
        → Lists files in src directory
    """
    try:
        dir_path = Path(directory)
        
        # Security: Prevent path traversal
        resolved = dir_path.resolve()
        cwd = Path.cwd().resolve()
        
        if not str(resolved).startswith(str(cwd)):
            return f"❌ Path traversal detected."
        
        if not dir_path.exists():
            return f"❌ Directory not found: {directory}"
        
        if not dir_path.is_dir():
            return f"❌ Not a directory: {directory}"
        
        items = []
        for item in sorted(dir_path.iterdir()):
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"📄 {item.name} ({size} bytes)")
        
        if not items:
            return f"Directory is empty: {directory}"
        
        return "\n".join(items)
    
    except Exception as e:
        return f"❌ Failed to list directory: {e}"


# Tool list for easy binding
ALL_TOOLS = [http_get, http_post, shell, git, write_file, read_file, list_files]


def get_enabled_tools() -> List:
    """
    Get list of enabled tools based on configuration.
    
    Returns:
        List of tool functions that are currently enabled.
    """
    tools = []
    
    if ALLOW_HTTP:
        tools.extend([http_get, http_post])
    
    if ALLOW_SHELL:
        tools.append(shell)
    
    if ALLOW_GIT:
        tools.append(git)
    
    # File system tools are always enabled (with path traversal protection)
    tools.extend([write_file, read_file, list_files])
    
    return tools


# Extensibility: Add new tools by implementing them as @tool decorated functions
# Example structure:
#
# @tool
# def your_new_tool(arg1: str, arg2: int) -> str:
#     """
#     Tool description for LLM.
#     
#     Args:
#         arg1: Description of argument
#         arg2: Description of argument
#     
#     Returns:
#         Description of return value
#     """
#     try:
#         # Implementation
#         return "Success message"
#     except Exception as e:
#         return f"❌ Error: {e}"
#
# Then add to ALL_TOOLS and/or get_enabled_tools()
