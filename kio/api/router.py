from __future__ import annotations

from fastapi import APIRouter

from kio.api.health.router import router as health_router
from kio.api.movie_api.router import router as movie_router
from kio.api.user_api.router import router as user_router

router = APIRouter()
router.include_router(health_router)
router.include_router(user_router)
router.include_router(movie_router)

