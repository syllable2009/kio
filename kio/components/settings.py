from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class KioSettings:
    """从环境变量读取的运行配置（与 README 中的 KIO_* 约定一致）。"""

    host: str
    port: int
    reload: bool


def load_kio_settings() -> KioSettings:
    return KioSettings(
        host=os.getenv("KIO_HOST", "0.0.0.0"),
        port=int(os.getenv("KIO_PORT", "9000")),
        reload=os.getenv("KIO_RELOAD", "1") == "1",
    )
