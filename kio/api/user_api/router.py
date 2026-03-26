from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from kio.api.user_api.dependencies import get_user_service
from kio.api.user_api.schemas import UserListResponse, UserResponse
from kio.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=UserListResponse)
def list_users(service: UserService = Depends(get_user_service)) -> UserListResponse:
    """获取所有用户列表。"""
    return service.list_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, service: UserService = Depends(get_user_service)
) -> UserResponse:
    """根据 ID 获取单个用户。"""
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
