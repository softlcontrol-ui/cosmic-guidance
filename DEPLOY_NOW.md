# 🚀 デプロイ手順（3ステップ）

## ✅ コード確認済み
**Gemini 2.5 Flashモデルを使用しており、すべて正常です。**
そのままデプロイできます！

---

## ステップ1️⃣: APIキーを取得（5分）

1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. 「Create API Key」をクリック
3. APIキーをコピー（`AIzaSy...` で始まる）

---

## ステップ2️⃣: GitHubにアップロード（5分）

### 方法A: Webインターフェース（簡単・推奨）

1. [GitHub](https://github.com/new) で新しいリポジトリを作成
   - 名前: `cosmic-guidance`
   - Public を選択
2. 「uploading an existing file」をクリック
3. **このフォルダの全ファイルを選択してドラッグ&ドロップ**
4. 「Commit changes」をクリック

### 方法B: Gitコマンド（上級者向け）

```bash
cd このフォルダのパス
git init
git add .
git commit -m "Initial commit: Cosmic Guidance app with Gemini 2.5 Flash"
git branch -M main
git remote add origin https://github.com/ユーザー名/cosmic-guidance.git
git push -u origin main
```

---

## ステップ3️⃣: Streamlit Cloudでデプロイ（10分）

1. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
2. GitHubでサインアップ/ログイン
3. 「New app」をクリック
4. 設定:
   - Repository: `ユーザー名/cosmic-guidance`
   - Branch: `main`
   - Main file: `app.py`
5. **「Advanced settings」をクリック**
6. **Secrets** に以下を入力:
   ```toml
   GEMINI_API_KEY = "ステップ1で取得したAPIキー"
   ```
7. 「Deploy!」をクリック

---

## ✅ 完成！

数分後、アプリが公開されます:
```
https://あなたのアプリ名.streamlit.app
```

---

## 📁 必要なファイル（すべて含まれています）

- ✅ `app.py` - メインアプリ（**Gemini 2.5 Flash使用**）
- ✅ `requirements.txt` - 依存パッケージ
- ✅ `.gitignore` - Git除外設定
- ✅ `.streamlit/config.toml` - テーマ設定
- ✅ `.streamlit/secrets.toml.example` - APIキー設定例

---

## 🐛 トラブルシューティング

### エラー: "API key not found"
→ Streamlit Cloud の「Settings」→「Secrets」でAPIキーを確認してください。

### デプロイが失敗する
→ `requirements.txt` と `.streamlit/config.toml` がGitHubにアップロードされているか確認してください。

### アプリが動かない
→ Google AI StudioでAPIキーが有効か確認してください。

---

## 📚 詳細ドキュメント

- `README.md` - 技術詳細
- `QUICKSTART.md` - 詳しい手順
- `SETUP_GUIDE.md` - 初心者向けガイド
- `FIXES_APPLIED.md` - 適用された修正内容

---

**所要時間**: 約20分  
**費用**: 完全無料 💰  

**さあ、始めましょう！** ✨
