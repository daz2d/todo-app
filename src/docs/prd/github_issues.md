 Based on the provided requirements and constraints, here are some focused GitHub issues for development tasks:

### Database/Models
1. Issue: Create User model with validation (2 pts)
   **Labels:** feature, database
   **Estimate:** 2 story points
   **Description:** Create a User model with fields for username, email, and password. Implement validation rules to ensure the data is well-formed and secure.
   **Acceptance Criteria:**
   - [ ] The User model has been created with required fields.
   - [ ] Validation rules have been implemented for each field in the User model.

2. Issue: Create Task model with validation (2 pts)
   **Labels:** feature, database
   **Estimate:** 2 story points
   - [ ] The Task model has been created with required fields such as title, description, and status.
   - [ ] Validation rules have been implemented for each field in the Task model.

### API Endpoints
1. Issue: Add GET /api/users endpoint (2 pts)
   **Labels:** feature, api
   **Estimate:** 2 story points
   - [ ] Implement a GET endpoint to retrieve all users from the database.
   - [ ] Ensure proper authentication and authorization for the endpoint.

2. Issue: Add POST /api/users endpoint (2 pts)
   **Labels:** feature, api
   **Estimate:** 2 story points
   - [ ] Implement a POST endpoint to create new users in the database.
   - [ ] Ensure proper authentication and authorization for the endpoint.

### Frontend Components
1. Issue: Implement login form component (3 pts)
   **Labels:** feature, frontend
   **Estimate:** 3 story points
   - [ ] Create a reusable login form component that handles user input and submits requests to the API for authentication.
   - [ ] Ensure proper error handling and user feedback when login fails or succeeds.

2. Issue: Implement task list component (3 pts)
   **Labels:** feature, frontend
   **Estimate:** 3 story points
   - [ ] Create a reusable task list component that displays tasks in a clean, modern format and allows users to interact with them (create, edit, mark as completed/incomplete, delete).
   - [ ] Implement filtering and searching functionality for the task list.

### Authentication
1. Issue: Implement login service (3 pts)
   **Labels:** feature, authentication
   **Estimate:** 3 story points
   - [ ] Create a service that handles user authentication by validating credentials against the database and returning an authenticated user object if successful.

2. Issue: Implement logout functionality (1 pt)
   **Labels:** feature, authentication
   **Estimate:** 1 story point
   - [ ] Implement a logout function that removes the authenticated user from the application's context and redirects the user to the login page.

### Business Logic
1. Issue: Implement task creation service (2 pts)
   **Labels:** feature, business logic
   **Estimate:** 2 story points
   - [ ] Create a service that handles creating new tasks in the database and returns them to the client.
   - [ ] Ensure proper validation of task data before saving it to the database.

2. Issue: Implement task updating service (2 pts)
   **Labels:** feature, business logic
   **Estimate:** 2 story points
   - [ ] Create a service that handles updating existing tasks in the database based on user input.
   - [ ] Ensure proper validation of task data before saving it to the database.

### Testing
1. Issue: Write unit tests for User model (2 pts)
   **Labels:** testing, database
   **Estimate:** 2 story points
   - [ ] Write unit tests for the User model to ensure that validation rules are working correctly and that data is being saved and retrieved properly.

2. Issue: Write unit tests for Task model (2 pts)
   **Labels:** testing, database
   **Estimate:** 2 story points
   - [ ] Write unit tests for the Task model to ensure that validation rules are working correctly and that data is being saved and retrieved properly.

### Documentation
1. Issue: Write setup instructions (2 pts)
   **Labels:** documentation
   **Estimate:** 2 story points
   - [ ] Create clear, concise setup instructions for new team members or external collaborators to easily onboard and start contributing to the project.

2. Issue: Write API documentation (3 pts)
   **Labels:** documentation
   **Estimate:** 3 story points
   - [ ] Write comprehensive API documentation that includes details about each endpoint, its purpose, required parameters, and expected responses.