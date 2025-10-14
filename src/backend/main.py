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