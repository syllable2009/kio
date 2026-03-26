from __future__ import annotations

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class UserListResponse(BaseModel):
    users: list[UserResponse]

