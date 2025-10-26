"""
Graph Tests

Verifies that the LangGraph workflow can execute.
"""

import sys
import os
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ['LLM_PROVIDER'] = os.getenv('LLM_PROVIDER', 'ollama')
os.environ['LLM_MODEL'] = os.getenv('LLM_MODEL', 'codellama:latest')
os.environ['MAX_TURNS'] = '2'  # Short test run
os.environ['LEARNING_ENABLED'] = 'false'  # Disable for faster testing


def test_graph_single_iteration():
    """
    Test that graph can execute one full iteration.
    
    Note: This is a basic smoke test. It verifies the graph runs without
    crashing, but does not validate business logic or output quality.
    """
    try:
        from src.graph import create_team_graph, TeamState
        
        print("\n" + "="*60)
        print("  GRAPH TEST - Single Iteration")
        print("="*60 + "\n")
        
        # Create graph
        print("Building graph...")
        graph = create_team_graph()
        
        # Create initial state
        initial_state: TeamState = {
            'user_goal': 'Create a simple hello world program that prints a greeting',
            'spec': '',
            'backend_notes': '',
            'frontend_notes': '',
            'review_notes': '',
            'approvals': [],
            'turns': 0,
            'approved': False,
            'memories_retrieved': []
        }
        
        print("Running graph (max 2 turns for test)...\n")
        
        # Execute graph
        final_state = graph.invoke(initial_state)
        
        # Validate output
        print("\n" + "-"*60)
        print("VALIDATION:")
        print("-"*60)
        
        # Check that SPEC was generated
        has_spec = len(final_state['spec']) > 0
        print(f"{'✅' if has_spec else '❌'} SPEC generated: {len(final_state['spec'])} chars")
        
        # Check that at least one agent produced output
        has_backend = len(final_state['backend_notes']) > 0
        has_frontend = len(final_state['frontend_notes']) > 0
        has_review = len(final_state['review_notes']) > 0
        
        print(f"{'✅' if has_backend else '❌'} Backend notes: {len(final_state['backend_notes'])} chars")
        print(f"{'✅' if has_frontend else '❌'} Frontend notes: {len(final_state['frontend_notes'])} chars")
        print(f"{'✅' if has_review else '❌'} Review notes: {len(final_state['review_notes'])} chars")
        
        # Check turns
        turns_valid = final_state['turns'] > 0 and final_state['turns'] <= 2
        print(f"{'✅' if turns_valid else '❌'} Turns executed: {final_state['turns']}")
        
        # Overall success
        success = has_spec and (has_backend or has_frontend or has_review) and turns_valid
        
        print("\n" + "="*60)
        if success:
            print("✅ GRAPH TEST PASSED")
            print("="*60 + "\n")
            return True
        else:
            print("❌ GRAPH TEST FAILED - See validation results above")
            print("="*60 + "\n")
            return False
    
    except Exception as e:
        print(f"\n❌ GRAPH TEST FAILED WITH EXCEPTION:\n{e}\n")
        
        import traceback
        print(traceback.format_exc())
        
        return False


def test_model_connection():
    """Test that we can connect to the LLM provider."""
    try:
        from src.llm import get_chat_model, test_model_connection
        
        print("\n" + "="*60)
        print("  MODEL CONNECTION TEST")
        print("="*60 + "\n")
        
        print(f"Provider: {os.getenv('LLM_PROVIDER')}")
        print(f"Model: {os.getenv('LLM_MODEL')}")
        print("\nTesting connection...\n")
        
        model = get_chat_model()
        connected = test_model_connection(model)
        
        if connected:
            print("✅ MODEL CONNECTION SUCCESSFUL")
            return True
        else:
            print("❌ MODEL CONNECTION FAILED")
            print("\nTroubleshooting:")
            print("1. Ensure Ollama is running: ollama serve")
            print("2. Verify model is pulled: ollama list")
            print("3. Pull model if missing: ollama pull codellama:latest")
            return False
    
    except Exception as e:
        print(f"❌ MODEL CONNECTION TEST FAILED:\n{e}")
        return False


def run_all_tests():
    """Run all graph tests."""
    print("\n" + "="*60)
    print("  GRAPH TESTS - LangGraph Execution Validation")
    print("="*60)
    
    # First test model connection
    model_ok = test_model_connection()
    
    if not model_ok:
        print("\n⚠️  Skipping graph test due to model connection failure")
        print("Fix model connection and try again.\n")
        return 1
    
    # Then test graph execution
    graph_ok = test_graph_single_iteration()
    
    if graph_ok:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
