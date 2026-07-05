#!/usr/bin/env python3
"""
main.py
365日天然石大辞典 → Instagram 自動投稿のメインスクリプト。

流れ:
  1. 今日（または指定日）の誕生日石データを取得
  2. 投稿用画像(1080x1080)を生成
  3. WordPressメディアライブラリにアップロードして公開URLを取得
  4. Instagram Graph APIで画像+キャプションを投稿

Usage:
    python3 main.py                  # 今日の日付で実行
    python3 main.py --month 7 --day 2   # 日付を指定して実行
    python3 main.py --dry-run        # 画像生成だけ行い、投稿はしない（動作確認用）
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from generate_image import generate, build_caption          # noqa: E402
from host_via_github import host_image                       # noqa: E402
from post_instagram import post_photo                         # noqa: E402


def run(month: int, day: int, dry_run: bool = False):
    print(f"=== {month}月{day}日の投稿処理を開始 ===")

    # STEP 1-2: 画像生成
    image_path = generate(month, day)
    caption = build_caption(month, day)
    print(f"[1/3] 画像生成完了: {image_path}")

    if dry_run:
        print("[DRY RUN] 投稿はスキップしました。画像とキャプションのみ生成済みです。")
        print("── キャプション ──")
        print(caption)
        return

    # STEP 3: GitHub Pages用フォルダにコピー（このあとGit側でcommit&pushが必要）
    image_url = host_image(str(image_path))
    print(f"[2/3] GitHub Pages公開URL: {image_url}")
    print("      ※ このURLが実際にアクセス可能になるまで、コミット後 数十秒〜1分ほど待ちます")
    import time
    time.sleep(45)

    # STEP 4: Instagramへ投稿
    media_id = post_photo(image_url=image_url, caption=caption)
    print(f"[3/3] Instagram投稿完了: media_id={media_id}")
    print("=== 完了 ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="365日天然石大辞典 Instagram自動投稿")
    parser.add_argument("--month", type=int, help="月 (1-12)。省略時は今日")
    parser.add_argument("--day", type=int, help="日。省略時は今日")
    parser.add_argument("--dry-run", action="store_true", help="投稿せず画像生成のみ行う")
    args = parser.parse_args()

    if args.month and args.day:
        m, d = args.month, args.day
    else:
        now = datetime.now()
        m, d = now.month, now.day

    run(m, d, dry_run=args.dry_run)
