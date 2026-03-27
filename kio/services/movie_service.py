from __future__ import annotations

from kio.api.movie.schemas import MovieListResponse, MovieResponse
from kio.db.repositories.movie_repository import MovieRepository
from kio.exceptions import ApiCode, NotFoundError


class MovieService:
    def __init__(self, repo: MovieRepository) -> None:
        self._repo = repo

    def list_movies(self) -> MovieListResponse:
        movies = self._repo.get_all()
        return MovieListResponse(movies=[MovieResponse(**m) for m in movies])

    def get_movie(self, movie_id: int) -> MovieResponse:
        movie = self._repo.get_by_id(movie_id)
        if movie is None:
            raise NotFoundError("Movie not found", api_code=ApiCode.MOVIE_NOT_FOUND)
        return MovieResponse(**movie)
