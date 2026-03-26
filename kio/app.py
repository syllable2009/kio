from __future__ import annotations

import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import uvicorn
from fastapi import FastAPI

from kio.api.router import router as api_router


def create_app() -> FastAPI:
    """FastAPI 工厂：装配各路由（组合根）。"""
    app = FastAPI(title="kio")
    app.include_router(api_router)
    return app


def main() -> None:
    host = os.getenv("KIO_HOST", "127.0.0.1")
    port = int(os.getenv("KIO_PORT", "9000"))
    reload = os.getenv("KIO_RELOAD", "1") == "1"
    # Python 工程化的路径语法,模块路径:对象/函数,运行dio文件夹下的app.py文件里的create_app函数
    uvicorn.run(
        "kio.app:create_app",  # 找函数
        factory=True,  # 告诉 uvicorn 这是个【工厂函数】
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
