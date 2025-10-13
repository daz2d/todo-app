 Based on the provided requirements and constraints, here are some focused GitHub issues for development tasks:

**Database/Models**
1. Issue: Create User model with validation
   **Labels:** database, user-management
   **Estimate:** 2 story points
   **Description:** Implement a User model in our chosen ORM (e.g., Sequelize) with fields for username, email, and password. Add validation rules to ensure proper data integrity.
   **Acceptance Criteria:**
   - [ ] A valid User instance can be created without errors.
   - [ ] Invalid User instances are rejected with appropriate error messages.

2. Issue: Create Task model with validation
   **Labels:** database, task-management
   **Estimate:** 2 story points
   **Description:** Implement a Task model in our chosen ORM (e.g., Sequelize) with fields for title, description, status, and user_id (foreign key). Add validation rules to ensure proper data integrity.
   **Acceptance Criteria:**
   - [ ] A valid Task instance can be created without errors.
   - [ ] Invalid Task instances are rejected with appropriate error messages.

**API Endpoints**
1. Issue: Add POST /api/users endpoint
   **Labels:** api, user-management
   **Estimate:** 2 story points
   **Description:** Implement a RESTful API endpoint for creating new users (POST /api/users).
   **Acceptance Criteria:**
   - [ ] A new User instance can be created and saved to the database upon successful POST request.
   - [ ] The response includes a status code of 201 Created and the newly created user's data.

2. Issue: Add GET /api/tasks endpoint
   **Labels:** api, task-management
   **Estimate:** 3 story points
   **Description:** Implement a RESTful API endpoint for retrieving all tasks (GET /api/tasks).
   **Acceptance Criteria:**
   - [ ] All Task instances can be retrieved and returned as JSON.
   - [ ] The response includes a status code of 200 OK.

**Frontend Components**
1. Issue: Implement login form component
   **Labels:** frontend, authentication
   **Estimate:** 3 story points
   **Description:** Create a reusable login form component that handles user input and communicates with the API for authentication.
   **Acceptance Criteria:**
   - [ ] The login form can be rendered on the page.
   - [ ] Upon successful submission, the user is authenticated and redirected to the Todo List.
   - [ ] Upon unsuccessful submission (e.g., invalid credentials), an error message is displayed.

**Business Logic**
1. Issue: Implement task creation service method
   **Labels:** business-logic, task-management
   **Estimate:** 2 story points
   **Description:** Create a service method for creating new tasks and associating them with the authenticated user.
   **Acceptance Criteria:**
   - [ ] A new Task instance can be created and saved to the database upon successful API request.
   - [ ] The response includes a status code of 201 Created and the newly created task's data.

**Testing**
1. Issue: Write unit tests for User model
   **Labels:** testing, user-management
   **Estimate:** 2 story points
   **Description:** Write unit tests to ensure proper validation and database interaction of the User model.
   **Acceptance Criteria:**
   - [ ] All test cases pass without any failures or errors.

**Documentation**
1. Issue: Write setup instructions for new team members
   **Labels:** documentation, onboarding
   **Estimate:** 2 story points
   **Description:** Write clear and concise setup instructions for new team members to quickly get up-to-speed with the project.
   **Acceptance Criteria:**
   - [ ] The instructions are easy to follow and include all necessary steps for setting up the development environment, including dependencies, database configuration, and API endpoints.