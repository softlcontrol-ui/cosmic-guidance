import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
from streamlit_js_eval import streamlit_js_eval, get_page_location
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
if 'save_status' not in st.session_state:
    st.session_state.save_status = None

# ローカルストレージからデータを読み込む（修正版）
def load_from_local_storage():
    """ブラウザのローカルストレージからデータを読み込む"""
    try:
        # JavaScriptを使ってローカルストレージから読み込み
        js_code = """
        const data = localStorage.getItem('cosmic_guidance_sessions');
        return data;
        """
        # 動的なkeyを使用して複数回の読み込みに対応
        result = streamlit_js_eval(
            js_eval=js_code, 
            key=f'load_sessions_{time.time()}'
        )
        
        if result and result != 'null' and result != None:
            sessions_data = json.loads(result)
            st.session_state.sessions = sessions_data.get('sessions', {})
            
            # 最後に使ったセッションを復元
            last_session_id = sessions_data.get('last_session_id')
            if last_session_id and last_session_id in st.session_state.sessions:
                load_session(last_session_id)
            return True
    except json.JSONDecodeError as e:
        st.error(f"⚠️ 保存データの読み込みエラー: {str(e)}")
    except Exception as e:
        st.error(f"⚠️ ローカルストレージ読み込みエラー: {str(e)}")
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
        'message_count': 0,
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

# ローカルストレージにデータを保存する（修正版）
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
        
        # JSONエンコーディングを一度だけ行う（修正箇所）
        json_str = json.dumps(save_data, ensure_ascii=False)
        
        # エスケープ処理を適切に行う
        escaped_json = json_str.replace('\\', '\\\\').replace("'", "\\'")
        
        # JavaScriptコードを生成（修正箇所）
        js_code = f"""
        try {{
            localStorage.setItem('cosmic_guidance_sessions', '{escaped_json}');
            return 'success';
        }} catch(e) {{
            return 'error: ' + e.toString();
        }}
        """
        
        # 動的なkeyで実行
        result = streamlit_js_eval(
            js_eval=js_code, 
            key=f'save_sessions_{time.time()}'
        )
        
        # 保存結果を確認
        if result == 'success':
            st.session_state.save_status = "✅ 自動保存完了"
        elif result and 'error' in str(result):
            st.session_state.save_status = f"⚠️ 保存エラー: {result}"
        
        return result == 'success'
        
    except Exception as e:
        st.session_state.save_status = f"⚠️ 保存エラー: {str(e)}"
        st.error(f"データ保存エラー: {str(e)}")
        return False

# Gemini API設定
def configure_gemini():
    """Gemini APIを設定"""
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    
    if not api_key:
        st.error("⚠️ APIキーが設定されていません。")
        st.info("""
        **設定方法:**
        1. `.streamlit/secrets.toml` ファイルを作成
        2. `GEMINI_API_KEY = "your-api-key"` を追加
        3. [Google AI Studio](https://aistudio.google.com/app/apikey) でAPIキーを取得
        """)
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

# プロフィール計算
def calculate_profile(birthdate_str):
    """生年月日から年齢と星座を計算"""
    birth = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.now()
    
    # 年齢計算
    age = today.year - birth.year
    if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
        age -= 1
    
    # 星座計算
    zodiac_dates = [
        (1, 20, "山羊座"), (2, 19, "水瓶座"), (3, 21, "魚座"),
        (4, 20, "牡羊座"), (5, 21, "牡牛座"), (6, 21, "双子座"),
        (7, 23, "蟹座"), (8, 23, "獅子座"), (9, 23, "乙女座"),
        (10, 23, "天秤座"), (11, 22, "蠍座"), (12, 22, "射手座")
    ]
    
    month, day = birth.month, birth.day
    for i, (end_month, end_day, sign) in enumerate(zodiac_dates):
        if month == end_month and day < end_day:
            if i == 0:
                zodiac = "山羊座"
            else:
                zodiac = zodiac_dates[i-1][2]
            break
        elif month == end_month and day >= end_day:
            zodiac = sign
            break
    
    return age, zodiac

# システムプロンプトを取得
def get_system_prompt():
    """AIの性格と振る舞いを定義するシステムプロンプト"""
    return f"""あなたは深い洞察力を持つ運命の導き手です。
相談者は{st.session_state.age}歳の{st.session_state.zodiac}の方です。

以下のガイドラインに従って応答してください：

1. **話し方**: 優しく神秘的でありながら、親しみやすい
2. **構成**: 
   - まず共感と理解を示す
   - 星座や宇宙のエネルギーの観点から洞察を提供
   - 具体的で実践的なアドバイスを含める
3. **避けること**: 
   - 否定的すぎる予言
   - 曖昧すぎる表現
   - 医療や法律の専門的助言
4. **強調すること**:
   - 希望と可能性
   - 自己成長の機会
   - 内なる力の存在"""

# メインアプリ
def main():
    model = configure_gemini()
    
    # 初回のみローカルストレージから読み込み（修正版）
    if not st.session_state.loaded_from_storage:
        # 少し待機してJavaScriptが利用可能になるのを待つ
        time.sleep(0.1)
        load_from_local_storage()
        st.session_state.loaded_from_storage = True
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <div class="logo">✨</div>
        <h1 class="main-title">運命の導き</h1>
        <p class="subtitle">COSMIC GUIDANCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 保存状態の表示（デバッグ用）
    if st.session_state.save_status:
        st.sidebar.caption(st.session_state.save_status)
    
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

宇宙があなたに送るメッセージをお伝えします。"""
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": welcome_message
            })
            
            # ローカルストレージに保存
            save_to_local_storage()
            
            st.rerun()
    
    else:
        # サイドバーにプロフィール表示
        with st.sidebar:
            st.markdown("### ✨ あなたのプロフィール")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="profile-info">
                    <div class="profile-label">生年月日</div>
                    <div class="profile-value">{st.session_state.birthdate}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="profile-info">
                    <div class="profile-label">年齢</div>
                    <div class="profile-value">{st.session_state.age}歳</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">星座</div>
                <div class="profile-value">{st.session_state.zodiac}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # セッション管理
            st.markdown("### 📚 過去のセッション")
            
            if st.session_state.sessions:
                # セッションリスト
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
                st.session_state.messages = []
                st.session_state.birthdate = None
                st.session_state.age = None
                st.session_state.zodiac = None
                st.session_state.current_session_id = None
                st.rerun()
            
            st.markdown("---")
            
            # データクリア（危険な操作なので最下部に）
            with st.expander("🗑️ すべてのデータを削除（危険）"):
                st.warning("この操作は取り消せません。すべてのセッションが削除されます。")
                if st.button("⚠️ 本当に削除する", use_container_width=True, type="secondary"):
                    # JavaScriptでローカルストレージをクリア
                    js_code = """
                    localStorage.removeItem('cosmic_guidance_sessions');
                    return 'cleared';
                    """
                    result = streamlit_js_eval(
                        js_eval=js_code, 
                        key=f'clear_all_{time.time()}'
                    )
                    
                    # セッション状態をクリア
                    st.session_state.messages = []
                    st.session_state.birthdate = None
                    st.session_state.age = None
                    st.session_state.zodiac = None
                    st.session_state.current_session_id = None
                    st.session_state.sessions = {}
                    st.session_state.loaded_from_storage = False
                    
                    st.success("✅ すべてのデータを削除しました")
                    time.sleep(1)
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
                        
                        # ローカルストレージに自動保存（修正版）
                        if save_to_local_storage():
                            st.toast("✅ 会話を自動保存しました", icon="✅")
                        else:
                            st.toast("⚠️ 自動保存に失敗しました", icon="⚠️")
                        
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
