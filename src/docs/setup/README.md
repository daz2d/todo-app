 ## Setup Instructions

### Prerequisites

- Python 3.x (Recommended: Python 3.8 or later)
- pip (Python package installer)
- SQLite3 (Database for local development)

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/todo-app.git
   ```

2. Navigate to the project directory:
   ```
   cd todo-app
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create and migrate the database schema:
   ```
   python src/backend/main.py db init
   python src/backend/main.py db migrate
   python src/backend/main.py db upgrade
   ```

5. Run the application (for development purposes):
   ```
   uvicorn src.backend.main:app --reload
   ```

6. Access the API at http://127.0.0.1:8000/docs in your web browser.

### Running Tests

1. Run unit tests:
   ```
   python -m pytest src.backend.tests.unit
   ```

2. Run integration tests:
   ```
   python -m pytest src.backend.tests.integration
   ```

These instructions should help you set up the project and get started with development. For more detailed information about the project, please refer to the documentation in the `docs` folder.