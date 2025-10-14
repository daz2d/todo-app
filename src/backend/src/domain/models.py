```
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from passlib.hash import pbkdf2_sha256
import datetime

app = FastAPI()

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    try:
        user.password = pbkdf2_sha256.hash(user.password)
        db.add(user)
        db.commit()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input") from e

@app.get("/api/users", response_model=List[User])
async def read_users():
    users = db.query(User).all()
    return users

@app.post("/api/tasks", response_model=Task)
async def create_task(task: Task):
    try:
        task.user_id = 1 # Replace with the user ID of the logged-in user
        db.add(task)
        db.commit()
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input") from e

@app.get("/api/tasks", response_model=List[Task])
async def read_tasks():
    tasks = db.query(Task).all()
    return tasks

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    try:
        task.user_id = 1 # Replace with the user ID of the logged-in user
        db.query(Task).filter(Task.id == task_id).update(task)
        db.commit()
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input") from e

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    try:
        db.query(Task).filter(Task.id == task_id).delete()
        db.commit()
        return {"message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input") from e

@app.get("/api/token", response_model=str)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    try:
        pbkdf2_sha256.verify(form_data.password, user.password)
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid username or password") from e
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token}

def create_access_token(*, data: dict):
    to_encode = data.copy()
    expire = datetime.timedelta(minutes=30)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```