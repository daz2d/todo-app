# Enhanced Technical Tasks

## Task #1: Create User model with validation
**Labels:** feature, Database
**Story Points:** 2
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `app/models/user.js` and `app/models/task.js`
- Dependencies: Import Express, Sequelize, and the necessary models from Sequelize's `sequelize`, `sequelize-cli`, and `dotenv` packages.

### Implementation Details
- Use Express.js to create RESTful API endpoints for User and Task management.
- Utilize Sequelize ORM (Object-Relational Mapping) to interact with the SQLite database.
- Create User model with fields: id, username, email, and password using `sequelize generate:model user --attributes id:integer, username:string, email:string, password:string`.
- Create Task model with fields: id, title, description, status (boolean), userId (foreign key to the User model) using `sequelize generate:model task --attributes id:integer, title:string, description:text, status:boolean, userId:integer`.
- Define relationships between User and Task models by associating them in their respective model files.
- Implement validation rules for each field using Sequelize's built-in validation methods.
- Include exact method signatures and return types for API endpoints (e.g., createUser, authenticateUser, addTask, markTaskAsDone, deleteTask).

### API Specification (if applicable)
```javascript
// User API endpoints
app.post('/api/users', authenticate, createUser);
app.post('/api/users/login', authenticate, loginUser);

// Task API endpoints
app.post('/api/tasks', authenticate, addTask);
app.put('/api/tasks/:taskId/markAsDone', authenticate, markTaskAsDone);
app.delete('/api/tasks/:taskId', authenticate, deleteTask);
```

### Database Changes (if applicable)
```sql
// Create User table
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

// Create Task table
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  status BOOLEAN DEFAULT FALSE,
  userId INTEGER REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Testing Requirements
- Unit tests for User and Task models using Mocha and Chai.
- Integration tests for user authentication, task creation, marking tasks as done, and deletion using Supertest.
- Test files should be located in `tests/unit` and `tests/integration`.

### Acceptance Criteria (Enhanced)
- The User model is created with necessary fields like id, username, email, and password, and validation rules are set for each field to ensure data integrity.
- The Task model is implemented with required fields like id, title, description, status, and userId, and relationships between User and Task models are defined.
- Authentication methods using JSON Web Tokens (JWT) are implemented for secure user authentication and authorization in the application.
- RESTful API endpoints for User and Task management are created using Express.js and Sequelize ORM.
- Unit tests and integration tests are written for specific functions and flows, ensuring correct functionality of the implemented features.

---

## Task #2: Add POST /api/users endpoint
**Labels:** feature, API
**Story Points:** 3
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `backend/src/routes/api/users.js`
- Dependencies: Import Express, body-parser, and JWT authentication middleware from the specified architecture.

### Implementation Details
- Use Express.js to create a new POST endpoint at `/api/users`.
- Validate user data using JSON schema validation or any other preferred method.
- Implement the logic for saving validated user data into the SQLite database.
- Create a response object with appropriate status code and message, and send it back to the client.

### API Specification (if applicable)
```javascript
app.post('/api/users', jwtAuth, (req, res) => {
  // Validate user data here
  // Save validated user data into database
  // Send response with status code and message
});
```

### Database Changes (if applicable)
- Create a new table `users` in the SQLite database schema with appropriate columns for user data.

### Testing Requirements
- Write unit tests for the POST /api/users endpoint to ensure proper handling of valid and invalid user data.
- Perform integration tests for the entire flow of adding, updating, and retrieving users in the application.

### Acceptance Criteria (Enhanced)
- The POST /api/users endpoint is created and functional with proper error handling for invalid user data.
- User data is validated before being saved to the database using JSON schema validation or any other preferred method.
- The PUT /api/tasks/:id endpoint is created and functional as a separate task, ensuring proper integration between these endpoints.
- Task status is updated correctly when the endpoint is called with a valid task id.
- Unit tests for specific functions related to user management are written and passing.
- Integration tests for the entire flow of adding, updating, and retrieving users in the application are written and passing.

---

## Task #3: Implement add task form component
**Labels:** feature, Frontend
**Story Points:** 3
**Priority:** 3 pts

 ## Technical Implementation

### File Structure
- Create/modify: `frontend/src/components/AddTaskForm.js` and `frontend/src/components/TaskList.js`
- Dependencies: Import React, Tailwind CSS, Axios for API calls, and any necessary context providers (e.g., AuthenticationContext)

### Implementation Details
- Use React to create a functional component for the AddTaskForm and a class component for the TaskList.
- Implement form validation using React's built-in state management and conditional rendering.
- In the AddTaskForm, handle form submission by making an API call to add a new task.
- In the TaskList, display tasks with checkboxes for marking as done and delete buttons for removing tasks. Handle these events by making appropriate API calls.

### API Specification (if applicable)
```json
POST /tasks
Request Body: { "title": string, "description": string, "completed": boolean }
Response: { "id": number, "title": string, "description": string, "completed": boolean }

GET /tasks
Response: [ { "id": number, "title": string, "description": string, "completed": boolean }, ... ]

PATCH /tasks/:id
Request Body: { "completed": boolean }
Response: { "id": number, "title": string, "description": string, "completed": boolean }

DELETE /tasks/:id
Response: { "message": "Task deleted successfully" }
```

### Database Changes (if applicable)
- In the SQLite database file (e.g., `frontend/database/db.sqlite3`), create a table named `tasks` with columns `id`, `title`, `description`, and `completed`.

### Testing Requirements
- Write unit tests for AddTaskForm and TaskList components using testing libraries such as Jest or React Testing Library.
- Write integration tests to test the end-to-end functionality of adding, marking as done, and deleting tasks.

### Acceptance Criteria (Enhanced)
- The AddTaskForm is functional and user-friendly with proper form validation and submission handling.
- Validation rules are applied to the form inputs to ensure data integrity (e.g., title and description should not be empty).
- The TaskList component is functional and user-friendly, displaying tasks correctly and allowing users to mark tasks as done and delete them.
- Tasks can be added, marked as done, and deleted from the list using API calls and proper state management in React.
- Error handling is implemented for API calls, ensuring that any errors are displayed to the user in a friendly manner.
- All components are tested thoroughly with unit tests and integration tests.

---

## Task #4: Implement login form component
**Labels:** feature, Authentication
**Story Points:** 3
**Priority:** 3 pts

 ## Technical Implementation

### File Structure
- Create: `frontend/src/components/LoginForm.js`
- Modify: `backend/routes/auth.js`, `backend/controllers/authController.js`, and `backend/models/user.js`
- Dependencies: Import React, Express, JWT, bcrypt, body-parser, cors, and Sequelize (if using an ORM)

### Implementation Details
- Use React to create a functional component for the login form.
- Include form fields for username and password, with appropriate input validation and error handling.
- On form submission, make an API call to the `/auth/login` endpoint created in Express.js.

### API Specification (if applicable)
```javascript
// backend/routes/auth.js
router.post('/login', authController.login);

// backend/controllers/authController.js
exports.login = async (req, res) => {
  try {
    const user = await User.findOne({ where: { username: req.body.username } });
    if (!user) return res.status(404).json({ error: 'User not found' });

    const isPasswordValid = await user.validatePassword(req.body.password);
    if (!isPasswordValid) return res.status(401).json({ error: 'Invalid password' });

    // Generate JWT token and send it as response
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};
```

### Database Changes (if applicable)
- If using an ORM like Sequelize, create a User model with attributes for username and password (hashed), and methods for validating passwords.

```javascript
// backend/models/user.js
const { DataTypes } = require('sequelize');
const sequelize = new Sequelize(/* database configuration */);

const User = sequelize.define('User', {
  username: {
    type: DataTypes.STRING,
    unique: true,
    allowNull: false,
  },
  password: {
    type: DataTypes.STRING,
    allowNull: false,
  },
});

User.prototype.validatePassword = function(password) {
  // Compare the provided password with the stored hashed password
};

module.exports = User;
```

### Testing Requirements
- Write unit tests for the login form component and API endpoints using a testing framework like Jest or Mocha.
- Create integration tests to test the flow of user authentication, including successful logins and error handling scenarios.

### Acceptance Criteria (Enhanced)
- The login form component is functional and secure, with proper input validation and error handling.
- User credentials are validated against the database using a hashed password comparison method.
- Upon successful validation, a JWT token is generated and sent to the client for further authentication.
- In case of errors or invalid credentials, appropriate HTTP status codes and error messages are returned.
- Unit tests and integration tests pass without any failures.

---

## Task #5: Implement task creation service
**Labels:** feature, BusinessLogic
**Story Points:** 3
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `backend/src/services/taskCreationService.js`
- Dependencies: Import Express, SQLite3, and any necessary middleware (e.g., body-parser)

### Implementation Details
- Use Express.js to create a new route for handling task creation and status updates.
- Implement the following methods in the `taskCreationService` module:
  - `createTask(req, res)`: Accepts a request containing task data (title, description, and status), saves it to the SQLite database, and returns a response with the saved task's ID.
  - `updateTaskStatus(req, res)`: Accepts a request containing a task ID and new status, updates the corresponding task in the database, and returns a response confirming the update.
- Ensure that both methods handle errors appropriately (e.g., missing data, database connection issues).

### API Specification (if applicable)
```javascript
// POST /tasks
{
  "title": "Task Title",
  "description": "Task Description",
  "status": "pending" // or "done"
}

// PUT /tasks/:id/status
{
  "status": "done" // or "pending"
}
```

### Database Changes (if applicable)
Assuming you have a `tasks` table with columns: `id`, `title`, `description`, and `status`. No additional database changes are needed for this task.

### Testing Requirements
- Write unit tests for the `createTask` and `updateTaskStatus` methods using a testing framework like Jest or Mocha.
- Perform integration tests to verify that the service can handle multiple concurrent requests, errors, and edge cases (e.g., invalid data).
- Store test files in the appropriate location (e.g., `backend/tests`).

### Acceptance Criteria (Enhanced)
- The task creation service is functional and saves tasks correctly to the SQLite database using the specified API endpoints.
- The task status update service is functional and updates tasks correctly in the SQLite database using the specified API endpoints.
- Unit tests for specific functions pass without any errors or unexpected behavior.
- Integration tests for specific flows pass without any errors or unexpected behavior.
- The service handles errors appropriately, returning meaningful error messages to the client when necessary.

---

## Task #6: Write unit tests for User model
**Labels:** testing, Database
**Story Points:** 2
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `src/models/userModel.js` (Backend) and `src/components/UserContext.js` (Frontend)
- Dependencies: Import Express, Mongoose, bcrypt, jsonwebtoken, and dotenv in the userModel file. For Frontend, import React, useState, useContext, and other necessary components as needed.

### Implementation Details
#### Backend
- Use Express.js to create routes for handling User model operations.
- Define a Mongoose schema for the User model with properties such as username, password, email, etc., and create a corresponding model instance.
- Implement methods like `registerUser`, `loginUser`, and `getUserById` with appropriate parameter validation, password hashing (using bcrypt), JWT token generation, and error handling.

#### Frontend
- Create a UserContext to manage user-related state, such as the authenticated user's data and JWT token.
- Implement functions for user registration and login using Axios or Fetch to call the API endpoints created on the backend.

### API Specification (Backend)
```javascript
// Register a new user
POST /api/users/register
{
  "username": "string",
  "email": "string",
  "password": "string"
}

// Login an existing user
POST /api/users/login
{
  "username": "string",
  "password": "string"
}

// Get user data by ID (requires authentication)
GET /api/users/:userId
(authenticate JWT token)
```

### Database Changes (if applicable)
```sql
CREATE TABLE users (
  _id MongoID PRIMARY KEY,
  username VARCHAR(255),
  email VARCHAR(255),
  password HASH,
  // Add more properties as needed
);
```

### Testing Requirements
- Write unit tests for the User model using a testing framework like Jest or Mocha.
- Create integration tests to test user registration and login flows in the frontend application.
- Place tests in appropriate folders (e.g., `src/__tests__`).

### Acceptance Criteria (Enhanced)
- All methods and properties of the User model are tested with appropriate test cases, including password hashing, JWT token generation, and error handling.
- The registration and login functions in the frontend application are tested to ensure they correctly interact with the backend API.
- The UserContext is tested to verify that it correctly manages user state and JWT tokens.

---

## Task #7: Document API endpoints
**Labels:** documentation, API
**Story Points:** 2
**Priority:** 2 pts

 ## Technical Implementation

### File Structure
- Create/modify: `backend/server.js` for the main server file.
- Dependencies: Import Express, SQLite3, JWT, and other necessary modules from their respective packages.

### Implementation Details
- Use Express.js to create routes and handle HTTP requests.
- Follow RESTful API design pattern for creating, reading, updating, and deleting (CRUD) operations on tasks.
- Create a `Task` model with properties like `id`, `title`, `description`, `completed`, and `createdAt`.
- Implement controllers for handling requests related to tasks, such as `TasksController` for managing CRUD operations.
- Include exact method signatures (e.g., `getTasks(req, res)`, `createTask(req, res)`) and return types (e.g., `res.status(200).json({...})`).

### API Specification (if applicable)
```javascript
// Routes for tasks
const tasksRouter = express.Router();

// Get all tasks
tasksRouter.get('/', async (req, res) => {
  // ... implement logic to fetch and return tasks
});

// Create a new task
tasksRouter.post('/', async (req, res) => {
  // ... implement logic to create a new task and return it
});

// Update a task by id
tasksRouter.put('/:id', async (req, res) => {
  // ... implement logic to update an existing task and return it
});

// Delete a task by id
tasksRouter.delete('/:id', async (req, res) => {
  // ... implement logic to delete a task and return status
});
```

### Database Changes (if applicable)
```sql
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT false,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Testing Requirements
- Write unit tests for specific functions using a testing framework like Jest.
- Implement integration tests for specific flows using tools like Supertest and Nock.
- Store test files in the `tests` directory with appropriate naming conventions (e.g., `tasksController.test.js`).

### Acceptance Criteria (Enhanced)
- Each API endpoint has a detailed description, input/output examples, and error handling information as specified in the original task.
- The database schema is created according to the provided specifications.
- All functions are tested both unitarily and integrally with passing tests.
- Code adheres to the architecture's technology stack and design patterns.

---

