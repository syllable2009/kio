from __future__ import annotations

from kio.db.repositories.user_repository import UserRepository
from kio.services.user_service import UserService


def get_user_service() -> UserService:
    repo = UserRepository()
    return UserService(repo)
