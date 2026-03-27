from __future__ import annotations

from fastapi import APIRouter, Depends

from kio.api.user.dependencies import get_user_service
from kio.exceptions import ApiCode, NotFoundError
from kio.schemas import ApiResponse
from kio.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=ApiResponse)
def list_users(service: UserService = Depends(get_user_service)) -> ApiResponse:
    """获取所有用户列表。"""
    return ApiResponse(code=ApiCode.SUCCESS.value, data=service.list_users())


@router.get("/{user_id}", response_model=ApiResponse)
def get_user(
    user_id: int, service: UserService = Depends(get_user_service)
) -> ApiResponse:
    """根据 ID 获取单个用户。"""
    user = service.get_user(user_id)
    if user is None:
        raise NotFoundError("User not found", api_code=ApiCode.USER_NOT_FOUND)
    return ApiResponse(code=ApiCode.SUCCESS.value, data=user)
