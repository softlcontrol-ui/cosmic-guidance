import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
from supabase import create_client, Client
import re

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
    
    /* ログインフォーム */
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: rgba(29, 15, 51, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 15px;
        backdrop-filter: blur(10px);
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
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}
if 'user' not in st.session_state:
    st.session_state.user = None
if 'supabase_loaded' not in st.session_state:
    st.session_state.supabase_loaded = False

# Supabase接続
@st.cache_resource
def get_supabase_client() -> Client:
    """Supabaseクライアントを取得"""
    supabase_url = st.secrets.get("SUPABASE_URL", None)
    supabase_key = st.secrets.get("SUPABASE_KEY", None)
    
    if not supabase_url or not supabase_key:
        st.error("⚠️ Supabase設定が不足しています。")
        st.stop()
    
    return create_client(supabase_url, supabase_key)

# メール検証
def is_valid_email(email):
    """メールアドレスの形式を検証"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# サインアップ
def sign_up(email, password):
    """新規ユーザー登録"""
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            st.success("✅ 登録完了！メールを確認して認証してください。")
            return True
        return False
    except Exception as e:
        st.error(f"⚠️ 登録エラー: {str(e)}")
        return False

# ログイン
def sign_in(email, password):
    """ログイン"""
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            st.session_state.user = response.user
            st.session_state.supabase_loaded = False  # データを再読み込み
            return True
        return False
    except Exception as e:
        st.error(f"⚠️ ログインエラー: {str(e)}")
        return False

# ログアウト
def sign_out():
    """ログアウト"""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.sessions = {}
        st.session_state.supabase_loaded = False
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ ログアウトエラー: {str(e)}")

# Supabaseからデータを読み込む
def load_from_supabase():
    """Supabaseからセッションデータを読み込む"""
    if not st.session_state.user:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # 認証されたユーザーのセッションを取得（最新5件）
        response = supabase.table('sessions').select('*').eq(
            'user_id', st.session_state.user.id
        ).order('updated_at', desc=True).limit(5).execute()
        
        if response.data:
            # セッションデータを復元
            st.session_state.sessions = {}
            for session in response.data:
                session_id = session['session_id']
                st.session_state.sessions[session_id] = {
                    'id': session_id,
                    'created_at': session['created_at'],
                    'updated_at': session['updated_at'],
                    'birthdate': session['birthdate'],
                    'age': session['age'],
                    'zodiac': session['zodiac'],
                    'messages': session['messages'],
                    'message_count': len(session['messages']),
                    'first_question': session['messages'][0]['content'][:50] if session['messages'] else None
                }
            
            # 最新のセッションをロード
            if response.data:
                latest = response.data[0]
                load_session(latest['session_id'])
            
            return True
    except Exception as e:
        st.warning(f"⚠️ データ読み込みエラー: {e}")
        return False

# 新しいセッションを作成
def create_new_session():
    """新しいセッションを作成"""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.current_session_id = session_id
    st.session_state.sessions[session_id] = {
        'id': session_id,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'birthdate': st.session_state.birthdate,
        'age': st.session_state.age,
        'zodiac': st.session_state.zodiac,
        'messages': [],
        'first_question': None
    }

# 現在のセッションを保存
def save_current_session():
    """現在のセッションを保存"""
    if st.session_state.current_session_id:
        # 最初の質問を抽出
        first_question = None
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                first_question = msg['content'][:50] + ('...' if len(msg['content']) > 50 else '')
                break
        
        st.session_state.sessions[st.session_state.current_session_id] = {
            'id': st.session_state.current_session_id,
            'created_at': st.session_state.sessions[st.session_state.current_session_id]['created_at'],
            'updated_at': datetime.now().isoformat(),
            'birthdate': st.session_state.birthdate,
            'age': st.session_state.age,
            'zodiac': st.session_state.zodiac,
            'messages': st.session_state.messages,
            'message_count': len(st.session_state.messages),
            'first_question': first_question
        }

# セッションをロード
def load_session(session_id):
    """指定されたセッションをロード"""
    if session_id in st.session_state.sessions:
        session = st.session_state.sessions[session_id]
        st.session_state.current_session_id = session_id
        st.session_state.birthdate = session['birthdate']
        st.session_state.age = session['age']
        st.session_state.zodiac = session['zodiac']
        st.session_state.messages = session['messages']

# Supabaseにデータを保存する
def save_to_supabase():
    """Supabaseにデータを保存する"""
    if not st.session_state.user or not st.session_state.current_session_id:
        return
    
    try:
        # 現在のセッションを保存
        save_current_session()
        
        supabase = get_supabase_client()
        session = st.session_state.sessions[st.session_state.current_session_id]
        
        # データを準備
        data = {
            'user_id': st.session_state.user.id,
            'session_id': st.session_state.current_session_id,
            'birthdate': session['birthdate'],
            'age': session['age'],
            'zodiac': session['zodiac'],
            'messages': session['messages'],
            'updated_at': datetime.now().isoformat()
        }
        
        # 既存のレコードをチェック
        existing = supabase.table('sessions').select('id').eq(
            'user_id', st.session_state.user.id
        ).eq('session_id', st.session_state.current_session_id).execute()
        
        if existing.data:
            # 更新
            supabase.table('sessions').update(data).eq(
                'user_id', st.session_state.user.id
            ).eq('session_id', st.session_state.current_session_id).execute()
        else:
            # 新規作成
            data['created_at'] = datetime.now().isoformat()
            supabase.table('sessions').insert(data).execute()
        
        return True
    except Exception as e:
        st.warning(f"⚠️ データ保存エラー: {e}")
        return False

# Gemini API設定
def configure_gemini():
    """Gemini APIを設定"""
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    
    if not api_key:
        st.error("⚠️ APIキーが設定されていません。")
        st.stop()
    
    genai.configure(api_key=api_key)
    
    # システムプロンプトを使用してモデルを初期化
    system_prompt = get_system_prompt() if st.session_state.birthdate else "あなたは運命の導き手です。"
    
    return genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=system_prompt
    )

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

# ログインページ
def login_page():
    """ログイン/サインアップページ"""
    st.markdown("""
    <div class="main-header">
        <div class="logo">✨</div>
        <h1 class="main-title">運命の導き</h1>
        <p class="subtitle">COSMIC GUIDANCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["ログイン", "新規登録"])
    
    with tab1:
        st.subheader("ログイン")
        email = st.text_input("メールアドレス", key="login_email")
        password = st.text_input("パスワード", type="password", key="login_password")
        
        if st.button("ログイン", use_container_width=True):
            if not email or not password:
                st.error("メールアドレスとパスワードを入力してください")
            elif not is_valid_email(email):
                st.error("正しいメールアドレスを入力してください")
            else:
                if sign_in(email, password):
                    st.success("✅ ログイン成功！")
                    st.rerun()
    
    with tab2:
        st.subheader("新規登録")
        new_email = st.text_input("メールアドレス", key="signup_email")
        new_password = st.text_input("パスワード（8文字以上）", type="password", key="signup_password")
        new_password_confirm = st.text_input("パスワード（確認）", type="password", key="signup_password_confirm")
        
        if st.button("登録", use_container_width=True):
            if not new_email or not new_password:
                st.error("すべての項目を入力してください")
            elif not is_valid_email(new_email):
                st.error("正しいメールアドレスを入力してください")
            elif len(new_password) < 8:
                st.error("パスワードは8文字以上にしてください")
            elif new_password != new_password_confirm:
                st.error("パスワードが一致しません")
            else:
                if sign_up(new_email, new_password):
                    st.info("📧 確認メールを送信しました。メールボックスを確認してください。")
    
    st.markdown("</div>", unsafe_allow_html=True)

# メインアプリ
def main():
    # ログインチェック
    if not st.session_state.user:
        login_page()
        return
    
    model = configure_gemini()
    
    # 初回のみSupabaseから読み込み
    if not st.session_state.supabase_loaded:
        load_from_supabase()
        st.session_state.supabase_loaded = True
    
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
            
            # 新しいセッションを作成
            create_new_session()
            
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
            
            # Supabaseに保存
            save_to_supabase()
            
            st.rerun()
    
    else:
        # サイドバーにプロフィール表示
        with st.sidebar:
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">ようこそ</div>
                <div class="profile-value">✉️ {st.session_state.user.email}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">あなたのプロフィール</div>
                <div class="profile-value">🎂 {st.session_state.birthdate}</div>
                <div class="profile-value">✨ {st.session_state.age}歳</div>
                <div class="profile-value">♈ {st.session_state.zodiac}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 ログアウト", use_container_width=True):
                sign_out()
            
            st.markdown("---")
            
            # 保存されたセッション一覧
            if len(st.session_state.sessions) > 0:
                st.subheader("💾 保存されたセッション")
                st.caption(f"{len(st.session_state.sessions)}件のセッション")
                
                # セッションを新しい順にソート
                sorted_sessions = sorted(
                    st.session_state.sessions.items(),
                    key=lambda x: x[1].get('updated_at', x[1]['created_at']),
                    reverse=True
                )
                
                for session_id, session in sorted_sessions:
                    # 現在のセッションかどうか
                    is_current = session_id == st.session_state.current_session_id
                    
                    # セッション情報
                    created = session['created_at'][:19]
                    msg_count = session.get('message_count', len(session.get('messages', [])))
                    first_q = session.get('first_question', '新しいセッション')
                    
                    # ボタンのラベル
                    label = f"{'🔵 ' if is_current else '📅 '}{created} ({msg_count}件)"
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(
                            label,
                            key=f"session_{session_id}",
                            use_container_width=True,
                            disabled=is_current,
                            help=f"最初の質問: {first_q}"
                        ):
                            load_session(session_id)
                            st.rerun()
                    
                    with col2:
                        # 削除ボタン
                        if st.button("🗑️", key=f"del_{session_id}", help="このセッションを削除"):
                            try:
                                # Supabaseから削除
                                supabase = get_supabase_client()
                                supabase.table('sessions').delete().eq(
                                    'user_id', st.session_state.user.id
                                ).eq('session_id', session_id).execute()
                                
                                # ローカルからも削除
                                del st.session_state.sessions[session_id]
                                if session_id == st.session_state.current_session_id:
                                    st.session_state.current_session_id = None
                                    st.session_state.messages = []
                                st.rerun()
                            except Exception as e:
                                st.error(f"削除エラー: {e}")
                    
                    # 最初の質問を表示
                    if first_q:
                        st.caption(f"💬 {first_q}")
                    
                    st.markdown("---")
            
            # 新しいセッション作成
            if st.button("➕ 新しいセッションを開始", use_container_width=True, type="primary"):
                st.session_state.messages = []
                st.session_state.birthdate = None
                st.session_state.age = None
                st.session_state.zodiac = None
                st.session_state.current_session_id = None
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
                    try:
                        # モデルを再初期化（最新のsystem_instructionを使用）
                        model = configure_gemini()
                        
                        # 会話履歴を構築
                        conversation_history = []
                        for msg in st.session_state.messages[:-1]:
                            role = "model" if msg["role"] == "assistant" else msg["role"]
                            conversation_history.append({
                                "role": role,
                                "parts": [{"text": msg["content"]}]
                            })
                        
                        # 会話履歴がある場合は、それを含める
                        if conversation_history:
                            chat = model.start_chat(history=conversation_history)
                            response = chat.send_message(prompt)
                        else:
                            response = model.generate_content(prompt)
                        
                        assistant_message = response.text
                        st.markdown(assistant_message)
                        
                        # アシスタントメッセージを追加
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                        
                        # Supabaseに自動保存
                        save_to_supabase()
                        
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
        © 2024 運命の導き - Powered by Google Gemini AI & Supabase Auth
    </footer>
    """, unsafe_allow_html=True)

Add login functionality with Supabase Auth
