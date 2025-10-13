 Based on the provided requirements and constraints, here are some focused GitHub issues for development tasks:

**Database/Models**
1. Issue: Create User model with validation
   **Labels:** database, models
   **Estimate:** 2 story points
   **Description:** Implement a User model with validation for email and password fields.
   **Acceptance Criteria:**
   - [ ] The User model is created with required fields (email, password).
   - [ ] Validation is implemented for email and password fields to ensure proper format.

2. Issue: Create Task model with validation
   **Labels:** database, models
   **Estimate:** 2 story points
   **Description:** Implement a Task model with validation for title and description fields.
   **Acceptance Criteria:**
   - [ ] The Task model is created with required fields (title, description).
   - [ ] Validation is implemented for title and description fields to ensure proper format.

**API Endpoints**
1. Issue: Add POST /api/users endpoint
   **Labels:** api, authentication
   **Estimate:** 2 story points
   **Description:** Implement a POST endpoint at /api/users for user registration.
   **Acceptance Criteria:**
   - [ ] A new user can be created by sending a POST request to the /api/users endpoint with valid data.
   - [ ] The response includes a status code 201 (Created) and the newly created user's data.

2. Issue: Add PUT /api/tasks/:id endpoint
   **Labels:** api, task management
   **Estimate:** 2 story points
   **Description:** Implement a PUT endpoint at /api/tasks/:id for updating a specific task.
   **Acceptance Criteria:**
   - [ ] A task can be updated by sending a PUT request to the appropriate endpoint with valid data.
   - [ ] The response includes a status code 200 (OK) and the updated task's data.

**Frontend Components**
1. Issue: Implement login form component
   **Labels:** frontend, authentication
   **Estimate:** 3 story points
   **Description:** Create a reusable login form component that handles user authentication.
   **Acceptance Criteria:**
   - [ ] A user can log in by entering their email and password and clicking the login button.
   - [ ] The response includes a status code 200 (OK) if the login is successful, or an error message if it fails.

2. Issue: Implement task list component
   **Labels:** frontend, task management
   **Estimate:** 3 story points
   **Description:** Create a reusable task list component that displays and manages tasks.
   **Acceptance Criteria:**
   - [ ] Tasks are displayed in a list format with the ability to mark them as done or delete them.
   - [ ] The user can add new tasks by clicking an "Add Task" button and entering a title and description.

**Authentication**
1. Issue: Implement email validation
   **Labels:** authentication, business logic
   **Estimate:** 2 story points
   **Description:** Implement a function to validate the format of user emails.
   **Acceptance Criteria:**
   - [ ] The function returns true if the email is valid and false otherwise.

**Business Logic**
1. Issue: Implement task status management
   **Labels:** business logic, task management
   **Estimate:** 2 story points
   **Description:** Implement functions to mark tasks as done or undone.
   **Acceptance Criteria:**
   - [ ] A task can be marked as done by calling the appropriate function and passing the task's ID.
   - [ ] The task's status is updated in the database accordingly.

**Testing**
1. Issue: Write tests for user model validation
   **Labels:** testing, models
   **Estimate:** 2 story points
   **Description:** Write unit tests to ensure the User model's validation works as expected.
   **Acceptance Criteria:**
   - [ ] All test cases pass with the correct results.

**Documentation**
1. Issue: Document user registration API endpoint
   **Labels:** documentation
   **Estimate:** 1 story point
   **Description:** Write clear and concise documentation for the POST /api/users endpoint.
   **Acceptance Criteria:**
   - [ ] The documentation includes a description of the endpoint, required request body fields, response format, and example requests and responses.