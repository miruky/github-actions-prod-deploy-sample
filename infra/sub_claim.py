"""信頼ポリシーに書く sub の値を作ります。

2026-07-15 以降に作成（または名前の変更、移管）したリポジトリは、
所有者とリポジトリの ID が入った形（repo:OWNER@ID/REPO@ID:...）になります。
使い方: python3 infra/sub_claim.py OWNER/REPO prd
"""
import json
import subprocess
import sys

repo, env = sys.argv[1], sys.argv[2]
info = json.loads(subprocess.run(["gh", "api", f"repos/{repo}"], check=True,
                                 capture_output=True, text=True).stdout)
owner, name = info["owner"]["login"], info["name"]
# 作成日で判断します。名前の変更や移管をしたリポジトリは、実際のトークンで確かめてください
if info["created_at"] >= "2026-07-15":
    print(f"repo:{owner}@{info['owner']['id']}/{name}@{info['id']}:environment:{env}")
else:
    print(f"repo:{owner}/{name}:environment:{env}")
