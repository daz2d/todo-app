```
import json
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, Task

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    db = get_db()
    user.hashed_password = bcrypt.hashpw(user.password, bcrypt.gensalt())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/api/users", response_model=List[User])
async def get_users():
    db = get_db()
    users = db.query(User).all()
    return users

@app.post("/api/tasks", response_model=Task)
async def create_task(task: Task, current_user: User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = get_db()
    task.owner_id = current_user.id
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    db = get_db()
    tasks = db.query(Task).all()
    return tasks

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    db = get_db()
    task.owner_id = current_user.id
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    db = get_db()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
```