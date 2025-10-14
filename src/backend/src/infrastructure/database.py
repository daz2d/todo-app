import os
import sys

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
Session = sessionmaker(bind=engine)

# Define repository classes with database operations
class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Task]:
        return self.session.query(Task).all()

    def create(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        return task

    def update(self, task: Task) -> Task:
        self.session.merge(task)
        self.session.commit()
        return task

    def delete(self, id: int) -> None:
        task = self.session.query(Task).get(id)
        if task is not None:
            self.session.delete(task)
            self.session.commit()

# Define the Task model with validation rules using Sequelize's `check` method
class Task(BaseModel):
    title = StringField(max_length=255, check=["notEmpty"])
    description = TextField(max_length=1024, check=["notEmpty"])
    status = BooleanField(check=["isBoolean"])
    user_id = ForeignKey("User.id", check=["exists"])

# Define the User model with validation rules using Sequelize's `check` method
class User(BaseModel):
    email = StringField(max_length=255, check=["notEmpty", "isEmail"])
    password = StringField(max_length=1024, check=["notEmpty", "minLength(8)"])

# Define the API routes with FastAPI
app = FastAPI()

@app.get("/tasks")
def get_all_tasks():
    tasks = TaskRepository().get_all()
    return {"data": tasks}

@app.post("/tasks")
def create_task(task: Task):
    task = TaskRepository().create(task)
    return {"data": task}

@app.put("/tasks/{id}")
def update_task(id: int, task: Task):
    task = TaskRepository().update(task)
    return {"data": task}

@app.delete("/tasks/{id}")
def delete_task(id: int):
    TaskRepository().delete(id)
    return {"message": f"Task with id {id} deleted successfully"}
```
This code defines a `Task` model with validation rules using Sequelize's `check` method, and a `User` model with validation rules using Sequelize's `check` method. It also defines the repository classes for querying, creating, updating, and deleting tasks. The API routes are defined using FastAPI to handle HTTP requests and responses.

The code uses environment variables to store the database configuration, which can be set in a `.env` file or through other means of configuration. The `DB_HOST`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` environment variables are used to connect to the PostgreSQL database.

The `TaskRepository` class is responsible for querying, creating, updating, and deleting tasks in the database. It uses Sequelize's `sessionmaker` to create a session object that can be used to interact with the database. The `get_all`, `create`, `update`, and `delete` methods are implemented using Sequelize's query language to retrieve, create, update, and delete tasks in the database.

The `Task` model is defined with validation rules for the title, description, status, and user_id fields. The `User` model is also defined with validation rules for the email and password fields.

The API routes are defined using FastAPI to handle HTTP requests and responses. The `/tasks` route returns a list of all tasks in the database, while the `/tasks/{id}` route updates or deletes a specific task based on its ID. The `create_task` and `update_task` routes create and update tasks respectively, while the `delete_task` route deletes a task with a specific ID.

This code is written in Python using Sequelize for database operations and FastAPI for API routing. It uses environment variables to store the database configuration and defines validation rules for the Task and User models using Sequelize's `check` method.