#!/usr/bin/env python3
"""
post_instagram.py
Instagram Graph API を使い、画像URL + キャプションで投稿を作成・公開する。

事前準備 (README.md 参照):
  1. Meta for Developers でアプリを作成
  2. Instagramビジネス/クリエイターアカウントをFacebookページに連携
  3. 長期アクセストークン (IG_ACCESS_TOKEN) と
     Instagram Business Account ID (IG_USER_ID) を取得
  4. .env に設定

Usage:
    from post_instagram import post_photo
    post_photo(image_url="https://.../07-02.png", caption="...")
"""
import os
import time
import requests

GRAPH_API_VERSION = "v19.0"
# Instagramログインによる直接アクセス方式 (IGAA... トークン) は graph.instagram.com を使用する。
# Facebookページ経由の旧方式 (EAA... トークン) の場合は graph.facebook.com に変更すること。
GRAPH_API_BASE = f"https://graph.instagram.com/{GRAPH_API_VERSION}"

IG_USER_ID = os.environ.get("IG_USER_ID", "")
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")


def _check_container_status(creation_id: str) -> str:
    url = f"{GRAPH_API_BASE}/{creation_id}"
    params = {"fields": "status_code", "access_token": IG_ACCESS_TOKEN}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("status_code", "UNKNOWN")


def post_photo(image_url: str, caption: str, max_wait_sec: int = 60) -> str:
    """
    画像URLとキャプションからInstagram投稿を作成する。
    戻り値: 公開された投稿のメディアID
    """
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        raise EnvironmentError("IG_USER_ID / IG_ACCESS_TOKEN が設定されていません")

    # STEP 1: メディアコンテナ作成
    create_url = f"{GRAPH_API_BASE}/{IG_USER_ID}/media"
    create_params = {
        "image_url": image_url,
        "caption": caption,
        "access_token": IG_ACCESS_TOKEN,
    }
    resp = requests.post(create_url, data=create_params, timeout=60)
