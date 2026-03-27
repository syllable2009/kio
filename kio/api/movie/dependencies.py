from __future__ import annotations

from kio.db.repositories.movie_repository import MovieRepository
from kio.services.movie_service import MovieService


def get_movie_service() -> MovieService:
    repo = MovieRepository()
    return MovieService(repo)
