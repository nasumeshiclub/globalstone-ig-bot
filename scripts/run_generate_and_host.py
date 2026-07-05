
#!/usr/bin/env python3
"""
run_generate_and_host.py
GitHub Actions内で実行する:
  1. 今日の画像を生成
  2. docs/images/ にコピー
  3. 公開URLを image_url.txt に保存
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_image import generate    # noqa: E402
from host_via_github import host_image  # noqa: E402

now = datetime.now()
path = generate(now.month, now.day)
url = host_image(str(path))

print(f"IMAGE_URL={url}")

with open(Path(__file__).resolve().parent.parent / "image_url.txt", "w") as f:
    f.write(url)
