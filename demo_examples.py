"""
Demo Examples - Generic Agile Development Team
=============================================

This script shows how to use the generic agile_dev_team framework
to build different types of applications with various configurations.
"""

from agile_dev_team import (
    run_development_project, 
    ProjectConfiguration, 
    ProjectType
)

def demo_web_app():
    """Demo: Todo List Web Application"""
    project_brief = """
    Create a complete Todo List web application with user authentication,
    task management (CRUD operations), filtering, search, and responsive design.
    Include a REST API backend and modern web frontend.
    """
    
    config = ProjectConfiguration(
        name="TodoApp",
        type=ProjectType.WEB_APP,
        brief=project_brief,
        preferred_languages=["Python", "JavaScript", "HTML", "CSS"],
        preferred_frameworks=["FastAPI", "Vanilla JS", "Bootstrap"],
        preferred_databases=["SQLite"],
        deployment_platform="docker"
    )
    
    print("🌐 Building Web Application...")
    return run_development_project(config)

def demo_api_service():
    """Demo: REST API Microservice"""
    project_brief = """
    Create a high-performance REST API microservice for user management
    with authentication, rate limiting, caching, and comprehensive logging.
    Include OpenAPI documentation and health monitoring endpoints.
    """
    
    config = ProjectConfiguration(
        name="UserService",
        type=ProjectType.API_SERVICE,
        brief=project_brief,
        preferred_languages=["Python"],
        preferred_frameworks=["FastAPI", "Redis"],
        preferred_databases=["PostgreSQL", "Redis"],
        deployment_platform="kubernetes",
        test_coverage_target=90
    )
    
    print("🔧 Building API Service...")
    return run_development_project(config)

def demo_cli_tool():
    """Demo: Command Line Tool"""
    project_brief = """
    Create a command-line tool for file management and batch processing.
    Include subcommands for organizing files, batch renaming, duplicate detection,
    and progress bars for long operations. Support configuration files and plugins.
    """
    
    config = ProjectConfiguration(
        name="FileManager",
        type=ProjectType.CLI_TOOL,
        brief=project_brief,
        preferred_languages=["Python"],
        preferred_frameworks=["Click", "Rich"],
        preferred_databases=["SQLite"],
        deployment_platform="traditional",
        include_ci_cd=False
    )
    
    print("⚡ Building CLI Tool...")
    return run_development_project(config)

def demo_data_science():
    """Demo: Data Analysis Project"""
    project_brief = """
    Create a data analysis project for financial market analysis.
    Include data ingestion, cleaning, visualization, statistical analysis,
    and predictive modeling. Generate automated reports and dashboards.
    """
    
    config = ProjectConfiguration(
        name="MarketAnalysis",
        type=ProjectType.DATA_SCIENCE,
        brief=project_brief,
        preferred_languages=["Python", "SQL"],
        preferred_frameworks=["Pandas", "NumPy", "Matplotlib", "Jupyter"],
        preferred_databases=["PostgreSQL"],
        deployment_platform="docker",
        include_deployment_config=False
    )
    
    print("📊 Building Data Science Project...")
    return run_development_project(config)

def demo_mobile_app():
    """Demo: Mobile Application"""
    project_brief = """
    Create a cross-platform mobile app for fitness tracking.
    Include workout logging, progress tracking, social features,
    offline sync, and push notifications. Support both iOS and Android.
    """
    
    config = ProjectConfiguration(
        name="FitnessTracker",
        type=ProjectType.MOBILE_APP,
        brief=project_brief,
        preferred_languages=["JavaScript", "TypeScript"],
        preferred_frameworks=["React Native", "Expo"],
        preferred_databases=["SQLite", "Firebase"],
        deployment_platform="mobile"
    )
    
    print("📱 Building Mobile App...")
    return run_development_project(config)

def main():
    """Run different project demos"""
    
    print("🎯 Generic Agile Development Team - Project Examples")
    print("=" * 60)
    
    examples = {
        "1": ("Todo Web App", demo_web_app),
        "2": ("API Microservice", demo_api_service), 
        "3": ("CLI Tool", demo_cli_tool),
        "4": ("Data Science Project", demo_data_science),
        "5": ("Mobile App", demo_mobile_app)
    }
    
    print("\nAvailable project examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}: {name}")
    
    choice = input("\nSelect project type (1-5): ").strip()
    
    if choice in examples:
        name, demo_func = examples[choice]
        print(f"\n🚀 Starting {name} development...")
        result = demo_func()
        
        if result:
            print(f"\n✅ {name} completed successfully!")
        else:
            print(f"\n❌ {name} failed")
    else:
        print("❌ Invalid choice. Running default Web App demo...")
        demo_web_app()

if __name__ == "__main__":
    main()