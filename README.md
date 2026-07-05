# 365日天然石大辞典 → Instagram 自動投稿プロジェクト

globalstone.jp の誕生日石データ（全366日分）を毎日自動でInstagramに投稿する仕組みです。

## 仕組みの全体像

```
[毎日 定時に自動実行]
        ↓
① 今日の日付から誕生日石データを取得（data/all_366_days.json）
        ↓
② 1080×1080のおしゃれな投稿画像を生成（Pillow）
        ↓
③ WordPressのメディアライブラリにアップロードして公開URLを取得
   （Instagram APIは「公開されている画像URL」が必須のため、
    すでに運用中のWordPressサーバーを画像置き場として利用）
        ↓
④ Instagram Graph API で画像＋キャプションを投稿
```

自動実行には **GitHub Actions**（無料枠で十分）を使います。
GitHubの操作に慣れていなくても、下記の手順通りに進めれば設定できます。

---

## フォルダ構成

```
ig-project/
├── main.py                      # 全体を実行するメインスクリプト
├── requirements.txt              # 必要なPythonパッケージ
├── .env.example                  # 環境変数のサンプル（実際の値はGitHub Secretsに入れる）
├── data/
│   └── all_366_days.json         # 全366日分の誕生日石データ
├── scripts/
│   ├── generate_image.py         # 投稿画像を生成
│   ├── upload_to_wordpress.py    # WordPressに画像をアップロード
│   └── post_instagram.py         # Instagramに投稿
├── output/                       # 生成された画像・キャプションの保存先（実行のたびに作られる）
└── .github/workflows/
    └── daily-post.yml            # 毎日自動実行するGitHub Actionsの設定
```

---

## セットアップ手順

### STEP 1｜WordPress側の準備（画像のアップロード先）

1. WordPress管理画面 → **ユーザー → プロフィール**
2. 一番下までスクロールして「**アプリケーションパスワード**」欄を探す
3. 名前欄に `instagram-bot` などと入力して「新規追加」
4. 表示されたパスワード（スペース区切りの16文字）を**必ずコピーして保存**（二度と表示されません）

これで `WP_USER`（あなたのWordPressユーザー名）と `WP_APP_PASSWORD`（今発行したパスワード）が揃います。

---

### STEP 2｜Instagram側の準備（投稿用API）

Instagramへの自動投稿には、個人アカウントではなく**ビジネス（またはクリエイター）アカウント**が必要です。

1. **Instagramアプリ側**
   - 設定 → アカウントの種類の切り替え → 「ビジネスアカウントに切り替える」
   - Facebookページと連携する（連携するFacebookページがなければ新規作成でOK、非公開のままでも構いません）

2. **Meta for Developers でアプリを作成**
   - https://developers.facebook.com/ にアクセスしてログイン
   - 「マイアプリ」→「アプリを作成」→ 種類は「ビジネス」を選択
   - アプリ名を入力（例：globalstone-instagram-bot）して作成

3. **Instagram Graph API を有効化**
   - 作成したアプリのダッシュボードで「製品を追加」→「Instagram Graph API」を追加
   - 連携したFacebookページ・Instagramビジネスアカウントを選択

4. **アクセストークンの取得**
   - Meta for Developers の「Graph APIエクスプローラー」を開く
   - 対象アプリ・Instagramのパーミッション（`instagram_basic`, `instagram_content_publish`, `pages_show_list` など）を付与してトークンを生成
   - 生成された**短期トークン**を、Metaの「アクセストークンデバッガー」で**長期トークン（60日間有効）**に交換する
   - ※ 60日ごとに更新が必要です（更新方法は下記「メンテナンス」参照）

5. **Instagram Business Account ID の取得**
   - Graph APIエクスプローラーで以下を実行：
     ```
     GET /me/accounts
     ```
     → 連携しているFacebookページのIDを確認
     ```
     GET /{ページID}?fields=instagram_business_account
     ```
     → 表示された `id` が `IG_USER_ID` です

これで `IG_USER_ID` と `IG_ACCESS_TOKEN` が揃います。

---

### STEP 3｜GitHubリポジトリの準備

1. GitHubで新しいリポジトリを作成（例：`globalstone-ig-bot`）。公開・非公開どちらでも可（**非公開推奨**）
2. このプロジェクトフォルダ（`ig-project/`）の中身をすべてアップロード
   - GitHub Desktop や `git push` を使う方法が簡単です
   - 分からない場合は、GitHubの「Add file → Upload files」からドラッグ&ドロップでもアップロード可能

---

### STEP 4｜GitHub Secretsに認証情報を登録

**重要：** 認証情報は `.env` ファイルに直接書かず、GitHubの「Secrets」という安全な場所に登録します。

1. GitHubリポジトリ画面 → **Settings → Secrets and variables → Actions**
2. 「New repository secret」で以下を1つずつ登録：

| Name | 値 |
|---|---|
| `WP_SITE_URL` | `https://globalstone.jp` |
| `WP_USER` | あなたのWordPressユーザー名 |
| `WP_APP_PASSWORD` | STEP1で発行したアプリケーションパスワード |
| `IG_USER_ID` | STEP2で取得したInstagram Business Account ID |
| `IG_ACCESS_TOKEN` | STEP2で取得した長期アクセストークン |

---

### STEP 5｜動作確認

1. GitHubリポジトリ → **Actions** タブを開く
2. 左メニューから「Daily Instagram Post」を選択
3. 右側の「Run workflow」ボタンを押して手動実行
4. 数十秒〜1分程度で完了。Instagramアカウントに投稿されているか確認

うまくいけば、以降は**毎日 朝9:00（日本時間）に自動投稿**されます。
（`.github/workflows/daily-post.yml` の `cron` の値を変更すれば投稿時刻も変更できます）

---

## ローカルでのテスト方法

GitHubに上げる前に、手元のパソコンで動作確認したい場合：

```bash
cd ig-project
pip install -r requirements.txt

# .envファイルを作成して認証情報を記入
cp .env.example .env
# ↑ .env を開いて実際の値に書き換える

# 画像生成だけ試す（投稿はしない）
python3 main.py --month 7 --day 2 --dry-run

# 実際に投稿する
python3 main.py --month 7 --day 2

# 今日の日付で投稿する
python3 main.py
```

※ ローカル実行時は `.env` の値を読み込むために、事前に以下を実行してください：
```bash
export $(cat .env | xargs)
```

---

## メンテナンス

### アクセストークンの更新（60日ごと）

Instagram/Facebookの長期アクセストークンは60日で失効します。期限が近づいたら：

1. Meta for Developers の「アクセストークンデバッガー」で新しいトークンを発行
2. GitHub Secretsの `IG_ACCESS_TOKEN` を新しい値に更新

更新を忘れると自動投稿が止まるため、カレンダーなどにリマインダーを設定しておくと安心です。

### 画像デザインの変更

`scripts/generate_image.py` の中でレイアウト・色・フォントサイズを調整できます。
変更後は `python3 main.py --dry-run` で確認してから本番投稿してください。

### キャプション文言の変更

`scripts/generate_image.py` 内の `build_caption()` 関数を編集してください。
ハッシュタグや文言はここで自由に変更できます。

---

## トラブルシューティング

| 症状 | 原因・対処 |
|---|---|
| 画像生成でエラー | 日本語フォントが不足 → GitHub Actions内では自動インストール済み。ローカルの場合は `fonts-noto-cjk` をインストール |
| WordPressアップロードで401エラー | アプリケーションパスワードが間違っている、またはユーザー名が違う |
| Instagram投稿で400エラー | アクセストークンの期限切れ、またはパーミッション不足 |
| 投稿されるが画像が真っ黒 | WordPress側の画像URLが正しく公開されているか確認（ブラウザで直接開けるか） |
