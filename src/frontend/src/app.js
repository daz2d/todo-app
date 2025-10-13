```
### JavaScript
```javascript
// Get references to the DOM elements
const form = document.querySelector('.todo-form');
const inputTitle = document.querySelector('input[name="title"]');
const inputDescription = document.querySelector('textarea[name="description"]');
const buttonAddTask = document.querySelector('button[type="submit"]');
const todoList = document.querySelector('.todo-list');

// Add event listener to the form
form.addEventListener('submit', handleFormSubmit);

// Function to handle form submission
function handleFormSubmit(event) {
  // Prevent default form behavior
  event.preventDefault();

  // Get the input values
  const title = inputTitle.value;
  const description = inputDescription.value;

  // Validate input
  if (!title) {
    alert('Please add a task');
    return;
  }

  // Make a POST request to the API
  fetch('/api/tasks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ title, description })
  })
    .then(response => response.json())
    .then(data => {
      // Clear the form inputs
      inputTitle.value = '';
      inputDescription.value = '';

      // Add the new task to the list
      const li = document.createElement('li');
      li.innerHTML = `
        <div class="view">
          <input class="toggle" type="checkbox"/>
          <label>${data.title}</label>
          <button class="destroy"></button>
        </div>
        <textarea class="edit">${data.description}</textarea>
      `;
      todoList.appendChild(li);
    });
}

// Function to handle task deletion
function handleTaskDeletion(event) {
  // Prevent default link behavior
  event.preventDefault();

  // Get the ID of the task to delete
  const id = event.target.dataset.id;

  // Make a DELETE request to the API
  fetch(`/api/tasks/${id}`, { method: 'DELETE' })
    .then(response => response.json())
    .then(data => {
      // Remove the task from the list
      const task = document.querySelector(`li[data-id="${id}"]`);
      todoList.removeChild(task);
    });
}

// Function to handle task toggle
function handleTaskToggle(event) {
  // Prevent default link behavior
  event.preventDefault();

  // Get the ID of the task to toggle
  const id = event.target.dataset.id;

  // Make a PUT request to the API
  fetch(`/api/tasks/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ completed: true })
  })
    .then(response => response.json())
    .then(data => {
      // Update the task in the list
      const task = document.querySelector(`li[data-id="${id}"]`);
      task.classList.toggle('completed');
    });
}
```