```
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
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

@app.delete("/users/{id}")
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