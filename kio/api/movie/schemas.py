from __future__ import annotations

from pydantic import BaseModel


class MovieResponse(BaseModel):
    id: int
    title: str
    director: str
    year: int


class MovieListResponse(BaseModel):
    movies: list[MovieResponse]

