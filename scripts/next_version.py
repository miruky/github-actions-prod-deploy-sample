"""最新のリリースタグと、選んだリリースの種類から、次の版番号を決めます。

使い方:
  python3 scripts/next_version.py --type minor --latest v1.2.0   # v1.3.0
  python3 scripts/next_version.py --type patch                   # タグがなければ v0.0.1
"""
import argparse
import re
import sys

TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def next_version(latest: str | None, release_type: str) -> str:
    major, minor, patch = (0, 0, 0)
    if latest:
        m = TAG.match(latest)
        if not m:
            raise ValueError(f"vX.Y.Z の形ではないタグです: {latest}")
        major, minor, patch = (int(x) for x in m.groups())
    if release_type == "major":
        return f"v{major + 1}.0.0"
    if release_type == "minor":
        return f"v{major}.{minor + 1}.0"
    if release_type == "patch":
        return f"v{major}.{minor}.{patch + 1}"
    raise ValueError(f"major、minor、patch のどれかを指定してください: {release_type}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, choices=["major", "minor", "patch"])
    parser.add_argument("--latest", default="")
    args = parser.parse_args()
    print(next_version(args.latest or None, args.type))
    return 0


if __name__ == "__main__":
    sys.exit(main())
