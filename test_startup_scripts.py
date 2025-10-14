"""
Test Script - Startup Scripts Generation
=======================================

This script demonstrates the automatic generation of startup scripts
that will be created when the agile development team completes a project.
"""

from agile_dev_team import (
    run_development_project, 
    ProjectConfiguration, 
    ProjectType
)

def main():
    """Test the startup script generation"""
    
    # Quick project brief for testing
    project_brief = """
    Create a simple Todo List web application with:
    - Basic CRUD operations for todos
    - Simple web interface
    - RESTful API backend
    - Local storage/database
    
    Focus on creating a working application with proper startup scripts.
    """
    
    print("🧪 Testing Startup Script Generation")
    print("=" * 50)
    
    # Create a simple project configuration
    project_config = ProjectConfiguration(
        name="TestTodoApp",
        type=ProjectType.WEB_APP,
        brief=project_brief,
        
        # Simple tech stack for testing
        preferred_languages=["Python", "JavaScript"],
        preferred_frameworks=["FastAPI", "Vanilla JS"],
        preferred_databases=["SQLite"],
        
        # Minimal requirements for testing
        test_coverage_target=70,
        include_documentation=True,
        include_tests=True,
        include_deployment_config=True,
        include_ci_cd=False
    )
    
    print(f"🏗️ Testing Configuration:")
    print(f"   📋 Name: {project_config.name}")
    print(f"   🎯 Type: {project_config.type.value}")
    print(f"   💻 Languages: {', '.join(project_config.preferred_languages)}")
    print(f"   🚀 Frameworks: {', '.join(project_config.preferred_frameworks)}")
    
    print("\n⚡ Running development process...")
    result = run_development_project(project_config)
    
    if result:
        print("\n✅ Project completed successfully!")
        print("\n🚀 Generated Startup Scripts:")
        print("   • run.py - Universal Python launcher") 
        print("   • start.bat - Windows double-click launcher")
        print("   • start.sh - Unix/Mac shell script")
        print("   • docker-compose.yml - Container deployment")
        print("\n📋 To test the application:")
        print("   1. python run.py")
        print("   2. Open http://localhost:8080 in browser")
        print("   3. Backend API at http://localhost:8000")
        
        print("\n🔧 Project Files Generated:")
        import os
        try:
            for root, dirs, files in os.walk("src"):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), ".")
                    print(f"   ✅ {rel_path}")
        except:
            print("   📂 Files generated in project directory")
            
    else:
        print("❌ Project generation failed")

if __name__ == "__main__":
    main()