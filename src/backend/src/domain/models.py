Here is an example of how you could implement the POST /api/users endpoint using FastAPI and Pydantic:
```
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str

engine = create_engine("sqlite:///users.db")
Session = sessionmaker(bind=engine)
session = Session()

@app.post("/api/users", response_model=User)
async def create_user(user: UserCreate = Depends()):
    user_data = user.dict()
    new_user = User(**user_data)
    session.add(new_user)
    session.commit()
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}
```
This code defines a `UserCreate` Pydantic model with the required fields for creating a user, and a `User` Pydantic model that represents the data of an existing user. The `create_user` endpoint is defined using FastAPI's `@app.post()` decorator, which takes a path parameter `/api/users` and a response model `User`.

The `create_user` function takes a `UserCreate` instance as an argument, validates it using FastAPI's `Depends()` decorator, creates a new `User` instance from the validated data, saves it to the database using SQLAlchemy, and returns a JSON response with the newly created user's data and a 201 Created status code.

To handle errors, you can use FastAPI's `HTTPException` class to raise custom error responses. For example:
```
from fastapi import HTTPException

@app.post("/api/users", response_model=User)
async def create_user(user: UserCreate = Depends()):
    # ...
    try:
        session.add(new_user)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to create user") from e
```
This code catches any exceptions that occur during the creation of a new user and raises an `HTTPException` with a 400 status code and a custom error message.