#!/usr/bin/env python3
"""
upload_to_wordpress.py
生成した画像をWordPressのメディアライブラリにアップロードし、
Instagram投稿用の公開URLを取得する。

WordPress側の準備:
  1. ユーザー → あなたのプロフィール → 「アプリケーションパスワード」を発行
  2. .env に WP_USER / WP_APP_PASSWORD / WP_SITE_URL を設定

Usage:
    from upload_to_wordpress import upload_image
    url = upload_image("/path/to/image.png")
"""
import os
import base64
import requests
from pathlib import Path

WP_SITE_URL = os.environ.get("WP_SITE_URL", "https://globalstone.jp")
WP_USER = os.environ.get("WP_USER", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")


def upload_image(image_path: str) -> str:
    """WordPressメディアライブラリに画像をアップロードし、公開URLを返す"""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    endpoint = f"{WP_SITE_URL}/wp-json/wp/v2/media"

    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode("utf-8")

    headers = {
        "Authorization": f"Basic {token}",
        "Content-Disposition": f'attachment; filename="{image_path.name}"',
        "Content-Type": "image/png",
    }

    with open(image_path, "rb") as f:
        response = requests.post(endpoint, headers=headers, data=f.read(), timeout=60)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"WordPressアップロード失敗: {response.status_code} {response.text}")

    data = response.json()
    source_url = data.get("source_url")
    if not source_url:
        raise RuntimeError(f"source_url が取得できませんでした: {data}")

    return source_url


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 upload_to_wordpress.py <image_path>")
        sys.exit(1)
    url = upload_image(sys.argv[1])
    print(f"✅ アップロード完了: {url}")
