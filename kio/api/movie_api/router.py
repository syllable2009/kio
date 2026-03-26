from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from kio.api.movie_api.dependencies import get_movie_service
from kio.api.movie_api.schemas import MovieListResponse, MovieResponse
from kio.services.movie_service import MovieService

router = APIRouter(prefix="/movie", tags=["movie"])


@router.get("", response_model=MovieListResponse)
def list_movies(
    service: MovieService = Depends(get_movie_service),
) -> MovieListResponse:
    """获取所有电影列表。"""
    return service.list_movies()


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int, service: MovieService = Depends(get_movie_service)
) -> MovieResponse:
    """根据 ID 获取单个电影。"""
    movie = service.get_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
