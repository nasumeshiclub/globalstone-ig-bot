#!/usr/bin/env python3
"""
host_via_github.py
生成した画像を、このリポジトリ内の docs/ フォルダにコピーする。
GitHub Pages (docs/ フォルダを公開設定) を使うことで、
その画像を「公開URL」としてInstagram APIに渡せるようにする。

事前準備:
  1. GitHubリポジトリの Settings → Pages
  2. "Source" を "Deploy from a branch" に設定
  3. Branch を "main" / フォルダを "/docs" に設定して Save
  4. 数分待つと https://<ユーザー名>.github.io/<リポジトリ名>/ が使えるようになる

Usage:
    from host_via_github import host_image
    url = host_image("/path/to/07-05.png", repo="nasumeshiclub/globalstone-ig-bot")
"""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs" / "images"

# 例: "nasumeshiclub/globalstone-ig-bot"
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "")
# 例: "nasumeshiclub"
GITHUB_USER = GITHUB_REPO.split("/")[0] if "/" in GITHUB_REPO else ""
GITHUB_REPO_NAME = GITHUB_REPO.split("/")[1] if "/" in GITHUB_REPO else ""


def host_image(image_path: str) -> str:
    """
    画像を docs/images/ にコピーし、GitHub Pages経由の公開URLを返す。
    GitHub Actions内で実行されると GITHUB_REPOSITORY が自動的に設定される。
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dest = DOCS_DIR / image_path.name
    shutil.copy(image_path, dest)

    if not GITHUB_USER or not GITHUB_REPO_NAME:
        raise EnvironmentError(
            "GITHUB_REPOSITORY が取得できません。GitHub Actions内で実行するか、"
            "環境変数 GITHUB_REPOSITORY を 'ユーザー名/リポジトリ名' の形式で設定してください。"
        )

    public_url = f"https://{GITHUB_USER}.github.io/{GITHUB_REPO_NAME}/images/{image_path.name}"
    return public_url


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 host_via_github.py <image_path>")
        sys.exit(1)
    url = host_image(sys.argv[1])
    print(f"✅ ホスティング準備完了: {url}")
    print("※ GitHubにコミット＆プッシュしてから数十秒〜1分待つと、このURLが実際に開けるようになります")
