import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import bcrypt
from supabase import create_client, Client

# ページ設定
st.set_page_config(
    page_title="THE PLAYER - 運命の攻略",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# カスタムCSS - ゲーミフィケーションデザイン
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
    
    /* リソースボックス */
    .resource-box {
        background: rgba(29, 15, 51, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .resource-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
    }
    
    .resource-item:last-child {
        border-bottom: none;
    }
    
    .resource-label {
        font-size: 0.95rem;
        color: #f4d16f;
    }
    
    .resource-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    /* クエストカード */
    .quest-card {
        background: rgba(29, 15, 51, 0.8);
        border: 2px solid rgba(212, 175, 55, 0.4);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .quest-card:hover {
        border-color: rgba(212, 175, 55, 0.8);
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
    }
    
    .quest-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #f4d16f;
        margin-bottom: 0.5rem;
    }
    
    .quest-cost {
        display: inline-block;
        background: linear-gradient(135deg, #d4af37 0%, #f4d16f 100%);
        color: #0a0118;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
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
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(10, 1, 24, 0.8) !important;
        border: 1px solid rgba(192, 192, 192, 0.2) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stDateInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
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
    
    /* プライマリボタン */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
    }
    
    /* ラベル */
    .stTextInput > label,
    .stDateInput > label,
    .stTextArea > label,
    .stSelectbox > label {
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
    
    /* Success box */
    .stSuccess {
        background-color: rgba(31, 92, 61, 0.4) !important;
        border: 1px solid rgba(55, 212, 118, 0.4) !important;
        border-radius: 15px !important;
    }
    
    /* Warning box */
    .stWarning {
        background-color: rgba(92, 61, 31, 0.4) !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 15px !important;
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
    
    /* プログレスバー */
    .stProgress > div > div {
        background: linear-gradient(135deg, #d4af37 0%, #f4d16f 100%);
    }
</style>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ==================== 運命の羅針盤 計算ロジック ====================

# 13の数字の意味定義
AVATARS = {
    1: "⚔️ パイオニア（開拓者）",
    2: "🤝 メディエーター（調停者）",
    3: "🎭 クリエイター（創造者）",
    4: "🏰 ビルダー（建設者）",
    5: "🌊 エクスプローラー（探検者）",
    6: "💚 サポーター（支援者）",
    7: "💡 ビジョナリー（先見者）",
    8: "👑 リーダー（統率者）",
    9: "🔥 トランスフォーマー（変革者）",
    10: "⚙️ アナリスト（分析者）",
    11: "📡 コミュニケーター（伝達者）",
    12: "🛡️ ストラテジスト（戦略家）",
    13: "🌟 ユニバーサリスト（普遍者）"
}

KINGDOMS = {
    1: "🗡️ 冒険の拠点",
    2: "🤲 調和の庭園",
    3: "🎨 クリエイティブスタジオ",
    4: "🏗️ 堅固な要塞",
    5: "🌍 グローバルベース",
    6: "💝 安らぎの聖域",
    7: "🌌 ドリームタワー",
    8: "👑 威厳の宮殿",
    9: "🔥 変革の炉",
    10: "📊 分析ラボ",
    11: "📢 コミュニケーションハブ",
    12: "🎯 戦略司令部",
    13: "✨ 統合の神殿"
}

MISSIONS = {
    1: "⚡ イニシアチブ：即座に動き出せ",
    2: "🤝 ハーモニー：調和を生み出せ",
    3: "🎪 クリエイティビティ：遊び心で創造せよ",
    4: "🔨 コンストラクション：基盤を固めよ",
    5: "🧭 エクスプロージョン：未知へ飛び込め",
    6: "💞 ケア：人を支えよ",
    7: "🔮 ビジョン：未来を描け",
    8: "⚡ パワー：強く押し進めよ",
    9: "🌀 トランスフォーム：変容を起こせ",
    10: "📐 アナリゼーション：分析し整理せよ",
    11: "📣 コミュニケーション：伝え繋げ",
    12: "🎯 ストラテジー：戦略を立てよ",
    13: "🌈 インテグレーション：統合せよ"
}

FIELDS = {
    1: "🚀 スタートライン（始まりの地）",
    2: "⚖️ バランスポイント（均衡の場）",
    3: "🎪 プレイグラウンド（遊びの庭）",
    4: "🏰 ファウンデーション（基礎の地）",
    5: "🌊 アドベンチャーゾーン（冒険領域）",
    6: "🏡 コンフォートゾーン（安心領域）",
    7: "🌌 ドリームフィールド（夢の原野）",
    8: "⚡ パワースポット（力の源泉）",
    9: "🔥 トランジションゾーン（変容の地）",
    10: "📊 アナリシスエリア（分析領域）",
    11: "🌐 ネットワークフィールド（繋がりの場）",
    12: "🎯 ストラテジーベース（戦略基地）",
    13: "✨ ユニバーサルフィールド（普遍の場）"
}

REWARDS = {
    1: "🎁 イニシアチブ（主導権）",
    2: "🤝 パートナーシップ（協力者）",
    3: "🎨 インスピレーション（霊感）",
    4: "🏆 スタビリティ（安定）",
    5: "🌟 チャンス（機会）",
    6: "💝 トラスト（信頼）",
    7: "🔮 ビジョン（洞察）",
    8: "👑 オーソリティ（権威）",
    9: "🔥 トランスフォーメーション（変革）",
    10: "📈 クラリティ（明晰さ）",
    11: "📢 オファー（抜擢）",
    12: "🎯 ストラテジー（戦略）",
    13: "✨ フルフィルメント（充足）"
}

MONTH_STAGES = {
    1: "🌅 ドーン（夜明け）",
    2: "🌱 スプラウト（芽吹き）",
    3: "🌸 ブロッサム（開花）",
    4: "☀️ ピーク（頂点）",
    5: "🌾 ハーベスト（収穫）",
    6: "🌙 トワイライト（黄昏）",
    7: "🌑 ダークネス（闇）",
    8: "🌠 リニューアル（再生）",
    9: "🔄 サイクル（循環）",
    10: "⚡ アクション（行動）",
    11: "🎭 エクスプレッション（表現）",
    12: "🧘 メディテーション（瞑想）",
    13: "🌈 インテグレーション（統合）",
    14: "✨ トランセンデンス（超越）"
}

MONTH_ZONES = {
    1: "🎯 フォーカスゾーン（集中）",
    2: "🤝 コネクションゾーン（繋がり）",
    3: "🎨 クリエイティブゾーン（創造）",
    4: "🏗️ ビルディングゾーン（構築）",
    5: "🌊 フローゾーン（流れ）",
    6: "💚 ヒーリングゾーン（癒やし）",
    7: "🔮 ビジョンゾーン（洞察）",
    8: "⚡ パワーゾーン（力）",
    9: "🔥 トランジションゾーン（移行）",
    10: "📊 アナリシスゾーン（分析）",
    11: "📣 コミュニケーションゾーン（伝達）",
    12: "🎯 ストラテジーゾーン（戦略）",
    13: "✨ ハーモニーゾーン（調和）",
    14: "🌈 トランセンデンスゾーン（超越）"
}

MONTH_SKILLS = {
    1: "⚔️ アタック（攻撃）",
    2: "🛡️ ディフェンス（防御）",
    3: "🎪 プレイ（遊び）",
    4: "🔨 ビルド（構築）",
    5: "🧭 エクスプロア（探索）",
    6: "💞 ケア（世話）",
    7: "🔮 ビジョン（洞察）",
    8: "⚡ プッシュ（推進）",
    9: "🌀 トランスフォーム（変容）",
    10: "📐 アナライズ（分析）",
    11: "📣 コミュニケート（伝達）",
    12: "🎯 ストラテジャイズ（戦略化）",
    13: "🌈 インテグレート（統合）",
    14: "✨ トランセンド（超越）"
}

# アバターレベル定義
AVATAR_LEVELS = {
    0: {"name": "Lv.0 NPC（眠れる村人）", "max_ap": 10, "exp_required": 0},
    1: {"name": "Lv.1 TRIAL（試練の挑戦者）", "max_ap": 15, "exp_required": 100},
    2: {"name": "Lv.2 NOVICE（見習い）", "max_ap": 20, "exp_required": 300},
    3: {"name": "Lv.3 ADEPT（熟練者）", "max_ap": 30, "exp_required": 600},
    4: {"name": "Lv.4 PLAYER（覚醒した主人公）", "max_ap": 50, "exp_required": 1000}
}

# キングダムランク定義
KINGDOM_RANKS = {
    0: {"name": "Rank 0: 荒地", "kp_required": 0, "gifts_required": 0},
    1: {"name": "Rank 1: 集落", "kp_required": 100, "gifts_required": 1},
    2: {"name": "Rank 2: 街", "kp_required": 500, "gifts_required": 2},
    3: {"name": "Rank 3: 都市", "kp_required": 1500, "gifts_required": 3},
    4: {"name": "Rank 4: 王国", "kp_required": 5000, "gifts_required": 5}
}

def calculate_essence_numbers(birthdate_str):
    """本質数を計算（固定値）"""
    birth = datetime.strptime(birthdate_str, "%Y-%m-%d")
    
    # 本質 人運：生年月日の全桁を足して13で割る
    year_sum = sum(int(d) for d in str(birth.year))
    month_sum = birth.month
    day_sum = birth.day
    
    essence_human = ((year_sum + month_sum + day_sum - 1) % 13) + 1
    
    # 本質 地運：月日のみで計算
    essence_earth = ((month_sum + day_sum - 1) % 13) + 1
    
    return essence_human, essence_earth

def calculate_destiny_numbers(birthdate_str, age):
    """運命数を計算（13年周期）"""
    essence_human, essence_earth = calculate_essence_numbers(birthdate_str)
    
    # 運命 人運：年齢 + 本質人運
    destiny_human = ((age + essence_human - 1) % 13) + 1
    
    # 運命 地運：年齢 + 本質地運
    destiny_earth = ((age + essence_earth - 1) % 13) + 1
    
    # 運命 天運：年齢 + 本質人運 + 本質地運
    destiny_heaven = ((age + essence_human + essence_earth - 1) % 13) + 1
    
    return destiny_human, destiny_earth, destiny_heaven

def calculate_month_numbers(birthdate_str):
    """月運を計算（28日周期）"""
    birth = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.now()
    
    # 誕生日からの経過日数
    days_since_birth = (today - birth).days
    
    # 28日周期での位置（1-28）
    cycle_position = (days_since_birth % 28) + 1
    
    # 14段階に変換（28日を14段階で分ける）
    month_heaven = ((cycle_position - 1) // 2) + 1  # 1-14
    month_earth = (((cycle_position + 9) - 1) // 2) % 14 + 1  # 1-14
    month_human = (((cycle_position + 18) - 1) // 2) % 14 + 1  # 1-14
    
    return month_heaven, month_earth, month_human

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

# ==================== THE PLAYER システム ====================

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

# THE PLAYER用の状態
if 'ap' not in st.session_state:
    st.session_state.ap = 10
if 'kp' not in st.session_state:
    st.session_state.kp = 0
if 'exp' not in st.session_state:
    st.session_state.exp = 0
if 'coin' not in st.session_state:
    st.session_state.coin = 0
if 'avatar_level' not in st.session_state:
    st.session_state.avatar_level = 0
if 'kingdom_rank' not in st.session_state:
    st.session_state.kingdom_rank = 0
if 'max_ap' not in st.session_state:
    st.session_state.max_ap = 10
if 'active_quest' not in st.session_state:
    st.session_state.active_quest = None
if 'show_report_form' not in st.session_state:
    st.session_state.show_report_form = False

# Phase 2用の状態
if 'gift_fragments' not in st.session_state:
    st.session_state.gift_fragments = 0
if 'completed_gifts' not in st.session_state:
    st.session_state.completed_gifts = 0
if 'last_login_date' not in st.session_state:
    st.session_state.last_login_date = None
if 'last_quest_date' not in st.session_state:
    st.session_state.last_quest_date = None
if 'entropy_warning_shown' not in st.session_state:
    st.session_state.entropy_warning_shown = False

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

# プレイヤーステータスを読み込む
def load_player_status():
    """Supabaseからプレイヤーステータスを読み込む"""
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # player_statusを取得
        response = supabase.table('player_status').select('*').eq(
            'username', st.session_state.username
        ).execute()
        
        if response.data:
            data = response.data[0]
            st.session_state.ap = data['ap']
            st.session_state.kp = data['kp']
            st.session_state.exp = data['exp']
            st.session_state.coin = data['coin']
            st.session_state.avatar_level = data['avatar_level']
            st.session_state.kingdom_rank = data['kingdom_rank']
            st.session_state.max_ap = data['max_ap']
            
            # Phase 2: 日付フィールド
            st.session_state.last_login_date = data.get('last_login_date')
            st.session_state.last_quest_date = data.get('last_quest_date')
            
            return True
        
        return False
    except Exception as e:
        st.warning(f"⚠️ ステータス読み込みエラー: {e}")
        return False

# プレイヤーステータスを保存する
def save_player_status():
    """Supabaseにプレイヤーステータスを保存する"""
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        data = {
            'username': st.session_state.username,
            'ap': st.session_state.ap,
            'kp': st.session_state.kp,
            'exp': st.session_state.exp,
            'coin': st.session_state.coin,
            'avatar_level': st.session_state.avatar_level,
            'kingdom_rank': st.session_state.kingdom_rank,
            'max_ap': st.session_state.max_ap,
            'last_login_date': datetime.now().date().isoformat() if st.session_state.last_login_date else datetime.now().date().isoformat(),
            'last_quest_date': st.session_state.last_quest_date,
            'updated_at': datetime.now().isoformat()
        }
        
        # 既存レコードをチェック
        existing = supabase.table('player_status').select('username').eq(
            'username', st.session_state.username
        ).execute()
        
        if existing.data:
            # 既存レコードがある場合は更新
            supabase.table('player_status').update(data).eq(
                'username', st.session_state.username
            ).execute()
        else:
            # 既存レコードがない場合は挿入
            supabase.table('player_status').insert(data).execute()
        
        return True
    except Exception as e:
        st.warning(f"⚠️ ステータス保存エラー: {e}")
        return False

# アクティブなクエストを読み込む
def load_active_quest():
    """アクティブなクエストを読み込む"""
    if not st.session_state.username:
        return None
    
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('quests').select('*').eq(
            'username', st.session_state.username
        ).eq('status', 'active').order('created_at', desc=True).limit(1).execute()
        
        if response.data:
            st.session_state.active_quest = response.data[0]
            return response.data[0]
        
        st.session_state.active_quest = None
        return None
    except Exception as e:
        st.warning(f"⚠️ クエスト読み込みエラー: {e}")
        return None

# クエストを作成する
def create_quest(quest_type, title, description, advice):
    """新しいクエストを作成する"""
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # AP消費量を決定
        ap_cost = 1 if quest_type == 'consultation' else 2
        
        # APが足りるかチェック
        if st.session_state.ap < ap_cost:
            st.error(f"⚠️ APが不足しています（必要: {ap_cost} AP、所持: {st.session_state.ap} AP）")
            return False
        
        # APを消費
        st.session_state.ap -= ap_cost
        
        # 月運情報を取得
        if st.session_state.birthdate:
            month_heaven, month_earth, month_human = calculate_month_numbers(st.session_state.birthdate)
            destiny_stage = MONTH_STAGES[month_heaven]
            destiny_zone = MONTH_ZONES[month_earth]
            destiny_skill = MONTH_SKILLS[month_human]
        else:
            destiny_stage = None
            destiny_zone = None
            destiny_skill = None
        
        # クエストデータを準備
        quest_data = {
            'username': st.session_state.username,
            'quest_type': quest_type,
            'ap_cost': ap_cost,
            'title': title,
            'description': description,
            'advice': advice,
            'status': 'active',
            'destiny_stage': destiny_stage,
            'destiny_zone': destiny_zone,
            'destiny_skill': destiny_skill,
            'created_at': datetime.now().isoformat(),
            'deadline_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Supabaseに保存
        result = supabase.table('quests').insert(quest_data).execute()
        
        if result.data:
            st.session_state.active_quest = result.data[0]
            
            # Phase 2: 月の課題の場合、最終受注日を更新
            if quest_type == 'monthly_challenge':
                st.session_state.last_quest_date = datetime.now().date().isoformat()
            
            # プレイヤーステータスを保存
            save_player_status()
            
            return True
        
        return False
    except Exception as e:
        st.error(f"⚠️ クエスト作成エラー: {e}")
        return False

# クエストを報告する
def report_quest(quest_id, report_text, zone_evaluation=None):
    """クエストを報告する"""
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # クエスト情報を取得
        quest_response = supabase.table('quests').select('*').eq('id', quest_id).execute()
        
        if not quest_response.data:
            st.error("⚠️ クエストが見つかりません")
            return False
        
        quest = quest_response.data[0]
        
        # 経過日数を計算
        created_at = datetime.fromisoformat(quest['created_at'].replace('Z', '+00:00'))
        now = datetime.now(created_at.tzinfo)
        days_elapsed = (now - created_at).days
        
        # AP報酬を計算
        if days_elapsed <= 7:
            ap_reward = quest['ap_cost'] * 2  # 7日以内なら2倍
        else:
            ap_reward = quest['ap_cost']  # 8日以降は等倍
        
        # KP報酬を計算（月の課題のみ）
        kp_reward = 0
        if quest['quest_type'] == 'monthly_challenge' and zone_evaluation:
            if zone_evaluation == 'Excellent':
                kp_reward = 30
            elif zone_evaluation == 'Great':
                kp_reward = 20
            elif zone_evaluation == 'Good':
                kp_reward = 10
        
        # EXP報酬（固定）
        exp_reward = 50
        
        # 報告データを準備
        report_data = {
            'quest_id': quest_id,
            'username': st.session_state.username,
            'report_text': report_text,
            'days_elapsed': days_elapsed,
            'ap_reward': ap_reward,
            'kp_reward': kp_reward,
            'exp_reward': exp_reward,
            'zone_evaluation': zone_evaluation,
            'reported_at': datetime.now().isoformat()
        }
        
        # 報告を保存
        supabase.table('quest_reports').insert(report_data).execute()
        
        # クエストのステータスを更新
        supabase.table('quests').update({'status': 'reported'}).eq('id', quest_id).execute()
        
        # プレイヤーステータスを更新
        st.session_state.ap = min(st.session_state.ap + ap_reward, st.session_state.max_ap)
        st.session_state.kp += kp_reward
        st.session_state.exp += exp_reward
        
        # レベルアップチェック
        check_level_up()
        
        # Phase 2: 月の課題の場合、ギフトカケラを追加
        if quest['quest_type'] == 'monthly_challenge':
            add_gift_fragment()
        
        # ステータスを保存
        save_player_status()
        
        # アクティブクエストをクリア
        st.session_state.active_quest = None
        
        return True, ap_reward, kp_reward, exp_reward, days_elapsed
    except Exception as e:
        st.error(f"⚠️ 報告エラー: {e}")
        return False, 0, 0, 0, 0

# レベルアップチェック
def check_level_up():
    """EXPに応じてアバターレベルをチェック・更新"""
    current_level = st.session_state.avatar_level
    
    for level in range(4, -1, -1):
        if st.session_state.exp >= AVATAR_LEVELS[level]['exp_required']:
            if level > current_level:
                st.session_state.avatar_level = level
                st.session_state.max_ap = AVATAR_LEVELS[level]['max_ap']
                st.success(f"🎉 レベルアップ！ {AVATAR_LEVELS[level]['name']}")
            break


# ==================== Phase 2: 新機能 ====================

# 自然回復チェック
def check_daily_login():
    """毎日のログイン時にAPを自然回復"""
    if not st.session_state.username:
        return
    
    today = datetime.now().date()
    last_login = st.session_state.last_login_date
    
    # 最終ログイン日が文字列の場合、dateオブジェクトに変換
    if isinstance(last_login, str):
        last_login = datetime.fromisoformat(last_login).date()
    
    # 初回ログインまたは日付が変わっている場合
    if last_login is None or last_login < today:
        # APが0の場合のみ+1回復
        if st.session_state.ap == 0:
            st.session_state.ap = 1
            st.success("☀️ 新しい日が始まりました！APが1回復しました。")
        
        # 最終ログイン日を更新
        st.session_state.last_login_date = today.isoformat()
        save_player_status()

# エントロピーチェック
def check_entropy():
    """28日ごとの月の課題受注チェック"""
    if not st.session_state.username or not st.session_state.last_quest_date:
        return None
    
    last_quest = st.session_state.last_quest_date
    if isinstance(last_quest, str):
        last_quest = datetime.fromisoformat(last_quest).date()
    
    today = datetime.now().date()
    days_since_quest = (today - last_quest).days
    
    # 28日経過したらペナルティ
    if days_since_quest >= 28:
        return "penalty"
    # 21日経過（残り7日）で警告
    elif days_since_quest >= 21:
        return "warning_7days"
    # 25日経過（残り3日）で最終警告
    elif days_since_quest >= 25:
        return "warning_3days"
    
    return None

# エントロピーペナルティ適用
def apply_entropy_penalty():
    """エントロピーペナルティを適用"""
    if not st.session_state.username:
        return False
    
    try:
        # AP半減
        st.session_state.ap = st.session_state.ap // 2
        
        # KP没収
        lost_kp = st.session_state.kp
        st.session_state.kp = 0
        
        # 最終クエスト日をリセット
        st.session_state.last_quest_date = datetime.now().date().isoformat()
        
        # 保存
        save_player_status()
        
        st.error(f"""
⚠️ **エントロピー（自然減衰）が発生しました！**

28日間、月の課題を受注しなかったため：
- AP半減: {st.session_state.ap * 2} → {st.session_state.ap}
- KP没収: {lost_kp} KP を失いました

定期的に月の課題を受注して、エントロピーを防ぎましょう！
        """)
        
        return True
    except Exception as e:
        st.error(f"ペナルティ適用エラー: {e}")
        return False

# ギフトデータを読み込む
def load_gifts():
    """Supabaseからギフトデータを読み込む"""
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # 今年のギフトを取得
        current_year = datetime.now().year
        response = supabase.table('gifts').select('*').eq(
            'username', st.session_state.username
        ).eq('gift_year', current_year).execute()
        
        if response.data:
            data = response.data[0]
            st.session_state.gift_fragments = data['fragment_count']
            st.session_state.completed_gifts = 1 if data['is_complete'] else 0
        else:
            # データがない場合は初期化
            st.session_state.gift_fragments = 0
            st.session_state.completed_gifts = 0
        
        return True
    except Exception as e:
        st.warning(f"⚠️ ギフトデータ読み込みエラー: {e}")
        return False

# ギフトカケラを追加
def add_gift_fragment():
    """月の課題クリアでカケラを追加"""
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        current_year = datetime.now().year
        
        # カケラを+1
        st.session_state.gift_fragments += 1
        
        # 5カケラで1ギフト完成
        if st.session_state.gift_fragments >= 5:
            st.session_state.completed_gifts += 1
            st.session_state.gift_fragments = 0
            
            # ギフト完成通知
            st.success(f"""
🎁 **天運ギフトが完成しました！**

カケラ5個を集めて、今年の天運ギフトが完成しました。
キングダムのランクアップに使用できます。

完成したギフト: {st.session_state.completed_gifts}個
            """)
        
        # Supabaseに保存
        gift_data = {
            'username': st.session_state.username,
            'gift_year': current_year,
            'gift_name': f'{current_year}年の天運ギフト',
            'fragment_count': st.session_state.gift_fragments,
            'is_complete': st.session_state.gift_fragments == 0 and st.session_state.completed_gifts > 0
        }
        
        # 既存レコードをチェック
        existing = supabase.table('gifts').select('username').eq(
            'username', st.session_state.username
        ).eq('gift_year', current_year).execute()
        
        if existing.data:
            # 既存レコードがある場合は更新
            supabase.table('gifts').update(gift_data).eq(
                'username', st.session_state.username
            ).eq('gift_year', current_year).execute()
        else:
            # 既存レコードがない場合は挿入
            supabase.table('gifts').insert(gift_data).execute()
        
        return True
    except Exception as e:
        st.warning(f"⚠️ ギフト追加エラー: {e}")
        return False

# キングダムランクアップ可能かチェック
def can_rankup_kingdom():
    """キングダムをランクアップできるかチェック"""
    current_rank = st.session_state.kingdom_rank
    
    # すでに最高ランク
    if current_rank >= 4:
        return False, "すでに最高ランク（Rank 4: 王国）です"
    
    next_rank = current_rank + 1
    required_kp = KINGDOM_RANKS[next_rank]['kp_required']
    required_gifts = KINGDOM_RANKS[next_rank]['gifts_required']
    
    # KP不足
    if st.session_state.kp < required_kp:
        return False, f"KPが不足しています（必要: {required_kp} KP、所持: {st.session_state.kp} KP）"
    
    # ギフト不足
    if st.session_state.completed_gifts < required_gifts:
        return False, f"天運ギフトが不足しています（必要: {required_gifts}個、所持: {st.session_state.completed_gifts}個）"
    
    return True, f"ランクアップ可能！（消費: {required_kp} KP + ギフト{required_gifts}個）"

# キングダムランクアップ実行
def rankup_kingdom():
    """キングダムをランクアップ"""
    if not st.session_state.username:
        return False
    
    # チェック
    can_rankup, message = can_rankup_kingdom()
    if not can_rankup:
        st.error(message)
        return False
    
    try:
        next_rank = st.session_state.kingdom_rank + 1
        required_kp = KINGDOM_RANKS[next_rank]['kp_required']
        required_gifts = KINGDOM_RANKS[next_rank]['gifts_required']
        
        # KPとギフトを消費
        st.session_state.kp -= required_kp
        st.session_state.completed_gifts -= required_gifts
        
        # ランクアップ
        st.session_state.kingdom_rank = next_rank
        
        # 保存
        save_player_status()
        
        st.success(f"""
🏰 **キングダムがランクアップしました！**

{KINGDOM_RANKS[next_rank-1]['name']} → {KINGDOM_RANKS[next_rank]['name']}

消費:
- {required_kp} KP
- 天運ギフト {required_gifts}個

理想の拠点が、また一歩近づきました！
        """)
        
        return True
    except Exception as e:
        st.error(f"ランクアップエラー: {e}")
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
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# プレイヤーレベルを計算（旧システムとの互換性）
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

# レベル名を取得（旧システムとの互換性）
def get_level_name(level):
    """レベル番号からレベル名を取得"""
    if level in AVATAR_LEVELS:
        return AVATAR_LEVELS[level]['name']
    return "Lv.? UNKNOWN"

# Supabaseからデータを読み込む
def load_from_supabase():
    """Supabaseからセッションデータを読み込む"""
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # プレイヤーステータスを読み込む
        load_player_status()
        
        # アクティブなクエストを読み込む
        load_active_quest()
        
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
            
            # プレイヤーレベルを計算（旧システム）
            st.session_state.player_level = calculate_player_level()
            
            # Phase 2: ギフトデータを読み込む
            load_gifts()
            
            # Phase 2: 自然回復チェック
            check_daily_login()
            
            # Phase 2: エントロピーチェック
            entropy_status = check_entropy()
            if entropy_status == "penalty":
                apply_entropy_penalty()
            elif entropy_status == "warning_7days" and not st.session_state.entropy_warning_shown:
                st.warning("⚠️ あと7日以内に月の課題を受注してください！エントロピーペナルティが発生します。")
                st.session_state.entropy_warning_shown = True
            elif entropy_status == "warning_3days":
                st.error("🚨 あと3日以内に月の課題を受注してください！エントロピーペナルティまで残りわずかです！")
            
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
        level_name = AVATAR_LEVELS.get(st.session_state.avatar_level, AVATAR_LEVELS[0])['name']
        kingdom_name = KINGDOM_RANKS.get(st.session_state.kingdom_rank, KINGDOM_RANKS[0])['name']
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
        
        return f"""あなたは『THE PLAYER』のガイド「アトリ」であり、プレイヤーが「現実（リアル）という名の神ゲー」を攻略するための導き手です。

【プレイヤー情報】
■ 基本情報
- ユーザー名: {st.session_state.username}
- アバターレベル: {level_name}
- キングダム: {kingdom_name}
- 生年月日: {st.session_state.birthdate}
- 年齢: {st.session_state.age}歳
- 星座: {st.session_state.zodiac}

■ リソース
- AP: {st.session_state.ap} / {st.session_state.max_ap}（行動力）
- KP: {st.session_state.kp}（建国資材）
- EXP: {st.session_state.exp}（経験値）
- COIN: {st.session_state.coin}（課金通貨）

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
あなたは深い洞察力を持つ運命の導き手「アトリ」であり、プレイヤーが現実を攻略するためのガイドです。

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
- 月のゾーン（{month_zone}）に合った行動を推奨する

**重要な原則:**
1. プレイヤーは自分の人生の主人公である
2. 運命は「攻略すべきステージ」である
3. アバターの特性を活かした戦略を提案する
4. 今年のミッションとフィールドを意識する
5. 最終的にはキングダム（理想の居場所）を築くことが目標
6. 月のゾーンに合致した行動を取ることでKPが獲得できる

美しい日本語で、古の賢者が現代のゲームマスターのように語りかけてください。"""
    return "あなたは運命の導き手「アトリ」です。"


# ログインページ
def login_page():
    """ログイン/サインアップページ"""
    st.markdown("""
    <div class="main-header">
        <div class="logo">🎮</div>
        <h1 class="main-title">THE PLAYER</h1>
        <p class="subtitle">現実（リアル）という名の神ゲーを攻略せよ</p>
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
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <div class="logo">🎮</div>
        <h1 class="main-title">THE PLAYER</h1>
        <p class="subtitle">現実（リアル）という名の神ゲーを攻略せよ</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 生年月日が未登録の場合
    if not st.session_state.birthdate:
        st.info("💡 最初に生年月日を登録してください")
        
        birthdate = st.date_input(
            "生年月日を入力してください",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.now()
        )
        
        if st.button("✨ 運命の羅針盤を開く", use_container_width=True):
            birthdate_str = birthdate.strftime("%Y-%m-%d")
            profile = calculate_profile(birthdate_str)
            
            # セッション状態を更新
            st.session_state.birthdate = birthdate_str
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
            
            # 新しいセッションを作成
            create_new_session()
            
            # ウェルカムメッセージ
            welcome_message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✨ 運命の羅針盤、開かれました ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ようこそ、{st.session_state.username}さん。

【基本情報】
 年齢: {profile['age']}歳
 星座: {profile['zodiac']}
 レベル: {AVATAR_LEVELS[st.session_state.avatar_level]['name']}
 キングダム: {KINGDOM_RANKS[st.session_state.kingdom_rank]['name']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【本質（WHO & GOAL）】固定値

 本質 人運 {profile['essence_human']}
 └ アバター: {profile['avatar']}

 本質 地運 {profile['essence_earth']}
 └ キングダム: {profile['kingdom']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【今年の攻略（{profile['age']}歳）】13年周期

 運命 人運 {profile['destiny_human']}
 └ ミッション: {profile['mission']}

 運命 地運 {profile['destiny_earth']}
 └ フィールド: {profile['field']}

 運命 天運 {profile['destiny_heaven']}
 └ 報酬: {profile['reward']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【今月の攻略】28日周期

 月 天運 {profile['month_heaven']}
 └ ステージ: {profile['month_stage']}

 月 地運 {profile['month_earth']}
 └ ゾーン: {profile['month_zone']}

 月 人運 {profile['month_human']}
 └ スキル: {profile['month_skill']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【人生攻略の公式】
1. WHO（アバター）: {profile['avatar']}の特性で
2. WHAT（ミッション）: {profile['mission']}
3. WHERE（フィールド）: {profile['field']}で活躍し
4. GET（報酬）: {profile['reward']}を獲得
5. GOAL（キングダム）: {profile['kingdom']}を築く

私はあなたの運命の導き手「アトリ」です。
この現実（リアル）という名の壮大なゲームを、共に攻略していきましょう。

さあ、クエストを受注して冒険を始めましょう！"""
            
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
                <div class="profile-label">プレイヤー</div>
                <div class="profile-value">👤 {st.session_state.username}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="resource-box">
                <div class="profile-label">リソース</div>
                <div class="resource-item">
                    <span class="resource-label">⚡ AP</span>
                    <span class="resource-value">{st.session_state.ap} / {st.session_state.max_ap}</span>
                </div>
                <div class="resource-item">
                    <span class="resource-label">🏰 KP</span>
                    <span class="resource-value">{st.session_state.kp}</span>
                </div>
                <div class="resource-item">
                    <span class="resource-label">✨ EXP</span>
                    <span class="resource-value">{st.session_state.exp}</span>
                </div>
                <div class="resource-item">
                    <span class="resource-label">🪙 COIN</span>
                    <span class="resource-value">{st.session_state.coin}</span>
                </div>
                <div class="resource-item">
                    <span class="resource-label">🎁 ギフト</span>
                    <span class="resource-value">{st.session_state.completed_gifts}個</span>
                </div>
                <div class="resource-item">
                    <span class="resource-label">✨ カケラ</span>
                    <span class="resource-value">{st.session_state.gift_fragments} / 5</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">レベル</div>
                <div class="level-badge">{AVATAR_LEVELS[st.session_state.avatar_level]['name']}</div>
                <div class="profile-label" style="margin-top: 0.5rem;">キングダム</div>
                <div class="level-badge">{KINGDOM_RANKS[st.session_state.kingdom_rank]['name']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Phase 2: ランクアップボタン
            if st.session_state.kingdom_rank < 4:
                can_rankup, message = can_rankup_kingdom()
                if can_rankup:
                    if st.button("🏰 キングダムをランクアップ", use_container_width=True, type="primary"):
                        if rankup_kingdom():
                            st.rerun()
                else:
                    st.caption(message)
            
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
                
                for session_id, session in sorted_sessions[:3]:  # 最新3件のみ表示
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
                st.session_state.current_session_id = None
                st.session_state.active_quest = None
                st.session_state.show_report_form = False
                st.rerun()
        
        # クエスト受注UI（アクティブなクエストがない場合）
        if not st.session_state.active_quest:
            st.markdown("### 📜 クエストを受注する")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="quest-card">
                    <div class="quest-title">💬 相談する</div>
                    <div class="quest-cost">消費: 1 AP</div>
                    <p style="color: #c0c0c0; font-size: 0.9rem;">日常の悩みや小さな疑問について、アトリに相談できます。</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("💬 相談する（1AP）", use_container_width=True, disabled=st.session_state.ap < 1):
                    if st.session_state.ap >= 1:
                        st.session_state.show_consultation_form = True
                        st.rerun()
            
            with col2:
                st.markdown("""
                <div class="quest-card">
                    <div class="quest-title">🎯 月の課題</div>
                    <div class="quest-cost">消費: 2 AP</div>
                    <p style="color: #c0c0c0; font-size: 0.9rem;">今月のメインクエスト。KP大量獲得のチャンス！</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🎯 月の課題（2AP）", use_container_width=True, disabled=st.session_state.ap < 2):
                    if st.session_state.ap >= 2:
                        st.session_state.show_challenge_form = True
                        st.rerun()
            
            # 相談フォーム
            if st.session_state.get('show_consultation_form', False):
                st.markdown("---")
                st.markdown("### 💬 相談内容を入力してください")
                
                consultation_text = st.text_area(
                    "相談内容",
                    placeholder="例: 仕事で新しいプロジェクトを任されましたが、不安です...",
                    height=150
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("キャンセル", use_container_width=True):
                        st.session_state.show_consultation_form = False
                        st.rerun()
                
                with col2:
                    if st.button("相談する", use_container_width=True, type="primary"):
                        if consultation_text:
                            with st.spinner("🌌 宇宙と対話中..."):
                                try:
                                    # AIに相談内容を投げる
                                    response = model.generate_content(consultation_text)
                                    advice = response.text
                                    
                                    # クエストを作成
                                    if create_quest(
                                        quest_type='consultation',
                                        title=consultation_text[:50],
                                        description=consultation_text,
                                        advice=advice
                                    ):
                                        st.session_state.messages.append({"role": "user", "content": consultation_text})
                                        st.session_state.messages.append({"role": "assistant", "content": advice})
                                        st.session_state.show_consultation_form = False
                                        save_to_supabase()
                                        st.success("✅ クエストを受注しました！行動後に報告してください。")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"エラー: {e}")
                        else:
                            st.warning("相談内容を入力してください")
            
            # 月の課題フォーム
            if st.session_state.get('show_challenge_form', False):
                st.markdown("---")
                st.markdown("### 🎯 今月の課題について相談")
                
                challenge_text = st.text_area(
                    "今月取り組みたいことや目標",
                    placeholder=f"今月のゾーン「{st.session_state.month_zone}」に沿った行動を考えましょう...",
                    height=150
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("キャンセル", key="cancel_challenge", use_container_width=True):
                        st.session_state.show_challenge_form = False
                        st.rerun()
                
                with col2:
                    if st.button("課題を受注", use_container_width=True, type="primary"):
                        if challenge_text:
                            with st.spinner("🌌 宇宙と対話中..."):
                                try:
                                    prompt = f"""今月の課題について相談です。

【相談内容】
{challenge_text}

【今月の運命】
- ステージ: {st.session_state.month_stage}
- ゾーン: {st.session_state.month_zone}
- スキル: {st.session_state.month_skill}

この運命を活かした具体的な行動プランを提案してください。"""
                                    
                                    response = model.generate_content(prompt)
                                    advice = response.text
                                    
                                    # クエストを作成
                                    if create_quest(
                                        quest_type='monthly_challenge',
                                        title=challenge_text[:50],
                                        description=challenge_text,
                                        advice=advice
                                    ):
                                        st.session_state.messages.append({"role": "user", "content": challenge_text})
                                        st.session_state.messages.append({"role": "assistant", "content": advice})
                                        st.session_state.show_challenge_form = False
                                        save_to_supabase()
                                        st.success("✅ 月の課題を受注しました！行動後に報告してください。")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"エラー: {e}")
                        else:
                            st.warning("課題内容を入力してください")
        
        else:
            # アクティブなクエスト表示
            quest = st.session_state.active_quest
            created_at = datetime.fromisoformat(quest['created_at'].replace('Z', '+00:00'))
            days_elapsed = (datetime.now(created_at.tzinfo) - created_at).days
            
            st.markdown("### 📜 進行中のクエスト")
            
            status_color = "#4CAF50" if days_elapsed <= 7 else "#FFA500"
            
            st.markdown(f"""
            <div class="quest-card" style="border-color: {status_color};">
                <div class="quest-title">{quest['title']}</div>
                <div class="quest-cost">{'💬 相談' if quest['quest_type'] == 'consultation' else '🎯 月の課題'}</div>
                <p style="color: #c0c0c0; font-size: 0.9rem;">経過日数: {days_elapsed}日 / 7日</p>
                <p style="color: {'#4CAF50' if days_elapsed <= 7 else '#FFA500'};">
                    {'⚡ 期限内報告で2倍APボーナス！' if days_elapsed <= 7 else '⚠️ 期限超過（AP報酬は等倍）'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📝 行動を報告する", use_container_width=True, type="primary"):
                st.session_state.show_report_form = True
                st.rerun()
        
        # 報告フォーム
        if st.session_state.get('show_report_form', False) and st.session_state.active_quest:
            st.markdown("---")
            st.markdown("### 📝 行動報告")
            
            report_text = st.text_area(
                "何を行動しましたか？",
                placeholder="例: アドバイスを参考に、プロジェクトリーダーに相談して役割分担を明確化しました...",
                height=150
            )
            
            zone_eval = None
            if st.session_state.active_quest['quest_type'] == 'monthly_challenge':
                st.markdown(f"**今月のゾーン**: {st.session_state.month_zone}")
                zone_eval = st.selectbox(
                    "ゾーンへの適合度（自己評価）",
                    options=['Good', 'Great', 'Excellent'],
                    help="Good: +10 KP, Great: +20 KP, Excellent: +30 KP"
                )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("キャンセル", key="cancel_report", use_container_width=True):
                    st.session_state.show_report_form = False
                    st.rerun()
            
            with col2:
                if st.button("報告を送信", use_container_width=True, type="primary"):
                    if report_text:
                        result = report_quest(
                            quest_id=st.session_state.active_quest['id'],
                            report_text=report_text,
                            zone_evaluation=zone_eval
                        )
                        
                        if result:
                            success, ap_reward, kp_reward, exp_reward, days = result
                            
                            st.success(f"""
✅ 報告完了！

**獲得した報酬:**
- ⚡ AP: +{ap_reward}
- 🏰 KP: +{kp_reward}
- ✨ EXP: +{exp_reward}

経過日数: {days}日
{'🎉 期限内報告！APが2倍になりました！' if days <= 7 else ''}
                            """)
                            
                            st.session_state.show_report_form = False
                            
                            # メッセージに追加
                            st.session_state.messages.append({
                                "role": "user",
                                "content": f"【行動報告】\n{report_text}"
                            })
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"素晴らしい行動でした！\n\n獲得報酬:\n- ⚡ AP: +{ap_reward}\n- 🏰 KP: +{kp_reward}\n- ✨ EXP: +{exp_reward}"
                            })
                            
                            save_to_supabase()
                            
                            st.rerun()
                    else:
                        st.warning("報告内容を入力してください")
        
        # チャット履歴を表示
        st.markdown("---")
        st.markdown("### 💬 会話履歴")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # ユーザー入力を無効化（クエスト必須）
        if st.session_state.active_quest:
            st.info("💡 クエスト進行中です。行動完了後に報告してください。")
        else:
            st.info("💡 質問するには、上の「💬 相談する」または「🎯 月の課題」ボタンからクエストを受注してください。")

if __name__ == "__main__":
    main()
    
    # フッター
    st.markdown("""
    <footer style='text-align: center; padding: 2rem 0; color: #c0c0c0; font-size: 0.8rem; opacity: 0.7;'>
        © 2024 THE PLAYER - Powered by Google Gemini AI
    </footer>
    """, unsafe_allow_html=True)

