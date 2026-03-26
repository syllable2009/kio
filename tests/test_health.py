from __future__ import annotations

from fastapi.testclient import TestClient

from dio.app import create_app as create_dio_app
from kio.app import create_app as create_kio_app


def test_kio_health() -> None:
    client = TestClient(create_kio_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_dio_health() -> None:
    client = TestClient(create_dio_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

