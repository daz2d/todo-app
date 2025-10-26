"""
Roles and Prompt Loading

Utilities for loading system prompts and policy documents.
"""

from pathlib import Path
from typing import Dict, Optional


class RolePrompts:
    """Manages loading and access to role-specific prompts."""
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize role prompts loader.
        
        Args:
            prompts_dir: Path to prompts directory. Defaults to ../prompts relative to this file.
        """
        if prompts_dir is None:
            self.prompts_dir = Path(__file__).parent.parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self.system_dir = self.prompts_dir / "system"
        self.policies_dir = self.prompts_dir / "policies"
        
        # Cache loaded prompts
        self._cache: Dict[str, str] = {}
    
    def _load_file(self, file_path: Path) -> str:
        """Load content from file with caching."""
        cache_key = str(file_path)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {file_path}\n"
                f"Expected location based on prompts directory: {self.prompts_dir}"
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._cache[cache_key] = content
        return content
    
    # System Prompts (Agent Roles)
    
    def get_pm_prompt(self) -> str:
        """Get Product Manager system prompt."""
        return self._load_file(self.system_dir / "pm.md")
    
    def get_backend_prompt(self) -> str:
        """Get Staff Backend Engineer system prompt."""
        return self._load_file(self.system_dir / "staff_backend.md")
    
    def get_frontend_prompt(self) -> str:
        """Get Staff Frontend Engineer system prompt."""
        return self._load_file(self.system_dir / "staff_frontend.md")
    
    def get_reviewer_prompt(self) -> str:
        """Get Code Reviewer system prompt."""
        return self._load_file(self.system_dir / "reviewer.md")
    
    def get_qa_tester_prompt(self) -> str:
        """Get QA Tester system prompt."""
        return self._load_file(self.system_dir / "qa_tester.md")
    
    # Policy Documents
    
    def get_safety_policy(self) -> str:
        """Get safety guardrails and security policy."""
        return self._load_file(self.policies_dir / "safety.md")
    
    def get_dos_and_donts(self) -> str:
        """Get team norms and best practices."""
        return self._load_file(self.policies_dir / "dos_and_donts.md")
    
    def get_definition_of_done(self) -> str:
        """Get Definition of Done criteria."""
        return self._load_file(self.policies_dir / "definition_of_done.md")
    
    # Combined Prompts
    
    def get_full_prompt(self, role: str) -> str:
        """
        Get complete prompt for a role (system prompt + policies).
        
        Args:
            role: Role name ('pm', 'backend', 'frontend', 'reviewer').
        
        Returns:
            Combined prompt with system instructions and policies.
        
        Raises:
            ValueError: If role is not recognized.
        """
        role = role.lower().strip()
        
        # Get role-specific system prompt
        if role == 'pm':
            system_prompt = self.get_pm_prompt()
        elif role in ('backend', 'be'):
            system_prompt = self.get_backend_prompt()
        elif role in ('frontend', 'fe'):
            system_prompt = self.get_frontend_prompt()
        elif role in ('reviewer', 'review'):
            system_prompt = self.get_reviewer_prompt()
        elif role in ('qa', 'qa_tester', 'tester'):
            system_prompt = self.get_qa_tester_prompt()
        else:
            raise ValueError(
                f"Unknown role: '{role}'. "
                f"Valid roles: 'pm', 'backend', 'frontend', 'reviewer', 'qa_tester'"
            )
        
        # Combine with policies
        safety = self.get_safety_policy()
        dos_and_donts = self.get_dos_and_donts()
        dod = self.get_definition_of_done()
        
        combined = f"""
{system_prompt}

---

# SAFETY POLICY

{safety}

---

# TEAM NORMS

{dos_and_donts}

---

# DEFINITION OF DONE

{dod}
"""
        
        return combined.strip()
    
    def get_all_prompts(self) -> Dict[str, str]:
        """
        Get all prompts as a dictionary.
        
        Returns:
            Dictionary with keys: 'pm', 'backend', 'frontend', 'reviewer',
            'safety', 'dos_and_donts', 'definition_of_done'.
        """
        return {
            'pm': self.get_pm_prompt(),
            'backend': self.get_backend_prompt(),
            'frontend': self.get_frontend_prompt(),
            'reviewer': self.get_reviewer_prompt(),
            'qa_tester': self.get_qa_tester_prompt(),
            'safety': self.get_safety_policy(),
            'dos_and_donts': self.get_dos_and_donts(),
            'definition_of_done': self.get_definition_of_done()
        }
    
    def clear_cache(self):
        """Clear the prompt cache (useful if files are modified)."""
        self._cache.clear()


# Convenience function
def load_role_prompt(role: str, prompts_dir: Optional[Path] = None) -> str:
    """
    Load complete prompt for a role.
    
    Args:
        role: Role name ('pm', 'backend', 'frontend', 'reviewer').
        prompts_dir: Optional custom prompts directory.
    
    Returns:
        Complete prompt including system instructions and policies.
    
    Examples:
        >>> pm_prompt = load_role_prompt('pm')
        >>> print(f"PM prompt length: {len(pm_prompt)} chars")
    """
    loader = RolePrompts(prompts_dir)
    return loader.get_full_prompt(role)


# Extensibility: To add new roles:
# 1. Create prompts/system/<role_name>.md
# 2. Add get_<role_name>_prompt() method to RolePrompts
# 3. Update get_full_prompt() to handle new role
# 4. Update get_all_prompts() dictionary
#
# Example:
#     def get_qa_prompt(self) -> str:
#         """Get QA Engineer system prompt."""
#         return self._load_file(self.system_dir / "qa_engineer.md")
