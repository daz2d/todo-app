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

@app.post("/users/")
def create_user(user: User):
    try:
        engine = create_engine("sqlite:///users.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        user_exists = session.query(User).filter_by(username=user.username).first()
        if user_exists:
            raise HTTPException(status_code=400, detail="Username already exists")
        session.add(user)
        session.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}

@app.get("/users/")
def read_users():
    try:
        engine = create_engine("sqlite:///users.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        users = session.query(User).all()
        return {"users": [user.to_dict() for user in users]}
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}

@app.put("/users/{username}")
def update_user(username: str, user: User):
    try:
        engine = create_engine("sqlite:///users.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        user_exists = session.query(User).filter_by(username=username).first()
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        user_exists.email = user.email
        user_exists.password = user.password
        session.commit()
        return {"message": "User updated successfully"}
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}

@app.delete("/users/{username}")
def delete_user(username: str):
    try:
        engine = create_engine("sqlite:///users.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        user_exists = session.query(User).filter_by(username=username).first()
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user_exists)
        session.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}
```