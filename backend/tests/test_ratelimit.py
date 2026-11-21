import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.ratelimit as ratelimit


@pytest.fixture
def client():
    ratelimit.reset_state()
    app = FastAPI()
    ratelimit.install_rate_limit(app)

    @app.post("/chat")
    def chat():
        return {"ok": True}

    @app.get("/health")
    def health():
        return {"ok": True}

    yield TestClient(app)
    ratelimit.reset_state()


def test_chat_is_limited_per_minute(client):
    limit = ratelimit.RATE_LIMITS["/chat"][0]

    for _ in range(limit):
        assert client.post("/chat").status_code == 200

    blocked = client.post("/chat")
    assert blocked.status_code == 429
    assert "Too many questions" in blocked.json()["detail"]
    assert int(blocked.headers["Retry-After"]) >= 1


def test_other_visitors_are_not_affected(client):
    limit = ratelimit.RATE_LIMITS["/chat"][0]
    for _ in range(limit):
        client.post("/chat", headers={"x-forwarded-for": "1.1.1.1"})

    assert client.post("/chat", headers={"x-forwarded-for": "1.1.1.1"}).status_code == 429
    assert client.post("/chat", headers={"x-forwarded-for": "2.2.2.2"}).status_code == 200


def test_get_requests_are_never_limited(client):
    for _ in range(50):
        assert client.get("/health").status_code == 200


def test_daily_cap_blocks_everyone(client, monkeypatch):
    monkeypatch.setattr(ratelimit, "DAILY_CHAT_CAP", 2)

    assert client.post("/chat", headers={"x-forwarded-for": "1.1.1.1"}).status_code == 200
    assert client.post("/chat", headers={"x-forwarded-for": "2.2.2.2"}).status_code == 200

    blocked = client.post("/chat", headers={"x-forwarded-for": "3.3.3.3"})
    assert blocked.status_code == 429
    assert "daily" in blocked.json()["detail"]
