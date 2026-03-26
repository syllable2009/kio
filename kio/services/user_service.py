from __future__ import annotations

from kio.api.user_api.schemas import UserListResponse, UserResponse
from kio.db.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def list_users(self) -> UserListResponse:
        users = self._repo.get_all()
        return UserListResponse(users=[UserResponse(**u) for u in users])

    def get_user(self, user_id: int) -> UserResponse | None:
        user = self._repo.get_by_id(user_id)
        if user is None:
            return None
        return UserResponse(**user)
