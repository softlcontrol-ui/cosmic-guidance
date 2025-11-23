import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
from streamlit_js_eval import streamlit_js_eval, get_page_location

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
if 'loaded_from_storage' not in st.session_state:
    st.session_state.loaded_from_storage = False
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}

# ローカルストレージからデータを読み込む（✅ 修正版）
def load_from_local_storage():
    """ブラウザのローカルストレージからデータを読み込む"""
    try:
        # JavaScriptを使ってローカルストレージから読み込み
        js_code = """
        const data = localStorage.getItem('cosmic_guidance_sessions');
        return data;
        """
        result = streamlit_js_eval(js_eval=js_code, key='load_sessions')
        
        if result and result != 'null':
            # ✅ 修正：1回だけJSON.parse
            sessions_data = json.loads(result)
            
            # ✅ 修正：型チェックを追加
            if isinstance(sessions_data, dict) and 'sessions' in sessions_data:
                st.session_state.sessions = sessions_data.get('sessions', {})
                
                # 最後に使ったセッションを復元
                last_session_id = sessions_data.get('last_session_id')
                if last_session_id and last_session_id in st.session_state.sessions:
                    load_session(last_session_id)
                return True
    except json.JSONDecodeError as e:
        st.error(f"❌ データ読み込みエラー: {e}")
    except Exception as e:
        pass
    return False

# 新しいセッションを作成
def create_new_session():
    """新しいセッションを作成"""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.current_session_id = session_id
    st.session_state.sessions[session_id] = {
        'id': session_id,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        # 最初の質問を抽出（ユーザーの最初のメッセージ）
        first_question = None
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                first_question = msg['content'][:50] + ('...' if len(msg['content']) > 50 else '')
                break
        
        st.session_state.sessions[st.session_state.current_session_id] = {
            'id': st.session_state.current_session_id,
            'created_at': st.session_state.sessions[st.session_state.current_session_id]['created_at'],
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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

# ローカルストレージにデータを保存する（✅ 修正版）
def save_to_local_storage():
    """ブラウザのローカルストレージにデータを保存する（最新5セッションまで）"""
    try:
        # 現在のセッションを保存
        save_current_session()
        
        # 最新5セッションのみ保持
        MAX_SESSIONS = 5
        sorted_sessions = sorted(
            st.session_state.sessions.items(),
            key=lambda x: x[1].get('updated_at', x[1]['created_at']),
            reverse=True
        )
        sessions_to_save = dict(sorted_sessions[:MAX_SESSIONS])
        
        save_data = {
            'sessions': sessions_to_save,
            'last_session_id': st.session_state.current_session_id,
            'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # ✅ 修正：JSON文字列に1回だけ変換
        json_str = json.dumps(save_data, ensure_ascii=False)
        
        # ✅ 修正：JavaScriptの文字列リテラルとしてエスケープ
        # バックスラッシュ、シングルクォート、改行をエスケープ
        escaped_json = json_str.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        
        # ✅ 修正：シングルクォートで囲んで保存（二重エンコードなし！）
        js_code = f"""
        try {{
            localStorage.setItem('cosmic_guidance_sessions', '{escaped_json}');
            console.log('✅ セッション保存成功');
        }} catch (e) {{
            console.error('❌ セッション保存失敗:', e);
        }}
        """
        streamlit_js_eval(js_eval=js_code, key=f'save_sessions_{datetime.now().timestamp()}')
    except Exception as e:
        st.error(f"❌ 保存エラー: {e}")

# Gemini API設定
def configure_gemini():
    """Gemini APIを設定"""
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    
    if not api_key:
        st.error("⚠️ GEMINI_API_KEYが設定されていません")
        st.info("Streamlit Community Cloudのダッシュボードで、Secrets に `GEMINI_API_KEY` を追加してください")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')

# システムプロンプト
def get_system_prompt():
    """システムプロンプトを生成"""
    birthdate_str = st.session_state.birthdate if st.session_state.birthdate else "未設定"
    age_str = f"{st.session_state.age}歳" if st.session_state.age else "未設定"
    zodiac_str = st.session_state.zodiac if st.session_state.zodiac else "未設定"
    
    return f"""あなたは神秘的な占い師です。相談者に対して、スピリチュアルで詩的な表現を使いながら、心に響くアドバイスを提供してください。

【相談者の情報】
- 生年月日: {birthdate_str}
- 年齢: {age_str}
- 星座: {zodiac_str}

【回答のスタイル】
- 神秘的で詩的な表現を使用
- 宇宙や星、運命といった言葉を織り交ぜる
- 相談者の悩みに寄り添い、希望を与える
- 具体的なアドバイスと抽象的なメッセージのバランスを取る
- 適度な絵文字（✨、🌙、⭐など）を使用
- 敬語を使い、丁寧な口調で

【禁止事項】
- 断定的な未来予測
- 医療的・法律的アドバイス
- 相談者を不安にさせる表現"""

# 星座を計算
def calculate_zodiac(birthdate):
    """生年月日から星座を計算"""
    month = birthdate.month
    day = birthdate.day
    
    zodiacs = {
        (3, 21, 4, 19): "牡羊座 ♈",
        (4, 20, 5, 20): "牡牛座 ♉",
        (5, 21, 6, 21): "双子座 ♊",
        (6, 22, 7, 22): "蟹座 ♋",
        (7, 23, 8, 22): "獅子座 ♌",
        (8, 23, 9, 22): "乙女座 ♍",
        (9, 23, 10, 23): "天秤座 ♎",
        (10, 24, 11, 22): "蠍座 ♏",
        (11, 23, 12, 21): "射手座 ♐",
        (12, 22, 1, 19): "山羊座 ♑",
        (1, 20, 2, 18): "水瓶座 ♒",
        (2, 19, 3, 20): "魚座 ♓"
    }
    
    for (start_month, start_day, end_month, end_day), zodiac in zodiacs.items():
        if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
            return zodiac
    
    return "魚座 ♓"  # デフォルト

# メイン関数
def main():
    # Gemini APIを設定
    global model
    model = configure_gemini()
    
    # 初回のみローカルストレージからロード
    if not st.session_state.loaded_from_storage:
        if load_from_local_storage():
            st.session_state.loaded_from_storage = True
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <div class="logo">✨</div>
        <h1 class="main-title">運命の導き</h1>
        <p class="subtitle">COSMIC GUIDANCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 生年月日入力（初回のみ）
    if st.session_state.birthdate is None:
        with st.form("birthdate_form"):
            st.markdown("### 🌟 あなたの情報を教えてください")
            birthdate_input = st.date_input(
                "生年月日",
                min_value=datetime(1900, 1, 1),
                max_value=datetime.now(),
                help="あなたの運命の扉を開くために、生年月日をお教えください"
            )
            
            submit = st.form_submit_button("✨ 運命の扉を開く", use_container_width=True)
            
            if submit:
                st.session_state.birthdate = birthdate_input.strftime("%Y-%m-%d")
                
                # 年齢を計算
                today = datetime.now()
                age = today.year - birthdate_input.year
                if today.month < birthdate_input.month or (today.month == birthdate_input.month and today.day < birthdate_input.day):
                    age -= 1
                st.session_state.age = age
                
                # 星座を計算
                st.session_state.zodiac = calculate_zodiac(birthdate_input)
                
                # 新しいセッションを作成
                create_new_session()
                
                # 自動保存
                save_to_local_storage()
                
                st.rerun()
    
    else:
        # サイドバーにプロフィールとセッション管理を表示
        with st.sidebar:
            st.markdown("### 👤 あなたのプロフィール")
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">🎂 生年月日</div>
                <div class="profile-value">{st.session_state.birthdate}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">📅 年齢</div>
                <div class="profile-value">{st.session_state.age}歳</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">⭐ 星座</div>
                <div class="profile-value">{st.session_state.zodiac}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # セッション管理
            st.subheader("📚 過去のセッション")
            st.caption(f"最新5件まで自動保存されます（現在: {len(st.session_state.sessions)}件）")
            
            if st.session_state.sessions:
                # セッションを更新日時でソート
                sorted_sessions = sorted(
                    st.session_state.sessions.items(),
                    key=lambda x: x[1].get('updated_at', x[1]['created_at']),
                    reverse=True
                )
                
                for session_id, session in sorted_sessions:
                    # 現在のセッションかどうか
                    is_current = session_id == st.session_state.current_session_id
                    
                    # セッション情報
                    created = session['created_at']
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
                            del st.session_state.sessions[session_id]
                            if session_id == st.session_state.current_session_id:
                                # 現在のセッションを削除した場合、クリア
                                st.session_state.current_session_id = None
                                st.session_state.messages = []
                            save_to_local_storage()
                            st.rerun()
                    
                    # 最初の質問を表示
                    if first_q:
                        st.caption(f"💬 {first_q}")
                    
                    st.markdown("---")
            
            # 新しいセッション作成
            if st.button("➕ 新しいセッションを開始", use_container_width=True, type="primary"):
                # ローカルストレージをクリア
                js_code = "localStorage.removeItem('cosmic_guidance_sessions');"
                streamlit_js_eval(js_eval=js_code, key=f'new_session_{datetime.now().timestamp()}')
                
                st.session_state.messages = []
                st.session_state.birthdate = None
                st.session_state.age = None
                st.session_state.zodiac = None
                st.session_state.current_session_id = None
                st.rerun()
            
            st.markdown("---")
            
            # 手動バックアップ（オプション）
            if len(st.session_state.messages) > 0:
                st.subheader("📥 現在のセッションをバックアップ")
                st.caption("現在のセッションをJSONファイルとして保存できます")
                
                save_data = {
                    "session_id": st.session_state.current_session_id,
                    "birthdate": st.session_state.birthdate,
                    "age": st.session_state.age,
                    "zodiac": st.session_state.zodiac,
                    "messages": st.session_state.messages,
                    "created_at": st.session_state.sessions[st.session_state.current_session_id]['created_at'] if st.session_state.current_session_id in st.session_state.sessions else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_messages": len(st.session_state.messages)
                }
                json_str = json.dumps(save_data, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label=f"💾 このセッションをダウンロード ({len(st.session_state.messages)}件)",
                    data=json_str,
                    file_name=f"session_{st.session_state.current_session_id}.json",
                    mime="application/json",
                    use_container_width=True,
                    help="現在のセッションをJSONファイルとして保存します"
                )
            
            st.markdown("---")
            
            # バックアップファイルの復元
            st.subheader("📂 バックアップから復元")
            uploaded_file = st.file_uploader(
                "保存したJSONファイルを選択",
                type=['json'],
                help="手動バックアップしたファイルから会話を新しいセッションとして復元できます"
            )
            
            if uploaded_file is not None:
                try:
                    load_data = json.load(uploaded_file)
                    
                    # 新しいセッションIDを生成
                    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # セッションデータを作成
                    st.session_state.sessions[session_id] = {
                        'id': session_id,
                        'created_at': load_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'birthdate': load_data.get("birthdate"),
                        'age': load_data.get("age"),
                        'zodiac': load_data.get("zodiac"),
                        'messages': load_data.get("messages", []),
                        'message_count': len(load_data.get("messages", [])),
                        'first_question': None
                    }
                    
                    # そのセッションをロード
                    load_session(session_id)
                    
                    # ローカルストレージにも保存
                    save_to_local_storage()
                    
                    st.success(f"✅ {len(st.session_state.messages)}件の会話を新しいセッションとして復元しました！")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ ファイルの読み込みに失敗: {str(e)}")
            
            st.markdown("---")
            
            # 全データクリア（危険な操作なので最下部に）
            with st.expander("🗑️ すべてのデータを削除（危険）"):
                st.warning("この操作は取り消せません。すべてのセッションが削除されます。")
                if st.button("⚠️ 本当に削除する", use_container_width=True, type="secondary"):
                    # ローカルストレージをクリア
                    js_code = "localStorage.removeItem('cosmic_guidance_sessions');"
                    streamlit_js_eval(js_eval=js_code, key=f'clear_all_{datetime.now().timestamp()}')
                    
                    # セッション状態をクリア
                    st.session_state.messages = []
                    st.session_state.birthdate = None
                    st.session_state.age = None
                    st.session_state.zodiac = None
                    st.session_state.current_session_id = None
                    st.session_state.sessions = {}
                    st.session_state.loaded_from_storage = False
                    
                    st.success("✅ すべてのデータを削除しました")
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
                        
                        # ローカルストレージに自動保存
                        save_to_local_storage()
                        
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
