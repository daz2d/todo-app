# Enhanced Technical Tasks

## Task #1: Create User model with validation
**Labels:** feature, database
**Story Points:** 2
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `backend/api/users/models/user.py` for User model and its validation rules.
- Create: `backend/api/tasks/models/task.py` for Task model and its validation rules.

### Implementation Details
- Use FastAPI as the web framework, following RESTful API design principles.
- Define the User and Task classes with required fields (username, email, password, and related fields).
- Implement data validation using Pydantic, ensuring well-formed and secure data.
- Create appropriate methods for creating, reading, updating, and deleting users and tasks.

### API Specification (if applicable)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    # Include fields that can be updated (e.g., email, password)

class TaskCreate(BaseModel):
    title: str
    description: str
    status: bool = False  # Default to incomplete

class TaskUpdate(BaseModel):
    # Include fields that can be updated (e.g., status)

@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    # Implement user creation logic and validation here

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    # Implement user updating logic and validation here

@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    # Implement task creation logic and validation here

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskUpdate):
    # Implement task updating logic and validation here
```

### Database Changes (if applicable)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT,
    status BOOLEAN DEFAULT FALSE
);
```

### Testing Requirements
- Write unit tests for User and Task classes using FastAPI's test client.
- Write integration tests to cover various user and task scenarios (e.g., creating, updating, deleting, filtering, searching).
- Store test files in `backend/tests` directory.

### Acceptance Criteria (Enhanced)
- The User model has been created with required fields (username, email, password) and validation rules.
- Validation rules have been implemented for each field in the User model.
- The Task model has been created with required fields (title, description, status) and validation rules.
- Validation rules have been implemented for each field in the Task model.
- Unit tests have been written for the User and Task classes to ensure proper functionality and validation.
- Integration tests have been written to cover various user and task scenarios.

---

## Task #2: Add GET /api/users endpoint
**Labels:** feature, api
**Story Points:** 2
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `backend/api/users.py`
- Dependencies: Import FastAPI, SQLAlchemy, and JWT from the specified architecture.

### Implementation Details
- Use FastAPI for creating the API endpoints.
- Follow RESTful API design patterns for the endpoint creation.
- Create a User model with appropriate fields (e.g., id, username, email, password_hash) using SQLAlchemy and ORM mapping to the SQLite database.
- Implement `get_users` and `create_user` routes for retrieving all users and creating new users respectively. Ensure proper authentication and authorization for both endpoints.

### API Specification (if applicable)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

router = APIRouter()

@router.get("/users", response_model=List[User])
async def get_users(db: Session = Depends(get_db), auth: AuthJWT = Depends(auth_middleware)):
    # Implement logic to retrieve all users from the database

@router.post("/users", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db), auth: AuthJWT = Depends(auth_middleware)):
    # Implement logic to create a new user in the database and return the created user object

def get_db():
    # Implement logic to connect to the SQLite database and return a session object

def auth_middleware(authorization: str = HTTPHeader(name="Authorization")):
    # Implement JWT authentication middleware to protect the endpoints
```

### Database Changes (if applicable)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
```

### Testing Requirements
- Write unit tests for the `get_users` and `create_user` functions to test their functionality and edge cases.
- Create integration tests to test the end-to-end flow of user creation, authentication, and authorization.
- Store tests in a separate folder (e.g., `tests`) with appropriate naming conventions (e.g., `test_users.py`).

### Acceptance Criteria (Enhanced)
- Implement the GET endpoint to retrieve all users from the database using SQLAlchemy's ORM.
- Ensure proper authentication and authorization for the GET endpoint by implementing JWT middleware.
- Implement a POST endpoint to create new users in the database, validating user input and hashing passwords before storing them securely.
- Ensure proper authentication and authorization for the POST endpoint by implementing JWT middleware.
- Write unit tests for both functions to test their functionality and edge cases.
- Write integration tests to test the end-to-end flow of user creation, authentication, and authorization.

---

## Task #3: Implement login form component
**Labels:** feature, frontend
**Story Points:** 3
**Priority:** 3 pts

 ## Technical Implementation

### File Structure
- Create/modify: `frontend/src/components/LoginForm.js` and `frontend/src/components/TaskList.js`
- Dependencies: Import React, Bootstrap, Axios for API calls, and any other necessary dependencies from the frontend tech stack.

### Implementation Details
- Use React's component-based architecture to create reusable LoginForm and TaskList components.
- In the LoginForm component, handle user input and submit requests to the API for authentication using Axios.
- In the TaskList component, implement filtering and searching functionality, allow users to interact with tasks (create, edit, mark as completed/incomplete, delete), and display tasks in a clean, modern format using Bootstrap.
- Ensure proper error handling and user feedback when login fails or succeeds by using React's state management and conditional rendering.

### API Specification (if applicable)
#### Login API
```javascript
POST /api/auth/login
Request Body: { "username": string, "password": string }
Response: { "token": string }
```

#### Tasks API
```javascript
GET /api/tasks (filter and search parameters can be included in the query)
POST /api/tasks (request body should include task details like title and description)
PUT /api/tasks/:id (request body should include updated task details)
DELETE /api/tasks/:id
```

### Database Changes (if applicable)
- SQLite does not require explicit schema definitions, but you may need to create tables for users and tasks. You can do this using SQL statements within the `frontend/src/database/schema.sql` file.

### Testing Requirements
- Unit tests for specific functions in both components (e.g., handling user input, API calls, state management)
- Integration tests for specific flows (e.g., login success and failure scenarios, task creation, editing, deletion)
- Store test files within the `frontend/src/tests` directory and follow naming conventions such as `LoginForm.test.js` or `TaskList.test.js`.

### Acceptance Criteria (Enhanced)
1. Create a reusable LoginForm component that handles user input, makes API calls to the /api/auth/login endpoint for authentication, and displays proper error messages if login fails.
2. Implement a TaskList component that fetches tasks from the /api/tasks endpoint, allows users to interact with tasks (create, edit, mark as completed/incomplete, delete), and filters and searches tasks using query parameters. The component should display tasks in a clean, modern format using Bootstrap.
3. Ensure proper error handling and user feedback when login fails or succeeds by updating the state of the LoginForm component and conditional rendering based on the state.
4. Implement filtering and searching functionality for the TaskList component by modifying the API calls to include query parameters like search terms, sorting criteria, and filters.
5. Write unit tests for specific functions in both components (e.g., handling user input, API calls, state management) using a testing library such as Jest or Mocha.
6. Write integration tests for specific flows (e.g., login success and failure scenarios, task creation, editing, deletion) to ensure that the application behaves correctly in various situations.

---

## Task #4: Implement login service
**Labels:** feature, authentication
**Story Points:** 1
**Priority:** 3 pts

 ## Technical Implementation

### File Structure
- Create: `backend/api/auth/router.py`
- Logout: `backend/api/auth/router.py`

### Dependencies
- Import FastAPI, dependencies from Pydantic (BaseModel, EmailStr, HTTPException) and Passlib for password hashing.

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFactory
from pydantic import BaseModel, EmailStr
from passlib.hash import bcrypt
```

### Implementation Details
- Create a FastAPI router for the authentication service.
- Define a User model (extend from BaseModel) with email and password fields.
- Implement a function to validate user credentials against the SQLite database. If successful, return an authenticated user object.
- Implement a logout function that removes the authenticated user from the application's context and redirects the user to the login page.

### API Specification
```python
router = APIRouter()

class User(BaseModel):
    email: EmailStr
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_factory = OAuth2PasswordRequestFactory(tokenUrl="token")

@router.post("/login", response_model=User)
async def login_user(user: User):
    # Implement user authentication logic here

@router.post("/logout")
async def logout_user(current_user: User = Depends(oauth2_factory.get_current_user)):
    # Implement user logout logic here
```

### Database Changes (if applicable)
- Create a Users table with columns email and hashed_password.

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,
    hashed_password TEXT
);
```

### Testing Requirements
- Write unit tests for the login and logout functions.
- Write integration tests to test the authentication flow.

### Acceptance Criteria (Enhanced)
1. Create a service that handles user authentication by validating credentials against the Users table in the SQLite database and returning an authenticated User object if successful.
2. Implement a logout function that removes the authenticated user from the application's context and redirects the user to the login page using FastAPI's response redirection functionality.
3. Write unit tests for the login and logout functions.
4. Write integration tests to test the authentication flow.
5. Ensure proper error handling is implemented for invalid credentials, unauthorized access attempts, etc.

---

## Task #5: Implement task creation service
**Labels:** feature, business logic
**Story Points:** 2
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `tasks/services/task_service.py`
- Dependencies: FastAPI, SQLAlchemy (for database ORM), PyJWT (for JWT authentication)

### Implementation Details
- Use the FastAPI framework for creating RESTful APIs.
- Create a TaskService class that handles creating and updating tasks in the database.
- Implement `create_task` and `update_task` methods within the TaskService class.
- Include proper input validation using Pydantic models for task data.

### API Specification (if applicable)
```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFactory
from jose import JWTError, jwt
import models
import schemas

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
oauth2 = OAuth2PasswordRequestFactory(tokenUrl="login")

# Create Task API
@app.post("/tasks/", response_model=schemas.TaskOut)
async def create_task(task: schemas.CreateTask, db: Session = Depends(get_db)):
    # Validate and save the task data to the database using SQLAlchemy ORM
    new_task = models.Task(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Update Task API
@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
async def update_task(task_id: int, updated_task: schemas.UpdateTask, db: Session = Depends(get_db)):
    # Find the task in the database by its ID and validate the user's authorization to modify it
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update the task data in the database using SQLAlchemy ORM
    for key, value in updated_task.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task
```

### Database Changes (if applicable)
Assuming you have a `Task` model defined in the `models.py` file:

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

### Testing Requirements
- Write unit tests for the `create_task` and `update_task` methods using a testing framework like pytest.
- Include test files within the `tests` directory (e.g., `test_task_service.py`)

### Acceptance Criteria (Enhanced)
- Create a service that handles creating new tasks in the database and returns them to the client, using proper input validation before saving data to the SQLite database.
  - Implement the `create_task` method within the TaskService class as specified above.
- Ensure proper validation of task data before saving it to the database when updating existing tasks.
  - Implement the `update_task` method within the TaskService class as specified above.
- Create a service that handles updating existing tasks in the database based on user input, using proper input validation before saving data to the SQLite database.
  - Implement the `update_task` method within the TaskService class as specified above.

---

## Task #6: Write unit tests for User model
**Labels:** testing, database
**Story Points:** 2
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `backend/api/users/models/user.py` for User model and related functions
- Tests: `backend/tests/test_users.py` for unit tests

### Implementation Details
- Use FastAPI for API development
- Follow RESTful API design principles
- Create a `User` class with appropriate attributes and validation using Pydantic
- Implement methods for creating, retrieving, updating, and deleting users in the `UserCrudOperations` class
- Include method signatures and return types as per FastAPI conventions (e.g., `async def create_user(user: User) -> UserResponse`)

### API Specification
```markdown
##### Create User
POST /users
Request Body:
{
  "username": "string",
  "email": "string",
  "password": "string"
}

Response:
201 Created
{
  "user_id": int,
  "username": "string",
  "email": "string",
  "created_at": datetime,
  "updated_at": datetime
}

##### Retrieve User
GET /users/{user_id}

Response:
200 OK
{
  "user_id": int,
  "username": "string",
  "email": "string",
  "created_at": datetime,
  "updated_at": datetime
}

##### Update User
PUT /users/{user_id}
Request Body:
{
  "username": "string",
  "email": "string"
}

Response:
200 OK
{
  "user_id": int,
  "username": "string",
  "email": "string",
  "created_at": datetime,
  "updated_at": datetime
}

##### Delete User
DELETE /users/{user_id}

Response:
204 No Content
```

### Database Changes (if applicable)
- Create the `users` table with columns: `user_id`, `username`, `email`, `password`, `created_at`, and `updated_at`. Use SQLite syntax for creating tables.

### Testing Requirements
- Write unit tests for the User model using FastAPI's built-in test client and pytest framework
- Include tests for validation, data persistence, and retrieval of users
- Test file location: `backend/tests/test_users.py`

### Acceptance Criteria (Enhanced)
- Write unit tests for the User model to ensure that validation rules are working correctly and that data is being saved and retrieved properly according to the provided API specifications and database schema.
- Write unit tests for the Task model if necessary, considering any integration points between Users and Tasks.
- Ensure all tests pass with no failures or errors.
- Code should follow the specified file structure, implementation details, API specification, and database schema.
- Tests should cover edge cases and potential error scenarios to ensure robustness and reliability of the application.

---

## Task #7: Write setup instructions
**Labels:** documentation
**Story Points:** 3
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `backend/src/api/todos/routes.py`
- Dependencies: Import FastAPI, Pydantic, SQLAlchemy, and the Todo model from your project structure.

### Implementation Details
- Use FastAPI to define RESTful API endpoints for creating, editing, marking as completed/incomplete, deleting, filtering, and searching tasks.
- Follow the FastAPI documentation patterns for each endpoint definition, including request/response structures and parameter validation.
- Implement specific classes and interfaces as needed (e.g., a Todo service class to handle business logic).
- Include exact method signatures and return types for each API endpoint.

### API Specification (if applicable)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

app = FastAPI()

class TodoIn(BaseModel):
    title: str
    description: str
    completed: bool = False

class TodoOut(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

@app.post("/todos/", response_model=TodoOut)
def create_todo(todo: TodoIn, db: Session):
    # Implement business logic and database interaction to create a new todo item
    pass

# Add similar endpoints for editing, marking as completed/incomplete, deleting, filtering, and searching tasks.
```

### Database Changes (if applicable)
```sql
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT False
);
```

### Testing Requirements
- Unit tests for specific functions in the Todo service class and API endpoints.
- Integration tests for specific flows involving multiple API endpoints (e.g., creating a todo item, marking it as completed, and retrieving updated data).
- Place unit tests within `backend/tests` folder, and integration tests within `backend/integration_tests`.

### Acceptance Criteria (Enhanced)
- Create clear, concise setup instructions for new team members or external collaborators to easily onboard and start contributing to the project.
  - Include steps for setting up a development environment, installing dependencies, and running tests.
- Write comprehensive API documentation that includes details about each endpoint, its purpose, required parameters, and expected responses.
  - Document all API endpoints defined in this task with their request/response structures, parameter validation rules, and any other relevant information.
- Ensure proper data persistence, input validation, error handling, and adherence to security best practices throughout the implementation.
- Implement unit tests for specific functions and integration tests for specific flows as specified above.
- Verify that all acceptance criteria are met by running tests and ensuring that the application behaves as expected.

---

