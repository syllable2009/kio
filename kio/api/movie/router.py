from __future__ import annotations

from fastapi import APIRouter, Depends

from kio.api.movie.dependencies import get_movie_service
from kio.exceptions import ApiCode
from kio.schemas import ApiResponse
from kio.services.movie_service import MovieService

router = APIRouter(prefix="/movie", tags=["movie"])


@router.get("", response_model=ApiResponse)
def list_movies(
    service: MovieService = Depends(get_movie_service),
) -> ApiResponse:
    """获取所有电影列表。"""
    return ApiResponse(code=ApiCode.SUCCESS.value, data=service.list_movies())


@router.get("/{movie_id}", response_model=ApiResponse)
def get_movie(
    movie_id: int, service: MovieService = Depends(get_movie_service)
) -> ApiResponse:
    """根据 ID 获取单个电影。"""
    return ApiResponse(code=ApiCode.SUCCESS.value, data=service.get_movie(movie_id))
