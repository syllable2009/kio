from __future__ import annotations

from fastapi.testclient import TestClient

from kio.app import create_app


def test_kio_health() -> None:
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
