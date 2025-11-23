import streamlit as st
import google.generativeai as genai
from datetime import datetime

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
        padding: 2rem 0 1rem;
        margin-bottom: 1rem;
    }
    
    .logo {
        font-size: 3rem;
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
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: 0.3em;
        background: linear-gradient(135deg, #d4af37 0%, #f4d16f 50%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #c0c0c0;
        letter-spacing: 0.2em;
        font-weight: 300;
    }
    
    /* チャットメッセージのスタイル */
    .stChatMessage {
        background-color: rgba(29, 15, 51, 0.6) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* ユーザーメッセージ */
    [data-testid="stChatMessageContent"] {
        color: #ffffff !important;
    }
    
    /* 入力欄 */
    .stTextInput > div > div > input,
    .stDateInput > div > div > input {
        background-color: rgba(10, 1, 24, 0.8) !important;
        border: 1px solid rgba(192, 192, 192, 0.2) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3) !important;
    }
    
    /* チャット入力欄 */
    .stChatInputContainer {
        background-color: rgba(29, 15, 51, 0.6) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 15px !important;
    }
    
    /* ボタン */
    .stButton > button {
        background: linear-gradient(135deg, #d4af37 0%, #f4d16f 100%);
        color: #0a0118;
        border: none;
        border-radius: 50px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(212, 175, 55, 0.6);
    }
    
    /* ラベル */
    .stTextInput > label,
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
    
    /* サイドバー（プロフィール表示用） */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1a0933 0%, #0a0118 100%);
    }
    
    .profile-info {
        background: rgba(29, 15, 51, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .profile-label {
        color: #f4d16f;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .profile-value {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 500;
    }
</style>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'birthdate' not in st.session_state:
    st.session_state.birthdate = None
if 'age' not in st.session_state:
    st.session_state.age = None
if 'zodiac' not in st.session_state:
    st.session_state.zodiac = None

# Gemini API設定
def configure_gemini():
    """Gemini APIを設定"""
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    
    if not api_key:
        st.error("⚠️ APIキーが設定されていません。Streamlit Secretsに `GEMINI_API_KEY` を設定してください。")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

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

# 年齢と星座を計算
def calculate_profile(birthdate_str):
    """生年月日から年齢と星座を計算"""
    birth = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    zodiac = get_zodiac_sign(birth.month, birth.day)
    return age, zodiac

# システムプロンプトを生成
def get_system_prompt():
    """ユーザー情報を含むシステムプロンプト"""
    if st.session_state.birthdate:
        return f"""あなたは深い洞察力を持つ運命の導き手です。
相談者と対話しながら、その人の人生を導いていきます。

【相談者の情報】
- 生年月日: {st.session_state.birthdate}
- 年齢: {st.session_state.age}歳
- 星座: {st.session_state.zodiac}

【あなたの役割】
- 相談者の質問に対して、神秘的で詩的、かつ具体的で実用的なアドバイスを提供する
- 必要に応じて、星座や年齢の情報を活用する
- 優しく、しかし力強く語りかける
- 説教臭くならず、相談者を信じ、背中を押すような言葉を選ぶ
- 会話は自然に、相談者が求める深さに合わせて応答する

美しい日本語で、まるで古の賢者が語りかけるように応答してください。
ただし、簡潔な質問には簡潔に、深い相談には深く応答してください。"""
    return "あなたは運命の導き手です。"

# メインアプリ
def main():
    model = configure_gemini()
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <div class="logo">✨</div>
        <h1 class="main-title">運命の導き</h1>
        <p class="subtitle">COSMIC GUIDANCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 生年月日が未設定の場合、入力画面を表示
    if st.session_state.birthdate is None:
        st.info("✨ **運命の導き**へようこそ。\n\nまず、あなたの生年月日を教えてください。")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            birthdate = st.date_input(
                "生年月日",
                value=datetime(1990, 1, 1),
                min_value=datetime(1900, 1, 1),
                max_value=datetime.now()
            )
        
        if st.button("✨ 対話を始める", use_container_width=True):
            birthdate_str = birthdate.strftime("%Y-%m-%d")
            age, zodiac = calculate_profile(birthdate_str)
            
            st.session_state.birthdate = birthdate_str
            st.session_state.age = age
            st.session_state.zodiac = zodiac
            
            # 初回メッセージ
            welcome_message = f"""✨ ようこそ。

あなたは{st.session_state.age}歳、{st.session_state.zodiac}の方ですね。

私はあなたの運命の導き手です。
人生の方向性、恋愛、仕事、健康...何でもお聞きください。

今、あなたの心に浮かんでいることは何ですか？"""
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": welcome_message
            })
            
            st.rerun()
    
    else:
        # サイドバーにプロフィール表示
        with st.sidebar:
            st.markdown("""
            <div class="profile-info">
                <div class="profile-label">あなたのプロフィール</div>
                <div class="profile-value">🎂 {birthdate}</div>
                <div class="profile-value">✨ {age}歳</div>
                <div class="profile-value">♈ {zodiac}</div>
            </div>
            """.format(
                birthdate=st.session_state.birthdate,
                age=st.session_state.age,
                zodiac=st.session_state.zodiac
            ), unsafe_allow_html=True)
            
            if st.button("🔄 新しいセッションを始める"):
                st.session_state.messages = []
                st.session_state.birthdate = None
                st.session_state.age = None
                st.session_state.zodiac = None
                st.rerun()
        
        # チャット履歴を表示
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # ユーザー入力
        if prompt := st.chat_input("あなたの問いを入力してください..."):
            # ユーザーメッセージを追加
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # AIの応答を生成
            with st.chat_message("assistant"):
                with st.spinner("🌌 宇宙と対話中..."):
               # 会話履歴を構築（Gemini APIでは "assistant" -> "model" に変換）
   conversation_history = []
   for msg in st.session_state.messages[:-1]:  # 最新のユーザーメッセージ以外
       role = "model" if msg["role"] == "assistant" else msg["role"]
       conversation_history.append({
           "role": role,
           "parts": [{"text": msg["content"]}]
       })
                    
                    # システムプロンプトを含めてリクエスト
                    system_prompt = get_system_prompt()
                    full_prompt = f"{system_prompt}\n\n【相談者の質問】\n{prompt}"
                    
                    try:
                        # 会話履歴がある場合は、それを含める
                        if conversation_history:
                            chat = model.start_chat(history=conversation_history)
                            response = chat.send_message(full_prompt)
                        else:
                            response = model.generate_content(full_prompt)
                        
                        assistant_message = response.text
                        st.markdown(assistant_message)
                        
                        # アシスタントメッセージを追加
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                        
                    except Exception as e:
                        error_message = f"エラーが発生しました: {str(e)}"
                        st.error(error_message)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_message
                        })

if __name__ == "__main__":
    main()
    
    # フッター
    st.markdown("""
    <footer style='text-align: center; padding: 2rem 0; color: #c0c0c0; font-size: 0.8rem; opacity: 0.7;'>
        © 2024 運命の導き - Powered by Google Gemini AI
    </footer>
    """, unsafe_allow_html=True)
