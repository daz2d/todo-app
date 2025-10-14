import os
import sys
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

# Import the Sequelize ORM and PostgreSQL adapter
from sequelize import Sequelize, Model
from sequelize_postgres import PostgreSQLAdapter

# Import the User model from the project's ORM configuration
from .models.user import User

# Define the Task model with fields for title, description, status (boolean), and user_id (foreign key)
class Task(Model):
    __tablename__ = 'tasks'

    id = Sequelize.Column(Sequelize.INTEGER, primary_key=True)
    title = Sequelize.Column(Sequelize.STRING, max_length=255, check=['notEmpty', 'max(255)'])
    description = Sequelize.Column(Sequelize.TEXT, max_length=1024, check=['notEmpty', 'max(1024)'])
    status = Sequelize.Column(Sequelize.BOOLEAN, check=['isBoolean'])
    user_id = Sequelize.Column(Sequelize.INTEGER, foreign_key='users.id')

# Define the API router and its endpoints
router = FastAPI()

@router.get('/tasks', response_model=List[Task])
def get_tasks(session: Session = Depends()):
    return session.query(Task).all()

@router.post('/tasks')
def create_task(task: Task, session: Session = Depends()):
    # Validate the task data using Sequelize's `check` method
    if not task.validate():
        raise HTTPException(status_code=400, detail='Invalid task data')

    # Create the task in the database
    session.add(task)
    session.commit()

    return task

@router.put('/tasks/{id}')
def update_task(id: int, task: Task, session: Session = Depends()):
    # Validate the task data using Sequelize's `check` method
    if not task.validate():
        raise HTTPException(status_code=400, detail='Invalid task data')

    # Update the task in the database
    session.query(Task).filter(Task.id == id).update(task)
    session.commit()

    return task

@router.delete('/tasks/{id}')
def delete_task(id: int, session: Session = Depends()):
    # Delete the task from the database
    session.query(Task).filter(Task.id == id).delete()
    session.commit()

    return {'message': f'Task {id} deleted successfully'}
```
This code defines a FastAPI application with endpoints for querying, creating, updating, and deleting tasks. The `Task` model is defined using Sequelize, with fields for title, description, status (boolean), and user_id (foreign key). Validation rules are defined using Sequelize's `check` method for each field. The API router is defined with endpoints for querying, creating, updating, and deleting tasks. The `get_tasks`, `create_task`, `update_task`, and `delete_task` functions are used to implement the corresponding endpoints.