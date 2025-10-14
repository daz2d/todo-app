```
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()

class User(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

@app.post("/users/", response_model=User)
async def create_user(user: User):
    try:
        engine = create_engine("sqlite:///users.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        user.save(session)
        session.commit()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/", response_model=list[User])
async def read_users():
    try:
        engine = create_engine("sqlite:///users.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        users = User.objects.all()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/users/{id}", response_model=User)
async def update_user(id: int, user: User):
    try:
        engine = create_engine("sqlite:///users.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        user.save(session)
        session.commit()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/users/{id}", response_model=User)
async def delete_user(id: int):
    try:
        engine = create_engine("sqlite:///users.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        user = User.objects.get(id=id)
        user.delete(session)
        session.commit()
        return {"message": f"User with id {id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```
This code creates a FastAPI app with endpoints for creating, reading, updating, and deleting users. The `User` model is defined using Pydantic, which provides data validation and serialization. The `create_user`, `read_users`, `update_user`, and `delete_user` functions are used to create, read, update, and delete users in the database. The `HTTPException` is raised if there is an error during any of these operations.

# Add GET /api/users endpoint
```
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError, decode
from datetime import timedelta
from typing import Optional

app = FastAPI()

engine = create_engine("sqlite:///users.db")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tasks = relationship("Task", backref="user")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    try:
        db = SessionLocal()
        db.add(user)
        db.commit()
        db.close()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users", response_model=List[User])
async def read_users():
    try:
        db = SessionLocal()
        users = db.query(User).all()
        db.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/tasks", response_model=Task)
async def create_task(task: Task):
    try:
        db = SessionLocal()
        db.add(task)
        db.commit()
        db.close()
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tasks", response_model=List[Task])
async def read_tasks():
    try:
        db = SessionLocal()
        tasks = db.query(Task).all()
        db.close()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(user.username, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/me", response_model=User)
async def read_users_me():
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.username == "").first()
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tasks/{task_id}", response_model=Task)
async def read_task(task_id: int):
    try:
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    try:
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task.title = task.title
        task.description = task.description
        task.completed = task.completed
        db.commit()
        db.close()
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/tasks/{task_id}", response_model=Task)
async def delete_task(task_id: int):
    try:
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(task)
        db.commit()
        db.close()
        return {"message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown():
    await db.close()
```