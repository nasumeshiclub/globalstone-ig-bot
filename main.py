#!/usr/bin/env python3
"""
generate_image.py
1080x1080 の Instagram投稿用画像を、その日の誕生日石データから生成する。

Usage:
    python3 generate_image.py --month 7 --day 2
    python3 generate_image.py            # 引数なしなら「今日」を使用
"""
import json
import argparse
import textwrap
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "all_366_days.json"
OUTPUT_DIR = BASE_DIR / "output"
FONT_DIR = Path("/usr/share/fonts/opentype/noto")

FONT_BOLD = FONT_DIR / "NotoSansCJK-Bold.ttc"
FONT_REGULAR = FONT_DIR / "NotoSansCJK-Regular.ttc"

NAVY = "#1a2744"
GOLD = "#c8a84b"
WHITE = "#ffffff"

W, H = 1080, 1080


def load_day(month: int, day: int) -> dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        all_days = json.load(f)
    for item in all_days:
        if item["month"] == month and item["day"] == day:
            return item
    raise ValueError(f"{month}月{day}日 のデータが見つかりません")


def hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def text_color_for_bg(hex_color: str) -> str:
    r, g, b = hex_to_rgb(hex_color)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#ffffff" if luminance < 140 else "#1a2744"


def draw_wrapped_text(draw, text, font, max_width, start_xy, fill, line_spacing=1.4, align="center"):
    """幅に応じて改行しながら中央揃えでテキスト描画。戻り値: 使用した高さ"""
    x, y = start_xy
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = ch
        else:
            current = test
    if current:
        lines.append(current)

    line_height = font.size * line_spacing
    total_height = line_height * len(lines)
    cur_y = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        lx = x - line_w / 2 if align == "center" else x
        draw.text((lx, cur_y), line, font=font, fill=fill)
        cur_y += line_height
    return total_height


def generate(month: int, day: int, out_path: Path = None) -> Path:
    data = load_day(month, day)

    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # 背景グラデーション風の装飾（誕生色を右下にアクセントとして使用）
    accent_hex = "#" + data["color_hex"] if not data["color_hex"].startswith("#") else data["color_hex"]
    try:
        accent_rgb = hex_to_rgb(accent_hex)
    except Exception:
        accent_rgb = hex_to_rgb("#c8a84b")

    # 上部帯（ゴールドの細ライン）
    draw.rectangle([0, 0, W, 10], fill=GOLD)

    # コーナー装飾（HUD風の角括弧）
    bracket_len = 60
    margin = 50
    lw = 4
    for (x0, y0, dx, dy) in [
        (margin, margin, 1, 1), (W - margin, margin, -1, 1),
        (margin, H - margin, 1, -1), (W - margin, H - margin, -1, -1),
    ]:
        draw.line([(x0, y0), (x0 + dx * bracket_len, y0)], fill=GOLD, width=lw)
        draw.line([(x0, y0), (x0, y0 + dy * bracket_len)], fill=GOLD, width=lw)

    font_badge = ImageFont.truetype(str(FONT_BOLD), 34)
    font_month = ImageFont.truetype(str(FONT_BOLD), 64)
    font_name = ImageFont.truetype(str(FONT_BOLD), 72)
    font_en = ImageFont.truetype(str(FONT_REGULAR), 28)
    font_word_label = ImageFont.truetype(str(FONT_REGULAR), 26)
    font_word = ImageFont.truetype(str(FONT_BOLD), 46)
    font_footer = ImageFont.truetype(str(FONT_REGULAR), 24)
    font_swatch_label = ImageFont.truetype(str(FONT_REGULAR), 22)

    cx = W // 2

    # バッジ
    badge_text = "365日天然石大辞典"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0]
    draw.rounded_rectangle(
        [cx - bw / 2 - 24, 90, cx + bw / 2 + 24, 90 + 54],
        radius=27, outline=GOLD, width=2
    )
    draw.text((cx, 90 + 27), badge_text, font=font_badge, fill=GOLD, anchor="mm")

    # 月日
    date_text = f"{month}月{day}日"
    draw.text((cx, 230), date_text, font=font_month, fill=WHITE, anchor="mm")

    # 石名
    y_name = 340
    used_h = draw_wrapped_text(
        draw, data["ja"], font_name, max_width=880,
        start_xy=(cx, y_name), fill=GOLD, align="center"
    )
    y_after_name = y_name + used_h + 10

    # 英名
    draw.text((cx, y_after_name + 10), data["en"], font=font_en, fill="#9aa5c0", anchor="mm")

    # 区切り線
    line_y = y_after_name + 55
    draw.line([(cx - 100, line_y), (cx + 100, line_y)], fill=GOLD, width=2)

    # 石言葉ラベル
    draw.text((cx, line_y + 40), "石言葉", font=font_word_label, fill="#9aa5c0", anchor="mm")

    # 石言葉本体
    word_y = line_y + 80
    draw_wrapped_text(
        draw, f"「{data['word']}」", font_word, max_width=880,
        start_xy=(cx, word_y), fill=WHITE, align="center"
    )

    # 誕生色スウォッチ
    swatch_y = 760
    swatch_size = 64
    draw.rounded_rectangle(
        [cx - swatch_size / 2, swatch_y, cx + swatch_size / 2, swatch_y + swatch_size],
        radius=10, fill=accent_rgb, outline=WHITE, width=2
    )
    draw.text(
        (cx, swatch_y + swatch_size + 30),
        f"誕生色：{data['color_name']}",
        font=font_swatch_label, fill="#c8c8d8", anchor="mm"
    )

    # フッター
    footer_y = H - 70
    draw.line([(margin, footer_y - 30), (W - margin, footer_y - 30)], fill="#33415f", width=1)
    draw.text((cx, footer_y), "globalstone.jp", font=font_footer, fill=GOLD, anchor="mm")

    out_path = out_path or (OUTPUT_DIR / f"{month:02d}-{day:02d}.png")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def build_caption(month: int, day: int) -> str:
    data = load_day(month, day)
    lines = [
        f"🌟{month}月{day}日の誕生日石は「{data['ja']}」🌟",
        "",
        f"✨石言葉：{data['word']}",
        f"📍主な産地：{data['origin']}",
        f"🎨誕生色：{data['color_name']}",
        "",
        f"詳しい意味・浄化方法・本物の見分け方はプロフィールのリンクから",
        "",
        "#誕生日石 #天然石 #パワーストーン #365日誕生日石大辞典",
        f"#{data['en'].replace(' ', '')}",
        f"#{month}月{day}日",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", type=int, help="月 (1-12)")
    parser.add_argument("--day", type=int, help="日")
    args = parser.parse_args()

    if args.month and args.day:
        m, d = args.month, args.day
    else:
        now = datetime.now()
        m, d = now.month, now.day

    path = generate(m, d)
    caption = build_caption(m, d)

    print(f"✅ 画像生成完了: {path}")
    print("── キャプション ──")
    print(caption)

    # main.py から呼び出す際に利用できるようキャプションもテキスト保存
    caption_path = OUTPUT_DIR / f"{m:02d}-{d:02d}.txt"
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(caption)
