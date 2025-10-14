"""
Demo - Todo App Development Project
==================================

This script demonstrates how to use the generic agile_dev_team framework
to build a specific type of application (Todo List Web App).
"""

from agile_dev_team import (
    run_development_project, 
    ProjectConfiguration, 
    ProjectType,
    create_project_from_brief
)

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
    
    print("🎯 Running Todo App Development Project")
    print("=" * 50)
    
    # Create project configuration for a Todo Web App
    project_config = ProjectConfiguration(
        name="TodoApp",
        type=ProjectType.WEB_APP,
        brief=project_brief,
        
        # Technology preferences for this project
        preferred_languages=["Python", "JavaScript", "HTML", "CSS"],
        preferred_frameworks=["FastAPI", "Vanilla JS", "Bootstrap"],
        preferred_databases=["SQLite", "PostgreSQL"],
        
        # Architecture preferences
        architecture_style="hexagonal",
        deployment_platform="docker",
        
        # Quality requirements
        test_coverage_target=85,
        security_requirements=["input_validation", "CORS", "authentication"],
        
        # Output preferences
        include_documentation=True,
        include_tests=True,
        include_deployment_config=True,
        include_ci_cd=False  # Keep it simple for demo
    )
    
    print(f"🏗️ Project Configuration:")
    print(f"   📋 Name: {project_config.name}")
    print(f"   🎯 Type: {project_config.type.value}")
    print(f"   💻 Languages: {', '.join(project_config.preferred_languages)}")
    print(f"   🚀 Frameworks: {', '.join(project_config.preferred_frameworks)}")
    print(f"   🗄️ Databases: {', '.join(project_config.preferred_databases)}")
    
    result = run_development_project(project_config)
    
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
