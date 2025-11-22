import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time

# ページ設定
st.set_page_config(
    page_title="運命の導き - Cosmic Guidance",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# カスタムCSS - 神秘的なデザイン
st.markdown("""
<style>
    /* 全体の背景 */
    .stApp {
        background: linear-gradient(135deg, #0a0118 0%, #1a0933 50%, #0a0118 100%);
        color: #ffffff;
    }
    
    /* ヘッダー */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .logo {
        font-size: 4rem;
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { 
            opacity: 0.8; 
            text-shadow: 0 0 10px #d4af37;
        }
        50% { 
            opacity: 1; 
            text-shadow: 0 0 20px #d4af37, 0 0 30px #d4af37;
        }
    }
    
    .main-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3rem;
        font-weight: 300;
        letter-spacing: 0.3em;
        background: linear-gradient(135deg, #d4af37 0%, #f4d16f 50%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 1rem 0;
    }
    
    .subtitle {
        font-size: 1rem;
        color: #c0c0c0;
        letter-spacing: 0.2em;
        font-weight: 300;
    }
    
    /* カード */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        background-color: rgba(10, 1, 24, 0.8) !important;
        border: 1px solid rgba(192, 192, 192, 0.2) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stDateInput > div > div > input:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3) !important;
    }
    
    /* ボタン */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #d4af37 0%, #f4d16f 100%);
        color: #0a0118;
        border: none;
        border-radius: 50px;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(212, 175, 55, 0.6);
    }
    
    /* 結果表示 */
    .result-box {
        background: rgba(29, 15, 51, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .result-title {
        font-family: 'Cormorant Garamond', serif;
        color: #f4d16f;
        font-size: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .result-content {
        line-height: 2;
        color: #ffffff;
        white-space: pre-wrap;
        font-size: 1.1rem;
    }
    
    /* ラベル */
    .stTextInput > label,
    .stTextArea > label,
    .stDateInput > label {
        color: #f4d16f !important;
        font-weight: 500 !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Info box */
    .stInfo {
        background-color: rgba(61, 31, 92, 0.4) !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 15px !important;
        color: #c0c0c0 !important;
    }
    
    /* フッター */
    footer {
        text-align: center;
        padding: 2rem 0;
        color: #c0c0c0;
        font-size: 0.9rem;
        opacity: 0.7;
    }
    
    /* スピナー */
    .stSpinner > div {
        border-top-color: #d4af37 !important;
    }
</style>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="main-header">
    <div class="logo">✨</div>
    <h1 class="main-title">運命の導き</h1>
    <p class="subtitle">COSMIC GUIDANCE</p>
</div>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'result' not in st.session_state:
    st.session_state.result = None

# Gemini API設定
def configure_gemini():
    """Gemini APIを設定"""
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    
    if not api_key:
        st.error("⚠️ APIキーが設定されていません。Streamlit Secretsに `GEMINI_API_KEY` を設定してください。")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# 星座を計算
def get_zodiac_sign(month, day):
    """生年月日から星座を取得"""
    zodiac_signs = [
        (1, 20, "山羊座"), (2, 19, "水瓶座"), (3, 21, "魚座"),
        (4, 20, "牡羊座"), (5, 21, "牡牛座"), (6, 22, "双子座"),
        (7, 23, "蟹座"), (8, 23, "獅子座"), (9, 23, "乙女座"),
        (10, 23, "天秤座"), (11, 22, "蠍座"), (12, 22, "射手座"),
        (12, 31, "山羊座")
    ]
    
    for m, d, sign in zodiac_signs:
        if month < m or (month == m and day <= d):
            return sign
    return "山羊座"

# ガイダンスを生成
def generate_guidance(model, birthdate, question):
    """AIからガイダンスを生成"""
    birth = datetime.strptime(birthdate, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    zodiac = get_zodiac_sign(birth.month, birth.day)
    
    prompt = f"""あなたは深い洞察力を持つ運命の導き手です。以下の情報をもとに、相談者に対して神秘的で詩的、かつ具体的で実用的なガイダンスを提供してください。

【相談者の情報】
- 生年月日: {birthdate}
- 年齢: {age}歳
- 星座: {zodiac}

【相談内容】
{question}

【ガイダンスの形式】
以下の3つの観点から、優しく、しかし力強く語りかけてください：

1. **宇宙からのメッセージ** - 星々が示す運命の流れと、今この瞬間の意味
2. **内なる声** - 相談者の魂が本当に求めているもの
3. **具体的な導き** - 今日からできる3つの行動指針

美しい日本語で、まるで古の賢者が語りかけるように。
ただし説教臭くならず、相談者を信じ、背中を押すような言葉を選んでください。

各セクションには適切な絵文字を使い、読みやすく構成してください。"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# メインコンテンツ
def main():
    # APIの設定
    model = configure_gemini()
    
    # 説明
    st.info("""
    ✨ **運命の導き**へようこそ。
    
    あなたの生年月日と問いを入力してください。
    宇宙の叡智があなたに語りかけます。
    """)
    
    # 入力フォーム
    with st.form("guidance_form"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            birthdate = st.date_input(
                "生年月日",
                value=datetime(1990, 1, 1),
                min_value=datetime(1900, 1, 1),
                max_value=datetime.now()
            )
        
        with col2:
            st.write("")  # スペース調整
        
        question = st.text_area(
            "あなたの問い",
            placeholder="今、あなたが知りたいことは何ですか？\n人生の方向性、恋愛、仕事、健康...何でも構いません。",
            height=150
        )
        
        submitted = st.form_submit_button("✨ 運命を読み解く")
    
    # フォームが送信された場合
    if submitted:
        if not question.strip():
            st.warning("問いを入力してください。")
            return
        
        # ローディングアニメーション
        with st.spinner("🌌 宇宙と対話中..."):
            time.sleep(1)  # 演出
            result = generate_guidance(
                model,
                birthdate.strftime("%Y-%m-%d"),
                question
            )
            st.session_state.result = result
    
    # 結果を表示
    if st.session_state.result:
        st.markdown(f"""
        <div class="result-box">
            <h2 class="result-title">✧ 導きの言葉 ✧</h2>
            <div class="result-content">{st.session_state.result}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # リセットボタン
        if st.button("🔄 新しい問いを立てる"):
            st.session_state.result = None
            st.rerun()

if __name__ == "__main__":
    main()
    
    # フッター
    st.markdown("""
    <footer>
        © 2024 運命の導き - Powered by Google Gemini AI
    </footer>
    """, unsafe_allow_html=True)
