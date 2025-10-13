# Enhanced Technical Tasks

## Task #1: Create User model with validation
**Labels:** database, task-management
**Story Points:** 2
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create/modify: `backend/api/v1/tasks/models/task_model.py`
- Dependencies: Import Sequelize, PostgreSQL adapter, and User model from the project's ORM configuration.

### Implementation Details
- Use Sequelize to define the Task model with fields for title, description, status (boolean), user_id (foreign key).
- Define validation rules using Sequelize's `check` method for each field:
  - title: `notEmpty()`, `max(255)`
  - description: `notEmpty()`, `max(1024)`
  - status: `isBoolean()`
  - user_id: `exists({ model: User })`
- Implement associated methods for querying, creating, updating, and deleting tasks.

### API Specification (if applicable)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter()

# Get all tasks for a user
@router.get("/", response_model=List[Task])
async def get_tasks(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return await db.query(Task).where(Task.user_id == user.id).all()

# Get a specific task by ID
@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    task = await db.query(Task).filter(and_(Task.id == task_id, Task.user_id == user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Create a new task
@router.post("/", response_model=Task)
async def create_task(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    new_task = Task(title="[New Task]", description="", status=False, user_id=user.id)
    await db.add(new_task)
    await db.flush()
    return new_task

# Update an existing task
@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, updated_task: TaskUpdate, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    task = await db.query(Task).filter(and_(Task.id == task_id, Task.user_id == user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = updated_task.title
    task.description = updated_task.description
    task.status = updated_task.status
    await db.flush()
    return task

# Delete a task
@router.delete("/{task_id}")
async def delete_task(task_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    task = await db.query(Task).filter(and_(Task.id == task_id, Task.user_id == user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
```

### Database Changes (if applicable)
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status BOOLEAN DEFAULT false,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
);
```

### Testing Requirements
- Unit tests for the Task model and associated methods using a testing framework like pytest.
- Integration tests for API endpoints using tools like Pytest-HTTPClient or FastAPI's built-in test client.
- Store tests in `backend/tests` directory with appropriate file naming conventions (e.g., `test_task_model.py`, `test_tasks_api.py`).

### Acceptance Criteria (Enhanced)
- A valid Task instance can be created, retrieved, updated, and deleted without errors using the provided API endpoints.
- Invalid Task instances are rejected with appropriate error messages as defined by Sequelize's validation rules.
- Unit tests for specific functions pass without any failures or warnings.
- Integration tests for specific flows pass without any failures or warnings.

---

## Task #2: Add POST /api/users endpoint
**Labels:** api, task-management
**Story Points:** 3
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create: `src/api/users.py`
- Dependencies: Import FastAPI, Pydantic, SQLAlchemy, and the User model from your project's existing models file (e.g., src/models/user.py)

### Implementation Details
- Use FastAPI to create a new POST endpoint for creating users at `/api/users`
- Define a Pydantic UserCreate schema with required fields for username, email, and password
- In the UsersRouter class, define a post method that takes the UserCreate instance as an argument, validates it using FastAPI's Depends(UserCreate), creates a new User instance from the validated data, saves it to the database using SQLAlchemy, and returns a JSON response with the newly created user's data and a 201 Created status code
- To handle errors, use FastAPI's HTTPException for custom error handling. For example, if validation fails or an error occurs during database operations, raise an appropriate exception with an informative message and the corresponding HTTP status code (e.g., 400 Bad Request)

### API Specification
```python
from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from src.models import User
from src.database import engine

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/api/users", response_model=User)
async def create_user(user: UserCreate):
    db = engine.connect()
    user_exists = db.execute(f"SELECT 1 FROM users WHERE email={user.email}").fetchone()

    if user_exists:
        raise HTTPException(status_code=409, detail="Email already in use")

    new_user = User(username=user.username, email=user.email, password=user.password)
    db.execute(new_user.insert())
    db.commit()
    db.close()

    return new_user
```
### Database Changes (if applicable)
- Add the Users table to your PostgreSQL database schema if it doesn't exist already:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
```
### Testing Requirements
- Write unit tests for the create_user function using a testing framework like pytest
- Write integration tests to test the end-to-end flow of creating and retrieving users
- Store tests in `tests/test_users.py`

### Acceptance Criteria (Enhanced)
- A new User instance can be created and saved to the database upon a successful POST request to `/api/users` with valid data, returning a JSON response containing the newly created user's data and a 201 Created status code.
- If an email already exists in the database, return a 409 Conflict status code and an error message.
- All Task instances can be retrieved and returned as JSON using the GET endpoint at `/api/tasks` with a 200 OK status code.

---

## Task #3: Implement login form component
**Labels:** frontend, authentication
**Story Points:** 3
**Priority:** Medium Priority

 ## Technical Implementation for Login Form Component

### File Structure
- Create: `frontend/src/components/LoginForm.js` and update `frontend/src/App.js`
- Dependencies: Import React, Tailwind CSS, Redux, Axios, and any necessary hooks or utilities from the frontend tech stack.

### Implementation Details
- Use React to create a functional component for the login form.
- Utilize Tailwind CSS classes for styling the form elements.
- Implement Redux actions and reducers for handling user authentication state changes.
- Create a form with fields for username, password, and a submit button.
- On form submission, use Axios to send a POST request to the API endpoint defined below.

### API Specification (if applicable)
```javascript
POST /api/v1/auth/login
Request Body: { "username": string, "password": string }
Response: { "token": string }
```

### Database Changes (if applicable)
- No direct database changes are required for this task. The API will handle user authentication and manage tokens.

### Testing Requirements
- Write unit tests for the LoginForm component, Redux actions, and reducers using a testing library such as Jest or Enzyme.
- Perform integration tests to ensure proper communication with the API and handling of errors.

### Acceptance Criteria (Enhanced)
- The login form can be rendered on the page with fields for username and password.
- Upon successful submission, an Axios request is sent to the specified API endpoint, and if the response contains a valid token, the user is redirected to the Todo List.
- Upon unsuccessful submission (e.g., invalid credentials), an error message is displayed, and no API request is made.
- The component should be styled using Tailwind CSS classes for a clean and consistent look.
- The component should utilize Redux actions and reducers to manage user authentication state changes.
- All tests pass without any errors or warnings.

---

## Task #4: Implement task creation service method
**Labels:** business-logic, task-management
**Story Points:** 2
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create: `backend/api/tasks/task_service.py`
- Dependencies: Import FastAPI, Pydantic, SQLAlchemy, and the Task model from your ORM (e.g., SQLAlchemy)

### Implementation Details
- Use FastAPI to define the API endpoint for creating tasks
- Define a new method `create_task(current_user: User)` in the `TaskService` class
- The method should create a new instance of the Task model, associate it with the authenticated user (using the `current_user` parameter), and save it to the database
- Return the newly created task data as a JSON response
- Use Pydantic for input validation and error handling

### API Specification
```python
from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from your_orm import models, schemas

app = FastAPI()

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.CreateTask, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    new_task = models.Task(**task.dict(), user=current_user)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
```

### Database Changes (if applicable)
Assuming you have a Task model with the following structure:

```python
class Task(Base):
    __tablename__ = "tasks"

    id: int = Field(primary_key=True, index=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    user_id: int
```

### Testing Requirements
- Write unit tests for the `create_task` method using a testing framework like pytest
- Include test cases for successful creation of tasks and edge cases (e.g., invalid input, missing user)
- Test files should be located in `backend/tests/unit/tasks/test_task_service.py`

### Acceptance Criteria (Enhanced)
- A new Task instance can be created and saved to the database upon successful API request with valid input
- The response includes a status code of 201 Created, the newly created task's data in JSON format, and appropriate headers (e.g., Content-Type: application/json)
- Error handling is implemented for invalid input and missing user, returning appropriate HTTP status codes and error messages in JSON format (e.g., 400 Bad Request for invalid input, 401 Unauthorized for missing user)

---

## Task #5: Write unit tests for User model
**Labels:** testing, user-management
**Story Points:** 2
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create/modify: `backend/api/users/models/user.py`
- Dependencies: Import FastAPI, Pydantic, SQLAlchemy, and the User model schema defined below.

### Implementation Details
- Use FastAPI for building the RESTful API.
- Define a User class that inherits from Pydantic's BaseModel to represent the user data structure. The User class should have attributes for username, email, password (hashed), and any other required fields.
- Create a UserDB model that extends SQLAlchemy's Base model and maps to the corresponding database table. Inherit from the User class and add an id attribute as a primary key.
- Implement CRUD operations (Create, Read, Update, Delete) for the UserDB model in the `users` router file (`backend/api/users/router.py`).

### API Specification (if applicable)
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter()

from .models import User, get_db

@router.post("/register", response_model=User)
async def create_user(user: User, db: Session = Depends(get_db)):
    # Implement user creation logic here

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    # Implement user retrieval logic here

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, updated_user: User, db: Session = Depends(get_db)):
    # Implement user update logic here

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Implement user deletion logic here
```

### Database Changes (if applicable)
Create a `users` table in the PostgreSQL database with columns for id, username, email, hashed_password, and any other required fields.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    # Add any other required columns here
);
```

### Testing Requirements
- Write unit tests for the UserDB CRUD operations using FastAPI's built-in testing tools or a third-party testing library like pytest.
- Create test cases for positive scenarios (e.g., successful user creation, retrieval, update, and deletion) as well as negative scenarios (e.g., invalid input validation, database errors).
- Store the tests in a separate file (`tests/test_users.py`) within the project structure.

### Acceptance Criteria (Enhanced)
- All unit tests for UserDB CRUD operations pass without any failures or errors.
- The `create_user`, `read_user`, `update_user`, and `delete_user` API endpoints are implemented correctly, returning the expected responses for each operation.
- Proper input validation is in place to ensure that only valid user data is accepted by the API.
- Database interactions are handled securely, with appropriate error handling for any potential issues (e.g., database connection errors or unique constraint violations).

---

## Task #6: Write setup instructions for new team members
**Labels:** documentation, onboarding
**Story Points:** 2
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create/modify: `backend/api/todo_api.py`
- Dependencies: Import FastAPI, Pydantic, SQLAlchemy, and any other necessary libraries from the specified architecture.

### Implementation Details
- Use FastAPI for building the RESTful API.
- Define routes, models (using Pydantic), and endpoints for creating, updating, deleting, and viewing tasks.
- Implement JWT authentication using FastAPI's built-in security features.
- Follow the RESTful API design pattern with standard HTTP methods (GET, POST, PUT, DELETE).

### API Specification (if applicable)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Todo
from schemas import TodoCreate, TodoUpdate
from database import get_db

router = APIRouter()

@router.post("/todos/", response_model=Todo)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    # Implement creating a new task in the database
    pass

@router.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    # Implement retrieving a specific task from the database
    pass

@router.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    # Implement updating a specific task in the database
    pass

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    # Implement deleting a specific task from the database
    pass
```

### Database Changes (if applicable)
```sql
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    completed BOOLEAN DEFAULT false
);
```

### Testing Requirements
- Unit tests for the `create_todo`, `read_todo`, `update_todo`, and `delete_todo` functions.
- Integration tests for testing the entire flow of creating, updating, deleting, and viewing tasks.
- Place unit tests in the `tests` folder with appropriate file names (e.g., `test_todo_api.py`).
- Place integration tests in a separate folder (e.g., `integration_tests`) with appropriate file names.

### Acceptance Criteria (Enhanced)
- The instructions are easy to follow and include all necessary steps for setting up the development environment, including dependencies, database configuration, and API endpoints.
  - Specifically, the developer should be able to run the FastAPI application locally using a PostgreSQL database.
- The provided code follows the specified architecture and includes exact method signatures and return types.
- Unit tests are written for each function and cover all possible edge cases.
- Integration tests are written to test the entire flow of creating, updating, deleting, and viewing tasks.
- Proper error handling is implemented throughout the codebase.
- The code is well-documented with clear comments explaining the purpose of each function and class.

---

