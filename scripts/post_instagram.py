#!/usr/bin/env python3
"""
run_post_instagram.py
GitHub Actions内で実行する:
  1. image_url.txt から公開URLを読み込む
  2. 今日のキャプションを生成
  3. Instagramに投稿する
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_image import build_caption   # noqa: E402
from post_instagram import post_photo       # noqa: E402

now = datetime.now()
caption = build_caption(now.month, now.day)

url_file = Path(__file__).resolve().parent.parent / "image_url.txt"
with open(url_file) as f:
    image_url = f.read().strip()

media_id = post_photo(image_url=image_url, caption=caption)
print(f"投稿完了 media_id={media_id}")
