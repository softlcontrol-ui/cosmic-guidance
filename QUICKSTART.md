# ⚡ クイックスタート - 3ステップで公開！

## 📦 完成するもの

**「運命の導き」** - AIがあなたの運命を読み解くWebアプリ  
URL: `https://あなたのアプリ名.streamlit.app`

---

## 🚀 3ステップ

### ステップ 1️⃣: APIキーを取得（5分）

1. [Google AI Studio](https://aistudio.google.com/app/apikey) を開く
2. 「Create API Key」をクリック
3. キーをコピー（`AIzaSy...` で始まる文字列）

### ステップ 2️⃣: GitHubにアップロード（5分）

1. [GitHub](https://github.com/new) で新しいリポジトリを作成
   - 名前: `cosmic-guidance`
   - Public を選択
2. 「uploading an existing file」をクリック
3. このフォルダの全ファイルをドラッグ&ドロップ
4. 「Commit changes」をクリック

### ステップ 3️⃣: デプロイ（10分）

1. [Streamlit Cloud](https://streamlit.io/cloud) を開く
2. 「New app」をクリック
3. リポジトリを選択: `あなたのユーザー名/cosmic-guidance`
4. Main file: `app.py`
5. **「Advanced settings」をクリック**
6. Secretsに以下を入力：
   ```
   GEMINI_API_KEY = "ステップ1で取得したAPIキー"
   ```
7. 「Deploy!」をクリック

---

## ✅ 完成！

数分後、あなたのアプリが公開されます！

URLをシェアして、みんなに使ってもらいましょう！

---

## 📖 詳しく知りたい？

- [初心者向けガイド](SETUP_GUIDE.md) - 画像付き詳細手順
- [README](README_streamlit.md) - 技術詳細とカスタマイズ方法

---

**所要時間**: 約20分  
**費用**: 完全無料 💰  
**難易度**: ★☆☆☆☆

**さあ、始めましょう！** ✨
