from __future__ import annotations

from fastapi.testclient import TestClient

from kio.app import create_app
from kio.exceptions.codes import ApiCode


def test_user_list() -> None:
    client = TestClient(create_app())
    resp = client.get("/user")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["message"] == ""
    data = body["data"]
    assert "users" in data
    assert len(data["users"]) == 3
    assert data["users"][0]["name"] == "张三"


def test_user_get_by_id() -> None:
    client = TestClient(create_app())
    resp = client.get("/user/1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["message"] == ""
    assert body["data"]["name"] == "张三"

    resp = client.get("/user/999")
    assert resp.status_code == 404
    assert resp.json() == {
        "code": ApiCode.USER_NOT_FOUND.value,
        "message": "User not found",
        "data": None,
    }


def test_movie_list() -> None:
    client = TestClient(create_app())
    resp = client.get("/movie")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["message"] == ""
    data = body["data"]
    assert "movies" in data
    assert len(data["movies"]) == 3
    assert data["movies"][0]["title"] == "肖申克的救赎"


def test_movie_get_by_id() -> None:
    client = TestClient(create_app())
    resp = client.get("/movie/2")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["message"] == ""
    assert body["data"]["title"] == "霸王别姬"

    resp = client.get("/movie/999")
    assert resp.status_code == 404
    assert resp.json() == {
        "code": ApiCode.MOVIE_NOT_FOUND.value,
        "message": "Movie not found",
        "data": None,
    }
