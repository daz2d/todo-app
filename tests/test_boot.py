"""
Boot Tests

Verifies that the repository is correctly wired and imports work.
"""

import sys
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all core modules can be imported."""
    try:
        # Core modules
        import src
        import src.llm
        import src.tools
        import src.mcp_bridge
        import src.memory
        import src.roles
        import src.graph
        import src.run_team
        
        print("✅ All imports successful")
        return True
    
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_graph_builder():
    """Test that graph can be built."""
    try:
        from src.graph import create_team_graph
        
        graph = create_team_graph()
        assert graph is not None, "Graph creation returned None"
        assert callable(graph.invoke), "Graph does not have invoke method"
        
        print("✅ Graph builder works")
        return True
    
    except Exception as e:
        print(f"❌ Graph builder failed: {e}")
        return False


def test_memory_system():
    """Test that memory system can be initialized."""
    try:
        from src.memory import MemorySystem
        
        memory = MemorySystem()
        summary = memory.get_summary()
        
        assert isinstance(summary, dict), "Memory summary is not a dict"
        assert 'enabled' in summary, "Memory summary missing 'enabled' key"
        
        if memory.enabled:
            memory.close()
        
        print("✅ Memory system initializes")
        return True
    
    except Exception as e:
        print(f"❌ Memory system failed: {e}")
        return False


def test_role_prompts():
    """Test that role prompts can be loaded."""
    try:
        from src.roles import RolePrompts
        
        prompts = RolePrompts()
        
        # Try loading each role prompt
        pm_prompt = prompts.get_pm_prompt()
        backend_prompt = prompts.get_backend_prompt()
        frontend_prompt = prompts.get_frontend_prompt()
        reviewer_prompt = prompts.get_reviewer_prompt()
        
        assert len(pm_prompt) > 0, "PM prompt is empty"
        assert len(backend_prompt) > 0, "Backend prompt is empty"
        assert len(frontend_prompt) > 0, "Frontend prompt is empty"
        assert len(reviewer_prompt) > 0, "Reviewer prompt is empty"
        
        print("✅ All role prompts load successfully")
        return True
    
    except Exception as e:
        print(f"❌ Role prompts failed: {e}")
        return False


def test_tools_configuration():
    """Test that tools can be configured."""
    try:
        from src.tools import get_enabled_tools
        
        tools = get_enabled_tools()
        
        assert isinstance(tools, list), "Tools is not a list"
        
        print(f"✅ Tools configured ({len(tools)} enabled)")
        return True
    
    except Exception as e:
        print(f"❌ Tools configuration failed: {e}")
        return False


def run_all_tests():
    """Run all boot tests."""
    print("\n" + "="*60)
    print("  BOOT TESTS - Repository Wiring Validation")
    print("="*60 + "\n")
    
    tests = [
        test_imports,
        test_graph_builder,
        test_memory_system,
        test_role_prompts,
        test_tools_configuration
    ]
    
    results = []
    for test in tests:
        print(f"\nRunning: {test.__name__}")
        result = test()
        results.append(result)
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("="*60 + "\n")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
