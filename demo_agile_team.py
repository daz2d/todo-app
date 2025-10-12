"""
Simple Demo - Run the Agile Development Team
===========================================

This script runs a smaller example to test the multi-agent system.
"""

from agile_dev_team import run_development_project

def main():
    """Run a simple project with the agile team"""
    
    # Simple project brief
    project_brief = """
    Create a simple Todo List web application:
    - Add new tasks
    - Mark tasks as done
    - Delete tasks
    - Simple HTML/CSS/JavaScript frontend
    - Basic data storage
    
    Keep it simple and clean.
    """
    
    print("🎯 Running Simple Todo App Project")
    print("=" * 50)
    
    result = run_development_project(project_brief)
    
    if result:
        print("\n✅ Project completed successfully!")
        print("\nYou can find:")
        print("- Requirements in result['requirements']")
        print("- UI Code in result['ui_code']")  
        print("- Backend Code in result['backend_code']")
        print("- Documentation in result['documentation']")
        print("- Test Results in result['test_results']")
        print("- Project Status in result['project_status']")
    else:
        print("❌ Project failed")

if __name__ == "__main__":
    main()
