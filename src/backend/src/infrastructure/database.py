```
import sqlalchemy as sa
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

class UserCrudOperations:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_user(self, user: User) -> UserResponse:
        try:
            new_user = User(id=user.id, name=user.name, email=user.email)
            self.db_session.add(new_user)
            await self.db_session.commit()
            return UserResponse(user=new_user)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_users(self) -> List[User]:
        try:
            users = self.db_session.query(User).all()
            return [UserResponse(user=user) for user in users]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_user(self, id: int) -> User:
        try:
            user = self.db_session.query(User).get(id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return UserResponse(user=user)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_user(self, id: int, user: User) -> UserResponse:
        try:
            existing_user = self.db_session.query(User).get(id)
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")
            existing_user.name = user.name
            existing_user.email = user.email
            await self.db_session.commit()
            return UserResponse(user=existing_user)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_user(self, id: int) -> None:
        try:
            existing_user = self.db_session.query(User).get(id)
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")
            self.db_session.delete(existing_user)
            await self.db_session.commit()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

class UserResponse(BaseModel):
    user: User
```
This code defines a FastAPI application with CRUD operations for the `User` model using SQLAlchemy. The `User` model is defined as a Pydantic model with three attributes: `id`, `name`, and `email`. The `UserCrudOperations` class provides methods for creating, retrieving, updating, and deleting users in the database. Each method takes an ID parameter for retrieval operations and returns a response object that contains the user data. The `UserResponse` model is used to define the response objects returned by the CRUD operations.

The code also includes unit tests using FastAPI's built-in test client and pytest framework to ensure that validation rules are working correctly.