from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from kio.api.router import router as api_router
from kio.components.settings import load_kio_settings
from kio.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    """FastAPI 工厂：装配各路由（组合根）。"""
    app = FastAPI(title="kio")
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


def main() -> None:
    s = load_kio_settings()
    uvicorn.run(
        "kio.app:create_app",
        factory=True,
        host=s.host,
        port=s.port,
        reload=s.reload,
    )


if __name__ == "__main__":
    main()
