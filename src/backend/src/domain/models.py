```
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

class Task(BaseModel):
    title: str
    description: str
    status: Optional[str] = None

    class Config:
        orm_mode = True
```