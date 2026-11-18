"""デプロイの確認に使う小さなLambda関数です。

ビルドのときに同梱した VERSION ファイルの中身と、関数に設定した環境名を返します。
"""
import json
import os
from pathlib import Path

VERSION_FILE = Path(__file__).with_name("VERSION")


def read_version() -> str:
    # ビルドで VERSION を同梱していないときは、ローカル実行とみなします
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    return "local"


def handler(event, context):
    # 呼び出し元が name を渡したときは、あいさつに名前を入れます
    name = event.get("name") if isinstance(event, dict) else None
    body = {
        "message": f"こんにちは、{name}さん" if name else "こんにちは、デプロイの見本です",
        "version": read_version(),
        "env": os.environ.get("APP_ENV", "local"),
    }
    return {"statusCode": 200, "body": json.dumps(body, ensure_ascii=False)}
