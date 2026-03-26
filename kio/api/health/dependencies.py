from __future__ import annotations

from kio.db.repositories.health_repository import HealthRepository
from kio.services.health_service import HealthService


def get_health_service() -> HealthService:
    repo = HealthRepository()
    return HealthService(repo)
