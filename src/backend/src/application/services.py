import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.task import Task

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/tasks", response_model=Task)
async def create_task(task: Task, db: Session = Depends(get_db)):
    try:
        db.add(task)
        db.commit()
        logger.info("Task created successfully")
        return task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail="Failed to create task")

@router.get("/tasks", response_model=List[Task])
async def get_all_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).all()
        logger.info("Tasks retrieved successfully")
        return tasks
    except Exception as e:
        logger.error(f"Error retrieving tasks: {e}")
        raise HTTPException(status_code=400, detail="Failed to retrieve tasks")

@router.get("/tasks/{id}", response_model=Task)
async def get_task_by_id(id: int, db: Session = Depends(get_db)):
    try:
        task = db.query(Task).filter(Task.id == id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        logger.info("Task retrieved successfully")
        return task
    except Exception as e:
        logger.error(f"Error retrieving task by ID: {e}")
        raise HTTPException(status_code=400, detail="Failed to retrieve task")

@router.put("/tasks/{id}", response_model=Task)
async def update_task(id: int, task: Task, db: Session = Depends(get_db)):
    try:
        existing_task = db.query(Task).filter(Task.id == id).first()
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
        for key, value in task.items():
            setattr(existing_task, key, value)
        db.commit()
        logger.info("Task updated successfully")
        return existing_task
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=400, detail="Failed to update task")

@router.delete("/tasks/{id}", response_model=Task)
async def delete_task(id: int, db: Session = Depends(get_db)):
    try:
        existing_task = db.query(Task).filter(Task.id == id).first()
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(existing_task)
        db.commit()
        logger.info("Task deleted successfully")
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=400, detail="Failed to delete task")