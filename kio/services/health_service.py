from __future__ import annotations

from kio.api.health.schemas import HealthResponse
from kio.db.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, repo: HealthRepository) -> None:
        self._repo = repo

    def health(self) -> HealthResponse:
        # 标准工程里这里可以做 DB ping / 外部依赖探活
        self._repo.ping()
        return HealthResponse(status="ok")

