 Based on the provided requirements and constraints, here are some focused GitHub issues for development tasks:

**Database/Models**

1. Issue: Create User model with validation (2 pts)
   **Labels:** feature, Database
   **Estimate:** 2 story points
   **Description:** Implement the User model with required fields and validation rules.
   **Acceptance Criteria:**
   - [ ] The User model is created with necessary fields like id, username, email, and password.
   - [ ] Validation rules are set for each field to ensure data integrity.

2. Issue: Create Task model (2 pts)
   **Labels:** feature, Database
   **Estimate:** 2 story points
   - [ ] Implement the Task model with required fields like id, title, description, and status.
   - [ ] Define relationships between User and Task models if needed.

**API Endpoints**

1. Issue: Add POST /api/users endpoint (2 pts)
   **Labels:** feature, API
   **Estimate:** 2 story points
   **Description:** Implement the API endpoint for creating new users.
   **Acceptance Criteria:**
   - [ ] The POST /api/users endpoint is created and functional.
   - [ ] User data is validated before being saved to the database.

2. Issue: Add PUT /api/tasks/:id endpoint (3 pts)
   **Labels:** feature, API
   **Estimate:** 3 story points
   **Description:** Implement the API endpoint for updating task status based on its id.
   **Acceptance Criteria:**
   - [ ] The PUT /api/tasks/:id endpoint is created and functional.
   - [ ] Task status is updated correctly when the endpoint is called with a valid task id.

**Frontend Components**

1. Issue: Implement add task form component (3 pts)
   **Labels:** feature, Frontend
   **Estimate:** 3 story points
   **Description:** Create a reusable form component for adding new tasks.
   **Acceptance Criteria:**
   - [ ] The add task form is functional and user-friendly.
   - [ ] Validation rules are applied to the form inputs to ensure data integrity.

2. Issue: Implement task list component (3 pts)
   **Labels:** feature, Frontend
   **Estimate:** 3 story points
   **Description:** Create a reusable component for displaying and managing tasks in the user's task list.
   **Acceptance Criteria:**
   - [ ] The task list component is functional and user-friendly.
   - [ ] Tasks can be added, marked as done, and deleted from the list.

**Authentication**

1. Issue: Implement login form component (3 pts)
   **Labels:** feature, Authentication
   **Estimate:** 3 story points
   **Description:** Create a reusable login form component for user authentication.
   **Acceptance Criteria:**
   - [ ] The login form is functional and secure.
   - [ ] User credentials are validated against the database before granting access.

**Business Logic**

1. Issue: Implement task creation service (2 pts)
   **Labels:** feature, BusinessLogic
   **Estimate:** 2 story points
   **Description:** Create a service for handling the creation of new tasks and saving them to the database.
   **Acceptance Criteria:**
   - [ ] The task creation service is functional and saves tasks correctly to the database.

2. Issue: Implement task status update service (3 pts)
   **Labels:** feature, BusinessLogic
   **Estimate:** 3 story points
   **Description:** Create a service for handling the updating of task status based on user interaction with the UI.
   **Acceptance Criteria:**
   - [ ] The task status update service is functional and updates tasks correctly in the database.

**Testing**

1. Issue: Write unit tests for User model (2 pts)
   **Labels:** testing, Database
   **Estimate:** 2 story points
   **Description:** Write unit tests to ensure the correct functionality of the User model.
   **Acceptance Criteria:**
   - [ ] All methods and properties of the User model are tested with appropriate test cases.

2. Issue: Write unit tests for Task model (2 pts)
   **Labels:** testing, Database
   **Estimate:** 2 story points
   **Description:** Write unit tests to ensure the correct functionality of the Task model.
   **Acceptance Criteria:**
   - [ ] All methods and properties of the Task model are tested with appropriate test cases.

**Documentation**

1. Issue: Document API endpoints (2 pts)
   **Labels:** documentation, API
   **Estimate:** 2 story points
   **Description:** Write clear and concise documentation for each API endpoint.
   **Acceptance Criteria:**
   - [ ] Each API endpoint has a detailed description, input/output examples, and error handling information.