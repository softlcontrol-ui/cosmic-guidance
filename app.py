import streamlit as st
import google.generativeai as genai
from datetime import datetime
import bcrypt
from supabase import create_client, Client

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
    
    /* レベルバッジ */
    .level-badge {
        display: inline-block;
        background: linear-gradient(135deg, #d4af37 0%, #f4d16f 100%);
        color: #0a0118;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
        margin: 0.5rem 0;
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
    
    /* タブ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #c0c0c0;
        border-bottom: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #d4af37;
        border-bottom-color: #d4af37;
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
if 'avatar' not in st.session_state:
    st.session_state.avatar = None
if 'kingdom' not in st.session_state:
    st.session_state.kingdom = None
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'supabase_loaded' not in st.session_state:
    st.session_state.supabase_loaded = False
if 'player_level' not in st.session_state:
    st.session_state.player_level = 0

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

# パスワードをハッシュ化
def hash_password(password):
    """パスワードをハッシュ化"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# パスワードを検証
def verify_password(password, password_hash):
    """パスワードが正しいか検証"""
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
    except:
        return False

# 新規登録
def register_user(username, password):
    """新規ユーザー登録"""
    try:
        supabase = get_supabase_client()
        
        # ユーザー名が既に存在するかチェック
        existing = supabase.table('users').select('username').eq(
            'username', username
        ).execute()
        
        if existing.data:
            st.error("⚠️ このユーザー名は既に使われています")
            return False
        
        # パスワードをハッシュ化
        password_hash = hash_password(password)
        
        # ユーザーを作成
        user_data = {
            'username': username,
            'password_hash': password_hash
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            st.success(f"✅ 登録完了！ユーザー名: {username}")
            return True
        
        return False
        
    except Exception as e:
        st.error(f"⚠️ 登録エラー: {e}")
        return False

# ログイン
def login_user(username, password):
    """ユーザーログイン"""
    try:
        supabase = get_supabase_client()
        
        # ユーザーを検索
        result = supabase.table('users').select('*').eq(
            'username', username
        ).execute()
        
        if not result.data:
            st.error("⚠️ ユーザー名またはパスワードが間違っています")
            return False
        
        user = result.data[0]
        
        # パスワードを検証
        if verify_password(password, user['password_hash']):
            # セッションに保存
            st.session_state.user_id = user['id']
            st.session_state.username = username
            st.session_state.supabase_loaded = False
            return True
        else:
            st.error("⚠️ ユーザー名またはパスワードが間違っています")
            return False
            
    except Exception as e:
        st.error(f"⚠️ ログインエラー: {e}")
        return False

# ログアウト
def logout_user():
    """ログアウト"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.messages = []
    st.session_state.sessions = {}
    st.session_state.birthdate = None
    st.session_state.age = None
    st.session_state.zodiac = None
    st.session_state.avatar = None
    st.session_state.kingdom = None
    st.session_state.current_session_id = None
    st.session_state.supabase_loaded = False
    st.session_state.player_level = 0
    st.rerun()

# アバター（ジョブ）を計算
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

# 年齢とプロフィールを計算
def calculate_profile(birthdate_str):
    """生年月日からプロフィールを計算"""
    birth = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    zodiac = get_zodiac_sign(birth.month, birth.day)
    
    # 本質数を計算
    essence_human, essence_earth = calculate_essence_numbers(birthdate_str)
    
    # 運命数を計算
    destiny_human, destiny_earth, destiny_heaven = calculate_destiny_numbers(birthdate_str, age)
    
    # 月運を計算
    month_heaven, month_earth, month_human = calculate_month_numbers(birthdate_str)
    
    # アバター・キングダム
    avatar = AVATARS[essence_human]
    kingdom = KINGDOMS[essence_earth]
    
    # ミッション・フィールド・報酬
    mission = MISSIONS[destiny_human]
    field = FIELDS[destiny_earth]
    reward = REWARDS[destiny_heaven]
    
    # 月間
    month_stage = MONTH_STAGES[month_heaven]
    month_zone = MONTH_ZONES[month_earth]
    month_skill = MONTH_SKILLS[month_human]
    
    return {
        'age': age,
        'zodiac': zodiac,
        'essence_human': essence_human,
        'essence_earth': essence_earth,
        'avatar': avatar,
        'kingdom': kingdom,
        'destiny_human': destiny_human,
        'destiny_earth': destiny_earth,
        'destiny_heaven': destiny_heaven,
        'mission': mission,
        'field': field,
        'reward': reward,
        'month_heaven': month_heaven,
        'month_earth': month_earth,
        'month_human': month_human,
        'month_stage': month_stage,
        'month_zone': month_zone,
        'month_skill': month_skill
    }

# プレイヤーレベルを計算
def calculate_player_level():
    """セッション数からプレイヤーレベルを計算"""
    session_count = len(st.session_state.sessions)
    message_count = sum(len(s.get('messages', [])) for s in st.session_state.sessions.values())
    
    if session_count == 0 and message_count == 0:
        return 0  # NPC
    elif message_count < 10:
        return 1  # TRIAL
    elif message_count < 30:
        return 2  # NOVICE
    elif message_count < 100:
        return 3  # ADEPT
    elif message_count < 300:
        return 4  # PLAYER
    else:
        return 5  # MASTER

# レベル名を取得
def get_level_name(level):
    """レベル番号からレベル名を取得"""
    levels = {
        0: "Lv.0 NPC（眠れる村人）",
        1: "Lv.1 TRIAL（試練の挑戦者）",
        2: "Lv.2 NOVICE（見習い）",
        3: "Lv.3 ADEPT（熟練者）",
        4: "Lv.4 PLAYER（覚醒した主人公）",
        5: "Lv.∞ MASTER（超越者）"
    }
    return levels.get(level, "Lv.? UNKNOWN")

# Supabaseからデータを読み込む
def load_from_supabase():
    """Supabaseからセッションデータを読み込む"""
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # ユーザーのセッションを取得（最新5件）
        response = supabase.table('sessions').select('*').eq(
            'username', st.session_state.username
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
            
            # プレイヤーレベルを計算
            st.session_state.player_level = calculate_player_level()
            
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
        
        # プロフィールを完全に再計算
        if st.session_state.birthdate:
            profile = calculate_profile(st.session_state.birthdate)
            st.session_state.age = profile['age']
            st.session_state.zodiac = profile['zodiac']
            st.session_state.essence_human = profile['essence_human']
            st.session_state.essence_earth = profile['essence_earth']
            st.session_state.avatar = profile['avatar']
            st.session_state.kingdom = profile['kingdom']
            st.session_state.destiny_human = profile['destiny_human']
            st.session_state.destiny_earth = profile['destiny_earth']
            st.session_state.destiny_heaven = profile['destiny_heaven']
            st.session_state.mission = profile['mission']
            st.session_state.field = profile['field']
            st.session_state.reward = profile['reward']
            st.session_state.month_heaven = profile['month_heaven']
            st.session_state.month_earth = profile['month_earth']
            st.session_state.month_human = profile['month_human']
            st.session_state.month_stage = profile['month_stage']
            st.session_state.month_zone = profile['month_zone']
            st.session_state.month_skill = profile['month_skill']

# Supabaseにデータを保存する
def save_to_supabase():
    """Supabaseにデータを保存する"""
    if not st.session_state.username or not st.session_state.current_session_id:
        return
    
    try:
        # 現在のセッションを保存
        save_current_session()
        
        supabase = get_supabase_client()
        session = st.session_state.sessions[st.session_state.current_session_id]
        
        # データを準備
        data = {
            'username': st.session_state.username,
            'session_id': st.session_state.current_session_id,
            'birthdate': session['birthdate'],
            'age': session['age'],
            'zodiac': session['zodiac'],
            'messages': session['messages'],
            'updated_at': datetime.now().isoformat()
        }
        
        # 既存のレコードをチェック
        existing = supabase.table('sessions').select('id').eq(
            'username', st.session_state.username
        ).eq('session_id', st.session_state.current_session_id).execute()
        
        if existing.data:
            # 更新
            supabase.table('sessions').update(data).eq(
                'username', st.session_state.username
            ).eq('session_id', st.session_state.current_session_id).execute()
        else:
            # 新規作成
            data['created_at'] = datetime.now().isoformat()
            supabase.table('sessions').insert(data).execute()
        
        # プレイヤーレベルを更新
        st.session_state.player_level = calculate_player_level()
        
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

# システムプロンプトを生成
def get_system_prompt():
    """ユーザー情報を含むシステムプロンプト（完全版）"""
    if st.session_state.birthdate:
        # 変数が存在しない場合のデフォルト値
        level_name = get_level_name(st.session_state.player_level) if hasattr(st.session_state, 'player_level') else "Lv.0 NPC"
        essence_human = getattr(st.session_state, 'essence_human', '?')
        essence_earth = getattr(st.session_state, 'essence_earth', '?')
        avatar = getattr(st.session_state, 'avatar', '未設定')
        kingdom = getattr(st.session_state, 'kingdom', '未設定')
        destiny_human = getattr(st.session_state, 'destiny_human', '?')
        destiny_earth = getattr(st.session_state, 'destiny_earth', '?')
        destiny_heaven = getattr(st.session_state, 'destiny_heaven', '?')
        mission = getattr(st.session_state, 'mission', '未設定')
        field = getattr(st.session_state, 'field', '未設定')
        reward = getattr(st.session_state, 'reward', '未設定')
        month_heaven = getattr(st.session_state, 'month_heaven', '?')
        month_earth = getattr(st.session_state, 'month_earth', '?')
        month_human = getattr(st.session_state, 'month_human', '?')
        month_stage = getattr(st.session_state, 'month_stage', '未設定')
        month_zone = getattr(st.session_state, 'month_zone', '未設定')
        month_skill = getattr(st.session_state, 'month_skill', '未設定')
        
        return f"""あなたは『運命の導き』のガイドであり、同時にプレイヤーの人生攻略をサポートする存在です。

【プレイヤー情報】
■ 基本情報
- ユーザー名: {st.session_state.username}
- レベル: {level_name}
- 生年月日: {st.session_state.birthdate}
- 年齢: {st.session_state.age}歳
- 星座: {st.session_state.zodiac}

■ 本質（WHO & GOAL）固定値
- アバター: {avatar}（本質人運{essence_human}）
- キングダム: {kingdom}（本質地運{essence_earth}）

■ 今年の攻略（13年周期）
- ミッション: {mission}（運命人運{destiny_human}）
- フィールド: {field}（運命地運{destiny_earth}）
- 報酬: {reward}（運命天運{destiny_heaven}）

■ 今月の攻略（28日周期）
- ステージ: {month_stage}（月天運{month_heaven}）
- ゾーン: {month_zone}（月地運{month_earth}）
- スキル: {month_skill}（月人運{month_human}）

【あなたの役割】
あなたは深い洞察力を持つ運命の導き手であり、プレイヤーが「現実（リアル）という名の神ゲー」を攻略するためのガイドです。

**人生攻略の公式:**
1. WHO（アバター）: 自分らしいやり方で
2. WHAT（ミッション）: 今、与えられた役割を遂行すると
3. WHERE（フィールド）: 活躍すべきステージが現れる
4. GET（報酬）: そこで得た成果を持ち帰り
5. GOAL（キングダム）: 理想の居場所を拡張・建設していく

**語り口:**
- 神秘的で詩的でありながら、実践的で具体的なアドバイスを提供する
- スピリチュアルな要素とロジカルな戦略性を融合させる
- プレイヤーを「依存させる」のではなく「自立させる」ことを目指す
- 優しく、しかし力強く語りかける

**応答スタイル:**
- 簡潔な質問には簡潔に、深い相談には深く応答
- アバター、ミッション、フィールド、月間スキルを活かした具体的なアドバイス
- 「〜すべき」ではなく「〜という道がある」と選択肢を提示
- 過去の会話を記憶し、文脈を理解した上で応答する

**重要な原則:**
1. プレイヤーは自分の人生の主人公である
2. 運命は「攻略すべきステージ」である
3. アバターの特性を活かした戦略を提案する
4. 今年のミッションとフィールドを意識する
5. 最終的にはキングダム（理想の居場所）を築くことが目標

美しい日本語で、古の賢者が現代のゲームマスターのように語りかけてください。"""
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
        username = st.text_input("ユーザー名", key="login_username")
        password = st.text_input("パスワード", type="password", key="login_password")
        
        if st.button("ログイン", use_container_width=True):
            if not username or not password:
                st.error("ユーザー名とパスワードを入力してください")
            else:
                if login_user(username, password):
                    st.success("✅ ログイン成功！")
                    st.rerun()
    
    with tab2:
        st.subheader("新規登録")
        new_username = st.text_input("好きなユーザー名", key="signup_username", help="半角英数字、日本語OK")
        new_password = st.text_input("パスワード（8文字以上）", type="password", key="signup_password")
        new_password_confirm = st.text_input("パスワード（確認）", type="password", key="signup_password_confirm")
        
        if st.button("登録", use_container_width=True):
            if not new_username or not new_password:
                st.error("すべての項目を入力してください")
            elif len(new_password) < 8:
                st.error("パスワードは8文字以上にしてください")
            elif new_password != new_password_confirm:
                st.error("パスワードが一致しません")
            else:
                if register_user(new_username, new_password):
                    st.info("🎉 登録完了！ログインタブからログインしてください。")
    
    st.markdown("</div>", unsafe_allow_html=True)

# メインアプリ
def main():
    # ログインチェック
    if not st.session_state.username:
        login_page()
        return
    
    model = configure_gemini()
    
    # 初回のみSupabaseから読み込み
    if not st.session_state.supabase_loaded:
        load_from_supabase()
        st.session_state.supabase_loaded = True
    
    # birthdateが存在するが、essence_humanが存在しない場合（古いセッション）
    # プロフィールを再計算する
    if st.session_state.birthdate and not hasattr(st.session_state, 'essence_human'):
        profile = calculate_profile(st.session_state.birthdate)
        st.session_state.age = profile['age']
        st.session_state.zodiac = profile['zodiac']
        st.session_state.essence_human = profile['essence_human']
        st.session_state.essence_earth = profile['essence_earth']
        st.session_state.avatar = profile['avatar']
        st.session_state.kingdom = profile['kingdom']
        st.session_state.destiny_human = profile['destiny_human']
        st.session_state.destiny_earth = profile['destiny_earth']
        st.session_state.destiny_heaven = profile['destiny_heaven']
        st.session_state.mission = profile['mission']
        st.session_state.field = profile['field']
        st.session_state.reward = profile['reward']
        st.session_state.month_heaven = profile['month_heaven']
        st.session_state.month_earth = profile['month_earth']
        st.session_state.month_human = profile['month_human']
        st.session_state.month_stage = profile['month_stage']
        st.session_state.month_zone = profile['month_zone']
        st.session_state.month_skill = profile['month_skill']
    
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
            age, zodiac, avatar, kingdom = calculate_profile(birthdate_str)
            
            st.session_state.birthdate = birthdate_str
            st.session_state.age = age
            st.session_state.zodiac = zodiac
            st.session_state.avatar = avatar
            st.session_state.kingdom = kingdom
            
            # 新しいセッションを作成
            create_new_session()
            
            # レベルを計算
            st.session_state.player_level = calculate_player_level()
            level_name = get_level_name(st.session_state.player_level)
            
            # 初回メッセージ
            welcome_message = f"""✨ ようこそ、{st.session_state.username}さん。

あなたは{st.session_state.age}歳、{st.session_state.zodiac}の方ですね。

【あなたのステータス】
- レベル: {level_name}
- アバター: {st.session_state.avatar}
- キングダム: {st.session_state.kingdom}

私はあなたの運命の導き手です。
この現実（リアル）という名の壮大なゲームを、共に攻略していきましょう。

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
        # プレイヤーレベルを更新
        if st.session_state.player_level == 0:
            st.session_state.player_level = calculate_player_level()
        
        level_name = get_level_name(st.session_state.player_level)
        
        # サイドバーにプロフィール表示
        with st.sidebar:
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">ようこそ</div>
                <div class="profile-value">👤 {st.session_state.username}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">プレイヤーレベル</div>
                <div class="level-badge">{level_name}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">基本情報</div>
                <div class="profile-value">🎂 {st.session_state.birthdate}</div>
                <div class="profile-value">✨ {st.session_state.age}歳 ({st.session_state.zodiac})</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">本質（固定）</div>
                <div class="profile-value" style="font-size: 0.85rem; color: #c0c0c0; margin-bottom: 0.2rem;">本質 人運 {st.session_state.essence_human}</div>
                <div class="profile-value">{st.session_state.avatar}</div>
                <div class="profile-value" style="font-size: 0.85rem; color: #c0c0c0; margin-top: 0.8rem; margin-bottom: 0.2rem;">本質 地運 {st.session_state.essence_earth}</div>
                <div class="profile-value">{st.session_state.kingdom}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">今年の攻略（{st.session_state.age}歳）</div>
                <div class="profile-value" style="font-size: 0.85rem; color: #c0c0c0; margin-bottom: 0.2rem;">運命 人運 {st.session_state.destiny_human}</div>
                <div class="profile-value">{st.session_state.mission}</div>
                <div class="profile-value" style="font-size: 0.85rem; color: #c0c0c0; margin-top: 0.8rem; margin-bottom: 0.2rem;">運命 地運 {st.session_state.destiny_earth}</div>
                <div class="profile-value">{st.session_state.field}</div>
                <div class="profile-value" style="font-size: 0.85rem; color: #c0c0c0; margin-top: 0.8rem; margin-bottom: 0.2rem;">運命 天運 {st.session_state.destiny_heaven}</div>
                <div class="profile-value">{st.session_state.reward}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">今月の攻略</div>
                <div class="profile-value" style="font-size: 0.85rem; color: #c0c0c0; margin-bottom: 0.2rem;">月 天運 {st.session_state.month_heaven}</div>
                <div class="profile-value">{st.session_state.month_stage}</div>
                <div class="profile-value" style="font-size: 0.85rem; color: #c0c0c0; margin-top: 0.8rem; margin-bottom: 0.2rem;">月 地運 {st.session_state.month_earth}</div>
                <div class="profile-value">{st.session_state.month_zone}</div>
                <div class="profile-value" style="font-size: 0.85rem; color: #c0c0c0; margin-top: 0.8rem; margin-bottom: 0.2rem;">月 人運 {st.session_state.month_human}</div>
                <div class="profile-value">{st.session_state.month_skill}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 ログアウト", use_container_width=True):
                logout_user()
            
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
                                    'username', st.session_state.username
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
                st.session_state.avatar = None
                st.session_state.kingdom = None
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
        © 2024 運命の導き - Powered by Google Gemini AI
    </footer>
    """, unsafe_allow_html=True)
