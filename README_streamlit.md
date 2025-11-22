# 運命の導き - Cosmic Guidance (Streamlit版)

Google AI Studio (Gemini API) を使った、運命を読み解くスピリチュアルなWebアプリです。

## 🌟 特徴

- 🔮 **AI占い**: Gemini AIがあなたの運命を読み解きガイダンスを提供
- 🎨 **神秘的なデザイン**: 宇宙的・スピリチュアルな美しいUI
- 🔒 **セキュア**: APIキーはサーバー側で安全に管理
- 🚀 **簡単デプロイ**: GitHub連携で自動デプロイ
- 💯 **完全無料**: Google AI Studio、GitHub、Streamlit Community Cloud、すべて無料

## 📦 必要なもの

1. **Google AI Studio APIキー** (無料)
2. **GitHubアカウント** (無料)
3. **Streamlit Community Cloudアカウント** (無料、GitHubでサインアップ)

## 🚀 セットアップ手順

### ステップ1: Google AI Studio APIキーの取得

1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. APIキーをコピー（後で使います）

### ステップ2: GitHubにリポジトリを作成

1. [GitHub](https://github.com/) にログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名を入力（例: `cosmic-guidance`）
4. 「Public」を選択
5. 「Create repository」をクリック

### ステップ3: コードをGitHubにアップロード

```bash
# このディレクトリで実行
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/cosmic-guidance.git
git push -u origin main
```

または、GitHubのWebインターフェースから直接アップロードも可能です：
1. リポジトリページで「Add file」→「Upload files」
2. すべてのファイルをドラッグ&ドロップ
3. 「Commit changes」をクリック

### ステップ4: Streamlit Community Cloudでデプロイ

1. [Streamlit Community Cloud](https://streamlit.io/cloud) にアクセス
2. GitHubアカウントでサインアップ/ログイン
3. 「New app」をクリック
4. 以下を入力：
   - Repository: `あなたのユーザー名/cosmic-guidance`
   - Branch: `main`
   - Main file path: `app.py`
5. 「Advanced settings」をクリック
6. 「Secrets」に以下を追加：
   ```toml
   GEMINI_API_KEY = "あなたのAPIキー"
   ```
7. 「Deploy!」をクリック

### 🎉 完成！

数分後、あなたのアプリが公開URLで利用可能になります！

例: `https://あなたのアプリ名.streamlit.app`

## 📁 ファイル構成

```
/
├── app.py                           # メインアプリケーション
├── requirements.txt                 # Python依存パッケージ
├── .gitignore                       # Git除外設定
├── .streamlit/
│   ├── config.toml                  # Streamlit設定
│   └── secrets.toml.example         # APIキー設定の例
└── README.md                        # このファイル
```

## 🔧 ローカルで開発する場合

### 1. 環境構築

```bash
# Python仮想環境を作成（推奨）
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. APIキーを設定

`.streamlit/secrets.toml` ファイルを作成：

```toml
GEMINI_API_KEY = "あなたのAPIキー"
```

**⚠️ 重要**: `secrets.toml` は絶対にGitにコミットしないでください！

### 3. アプリを起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 🎨 カスタマイズ

### プロンプトの変更

`app.py` の `generate_guidance()` 関数内の `prompt` 変数を編集：

```python
prompt = f"""あなたは深い洞察力を持つ運命の導き手です...
```

### デザインの変更

`app.py` の `st.markdown()` 内のCSSを編集：

```python
st.markdown("""
<style>
    /* ここでカラーやフォントを変更 */
    .stApp {
        background: linear-gradient(135deg, #0a0118 0%, #1a0933 50%, #0a0118 100%);
    }
</style>
""", unsafe_allow_html=True)
```

### テーマ設定

`.streamlit/config.toml` を編集：

```toml
[theme]
primaryColor = "#d4af37"      # メインカラー
backgroundColor = "#0a0118"    # 背景色
textColor = "#ffffff"          # テキスト色
```

## 💡 使い方のコツ

### APIキーの無料枠

Google AI Studioの無料枠：
- **60リクエスト/分**
- **1,500リクエスト/日**

通常の使用では十分です。

### プライバシー

- ユーザーの入力データは保存されません
- すべての処理はセッション内で完結
- APIキーはStreamlit Secretsで安全に管理

## 🐛 トラブルシューティング

### 「APIキーが設定されていません」エラー

→ Streamlit Community Cloudの「Settings」→「Secrets」でAPIキーを設定してください。

### デプロイが失敗する

→ `requirements.txt` が正しくコミットされているか確認してください。

### ローカルで動かない

→ 仮想環境が有効化されているか、`pip install -r requirements.txt` を実行したか確認してください。

## 🔄 更新方法

コードを変更したら：

```bash
git add .
git commit -m "更新内容"
git push
```

Streamlit Community Cloudが自動的に再デプロイします！

## 📊 アクセス解析（オプション）

Streamlit Community Cloudでは、以下の情報が確認できます：
- アクセス数
- ユーザー数
- エラーログ

アプリのダッシュボードから「Analytics」で確認可能。

## 🌐 独自ドメインの設定（オプション）

Streamlit Community Cloudでは、独自ドメインの設定も可能です：
1. アプリの「Settings」→「General」
2. 「Custom domain」を設定

## 📄 ライセンス

このプロジェクトはMITライセンスです。自由に改変・配布できます。

## 🙏 謝辞

- **Google AI Studio** - Gemini API
- **Streamlit** - 素晴らしいフレームワーク
- **GitHub** - コード管理

## 🆘 サポート

質問や問題があれば、GitHubのIssuesで報告してください！

---

**作成者**: Claude & あなた  
**バージョン**: 2.0.0 (Streamlit版)  
**更新日**: 2024年11月

✨ **あなたの運命が、この宇宙の中で輝きますように。** ✨
