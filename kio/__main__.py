from __future__ import annotations

import os

import uvicorn

from kio.app import create_app


def main() -> None:
    host = os.getenv("KIO_HOST", "0.0.0.0")
    port = int(os.getenv("KIO_PORT", "8000"))
    reload = os.getenv("KIO_RELOAD", "1") == "1"

    uvicorn.run(create_app(), host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()

