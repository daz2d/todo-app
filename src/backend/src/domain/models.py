```
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    password: Optional[str] = None

    class Config:
        orm_mode = True
```
This code defines a `User` model using Pydantic's `BaseModel`. The `id`, `name`, and `email` fields are required, while the `password` field is optional. The `Config` class specifies that the ORM mode should be used for this model.

To test this code, you can use FastAPI's built-in test client and pytest framework to create a test suite that validates the input data and ensures that the validation rules are working correctly. Here is an example of how you could write such a test:
```
import pytest
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    user = {"id": 1, "name": "John Doe", "email": "johndoe@example.com"}
    response = client.post("/users", json=user)
    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["name"] == "John Doe"
    assert response.json()["email"] == "johndoe@example.com"
```
This test creates a new user with an ID of 1, name of "John Doe", and email address of "johndoe@example.com". It then sends a POST request to the `/users` endpoint with this data, and checks that the response has a status code of 201 (created), and that the JSON response contains the expected user ID, name, and email address.

You can also write tests for other methods in the `UserCrudOperations` class, such as retrieving a specific user by ID, updating a user's information, or deleting a user. These tests would use similar code to the one above, but with different endpoints and input data.