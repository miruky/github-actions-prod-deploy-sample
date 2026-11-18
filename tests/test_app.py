import json

from src import app


def test_handler_returns_version_and_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "dev")
    res = app.handler({}, None)
    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert body["env"] == "dev"
    assert body["version"]
