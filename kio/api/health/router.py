from __future__ import annotations

from fastapi import APIRouter, Depends

from kio.api.health.dependencies import get_health_service
from kio.api.health.schemas import HealthResponse
from kio.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    return service.health()
