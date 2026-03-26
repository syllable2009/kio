from __future__ import annotations

from fastapi.testclient import TestClient

from kio.app import create_app


def test_user_list() -> None:
    client = TestClient(create_app())
    resp = client.get("/user")
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data
    assert len(data["users"]) == 3
    assert data["users"][0]["name"] == "张三"


def test_user_get_by_id() -> None:
    client = TestClient(create_app())
    resp = client.get("/user/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "张三"

    resp = client.get("/user/999")
    assert resp.status_code == 404


def test_movie_list() -> None:
    client = TestClient(create_app())
    resp = client.get("/movie")
    assert resp.status_code == 200
    data = resp.json()
    assert "movies" in data
    assert len(data["movies"]) == 3
    assert data["movies"][0]["title"] == "肖申克的救赎"


def test_movie_get_by_id() -> None:
    client = TestClient(create_app())
    resp = client.get("/movie/2")
    assert resp.status_code == 200
    assert resp.json()["title"] == "霸王别姬"

    resp = client.get("/movie/999")
    assert resp.status_code == 404
