from __future__ import annotations

from fastapi import APIRouter, Depends

from kio.api.health.dependencies import get_health_service
from kio.api.health.schemas import HealthResponse
from kio.exceptions import ApiCode
from kio.schemas import ApiResponse
from kio.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/", summary="首页")
@router.get("/health", response_model=ApiResponse)
def health(service: HealthService = Depends(get_health_service)) -> ApiResponse:
    return ApiResponse(code=ApiCode.SUCCESS.value, data=service.health())


@router.get("/crawler", response_model=ApiResponse)
async def ping() -> ApiResponse:
    from kio.services.crawlee_service import beautiful_soup_crawler

    await beautiful_soup_crawler()
    return ApiResponse(code=ApiCode.SUCCESS.value, data="crawler")
