 Based on the provided requirements and constraints, here are some focused GitHub issues for development tasks:

**Database/Models**
1. Issue: Create User model with validation
   **Labels:** database, User Management Context
   **Estimate:** 2 story points
   **Description:** Define a User model with fields for username, email, password, and role (user or admin). Implement validation rules for each field to ensure data integrity.
   **Acceptance Criteria:**
   - [ ] Username is unique across all users
   - [ ] Email is valid and unique across all users
   - [ ] Password meets minimum length and complexity requirements
   - [ ] Role is either 'user' or 'admin'

2. Issue: Create Task model with validation
   **Labels:** database, Task Management Context
   **Estimate:** 2 story points
   **Description:** Define a Task model with fields for title, description (optional), status, and assigned user ID. Implement validation rules to ensure data consistency.
   **Acceptance Criteria:**
   - [ ] Title is not empty
   - [ ] Status can only be 'incomplete' or 'completed'
   - [ ] Assigned user exists in the database

**API Endpoints**
1. Issue: Add POST /api/users endpoint
   **Labels:** API, User Management Context
   **Estimate:** 2 story points
   **Description:** Implement a POST endpoint for creating new users with proper request and response handling.
   **Acceptance Criteria:**
   - [ ] Returns a 201 Created status code upon successful creation
   - [ ] Returns an error message (4xx) if validation fails

2. Issue: Add GET /api/tasks endpoint
   **Labels:** API, Task Management Context
   **Estimate:** 2 story points
   **Description:** Implement a GET endpoint for retrieving all tasks for a specific user based on the provided JWT token.
   **Acceptance Criteria:**
   - [ ] Returns an array of tasks for the authenticated user
   - [ ] Returns an error message (4xx) if authentication fails or the user does not exist

**Frontend Components**
1. Issue: Implement login form component
   **Labels:** frontend, Authentication
   **Estimate:** 3 story points
   **Description:** Create a reusable login form that accepts username, email, and password inputs, and handles user authentication using the API endpoints.
   **Acceptance Criteria:**
   - [ ] User can successfully log in with valid credentials
   - [ ] User is redirected to the tasks list upon successful login
   - [ ] Error messages are displayed for invalid credentials or other errors

**Authentication**
1. Issue: Implement user registration
   **Labels:** Authentication, User Management Context
   **Estimate:** 3 story points
   **Description:** Create a user registration endpoint and form to allow new users to sign up with their email and password.
   **Acceptance Criteria:**
   - [ ] Returns a 201 Created status code upon successful registration
   - [ ] Sends an activation email to the newly registered user
   - [ ] User can activate their account by clicking on the provided link in the email

**Business Logic**
1. Issue: Implement task creation logic
   **Labels:** Business Logic, Task Management Context
   **Estimate:** 2 story points
   **Description:** Create a service method to handle the creation of new tasks using the API endpoint and store them in the database.
   **Acceptance Criteria:**
   - [ ] A new task is created in the database upon successful submission through the API
   - [ ] The newly created task is returned with a 201 Created status code

**Testing**
1. Issue: Write tests for User model and API endpoint
   **Labels:** Testing, User Management Context
   **Estimate:** 3 story points
   **Description:** Write unit tests to ensure the User model and associated API endpoint function correctly.
   **Acceptance Criteria:**
   - [ ] All validation rules are properly enforced
   - [ ] The API endpoint returns the correct response for valid and invalid requests

**Documentation**
1. Issue: Document user registration process
   **Labels:** Documentation, User Management Context
   **Estimate:** 1 story point
   **Description:** Write clear instructions on how users can register an account on the Todo List web application.
   **Acceptance Criteria:**
   - [ ] Instructions are easy to understand and follow
   - [ ] All necessary steps are included, including activation of the account via email