from __future__ import annotations


class MovieRepository:
    """电影数据访问层（Mock 数据）。"""

    _MOCK_MOVIES = [
        {"id": 1, "title": "肖申克的救赎", "director": "弗兰克·德拉邦特", "year": 1994},
        {"id": 2, "title": "霸王别姬", "director": "陈凯歌", "year": 1993},
        {"id": 3, "title": "阿甘正传", "director": "罗伯特·泽米吉斯", "year": 1994},
    ]

    def get_all(self) -> list[dict]:
        return self._MOCK_MOVIES

    def get_by_id(self, movie_id: int) -> dict | None:
        for movie in self._MOCK_MOVIES:
            if movie["id"] == movie_id:
                return movie
        return None
