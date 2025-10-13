# Enhanced Technical Tasks

## Task #1: Create User model with validation
**Labels:** database, Task Management Context
**Story Points:** 2
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create/modify: `src/models/user.ts` for defining the User model and its validation rules.
- Dependencies: Import necessary packages from TypeScript, Express.js, and PostgreSQL (if using an ORM like Sequelize or TypeORM).

### Implementation Details
- Use Express.js to create API endpoints for handling user registration and authentication.
- Follow the REST architecture style for designing API endpoints.
- Define a User class with properties for username, email, password, role, title, status, and assignedUserID.
- Implement validation rules using TypeScript interfaces and Express.js middleware functions such as `express-validator`.
  - Ensure the username is unique across all users by adding a custom validation function that checks the database for existing usernames.
  - Validate email format using built-in Express.js validators or third-party libraries like `email-validator`.
  - Implement password complexity and length requirements using regular expressions or external libraries like `bcrypt` for hashing and salting passwords.
  - Ensure the role is either 'user' or 'admin'.
  - Validate that the title is not empty.
  - Restrict the status to 'incomplete' or 'completed'.
  - Verify that the assigned user exists in the database by querying the database before creating a new user.

### API Specification (if applicable)
```json
POST /api/users
{
  "username": "<string>",
  "email": "<valid email>",
  "password": "<hashed password>",
  "role": "<'user' | 'admin'>",
  "title": "<non-empty string>",
  "status": "<'incomplete' | 'completed'>",
  "assignedUserID": <existing user ID>
}
```

### Database Changes (if applicable)
If using an ORM like Sequelize or TypeORM, create a User model with the specified properties and validation rules. Define the relationships between the User and other models if necessary.

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role VARCHAR(10) CHECK(role IN ('user', 'admin')),
  title TEXT NOT NULL,
  status VARCHAR(15) CHECK(status IN ('incomplete', 'completed')),
  assigned_user_id INT REFERENCES users(id)
);
```

### Testing Requirements
- Write unit tests for the User model and validation functions using a testing framework like Jest or Mocha.
- Perform integration tests to ensure that user registration works correctly with the API endpoints, database, and authentication methods.

### Acceptance Criteria (Enhanced)
- A developer should be able to create a User model with the specified properties and validation rules using TypeScript, Express.js, and PostgreSQL (or an ORM).
- The user registration endpoint should accept the provided JSON payload, validate it according to the defined rules, and store the new user in the database if valid.
- If any validation errors occur, the API should return a meaningful error message to the client.
- The user registration process should work seamlessly with authentication methods like JWT for secure user sessions.

---

## Task #2: Add POST /api/users endpoint
**Labels:** API, Task Management Context
**Story Points:** 2
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create: `src/api/users/userController.ts`
- Dependencies: Import Express, JWT, and any necessary models or utilities from your project.

### Implementation Details
- Use the Express.js web framework to create a new POST endpoint at `/api/users`.
- Authenticate incoming requests using JSON Web Tokens (JWT).
- Validate user input data using TypeScript type checking and any necessary validation libraries.
- If validation fails, return an error message with a 4xx status code.
- Retrieve the authenticated user from your database using their ID or other appropriate identifier.
- If authentication fails, the user does not exist, or there is an error during data retrieval, return an error message with a 4xx status code.
- If everything is successful, create a new user in your database and return a 201 Created status code along with the newly created user's tasks.

### API Specification (if applicable)
```javascript
app.post('/api/users', authenticate, async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    if (!user) return res.status(404).json({ error: 'User not found' });

    // Implement the logic to create new tasks for the user here

    res.status(201).json(user.tasks);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'An error occurred while processing your request' });
  }
});
```

### Database Changes (if applicable)
- Create a `User` model with properties for the user's tasks and any other necessary data.
- Ensure that your database schema supports storing arrays or relationships for tasks associated with each user.

### Testing Requirements
- Write unit tests for the `userController.ts` file to test specific functions like authentication, validation, and task creation.
- Write integration tests to test end-to-end scenarios such as creating a new user and retrieving their tasks.
- Store your tests in appropriate folders within your project (e.g., `src/tests`).

### Acceptance Criteria (Enhanced)
- Returns a 201 Created status code upon successful creation of the user's tasks.
- Validates incoming data and returns an error message with a 4xx status code if validation fails.
- Retrieves the authenticated user from your database and returns their tasks.
- Returns an error message with a 4xx status code if authentication fails, the user does not exist, or there is an error during data retrieval.
- Passes all unit tests and integration tests related to this task.

---

## Task #3: Implement login form component
**Labels:** frontend, Authentication
**Story Points:** 3
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create/modify: `frontend/src/components/LoginForm.tsx`
- Dependencies: Import React, TypeScript, and any necessary third-party libraries such as Axios for API calls.

### Implementation Details
- Use the React library to create a functional component called `LoginForm`.
- Inside this component, define three controlled inputs for username, email, and password using the `useState` hook.
- Create a form element with these inputs and an submit button.
- On form submission, validate user input using regular expressions or other validation methods to ensure the entered data is in the correct format (e.g., email should be a valid email address).
- If validation passes, make an API call to the authentication endpoint using Axios, passing the username, email, and password as request body parameters.
- Handle the response from the API call:
  - If successful login, redirect the user to the tasks list page (`/tasks`) using the `useHistory` hook from React Router.
  - In case of invalid credentials or other errors, display error messages to the user.

### API Specification (if applicable)
Assuming the authentication endpoint is defined as follows:
```
POST /api/auth/login

Request body:
{
  "username": string,
  "email": string,
  "password": string
}

Response:
{
  "accessToken": string,
  "refreshToken": string,
  "expiresIn": number,
  "error": null (if successful) or an error message (in case of failure)
}
```
### Database Changes (if applicable)
- No database changes are required for this task as the authentication process is handled by the backend.

### Testing Requirements
- Write unit tests for the `LoginForm` component to test its functionality, including form validation and API call handling.
- Use a testing library such as Jest or Mocha for writing these tests.
- Create test files in a separate folder (e.g., `frontend/src/tests/components/LoginForm.test.tsx`).

### Acceptance Criteria (Enhanced)
- User can successfully log in with valid credentials by providing a valid username, email, and password in the provided form.
- Upon successful login, the user is redirected to the tasks list page (`/tasks`).
- Error messages are displayed for invalid credentials or other errors during the login process.
- Unit tests for the `LoginForm` component pass with no failures.

---

## Task #4: Implement user registration
**Labels:** Authentication, User Management Context
**Story Points:** 3
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create: `src/routes/auth/register.ts`
- Modify: `src/controllers/UserController.ts`, `src/services/EmailService.ts`, and `src/models/User.ts`
- Dependencies: Import Express, JWT, bcryptjs, nodemailer, and mongoose

### Implementation Details
- Use Express.js for routing and API creation
- Implement a POST method at `/api/auth/register` endpoint
- In the UserController, create a `register` function that handles the registration logic
  - Validate user input using Joi or similar validation library
  - Hash the password using bcryptjs
  - Save the new user to the database using Mongoose
- Send an activation email to the newly registered user using nodemailer
- Return a 201 Created status code and a JSON response with a message and the user's ID

### API Specification (if applicable)
```json
POST /api/auth/register
{
  "email": "<user email>",
  "password": "<hashed password>"
}

Response:
{
  "message": "User registered successfully. Please activate your account.",
  "userId": "<generated user id>"
}
```

### Database Changes (if applicable)
- Add a new `users` collection to the PostgreSQL database with the following schema:

```sql
CREATE TABLE users (
    userId SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    passwordHash TEXT NOT NULL,
    isActive BOOLEAN DEFAULT false,
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Testing Requirements
- Unit tests for the `register` function in UserController.ts
- Integration tests for the registration flow, including email sending and account activation
- Place test files under `src/tests/unit` and `src/tests/integration`, respectively

### Acceptance Criteria (Enhanced)
- Returns a 201 Created status code upon successful registration
  - Include the user's ID in the response JSON
- Sends an activation email to the newly registered user
  - The email contains a unique link for account activation
- User can activate their account by clicking on the provided link in the email
  - Upon activation, the `isActive` field in the user document is set to true in the database

---

## Task #5: Implement task creation logic
**Labels:** Business Logic, Task Management Context
**Story Points:** 2
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create: `src/services/taskService.ts`
- Dependencies: Import Express, PostgreSQL client (e.g., `pg`), and any necessary interfaces or models from the project context.

### Implementation Details
- Use Express.js to create a new API endpoint for task creation at `/api/tasks`.
- Implement a method called `createTask(task: Task)` in the `taskService` class, which takes a `Task` object as an argument and handles the creation of tasks using the PostgreSQL database.
- The `Task` object should have properties such as `title`, `description`, `status`, and any other necessary fields defined by the project context.

### API Specification (if applicable)
```json
POST /api/tasks
Request Body:
{
  "title": "string",
  "description": "string",
  // include other properties as needed
}
Response:
{
  "statusCode": 201,
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    // include other properties as needed
  }
}
```
### Database Changes (if applicable)
```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  title VARCHAR(255),
  description TEXT,
  status BOOLEAN DEFAULT false,
  // include other fields as needed
);
```
### Testing Requirements
- Write unit tests for the `createTask` method in a separate file (e.g., `src/tests/taskService.test.ts`) using a testing framework such as Jest or Mocha.
- Include integration tests for the task creation flow, ensuring that data is correctly saved to the database and returned through the API.

### Acceptance Criteria (Enhanced)
- A new `Task` object with the provided data is created in the PostgreSQL database upon successful submission through the API.
- The newly created `Task` object is returned with a 201 Created status code and included in the response body.
- Unit tests for the `createTask` method pass without any errors or failures.
- Integration tests for the task creation flow pass without any errors or failures.

---

## Task #6: Write tests for User model and API endpoint
**Labels:** Testing, User Management Context
**Story Points:** 3
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create/modify: `src/api/user.ts` (Backend) and `src/components/UserForm.tsx` (Frontend)
- Dependencies: Import Express, TypeORM, JWT, bcryptjs, cors, and any necessary React components

### Implementation Details

#### Backend

1. Define the User model with properties such as `id`, `username`, `password`, and any other required fields.
2. Create a UserRepository that extends TypeORM's Repository class to handle database operations.
3. Implement authentication middleware using JWT for securing API endpoints.
4. Implement the following API endpoints:
   - POST /api/users (Create a new user)
     - Request body example: `{ "username": "exampleUser", "password": "examplePassword" }`
     - Response example: `{ "id": 1, "username": "exampleUser" }`
   - PUT /api/users/:id (Update an existing user)
     - Request body example: `{ "username": "newUsername", "password": "newPassword" }`
     - Response example: `{ "id": 1, "username": "newUsername" }`
   - DELETE /api/users/:id (Delete a user)
     - Response example: `{ "message": "User deleted successfully" }`

#### Frontend

1. Create a UserForm component to handle user input and communicate with the backend API.
2. Implement functions for creating, updating, and deleting users based on the API endpoints defined above.
3. Use React hooks such as `useState` and `useEffect` to manage local state and fetch data from the API when needed.
4. Ensure proper error handling for any API errors or invalid user input.

### Database Changes (if applicable)
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);
```

### Testing Requirements
- Write unit tests for the User model and API endpoints using a testing framework such as Jest.
- Ensure that all validation rules are properly enforced (e.g., unique usernames, strong passwords).
- Test edge cases to ensure robustness and handle unexpected input or errors gracefully.
- Test integration with the frontend UserForm component to verify proper communication between components.

### Acceptance Criteria (Enhanced)
- All validation rules are properly enforced in both backend and frontend.
- The API endpoint returns the correct response for valid and invalid requests.
- The UserForm correctly handles user input and communicates with the backend API.
- Unit tests pass for all functions related to the User model and API endpoints.
- Integration tests pass for specific flows involving the UserForm and backend API.

---

## Task #7: Document user registration process
**Labels:** Documentation, User Management Context
**Story Points:** 1
**Priority:** Medium Priority

 ## Technical Implementation

### File Structure
- Create/modify: `backend/src/userManagement/userRegistration.ts`
- Dependencies: Import Express, JWT, bcryptjs, and mongoose from their respective packages

### Implementation Details
- Use the Express web framework to create a new API endpoint for user registration
- Utilize TypeScript for static typing and better error handling
- Create a `User` model using Mongoose to interact with the MongoDB database
- Implement a `register` function that accepts a request body containing user data (username, email, password)
- Hash the provided password using bcryptjs before storing it in the database
- Generate a JWT token upon successful registration and return it along with the user data in the response
- Handle errors such as validation errors, duplicate emails, and internal server errors appropriately

### API Specification (if applicable)
```javascript
app.post('/api/users/register', async (req, res) => {
  try {
    const user = await User.create(req.body);
    const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET);
    res.json({ user, token });
  } catch (err) {
    // Handle errors and return appropriate response
  }
});
```

### Database Changes (if applicable)
```sql
// In the User schema definition:
const userSchema = new mongoose.Schema({
  username: String,
  email: String,
  password: String,
  // Other fields as needed
});
userSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  const salt = await bcryptjs.genSalt(10);
  this.password = await bcryptjs.hash(this.password, salt);
});
```

### Testing Requirements
- Write unit tests for the `User` model and the `register` function using a testing framework like Jest or Mocha
- Write integration tests to verify the registration flow, including email activation (if applicable)
- Store test files in the appropriate folder within the `tests` directory

### Acceptance Criteria (Enhanced)
- The provided instructions are easy to understand and follow for a developer
- All necessary steps for user registration, including hashing passwords and generating JWT tokens, are included
- The API endpoint is specified with exact method signature and return type
- Database schema changes for the `User` model are provided
- Import statements and dependencies needed for the task are listed
- Error handling requirements are outlined to ensure robustness and resilience of the implementation
- Testing requirements specific to user registration are detailed, including unit tests and integration tests

---

