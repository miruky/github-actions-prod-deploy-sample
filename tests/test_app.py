import json

from src import app


def test_handler_returns_version_and_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "dev")
    res = app.handler({}, None)
    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert body["env"] == "dev"
    assert body["version"]


def test_handler_returns_message():
    body = json.loads(app.handler({}, None)["body"])
    assert body["message"]


def test_handler_uses_name():
    body = json.loads(app.handler({"name": "miruky"}, None)["body"])
    assert body["message"] == "こんにちは、mirukyさん"


def test_handler_accepts_non_dict_event():
    # テストの画面などから文字列や配列が渡されても落ちないこと
    body = json.loads(app.handler(["x"], None)["body"])
    assert body["message"] == "こんにちは、デプロイの見本です"


def test_handler_returns_region(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "ap-northeast-1")
    body = json.loads(app.handler({}, None)["body"])
    assert body["region"] == "ap-northeast-1"


def test_handler_in_english():
    body = json.loads(app.handler({"name": "miruky", "lang": "en"}, None)["body"])
    assert body["message"] == "Hello, miruky"
