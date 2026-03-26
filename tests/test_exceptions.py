from __future__ import annotations

from fastapi.testclient import TestClient

from kio.app import create_app


def test_not_found_response_shape() -> None:
    client = TestClient(create_app())
    resp = client.get("/user/999")
    assert resp.status_code == 404
    data = resp.json()
    assert data == {
        "code": "USER_NOT_FOUND",
        "message": "User not found",
    }


def test_validation_error_shape() -> None:
    client = TestClient(create_app())
    resp = client.get("/user/not_an_int")
    assert resp.status_code == 422
    data = resp.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "请求参数校验失败"
    assert "details" in data
