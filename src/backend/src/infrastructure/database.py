Here is an example of how you could implement the POST /api/users endpoint using FastAPI and SQLAlchemy:
```
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

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

class UsersRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        new_user = User(username=user.username, email=user.email, password=user.password)
        self.db.add(new_user)
        self.db.commit()
        return new_user

@app.post("/api/users")
def create_user(user: UserCreate = Depends(), db: Session = Depends(UsersRepository)) -> User:
    try:
        user = db.create_user(user)
        return JSONResponse(status_code=201, content={"data": {"id": user.id, "username": user.username, "email": user.email}})
    except HTTPException as e:
        raise e
```
This code defines a `UserCreate` Pydantic model for creating new users, and a `User` Pydantic model for representing existing users in the database. It also defines a `UsersRepository` class with a `create_user()` method that creates a new user instance from the validated data and saves it to the database using SQLAlchemy.

The `create_user()` method is decorated with `@app.post("/api/users")` and takes two arguments: `user` (a `UserCreate` instance) and `db` (a `Session` object). The `Depends()` function is used to inject the `UsersRepository` class into the method, so that it can be used to create new users in the database.

The method first tries to create a new user instance from the validated data using the `create_user()` method of the `UsersRepository` class. If this succeeds, it returns a JSON response with the newly created user's data and a 201 Created status code. If an error occurs during the creation process, the method raises an HTTPException with the appropriate error message.

This implementation follows the architecture specification by using FastAPI for routing and Pydantic for data validation, and it includes proper error handling to ensure that any errors that occur during the creation process are handled appropriately.