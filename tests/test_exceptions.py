from __future__ import annotations

from fastapi.testclient import TestClient

from kio.app import create_app
from kio.exceptions.codes import ApiCode


def test_not_found_response_shape() -> None:
    client = TestClient(create_app())
    resp = client.get("/user/999")
    assert resp.status_code == 404
    assert resp.json() == {
        "code": ApiCode.USER_NOT_FOUND.value,
        "message": "User not found",
        "data": None,
    }


def test_validation_error_shape() -> None:
    client = TestClient(create_app())
    resp = client.get("/user/not_an_int")
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == ApiCode.VALIDATION_ERROR.value
    assert body["message"] == "请求参数校验失败"
    assert "details" in body["data"]
