"""
Simple Demo - Run the Agile Development Team
===========================================

This script runs a smaller example to test the multi-agent system.
"""

from agile_dev_team import run_development_project

def main():
    """Run a simple project with the agile team"""
    
    # Comprehensive project brief for a full application
    project_brief = """
    Create a complete, production-ready Todo List web application with the following features:
    
    CORE FUNCTIONALITY:
    - User can create new tasks with title and description
    - User can mark tasks as completed/incomplete
    - User can edit existing tasks
    - User can delete tasks
    - User can view all tasks in a clean list format
    - User can filter tasks (all, active, completed)
    - User can search tasks by title/description
    
    TECHNICAL REQUIREMENTS:
    - Modern, responsive web interface that works on desktop and mobile
    - RESTful API backend with proper HTTP methods (GET, POST, PUT, DELETE)
    - Data persistence (database or file storage)
    - Input validation and error handling
    - Clean, professional UI/UX design
    - Cross-browser compatibility
    
    QUALITY REQUIREMENTS:
    - Comprehensive test coverage (unit and integration tests)
    - Proper error handling and user feedback
    - Security best practices
    - Performance optimization
    - Clear documentation and setup instructions
    - Production deployment guidelines
    
    DELIVERABLES:
    - Fully functional frontend (HTML, CSS, JavaScript)
    - Complete backend API with all endpoints
    - Database schema and data models
    - Comprehensive test suite
    - Documentation (README, API docs, deployment guide)
    - Production-ready code with proper structure
    
    This should be a complete application that can be deployed and used in production.
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
