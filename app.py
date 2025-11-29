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
    
    /* チャットスクロール領域 */
    .chat-wrapper {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem 0;
    }
    
    .chat-wrapper::-webkit-scrollbar {
        width: 10px;
    }
    
    .chat-wrapper::-webkit-scrollbar-track {
        background: #1e1e1e;
        border-radius: 5px;
    }
    
    .chat-wrapper::-webkit-scrollbar-thumb {
        background: #555;
        border-radius: 5px;
    }
    
    .chat-wrapper::-webkit-scrollbar-thumb:hover {
        background: #777;
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

# 年の装備（道具）詳細データベース - 13種類
YEARLY_EQUIPMENT = {
    0: {
        'name': 'Reset Button',
        'japanese': 'リセット・ボタン',
        'function': '強制終了と初期化',
        'description': '複雑になりすぎた人間関係や、動かなくなったプロジェクトを「なかったこと」にする道具。ボタンを押すだけで、目の前が真っ白な更地に戻る。',
        'usage': '修理しようとせず、迷わずボタンを押すこと。思考を停止させ、「ゼロに戻す」機能を使う。'
    },
    1: {
        'name': 'First Pickaxe',
        'japanese': '最初のツルハシ',
        'function': '一点突破と開拓',
        'description': '誰もいない荒野や、硬い壁に「最初の風穴」を開けるための道具。切れ味は鋭いが、範囲は狭い。',
        'usage': '誰かと一緒に持とうとせず、一人で振り下ろすこと。「私がやる」という意志の力を込めて使う。'
    },
    2: {
        'name': 'High-Spec Binoculars',
        'japanese': '高性能双眼鏡',
        'function': '遠見と分析',
        'description': '遠くの未来や、相手の心の中を拡大して見るための道具。動かずに情報を集めるのに特化している。',
        'usage': '足は動かさず、レンズを覗くことに集中すること。焦って走り出すと、この道具の性能は発揮されない。'
    },
    3: {
        'name': 'Magic Crayon',
        'japanese': '魔法のクレヨン',
        'function': '具現化と彩り',
        'description': '空中に描いたものが実体化するような、創造の道具。理屈抜きで、楽しんで描けば描くほど、世界がカラフルになる。',
        'usage': '上手く描こうとせず、落書きのように自由に使うこと。「面白そう」という衝動で手を動かす。'
    },
    4: {
        'name': 'Spirit Level',
        'japanese': '水平器と定規',
        'function': '計測と安定',
        'description': '積み上げたものが崩れないよう、正確に測り、固定するための道具。地味だが、強固な城を建てるには不可欠。',
        'usage': '感覚で進めず、メモリ（数字や実績）に合わせてきっちりと使うこと。確実性を最優先する。'
    },
    5: {
        'name': 'Megaphone',
        'japanese': 'メガホン',
        'function': '拡散と主張',
        'description': '自分の声を何倍にも大きくして、遠くまで届ける道具。自分の存在を世界にアピールし、注目を集める。',
        'usage': '空気を読まず、大声で叫ぶこと（発信する）。「私はここにいる！」と主張するために使う。'
    },
    6: {
        'name': 'Watering Can',
        'japanese': '恵みのジョウロ',
        'function': '育成と調和',
        'description': '乾いた場所に水をやり、種を育てる道具。攻撃力はないが、周囲を癒やし、味方を増やす効果がある。',
        'usage': '自分のためではなく、他者（花）のために使うこと。見返りを求めず、ただ注ぐだけでいい。'
    },
    7: {
        'name': 'Vision Compass',
        'japanese': 'ビジョン・コンパス',
        'function': '指針と理想',
        'description': '現実の地図には載っていない「理想郷」の方角を指し示す特殊な羅針盤。嵐の中でも、目指すべき場所を見失わない。',
        'usage': '足元の悪路は見ず、針が指す「遠くの未来」だけを見つめて進むこと。'
    },
    8: {
        'name': 'Surfboard',
        'japanese': 'サーフボード',
        'function': '波乗りと加速',
        'description': '自力で泳ぐのではなく、押し寄せる「時代の波」や「他人の力」に乗って、高速で移動するための道具。',
        'usage': '波に逆らわず、バランスを取ることに集中すること。来た波（オファー）には、とりあえず乗ってみる。'
    },
    9: {
        'name': 'Sorting Shears',
        'japanese': '選別のハサミ',
        'function': '剪定と完了',
        'description': '伸びすぎた枝葉や、不要になった過去を切り落とす道具。本当に大切な「幹」だけを残し、美しく整える。',
        'usage': '情に流されず、スパッと切ること。「もったいない」と思わず、身軽になるために使う。'
    },
    10: {
        'name': 'Dynamite',
        'japanese': '変革のダイナマイト',
        'function': '破壊と刷新',
        'description': '古くなって使えなくなった建物やシステムを、一撃で破壊する道具。更地にして、新しい建設を可能にする。',
        'usage': '爆発を恐れないこと。過去の成功体験ごと吹き飛ばす覚悟で、点火スイッチを押す。'
    },
    11: {
        'name': 'Miracle Rod',
        'japanese': '奇跡の杖',
        'function': '直感と魔法',
        'description': '一振りすれば、壁に扉が現れたり、ワープしたりする魔法の杖。理屈では説明できないショートカットを起こす。',
        'usage': '使い方のマニュアルはない。「今だ！」と閃いた瞬間に振る。頭で考えずに使うこと。'
    },
    12: {
        'name': 'Relay Baton',
        'japanese': '継承のバトン',
        'function': '接続と委託',
        'description': '自分が走るのをやめ、次の走者に想いと記録を託すための道具。これを持つことで、チーム全体の勝利が確定する。',
        'usage': '握りしめ続けず、適切な相手に「渡す」こと。自分がゴールするのではなく、繋ぐことを目的にする。'
    }
}

# 年のフィールド（攻略エリア）詳細データベース - 13種類
YEARLY_FIELD = {
    0: {
        'name': 'BLANK FIELD',
        'japanese': '始まりの更地',
        'situation': '古い建物が撤去され、何もない地平線が広がる場所。静寂に包まれ、すべてがリセットされている。',
        'quest': '整地と浄化。装備した道具を使って、残っている瓦礫をきれいに片付け、次なる建設のために土地を清める作業。無理に建てようとせず、空っぽの状態を維持する。'
    },
    1: {
        'name': 'STARTUP GARAGE',
        'japanese': '創業のガレージ',
        'situation': '雑多なパーツや素材が転がっている、活気ある作業場。まだ何者でもないが、何かを始めようとする熱気に満ちている。',
        'quest': '種まきとプロトタイプ作成。装備した道具を使って、手元にある素材を組み合わせ、最初の試作品を作る。小さな「一歩」を刻み、自分の旗を立てる作業。'
    },
    2: {
        'name': 'CROSSROAD CAFE',
        'japanese': '分岐点のカフェ',
        'situation': '幾つもの道が交差する場所にある、見晴らしの良いカフェ。旅人たちが地図を広げ、次の行き先を相談している。',
        'quest': 'ルート選定と情報収集。装備した道具を使って、それぞれの道の先を偵察する。焦って出発せず、座ってコーヒーを飲みながら、最も有利なルートを見極める作業。'
    },
    3: {
        'name': 'CREATIVE PARK',
        'japanese': '創造の広場',
        'situation': '音楽が鳴り、人々が自由に表現を楽しんでいる開放的な公園。ルール無用で、面白いことが次々と起きている。',
        'quest': '表現とエンタメ。装備した道具を使って、自分のアイデアを形にしたり、即興でパフォーマンスをする。周りを巻き込んで「楽しい！」の渦を作る作業。'
    },
    4: {
        'name': 'SOLID BASE',
        'japanese': '堅牢な土台',
        'situation': '石畳やレンガ造りの建物が並ぶ、秩序ある建設現場。安全第一で、確実な作業が進められている。',
        'quest': '基礎工事とルール作り。装備した道具を使って、歪みのない正確な土台を築く。毎日のルーティンを守り、崩れないシステムを構築する地道な作業。'
    },
    5: {
        'name': 'WINDY PORT',
        'japanese': '風の港',
        'situation': '世界中から船が出入りし、常に新しい風が吹いている港町。留まる人はおらず、情報は一瞬で入れ替わる。',
        'quest': '交易と冒険。装備した道具を使って、新しい情報を発信したり、未知の船に飛び乗ったりする。変化の波を乗りこなし、活動範囲を広げる作業。'
    },
    6: {
        'name': 'COMMUNITY GARDEN',
        'japanese': '調和の庭',
        'situation': '美しい花々が咲き乱れ、人々が穏やかに談笑している庭園。争いはなく、助け合いの精神に満ちている。',
        'quest': '水やりと交流。装備した道具を使って、花（人）に水をやり、関係性を育てる。困っている人に手を貸し、コミュニティの絆を深める作業。'
    },
    7: {
        'name': 'OBSERVATORY',
        'japanese': '天空の展望台',
        'situation': '雲の上にある静かな塔。地上の雑音は届かず、星空や遥か彼方の景色だけが見える。',
        'quest': 'ビジョン策定と理想の追求。装備した道具を使って、本当の目的地（理想）の方角を定める。現実的な制約を忘れ、最高の未来図を描く作業。'
    },
    8: {
        'name': 'EXPANSION CITY',
        'japanese': '繁栄の都市',
        'situation': '高層ビルが立ち並び、莫大な富と権力が動いている大都市。個人の力ではなく、組織やシステムが主役の場所。',
        'quest': '拡大と統率。装備した道具を使って、大きなビジネスの波に乗る。オファーを受け入れ、チームを動かし、成果を最大化する作業。'
    },
    9: {
        'name': 'ARCHIVE LIBRARY',
        'japanese': '知恵の書庫',
        'situation': 'あらゆる記録が収められた静謐な図書館。一つの時代の終わりを告げる鐘が鳴り響いている。',
        'quest': '編集と総決算。装備した道具を使って、膨大なデータの中から「本質」だけを切り抜き、残りを処分する。物語のエンディングを美しく仕上げる作業。'
    },
    10: {
        'name': 'TRANSFORM ZONE',
        'japanese': '変容の実験室',
        'situation': '古い物質が分解され、新しいエネルギーに変換されている実験室。爆発や化学反応が絶え間なく起きている。',
        'quest': '破壊と再構築。装備した道具を使って、古くなった常識や枠組みを壊す。形を変えることを恐れず、新しい自分へとアップデートする作業。'
    },
    11: {
        'name': 'MIRACLE DESERT',
        'japanese': '奇跡の砂漠',
        'situation': '地図にない幻の砂漠。ここでは物理法則が通用せず、蜃気楼の中に真実が隠されている。',
        'quest': '直感探索と魔法。装備した道具を使って、見えない道を見つけ出す。論理ではなく「ピンときた」方向に進み、隠された宝（チャンス）を掘り当てる作業。'
    },
    12: {
        'name': 'CONTROL ROOM',
        'japanese': '中央指令室',
        'situation': 'すべてのモニターが並び、世界全体の状況を把握できる場所。直接現場には出ず、通信だけで指示を送る。',
        'quest': '調整と引き継ぎ。装備した道具を使って、適切な人に適切な役割を渡す。全体がスムーズに動くように微調整を行い、次世代へシステムを託する作業。'
    }
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

# 年の報酬（天運ギフト）詳細データベース - 13種類
YEARLY_GIFT = {
    0: {
        'name': 'Complete Reset',
        'japanese': '完全なる白紙',
        'overview': '過去のデータやしがらみを全て消去し、ゼロから再構築できる権利。「変容と形の更新」の力が宿っている。',
        'effects': [
            '抱えていた重荷が消え、身軽になれる',
            'どんな自分にもなれる「無限の可能性」が手に入る',
            '複雑だった問題が強制終了し、静寂が訪れる'
        ],
        'building_material': '整地・解体工事。古くなった設備を取り壊し、新しい建物を建てるためのスペースを確保する。キングダムの敷地を拡張し、更地にするための必須プロセス。'
    },
    1: {
        'name': 'Starter Kit',
        'japanese': '冒険の書',
        'overview': '見えなかった状況が姿を現し、新しい物語を始めるための初期装備一式。「輝く未来」への地図の断片。',
        'effects': [
            '「自分は何者か」というアイデンティティが確立される',
            '霧が晴れるように、進むべき最初の一歩が見えてくる',
            '周囲から「あの人は新しいことを始めた」と認知される'
        ],
        'building_material': '礎石（定礎）。新しい建物の「最初の石」を置く。キングダムに新しいエリアや機能を追加する際の、基準点となる重要な石。'
    },
    2: {
        'name': 'Scouting Report',
        'japanese': '偵察報告書',
        'overview': '進むべき道（太陽の道か月の道か）を見極めるための詳細な分析データ。機会を待つ間に得られる、確かな指針。',
        'effects': [
            '焦って失敗することを回避できる',
            '表面的な情報ではなく、物事の裏側にある「真実」を知ることができる',
            '最良のタイミングで動くための「確信」が手に入る'
        ],
        'building_material': '設計図・測量。どこに何を配置すれば最適かを決めるための精密な図面。無駄な建築を防ぎ、キングダムの動線を最適化する。'
    },
    3: {
        'name': 'Invitation Letter',
        'japanese': '新世界への招待状',
        'overview': '現在と過去が混ざり合い、新しい世界への扉を開くためのチケット。思わぬ出会いや出来事を引き寄せるパスポート。',
        'effects': [
            '想像もしなかった楽しいコミュニティに参加できる',
            '運命的な「結合」が起き、新しいパートナーや仲間ができる',
            '退屈な日常が、刺激的なエンターテインメントに変わる'
        ],
        'building_material': '装飾・インテリア。無機質だった建物に、彩りや遊び心を加える。居住性を高め、住人たちが楽しく過ごせるための娯楽施設やアートを追加する。'
    },
    4: {
        'name': 'Trust License',
        'japanese': '信頼の証',
        'overview': '社会的な信用や、人生の土台となる安定した基盤。これまでの体験と学びが結晶化した、揺るぎない実績の証明書。',
        'effects': [
            '周囲から「あなたなら任せられる」と高く評価される',
            '経済的、精神的な安定が手に入る',
            '自分の城を建てるための、強固な土地が得られる'
        ],
        'building_material': '柱・城壁。キングダムを支える太い柱や、外敵から守る頑丈な壁。この素材が多いほど、キングダムの防御力と耐久度が上がり、崩れなくなる。'
    },
    5: {
        'name': 'Change Skin',
        'japanese': '変容のマント',
        'overview': '周囲の状況に合わせて自在に姿を変えられる、メタモルフォーゼ（変身）の能力。新しい環境に溶け込むための適応力。',
        'effects': [
            'どんな環境でも生き抜けるサバイバル能力が身につく',
            '膠着していた状態が動き出し、新しい展開が訪れる',
            '古い自分を脱ぎ捨て、バージョンアップした自分になれる'
        ],
        'building_material': '換気システム・窓。閉鎖的だった空間に風を通す。新しい流行や技術を取り入れるための窓口を作り、キングダムの空気を常に新鮮に保つ。'
    },
    6: {
        'name': 'Union Key',
        'japanese': '結束の鍵',
        'overview': '世界を拡大し、他者と繋がるためのマスターキー。様々な価値観を受け入れ、共鳴することで開かれる扉。',
        'effects': [
            '孤独感が消え、愛と調和に満ちた居場所ができる',
            '自分にない才能を持った人々と協力体制が築ける',
            '精神的に満たされ、平和な心を手に入れることができる'
        ],
        'building_material': '広場・ゲストルーム。人と人が交流するためのスペース。住人同士の結束を高めたり、外部からの客人を招き入れるための、温かい居場所を作る。'
    },
    7: {
        'name': 'Victory Title',
        'japanese': '勝利の称号',
        'overview': 'これまでの評価が変容し、一つの「完成」として認められた証。人生のタイトルが定まり、生きる意味が明確になるトロフィー。',
        'effects': [
            '迷いが消え、自分が目指すべき「頂上」がはっきり見える',
            '社会的な評価が一変し、一目置かれる存在になる',
            '独自の美学や哲学が完成し、自信を持って生きられる'
        ],
        'building_material': '塔・シンボル。遠くからでも見える、キングダムの象徴（ランドマーク）。高さを出し、キングダムの理念や理想を周囲に示すためのアンテナ。'
    },
    8: {
        'name': 'Royal Offer',
        'japanese': '王からの勅命',
        'overview': '他者から与えられる「新しい居場所」や「役割」。自分一人では辿り着けない場所へ連れて行ってくれる、運命の招待状。',
        'effects': [
            '自分で営業しなくても、向こうからチャンスがやってくる',
            '実力以上の大きなステージに引き上げられる（棚ぼた運）',
            '不足していた部分を、他者が完璧に補ってくれる'
        ],
        'building_material': '宝物庫・交易路。外部からの富や資源を貯蔵する蔵、あるいは物資を運び入れるための道路。キングダムの経済を潤し、規模を拡大させるための設備。'
    },
    9: {
        'name': 'Completed Map',
        'japanese': '完成した地図',
        'overview': '人生の地図を完成させるための最後のピース。過去を清算し、次のステージへ進むために必要な「卒業証書」。',
        'effects': [
            '長年の悩みや課題が解決し、スッキリする',
            '過去の経験がすべて「知恵」に変わり、無駄がなかったと悟る',
            '次の旅へ向けて、身軽で自由な状態になれる'
        ],
        'building_material': '屋根・門。建物の一つの区画を完成させる仕上げ。雨風をしのぐ屋根や、エリアを区切る門を設置し、一つの機能を「完結」させる。'
    },
    10: {
        'name': 'Next Stage Ticket',
        'japanese': '次次元への切符',
        'overview': '新たな道が出現し、これまでの延長線上ではない未来へ進む権利。運命の螺旋が一段上がり、次元上昇（アセンション）するパス。',
        'effects': [
            '停滞していた壁が壊れ、一気に視界が開ける',
            '今までとは全く違う、ハイレベルな環境や人間関係に移行する',
            '「本当の人生」がここから始まると実感できる'
        ],
        'building_material': '増築・別館。既存の建物とは全く違う様式の、新しい棟を建てる。キングダムの機能や見た目をガラリと変え、バージョンアップさせるための大規模改修素材。'
    },
    11: {
        'name': 'Miracle Trigger',
        'japanese': '奇跡の引き金',
        'overview': '何かが始まる「きっかけ」となる矢印。一直線ではないが、確実に前へと進むためのサインや予兆。',
        'effects': [
            '偶然の連続（シンクロニシティ）が起き、トントン拍子に進む',
            '理屈では説明できない「ラッキー」な出来事に遭遇する',
            '眠っていた才能や可能性が、突然目覚める'
        ],
        'building_material': 'パワースポット・隠し通路。論理的な構造とは関係のない、不思議な力が宿る祭壇や、一瞬で移動できる隠し通路。キングダムに魔法的な効果を付与する。'
    },
    12: {
        'name': 'Realization Gem',
        'japanese': '具現化の宝石',
        'overview': '心の中の思いや希望が、現実の世界で具体的な「形」となった結晶。11で掴んだきっかけが実を結び、手で触れられる成果となったもの。',
        'effects': [
            '夢物語だと思っていたことが、現実の生活の一部になる',
            '自分の成果が、他者の役にも立つ「遺産（レガシー）」となる',
            '努力が報われ、目に見える豊かさとして手元に残る'
        ],
        'building_material': '記念碑・ライブラリー。これまでの歴史や知恵を保存するための場所。キングダムの伝統を守り、次世代へ継承するための重要なアーカイブ施設。'
    }
}

MONTH_STAGES = {
    0: "✨ クリアリング（浄化）",
    1: "🌅 スタートアップ（起動）",
    2: "🌱 セレクション（選択）",
    3: "🌸 イマジネーション（想像）",
    4: "☀️ ファウンデーション（定着）",
    5: "🌾 クロッシング（交流）",
    6: "🌙 メンテナンス（調和）",
    7: "🌑 アチーブメント（達成）",
    8: "🌠 ハードモード（試練）",
    9: "🔄 ハーベスト（収穫）",
    10: "⚡ マーケット（還元）",
    11: "🎭 ラビリンス（迷宮）",
    12: "🧘 コントリビューション（奉仕）"
}

MONTH_ZONES = {
    0: "🌈 ベイカントロット（更地）",
    1: "🎯 スカベンジャーエリア（収集）",
    2: "🤝 オブザベーションデッキ（観測）",
    3: "🎨 ウィンドトンネル（風の通り道）",
    4: "🏗️ フォートレス（要塞）",
    5: "🌊 チェンジャブルウェザー（変わりやすい天気）",
    6: "💚 コミュニティホール（集会所）",
    7: "🔮 ミラージュタワー（蜃気楼の塔）",
    8: "⚡ ハイスピードストリーム（高速ベルトコンベア）",
    9: "🔥 チェックアウトカウンター（精算カウンター）",
    10: "📊 ワープゾーン（ワープゾーン）",
    11: "📣 マジックフィールド（魔法陣）",
    12: "🎯 コントロールタワー（管制塔）"
}

MONTH_SKILLS = {
    0: "✨ ゼロセンス（思考停止）",
    1: "⚔️ ファーストストライク（先制攻撃）",
    2: "🛡️ ディープスキャン（深層分析）",
    3: "🎪 ジョイスパーク（娯楽化）",
    4: "🔨 グラウンディング（足場固め）",
    5: "🧭 ブレイブシャウト（自己主張）",
    6: "💞 ヒーリングリンク（調和）",
    7: "🔮 イーグルアイ（俯瞰視点）",
    8: "⚡ パワーサーフィン（便乗）",
    9: "🌀 エッセンシャルカット（断捨離）",
    10: "📐 パラダイムシフト（変革）",
    11: "📣 ミラクルフラッシュ（直感行動）",
    12: "🎯 バトンパス（委譲）"
}

# ==================== マンスリー・ストラテジー 詳細データ ====================

def get_month_stage_detail(stage_num):
    """月天運（ステージ）の詳細情報を取得 - 13段階（0-12）"""
    details = {
        0: {"english": "CLEARING", "theme": "浄化", "description": "全てのログを整理し、不要なデータを削除する年末処理のようなステージ。新しいことを始めるのではなく、「終わらせる」「手放す」ことに専念し、メモリを空けることで、次なるStage 1がスムーズに起動します。"},
        1: {"english": "STARTUP", "theme": "起動", "description": "新しい意志が芽吹く、始まりのステージ。ここでは「壮大な計画」よりも「とりあえずログインする（小さな一歩を踏み出す）」ことが推奨されます。動き出しにボーナスがつきます。"},
        2: {"english": "SELECTION", "theme": "選択", "description": "外野の声が遮断された、静かな個室ステージ。アクションを起こすよりも、マップを広げて「どちらのルートに進むか」をじっくり選ぶことに適しています。判断力が強化されるエリアです。"},
        3: {"english": "IMAGINATION", "theme": "想像", "description": "自由な発想が許される実験室のようなステージ。「こうなったら面白い」という妄想やシミュレーションが、現実化しやすい補正がかかります。外向きの意識を持つことで道が開けます。"},
        4: {"english": "FOUNDATION", "theme": "定着", "description": "安全地帯で、足場を固めるステージ。生活リズム、仕事のルーティン、人間関係の土台など、地味ですが重要な「足元」を整備することで、防御力が大幅にアップします。"},
        5: {"english": "CROSSING", "theme": "交流", "description": "多くのプレイヤーが行き交う、賑やかな広場ステージ。ソロプレイよりも、他者との会話や情報交換（チャット）が攻略の鍵となります。新しい出会いイベントが発生しやすい期間です。"},
        6: {"english": "MAINTENANCE", "theme": "調和", "description": "心身のバランスを整えるための休息ステージ。無理に先へ進もうとするとペナルティ（疲労）が発生しやすいため、装備の手入れや体調管理に専念するのが吉です。"},
        7: {"english": "ACHIEVEMENT", "theme": "達成", "description": "前半戦のゴール地点となるステージ。これまでの努力が「形」となって現れやすく、達成感を味わえます。ここで一度セーブし、現状を確認することで、後半戦へのフラグが立ちます。"},
        8: {"english": "HARD MODE", "theme": "試練", "description": "通常より難易度が高い、ボス戦のようなステージ。試練や壁が現れますが、それは「限界突破」のためのイベントです。逃げずに挑むことで、大量の経験値とレベルアップが約束されています。"},
        9: {"english": "HARVEST", "theme": "収穫", "description": "ここまでのプレイに対する報酬（ドロップアイテム）を受け取るステージ。成果が目に見える形で手に入ります。遠慮せず「受け取る」コマンドを選択し、感謝することで運気がさらに上がります。"},
        10: {"english": "MARKET", "theme": "還元", "description": "手に入れたアイテムや情報を、他者と分かち合う市場のようなステージ。独り占めせず「共有」や「貢献」を行うことで、さらに大きな循環（トレード）が生まれ、次の展開へと繋がります。"},
        11: {"english": "LABYRINTH", "theme": "迷宮", "description": "霧がかかり、視界が悪くなる迷宮ステージ。マップ（論理）が役に立たず、不安になりますが、ここは「直感」のステータスが試される場所。迷いを受け入れ、心の声に従うことで隠し通路が見つかります。"},
        12: {"english": "CONTRIBUTION", "theme": "奉仕", "description": "自分のクエストではなく、他者のクエストを手伝うためのステージ。「人のために時間を使う」ことで、徳（カルマ）が浄化され、来期に向けた幸運の種まきが完了します。"}
    }
    return details.get(stage_num, {})

def get_month_zone_detail(zone_num):
    """月地運（ゾーン）の詳細情報を取得 - 13段階（0-12）"""
    details = {
        0: {"english": "VACANT LOT", "constraint": "新規建築・禁止", "hint": "焦って新しい予定を入れないこと。空白を作れば作るほど、次のサイクルのためのエネルギーがチャージされます。"},
        1: {"english": "SCAVENGER AREA", "constraint": "持ち込み禁止・現地調達", "hint": "遠くを見すぎないこと。半径5メートル以内にある「使えるもの」「協力してくれそうな人」を見逃さないでください。"},
        2: {"english": "OBSERVATION DECK", "constraint": "移動速度ダウン・視界良好", "hint": "「動けない」と焦る必要はありません。「今は作戦タイムだ」と割り切り、情報収集とシミュレーションに時間を使いましょう。"},
        3: {"english": "WIND TUNNEL", "constraint": "操縦不能・乱気流", "hint": "ハンドルを握りしめず、風任せにドリフトすること。「面白そうな方へ流される」のが、このゾーンの正解ルートです。"},
        4: {"english": "FORTRESS", "constraint": "防御力アップ・変化無効", "hint": "派手なアクションは控え、地味なルーティンワークや基礎練習に徹すること。ここで固めた足場は、絶対に崩れません。"},
        5: {"english": "CHANGEABLE WEATHER", "constraint": "環境激変・適応力テスト", "hint": "計画通りにいかなくても怒らないこと。「そう来たか！」と面白がり、即座にプランBへ切り替える反射神経を磨きましょう。"},
        6: {"english": "COMMUNITY HALL", "constraint": "ソロプレイ禁止・協力必須", "hint": "「自分でやった方が早い」と思っても、あえて誰かに声をかけましょう。おしゃべりや交流の中に、攻略のヒントが隠されています。"},
        7: {"english": "MIRAGE TOWER", "constraint": "重力軽減・現実感希薄", "hint": "目の前の雑務は最低限にして、意識を「未来」や「理想」に飛ばしましょう。妄想することが、ここでは立派な攻略行動です。"},
        8: {"english": "HIGH SPEED STREAM", "constraint": "強制移動・途中下車不可", "hint": "抵抗して逆走しようとしないこと。「なるようになれ」と腹を括り、この高速移動が連れて行ってくれる景色を楽しみましょう。"},
        9: {"english": "CHECKOUT COUNTER", "constraint": "持ち出し制限・整理整頓", "hint": "「広げる」ことより「畳む」ことを意識しましょう。やり残したことを完了させ、身軽になることでクリアとなります。"},
        10: {"english": "WARP ZONE", "constraint": "現在地不明・システム更新", "hint": "「前のやり方」を捨てること。何が起きても「これは新しいステージへの転送演出だ」と捉え、変化を受け入れてください。"},
        11: {"english": "MAGIC FIELD", "constraint": "論理無効・直感優位", "hint": "「なぜ？」と考えないこと。ピンときた方向に道があります。偶然やラッキーも、ここでは実力のうちです。"},
        12: {"english": "CONTROL TOWER", "constraint": "直接介入禁止・遠隔操作", "hint": "自分が動けないもどかしさを手放し、「全体を見る目」を持ちましょう。適切な人にパスを出すことが、最速のクリア方法です。"}
    }
    return details.get(zone_num, {})

def get_month_skill_detail(skill_num):
    """月人運（スキル）の詳細情報を取得 - 13段階（0-12）"""
    details = {
        0: {"english": "ZERO SENSE", "effect": "思考停止・感覚覚醒", "action": "迷ったら目を閉じ、深呼吸して「嫌だ」と感じるものを拒絶する"},
        1: {"english": "FIRST STRIKE", "effect": "先制攻撃・単独行動", "action": "相談せずに一人で始める"},
        2: {"english": "DEEP SCAN", "effect": "深層分析・未来予測", "action": "情報を集めて比較検討する"},
        3: {"english": "JOY SPARK", "effect": "娯楽化・アイデア創造", "action": "面白そう！と口にする"},
        4: {"english": "GROUNDING", "effect": "足場固め・現実化", "action": "計画表を作る"},
        5: {"english": "BRAVE SHOUT", "effect": "自己主張・拡散", "action": "遠慮せず意見を言う"},
        6: {"english": "HEALING LINK", "effect": "調和・結合", "action": "誰かに優しくする"},
        7: {"english": "EAGLE EYE", "effect": "俯瞰視点・理想設定", "action": "10年後を想像する"},
        8: {"english": "POWER SURFING", "effect": "便乗・他力活用", "action": "流れに身を任せる"},
        9: {"english": "ESSENTIAL CUT", "effect": "断捨離・完結", "action": "やらないことを決める"},
        10: {"english": "PARADIGM SHIFT", "effect": "強制変革・脱皮", "action": "成功パターンを捨てる"},
        11: {"english": "MIRACLE FLASH", "effect": "直感行動・壁抜け", "action": "0.1秒で決める"},
        12: {"english": "BATON PASS", "effect": "委譲・継承", "action": "誰かを主役にする"}
    }
    return details.get(skill_num, {})

# アバターレベル定義
# ==================== Phase 4: アバターレベルシステム（EXPベース）====================

# レベル定義（より戦略的な成長曲線）
AVATAR_LEVELS = {
    0: {
        "name": "Lv.0 NPC（眠れる村人）",
        "english": "NPC - Sleeping Villager",
        "max_ap": 10,
        "exp_required": 0,
        "coin_reward": 0,
        "description": "まだ目覚めていない、普通の人。現実をゲームとして認識していない状態。"
    },
    1: {
        "name": "Lv.1 TRIAL（試練の挑戦者）",
        "english": "TRIAL - Challenger",
        "max_ap": 15,
        "exp_required": 100,
        "coin_reward": 50,
        "description": "運命の羅針盤を手に入れ、人生をゲームとして攻略し始めた。最初の一歩を踏み出した状態。"
    },
    2: {
        "name": "Lv.2 NOVICE（見習い）",
        "english": "NOVICE - Apprentice",
        "max_ap": 20,
        "exp_required": 300,
        "coin_reward": 100,
        "description": "クエストをこなし、経験を積んでいる。攻略法が少しずつ見えてきた状態。"
    },
    3: {
        "name": "Lv.3 ADEPT（熟練者）",
        "english": "ADEPT - Expert",
        "max_ap": 30,
        "exp_required": 700,
        "coin_reward": 150,
        "description": "戦略的に人生を攻略できるようになった。ZONE制約やスキルを使いこなせる状態。"
    },
    4: {
        "name": "Lv.4 MASTER（達人）",
        "english": "MASTER - Virtuoso",
        "max_ap": 40,
        "exp_required": 1500,
        "coin_reward": 200,
        "description": "人生の攻略法を体得し、自在に運命を操れるようになった。真のプレイヤーの一歩手前。"
    },
    5: {
        "name": "Lv.5 PLAYER（覚醒した主人公）",
        "english": "PLAYER - Awakened Protagonist",
        "max_ap": 50,
        "exp_required": 3000,
        "coin_reward": 300,
        "description": "完全に目覚めた状態。現実（リアル）という名の神ゲーを、最高難易度で攻略できる真の主人公。"
    }
}

# レベルアップ時の絵文字
LEVEL_UP_EMOJIS = {
    0: "😴",
    1: "⚡",
    2: "🌱",
    3: "⚔️",
    4: "🔥",
    5: "👑"
}

# キングダムランク定義
# Phase 3: KINGDOM_RANKSは廃止（KPベースの自動ランクアップに移行）
# 代わりにKINGDOM_RANK_THRESHOLDSを使用

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

def calculate_essence_earth(birthdate_str):
    """本質地運のみを計算（キングダムランクシステム用）"""
    birth = datetime.strptime(birthdate_str, "%Y-%m-%d")
    month_sum = birth.month
    day_sum = birth.day
    essence_earth = ((month_sum + day_sum - 1) % 13) + 1
    return essence_earth

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
    """月運を計算（28日周期）- 13段階（0-12）"""
    birth = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.now()
    
    # 誕生日からの経過日数
    days_since_birth = (today - birth).days
    
    # 28日周期での位置（0-27）
    cycle_position = days_since_birth % 28
    
    # 13段階に変換（28日を13段階で分ける）
    # 28 ÷ 13 ≈ 2.15日 per stage
    month_heaven = int((cycle_position * 13) / 28)  # 0-12
    month_earth = int(((cycle_position + 9) * 13) / 28) % 13  # 0-12
    month_human = int(((cycle_position + 18) * 13) / 28) % 13  # 0-12
    
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

# ==================== キングダムランクシステム ====================

# ランク閾値定義（KPベース）
KINGDOM_RANK_THRESHOLDS = {
    0: 0,      # Rank 0: Wasteland（荒れ地）
    1: 100,    # Rank 1: Base Camp（整地）
    2: 300,    # Rank 2: Hideout（建設中）
    3: 600,    # Rank 3: Community（拡張）
    4: 1000    # Rank 4: Kingdom（完成）
}

# ランク名称
KINGDOM_RANK_NAMES = {
    0: "Wasteland（荒れ地）",
    1: "Base Camp（整地）",
    2: "Hideout（建設中）",
    3: "Community（拡張）",
    4: "Kingdom（完成）"
}

# ランク絵文字
KINGDOM_RANK_EMOJIS = {
    0: "🏜️",
    1: "⛺",
    2: "🏠",
    3: "🏘️",
    4: "🏰"
}

# 13種類のキングダム発展データ（完全版）
KINGDOM_DEVELOPMENT = {
    0: {  # オープン・テラス
        'name': 'オープン・テラス',
        'subtitle': '風通しの良い広場',
        'ranks': {
            0: {'name': '密室', 'english': 'Closed Room', 'description': '傷つくのを恐れて壁を作り、誰も入れないように閉じこもっている。空気が澱み、窒息しそうな閉塞感がある。'},
            1: {'name': '換気', 'english': 'Ventilation', 'description': '窓を少し開け、外の空気や人の気配を感じ始める。世界は敵ばかりではないと気づく。'},
            2: {'name': '庭先', 'english': 'Garden Chair', 'description': '自分のテリトリーに、信頼できる人を少しだけ招き入れる。「来るもの拒まず」の練習を始める。'},
            3: {'name': '公園', 'english': 'Public Park', 'description': '多くの人が憩う場所となる。様々な情報やチャンスが行き交い、予期せぬ出会いが生まれる。'},
            4: {'name': 'オープン・テラス', 'english': 'Open Terrace', 'description': '【完成】境界線がなく、世界と一体化した自由な広場。あなたがそこにいるだけで、雲のように形を変えながら、あらゆる可能性を受け入れる聖域となる。'}
        }
    },
    1: {  # マグネット・ベース
        'name': 'マグネット・ベース',
        'subtitle': '引き寄せの基地',
        'ranks': {
            0: {'name': '散乱', 'english': 'Scrap Yard', 'description': '必要なものが何もなく、ガラクタばかりが集まっている。あるいは、自分から必死に探し回り、疲れ果てている。'},
            1: {'name': '磁石', 'english': 'Antenna', 'description': '「私はこれが好き」という旗を立てる。自分の磁力を信じ、探し回るのをやめて「待つ」姿勢を作る。'},
            2: {'name': '工房', 'english': 'Atelier', 'description': '集まってきた少数の材料や仲間を使って、ブリコラージュ（即興制作）を始める。小さな循環が生まれる。'},
            3: {'name': '秘密基地', 'english': 'Secret Base', 'description': '独自の魅力に惹かれた人々が集い、独自の文化が形成される。計画書のない、偶発的な創造が連続する。'},
            4: {'name': 'マグネット・ベース', 'english': 'Magnet Base', 'description': '【完成】座っているだけで、世界中から最高の人材と物資が吸い寄せられる場所。集まったピースが自動的に組み上がり、巨大な城となる。'}
        }
    },
    2: {  # フロンティア・ポート
        'name': 'フロンティア・ポート',
        'subtitle': '最先端の港',
        'ranks': {
            0: {'name': '澱んだ池', 'english': 'Dead End', 'description': '変化がなく、水が腐っている。過去の栄光や安定にしがみつき、「ここから動きたくない」と停滞している。'},
            1: {'name': '筏作り', 'english': 'Raft Building', 'description': '「ここではないどこか」へ行くための準備を始める。現状への違和感を認め、脱出の計画を立てる。'},
            2: {'name': '桟橋', 'english': 'Pier', 'description': '小さな船が出入りし始める。外の世界からのニュースが届き、未来への希望が湧いてくる。'},
            3: {'name': '貿易所', 'english': 'Trading Post', 'description': '多くの旅人が行き交い、常に新しい風が吹いている。一つの場所に留まらず、常に更新され続ける環境。'},
            4: {'name': 'フロンティア・ポート', 'english': 'Frontier Port', 'description': '【完成】常に最先端の船が出航する、希望の港。ここにいれば、世界中の「次（ネクスト）」に一番乗りできる。永遠に成長し続ける場所。'}
        }
    },
    3: {  # スカイ・バルーン
        'name': 'スカイ・バルーン',
        'subtitle': '空飛ぶ気球',
        'ranks': {
            0: {'name': '檻', 'english': 'Cage', 'description': '地面に鎖で繋がれ、重たい荷物（責任や常識）を背負わされている。「こうすべき」に縛られ、息ができない。'},
            1: {'name': '凧揚げ', 'english': 'Kite', 'description': '風の存在に気づく。少しだけ荷物を下ろし、心の中で「もし自由だったら」と空を見上げる。'},
            2: {'name': 'テント', 'english': 'Mobile Living', 'description': '一箇所に定住するのをやめ、身軽になる。風向きが変わればすぐに移動できる柔軟性を持つ。'},
            3: {'name': '飛行船', 'english': 'Airship', 'description': '多くの人を乗せて、風に乗って旅をする。変化を楽しみ、トラブルさえも「面白いイベント」に変える。'},
            4: {'name': 'スカイ・バルーン', 'english': 'Sky Balloon', 'description': '【完成】重力から解放された、完全な自由空間。風まかせに漂いながら、誰も見たことのない景色を楽しみ続ける。'}
        }
    },
    4: {  # ストーン・キャッスル
        'name': 'ストーン・キャッスル',
        'subtitle': '堅牢な城',
        'ranks': {
            0: {'name': '砂上の楼閣', 'english': 'Sand Castle', 'description': '基礎がなく、少しの風で崩れそう。「大丈夫だろうか」という不安が常にあり、見栄えだけを気にしている。'},
            1: {'name': '基礎工事', 'english': 'Base Work', 'description': '地味な穴掘りと石積み。成果は見えないが、確実なデータと経験を積み重ねる一番大事な時期。'},
            2: {'name': '石壁', 'english': 'Wall', 'description': '自分を守る壁が完成。外敵（不安要素）をシャットアウトし、安心できるプライベート空間を確保する。'},
            3: {'name': '砦', 'english': 'Fort', 'description': '機能を持ち、他人を守れるようになる。信頼できる仲間が集まり、盤石な組織となる。'},
            4: {'name': 'ストーン・キャッスル', 'english': 'Stone Castle', 'description': '【完成】歴史に残る大要塞。何が起きても揺るがない絶対的な安心と信頼が、そこにはある。'}
        }
    },
    5: {  # シーズン・ガーデン
        'name': 'シーズン・ガーデン',
        'subtitle': '四季の庭',
        'ranks': {
            0: {'name': '荒れ地', 'english': 'Wasteland', 'description': '手入れがされず、雑草が生い茂っている。あるいは「ずっと春でなければならない」と変化を拒否し、無理をしている。'},
            1: {'name': '耕作', 'english': 'Cultivation', 'description': '自分の役割を一つ一つ確認し、不要なものを抜く。それぞれの種（役割）に適した場所を作る。'},
            2: {'name': '苗床', 'english': 'Nursery', 'description': '小さな芽が出始める。役割分担が機能し始め、それぞれの個性が育つ環境が整う。'},
            3: {'name': '果樹園', 'english': 'Orchard', 'description': '季節ごとに違う収穫がある。連携がスムーズになり、変化が「豊かさ」を生むサイクルに入る。'},
            4: {'name': 'シーズン・ガーデン', 'english': 'Season Garden', 'description': '【完成】移ろいゆく季節（役割）の全てが美しい、完璧な調和の庭。常に新陳代謝し、生命力に溢れている。'}
        }
    },
    6: {  # ブリッジ・アイランド
        'name': 'ブリッジ・アイランド',
        'subtitle': '橋のかかった島々',
        'ranks': {
            0: {'name': '孤島', 'english': 'Lonely Island', 'description': '周囲との交流を絶ち、ポツンと取り残されている。誰にも理解されない寂しさを抱えている。'},
            1: {'name': 'ボトルメール', 'english': 'Message in a Bottle', 'description': '海に向かってメッセージを投げる。「私はここにいる」と外の世界へシグナルを送り、接点を探す。'},
            2: {'name': '桟橋', 'english': 'Pier', 'description': '小さな船が着ける場所を作る。特定の人との深い対話や、少人数のコミュニティが生まれる。'},
            3: {'name': '連絡船', 'english': 'Ferry', 'description': '定期的な交流が始まる。自分と似た価値観を持つ島々（人々）と繋がり、協力関係を築く。'},
            4: {'name': 'ブリッジ・アイランド', 'english': 'Bridge Island', 'description': '【完成】無数の橋で繋がれた、豊かな経済圏。個性を保ちながらも孤独ではない、愛と交流のサンクチュアリ。'}
        }
    },
    7: {  # ドリーム・タワー
        'name': 'ドリーム・タワー',
        'subtitle': '理想の塔',
        'ranks': {
            0: {'name': '地下室', 'english': 'Underground', 'description': '目の前の現実に埋没し、空を見上げることを忘れている。「どうせ無理だ」と夢を封印し、暗い場所にいる。'},
            1: {'name': '梯子', 'english': 'Ladder', 'description': '地面に梯子をかける。少し高い位置から周囲を見渡し、「あそこへ行きたい」という方向性を確認する。'},
            2: {'name': '展望台', 'english': 'Observatory', 'description': '自分一人だけの構想部屋。世間の常識から離れ、遠い未来を詳細にシミュレーションする。'},
            3: {'name': '灯台', 'english': 'Lighthouse', 'description': '塔に明かりが灯り、周囲からも見えるようになる。その光（理想）に惹かれて、仲間が集まり始める。'},
            4: {'name': 'ドリーム・タワー', 'english': 'Dream Tower', 'description': '【完成】雲を突き抜ける高さに達した理想郷。下界の常識は通用しない。ここからは、過去も未来も全てが見渡せる。'}
        }
    },
    8: {  # リバー・サイド
        'name': 'リバー・サイド',
        'subtitle': '大河のほとり',
        'ranks': {
            0: {'name': '干上がった川', 'english': 'Dry River', 'description': '流れがなく、何も運ばれてこない。あるいは、自力で水を引こうとして力尽きている。孤独な努力。'},
            1: {'name': '水脈', 'english': 'Source', 'description': 'わずかな水の流れを見つける。人の縁や、小さなチャンスの芽を大切にし始める。'},
            2: {'name': '小川', 'english': 'Stream', 'description': '流れに乗る感覚を掴む。流れてくる小さな丸太（助け）に掴まり、楽に進むことを覚える。'},
            3: {'name': '運河', 'english': 'Canal', 'description': '流れを整備し、多くの船が行き交う場所にする。自分だけでなく、周りの人も運ぶシステムを作る。'},
            4: {'name': 'リバー・サイド', 'english': 'River Side', 'description': '【完成】悠久の大河のほとりで、豊かさを享受する。自ら動かなくても、必要なものは全て上流から運ばれてくる。'}
        }
    },
    9: {  # クライミング・マウンテン
        'name': 'クライミング・マウンテン',
        'subtitle': '登山道',
        'ranks': {
            0: {'name': '平地', 'english': 'Flat Land', 'description': '目指すべき山が見つからず、退屈な日々を過ごしている。向上心を持て余し、エネルギーが内側で腐っている。'},
            1: {'name': '登山口', 'english': 'Gate', 'description': '「あの山に登ろう」と目標を定める。必要な装備を整え、最初の一歩を踏み出す。'},
            2: {'name': 'ベースキャンプ', 'english': 'Base Camp', 'description': '中腹まで到達する。厳しさも知るが、振り返ると絶景が広がっていることに気づき、達成感を味わう。'},
            3: {'name': '稜線', 'english': 'Ridge', 'description': '頂上が見えてくる。困難な道だが、挑戦すること自体に喜びを感じ、仲間と共に励まし合う。'},
            4: {'name': 'サミット', 'english': 'Summit', 'description': '【完成】雲海を見下ろす頂。達成の喜びと共に、さらに高い次の山（目標）を見つけ、魂が震える。'}
        }
    },
    10: {  # シェア・シップ
        'name': 'シェア・シップ',
        'subtitle': '相乗り船',
        'ranks': {
            0: {'name': '漂流', 'english': 'Drift', 'description': '一人で海に投げ出されている。どこへ行けばいいかわからず、孤独と不安に苛まれている。'},
            1: {'name': '発見', 'english': 'Discovery', 'description': '遠くに大きな船（誰かの夢）を見つける。「あの船に乗りたい」という希望を持つ。'},
            2: {'name': '乗船', 'english': 'Boarding', 'description': '勇気を出して船に乗り込む。船長（リーダー）の夢を共有し、自分にできる役割を探す。'},
            3: {'name': '航海', 'english': 'Voyage', 'description': 'クルーの一員として活躍する。船長の夢が叶うことが、自分の夢の実現だと実感する。'},
            4: {'name': 'シェア・シップ', 'english': 'Share Ship', 'description': '【完成】信頼できる仲間と共に、約束の地へたどり着く。誰かの夢の一部になることで、一人では見られなかった景色を見る。'}
        }
    },
    11: {  # ミステリー・ピラミッド
        'name': 'ミステリー・ピラミッド',
        'subtitle': '神秘の遺跡',
        'ranks': {
            0: {'name': '迷路', 'english': 'Labyrinth', 'description': '出口のない迷路で迷っている。予測不能な出来事に振り回され、「なぜ私だけ」と被害者意識を持っている。'},
            1: {'name': '手掛かり', 'english': 'Key', 'description': '偶然の中に意味を見つける。「これは何かのサインかも？」と直感を信じ始める。'},
            2: {'name': '発掘', 'english': 'Dig', 'description': '砂を掘り起こし、隠された扉を開ける。常識外れな行動を試し、小さな奇跡を体験する。'},
            3: {'name': '解読', 'english': 'Decode', 'description': '遺跡の謎（宇宙の法則）を理解する。カオスを楽しみ、波乗りするようにトラブルを乗りこなす。'},
            4: {'name': 'ミステリー・ピラミッド', 'english': 'Mystery Pyramid', 'description': '【完成】ここでは毎日が奇跡。思考が現実化するスピードが極限まで速まった、魔法の領域。'}
        }
    },
    12: {  # コントロール・ルーム
        'name': 'コントロール・ルーム',
        'subtitle': '司令室',
        'ranks': {
            0: {'name': '戦場', 'english': 'Battlefield', 'description': '自ら剣を持って最前線で戦い、傷ついている。全体が見えず、目の前の敵に翻弄されている。'},
            1: {'name': '撤退', 'english': 'Retreat', 'description': '一歩引いて、状況を俯瞰する。「自分が動くべきではない」と気づき、安全な場所を確保する。'},
            2: {'name': '整理', 'english': 'Organize', 'description': '手の届く範囲（デスク周りや身近な人間関係）を完璧に整える。自分のテリトリーを確立する。'},
            3: {'name': '采配', 'english': 'Command', 'description': '適切な人に適切な指示を出す。自分が動かなくても、指先一つで世界がスムーズに回り始める。'},
            4: {'name': 'コントロール・ルーム', 'english': 'Control Room', 'description': '【完成】全ての状況をモニターし、調和を保つ静かな部屋。あなたがいる限り、この世界に平和と秩序が保たれる。'}
        }
    }
}


def get_kingdom_rank_from_kp(kp: int) -> int:
    """KPから現在のキングダムランクを判定"""
    if kp >= KINGDOM_RANK_THRESHOLDS[4]:
        return 4
    elif kp >= KINGDOM_RANK_THRESHOLDS[3]:
        return 3
    elif kp >= KINGDOM_RANK_THRESHOLDS[2]:
        return 2
    elif kp >= KINGDOM_RANK_THRESHOLDS[1]:
        return 1
    else:
        return 0


def get_next_rank_kp(current_rank: int):
    """次のランクに必要なKPを取得"""
    if current_rank >= 4:
        return None
    return KINGDOM_RANK_THRESHOLDS[current_rank + 1]


def get_kingdom_info(kingdom_number: int, rank: int) -> dict:
    """指定されたキングダム番号とランクの情報を取得"""
    # 既存システムは1-13、新システムは0-12なので変換
    kingdom_index = (kingdom_number - 1) % 13
    
    if kingdom_index not in KINGDOM_DEVELOPMENT:
        return None
    
    kingdom = KINGDOM_DEVELOPMENT[kingdom_index]
    rank_info = kingdom['ranks'].get(rank, {})
    
    return {
        'kingdom_name': kingdom['name'],
        'kingdom_subtitle': kingdom['subtitle'],
        'rank': rank,
        'rank_name': rank_info.get('name', ''),
        'rank_english': rank_info.get('english', ''),
        'rank_description': rank_info.get('description', ''),
        'rank_emoji': KINGDOM_RANK_EMOJIS.get(rank, ''),
        'rank_display': KINGDOM_RANK_NAMES.get(rank, '')
    }


def calculate_rank_progress(kp: int, current_rank: int) -> dict:
    """現在のランクでの進捗状況を計算"""
    if current_rank >= 4:
        return {
            'percentage': 100,
            'current_kp': kp,
            'next_kp': None,
            'remaining_kp': 0
        }
    
    current_threshold = KINGDOM_RANK_THRESHOLDS[current_rank]
    next_threshold = KINGDOM_RANK_THRESHOLDS[current_rank + 1]
    
    kp_in_rank = kp - current_threshold
    kp_needed = next_threshold - current_threshold
    
    percentage = min(100, (kp_in_rank / kp_needed) * 100) if kp_needed > 0 else 0
    
    return {
        'percentage': percentage,
        'current_kp': kp,
        'next_kp': next_threshold,
        'remaining_kp': max(0, next_threshold - kp)
    }


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

# 新規: 対話システム用の状態
if 'pending_quest' not in st.session_state:
    st.session_state.pending_quest = None
if 'waiting_for_yes' not in st.session_state:
    st.session_state.waiting_for_yes = False
if 'last_user_input' not in st.session_state:
    st.session_state.last_user_input = ""
if 'last_ap_cost' not in st.session_state:
    st.session_state.last_ap_cost = 0

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

# クエストを作成する（YESボタン押下時に呼ばれる）
def create_quest(quest_type, title, description, advice, initial_cost):
    """
    新しいクエストを作成する
    initial_cost: 相談時に既に消費したAP（1 or 2）
    この関数呼び出し時はAP消費しない（既に消費済み）
    """
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
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
            'ap_cost': initial_cost,  # 互換性のため残す
            'initial_cost': initial_cost,  # 新フィールド: 初期コスト
            'followup_count': 0,  # 新フィールド: 途中相談回数
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

def increment_followup_count(quest_id):
    """
    途中相談回数をインクリメント
    進行中のクエストへの追加相談時に呼ぶ
    """
    try:
        supabase = get_supabase_client()
        
        # 現在のfollowup_countを取得
        quest_response = supabase.table('quests').select('followup_count').eq('id', quest_id).execute()
        
        if quest_response.data:
            current_count = quest_response.data[0].get('followup_count', 0)
            new_count = current_count + 1
            
            # インクリメント
            supabase.table('quests').update({
                'followup_count': new_count
            }).eq('id', quest_id).execute()
            
            # セッション状態も更新
            if st.session_state.active_quest:
                st.session_state.active_quest['followup_count'] = new_count
            
            return True
        return False
    except Exception as e:
        st.error(f"⚠️ 途中相談カウントエラー: {e}")
        return False

def is_monthly_challenge_request(user_input):
    """
    ユーザー入力が月の課題申請かどうかを判定
    """
    keywords = [
        "今月の課題",
        "月の課題",
        "月次ミッション",
        "今月のクエスト",
        "マンスリークエスト",
        "今月のミッション"
    ]
    return any(keyword in user_input for keyword in keywords)

def extract_quest_title(response_text):
    """
    AIの返答からクエストタイトルを抽出
    【提案クエスト】や『』で囲まれた部分を探す
    """
    import re
    
    # 『』で囲まれた部分を探す
    match = re.search(r'『(.+?)』', response_text)
    if match:
        return match.group(1)
    
    # 【提案クエスト】の次の行を探す
    lines = response_text.split('\n')
    for i, line in enumerate(lines):
        if '【提案クエスト】' in line or '提案クエスト' in line:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # 『』を除去
                next_line = next_line.replace('『', '').replace('』', '')
                return next_line[:50]  # 最大50文字
    
    # 見つからない場合は最初の50文字
    return response_text[:50].replace('\n', ' ').strip()

# クエストを報告する
def evaluate_zone_compliance_with_ai(quest_advice, report_text, zone_info):
    """
    AIがZONE適合度を判定する
    
    Args:
        quest_advice: クエスト時のアドバイス
        report_text: ユーザーの報告内容
        zone_info: 今月のZONE情報（制約と攻略法）
    
    Returns:
        評価（'Excellent', 'Great', 'Good', 'Poor'）
    """
    try:
        # Gemini APIを使用してZONE適合度を判定
        model = configure_gemini()
        
        evaluation_prompt = f"""あなたは『THE PLAYER』の評価AIです。

【ZONE情報】
{zone_info}

【クエスト時のアドバイス】
{quest_advice}

【プレイヤーの報告】
{report_text}

上記の報告内容が、ZONEの制約に適っているかを評価してください。

評価基準:
- **Excellent**: ZONE制約を完璧に理解し、推奨された行動を実行している
- **Great**: ZONE制約をよく理解し、概ね推奨行動を実行している
- **Good**: ZONE制約を理解し、部分的に推奨行動を実行している
- **Poor**: ZONE制約を無視した行動、または報告が不十分

**重要**: 以下の形式でのみ回答してください（他の文章は一切含めないこと）：
Excellent
または
Great
または
Good
または
Poor
"""
        
        response = model.generate_content(evaluation_prompt)
        evaluation = response.text.strip()
        
        # 評価が正しい形式か確認
        if evaluation in ['Excellent', 'Great', 'Good', 'Poor']:
            return evaluation
        else:
            # AIが正しく返答しなかった場合はGoodをデフォルトに
            return 'Good'
            
    except Exception as e:
        print(f"AI評価エラー: {e}")
        # エラー時はGoodをデフォルトに
        return 'Good'


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
        
        # AP報酬を計算（initial_costベース）
        # 途中相談のコストは返還対象外
        initial_cost = quest.get('initial_cost', quest.get('ap_cost', 1))
        
        if days_elapsed <= 7:
            ap_reward = initial_cost * 2  # 7日以内なら2倍
        else:
            ap_reward = initial_cost  # 8日以降は等倍
        
        # KP報酬を計算（月の課題のみ）
        kp_reward = 0
        ai_evaluation = None
        
        if quest['quest_type'] == 'monthly_challenge':
            # 月運情報を取得
            if st.session_state.birthdate:
                profile = calculate_profile(st.session_state.birthdate)
                zone_info = f"""
今月のZONE: {profile.get('month_zone', 'Unknown')}
制約: {profile.get('month_zone_constraint', '')}
攻略法: {profile.get('month_skill', 'Unknown')}
"""
                
                # AIにZONE適合度を判定させる
                with st.spinner("🤖 AIがZONE適合度を評価中..."):
                    ai_evaluation = evaluate_zone_compliance_with_ai(
                        quest_advice=quest.get('advice', ''),
                        report_text=report_text,
                        zone_info=zone_info
                    )
                
                # AI評価に基づいてKPを付与
                if ai_evaluation == 'Excellent':
                    kp_reward = 150  # Excellentは大幅増量
                elif ai_evaluation == 'Great':
                    kp_reward = 100
                elif ai_evaluation == 'Good':
                    kp_reward = 50
                else:  # Poor
                    kp_reward = 10  # 最低限の報酬
            
            # ユーザーの自己評価も記録（参考用）
            final_evaluation = ai_evaluation or zone_evaluation
        else:
            # 通常の相談の場合は基本報酬のみ
            kp_reward = 100
            final_evaluation = None
        
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
            'zone_evaluation': final_evaluation if quest['quest_type'] == 'monthly_challenge' else None,
            'user_evaluation': zone_evaluation,  # ユーザー自己評価
            'ai_evaluation': ai_evaluation,  # AI評価
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
        
        # キングダムランクアップチェック
        check_kingdom_rank_up()
        
        # Phase 2: 月の課題の場合、ギフトカケラを追加
        if quest['quest_type'] == 'monthly_challenge':
            add_gift_fragment()
        
        # ステータスを保存
        save_player_status()
        
        # アクティブクエストをクリア
        st.session_state.active_quest = None
        
        return True, ap_reward, kp_reward, exp_reward, days_elapsed, ai_evaluation
    except Exception as e:
        st.error(f"⚠️ 報告エラー: {e}")
        return False, 0, 0, 0, 0, None

# レベルアップチェック
def check_level_up():
    """
    Phase 4: EXPに応じてアバターレベルをチェック・更新
    レベルアップ時の報酬:
    - AP全回復（成長ボーナス）
    - COIN報酬
    - Max AP増加
    """
    current_level = st.session_state.avatar_level
    
    # レベル5から下に向かってチェック（最高レベルから判定）
    for level in range(5, -1, -1):
        if st.session_state.exp >= AVATAR_LEVELS[level]['exp_required']:
            if level > current_level:
                # レベルアップ！
                st.session_state.avatar_level = level
                st.session_state.max_ap = AVATAR_LEVELS[level]['max_ap']
                
                # AP全回復（成長ボーナス）
                old_ap = st.session_state.ap
                st.session_state.ap = st.session_state.max_ap
                
                # COIN報酬
                coin_reward = AVATAR_LEVELS[level]['coin_reward']
                if coin_reward > 0:
                    st.session_state.coin += coin_reward
                
                # レベルアップ通知
                emoji = LEVEL_UP_EMOJIS.get(level, "⭐")
                st.balloons()
                st.success(f"""
{emoji} **レベルアップ！**

**{AVATAR_LEVELS[level]['name']}**
{AVATAR_LEVELS[level]['english']}

{AVATAR_LEVELS[level]['description']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🎁 レベルアップ報酬**
- ⚡ AP全回復: {old_ap} → {st.session_state.max_ap}
- 📦 Max AP増加: {AVATAR_LEVELS[current_level]['max_ap']} → {st.session_state.max_ap}
- 🪙 COIN: +{coin_reward}

現在の総COIN: {st.session_state.coin} COIN
                """)
            break


def check_kingdom_rank_up():
    """
    KPに応じてキングダムランクをチェック・更新
    ランクアップした場合はTrue、ランクアップ情報を返す
    """
    old_rank = st.session_state.kingdom_rank
    new_rank = get_kingdom_rank_from_kp(st.session_state.kp)
    
    if new_rank > old_rank:
        # ランクアップ！
        st.session_state.kingdom_rank = new_rank
        
        # キングダム情報を取得
        essence_earth = calculate_essence_earth(st.session_state.birthdate) if st.session_state.birthdate else 1
        kingdom_info = get_kingdom_info(essence_earth, new_rank)
        
        # ランクアップ通知を表示
        st.balloons()
        st.success(f"""
🏰 **キングダムランクアップ！**

{kingdom_info['rank_emoji']} **{kingdom_info['rank_display']}** に到達しました！

**{kingdom_info['rank_name']}（{kingdom_info['rank_english']}）**

{kingdom_info['rank_description']}
        """)
        
        return True, kingdom_info
    
    return False, None


# ==================== Phase 2: 新機能 ====================

# アイテム使用: 覚醒ドリンク
def use_energy_drink():
    """
    覚醒ドリンクを使用してAP全回復
    「資本の力（課金）」
    コスト: 100 COIN
    効果: AP即座に全回復
    """
    if st.session_state.coin < 100:
        return False, "COINが不足しています（必要: 100 COIN）"
    
    if st.session_state.ap >= st.session_state.max_ap:
        return False, "APは既に最大です"
    
    # COIN消費
    st.session_state.coin -= 100
    
    # AP全回復
    old_ap = st.session_state.ap
    st.session_state.ap = st.session_state.max_ap
    recovered = st.session_state.ap - old_ap
    
    # 保存
    save_player_status()
    
    return True, f"⚡ 覚醒ドリンクを使用！ AP +{recovered} 回復（{st.session_state.ap}/{st.session_state.max_ap}）"

# 自然回復チェック（ログインボーナス）
def check_daily_login():
    """
    毎日のログイン時にAPを回復（セーフティネット）
    「睡眠による意志力の回復」
    日付が変わった後の初回ログインで +1 AP 固定
    """
    if not st.session_state.username:
        return
    
    today = datetime.now().date()
    last_login = st.session_state.last_login_date
    
    # 最終ログイン日が文字列の場合、dateオブジェクトに変換
    if isinstance(last_login, str):
        last_login = datetime.fromisoformat(last_login).date()
    
    # 初回ログインまたは日付が変わっている場合
    if last_login is None or last_login < today:
        # ログインボーナス: +1 AP（Max APを超えない）
        old_ap = st.session_state.ap
        st.session_state.ap = min(st.session_state.ap + 1, st.session_state.max_ap)
        
        if st.session_state.ap > old_ap:
            st.success(f"☀️ 新しい日が始まりました！ログインボーナス +1 AP（現在: {st.session_state.ap}/{st.session_state.max_ap}）")
        
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
    """
    月の課題クリア時にギフトのカケラを+1
    5カケラで1ギフト完成 → gifts テーブルに記録
    """
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # カケラを+1
        st.session_state.gift_fragments += 1
        
        # 5カケラで1ギフト完成
        if st.session_state.gift_fragments >= 5:
            # カケラをリセット
            st.session_state.gift_fragments = 0
            
            # 完成ギフト数を+1
            st.session_state.completed_gifts += 1
            
            # 今年の天運ギフトを取得
            current_age = st.session_state.age
            current_year = datetime.now().year
            destiny_heaven = st.session_state.destiny_heaven
            
            # ギフト番号を計算（0-12）
            gift_num = (destiny_heaven - 1) % 13
            gift_detail = YEARLY_GIFT[gift_num]
            
            # gifts テーブルに記録
            gift_record = {
                'username': st.session_state.username,
                'gift_number': gift_num,
                'gift_name': gift_detail['name'],
                'gift_japanese': gift_detail['japanese'],
                'acquired_age': current_age,
                'acquired_year': current_year,
                'source': 'fragment_synthesis',
                'used_for_rankup': False
            }
            
            supabase.table('gifts').insert(gift_record).execute()
            
            # ギフト完成通知
            st.success(f"""
🎁 **天運ギフトが完成しました！**

**{gift_detail['name']}（{gift_detail['japanese']}）**

{gift_detail['overview']}

**効果**:
""" + "\n".join([f"- {effect}" for effect in gift_detail['effects']]) + f"""

**建材としての役割**:
{gift_detail['building_material']}

完成したギフト総数: {st.session_state.completed_gifts}個
            """)
            
            return True, 'gift_completed'
        else:
            # カケラ追加の通知
            st.info(f"""
✨ **ギフトのカケラを獲得しました！**

現在のカケラ: {st.session_state.gift_fragments} / 5

あと{5 - st.session_state.gift_fragments}個で天運ギフトが完成します。
            """)
            
            return True, 'fragment_added'
            
    except Exception as e:
        st.warning(f"⚠️ ギフト処理エラー: {e}")
        return False, 'error'


def get_user_gifts(include_used=False):
    """
    ユーザーが獲得したギフト一覧を取得
    
    Args:
        include_used: ランクアップに使用済みのギフトも含めるか
    
    Returns:
        list: ギフトのリスト
    """
    if not st.session_state.username:
        return []
    
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('gifts').select('*').eq('username', st.session_state.username)
        
        if not include_used:
            query = query.eq('used_for_rankup', False)
        
        result = query.order('acquired_at', desc=True).execute()
        
        return result.data if result.data else []
    except Exception as e:
        st.error(f"⚠️ ギフト取得エラー: {e}")
        return []


def get_available_gifts_count():
    """ランクアップに使用可能なギフトの数を取得"""
    gifts = get_user_gifts(include_used=False)
    return len(gifts)


def use_gift_for_rankup(gift_id):
    """
    ギフトをランクアップに使用する
    
    Args:
        gift_id: 使用するギフトのID
    
    Returns:
        bool: 成功したかどうか
    """
    if not st.session_state.username:
        return False
    
    try:
        supabase = get_supabase_client()
        
        # ギフトを「使用済み」にマーク
        supabase.table('gifts').update({
            'used_for_rankup': True,
            'used_at': datetime.now().isoformat()
        }).eq('id', gift_id).execute()
        
        # 完成ギフト数を減らす
        st.session_state.completed_gifts -= 1
        
        return True
    except Exception as e:
        st.error(f"⚠️ ギフト使用エラー: {e}")
        return False

# ============================================================
# 旧ランクアップシステム（Phase 3では廃止）
# Phase 1-2のKINGDOM_RANKSベースのランクアップシステム
# Phase 3ではKPベースの自動ランクアップに移行
# ============================================================

# # キングダムランクアップ可能かチェック
# def can_rankup_kingdom():
#     """キングダムをランクアップできるかチェック"""
#     current_rank = st.session_state.kingdom_rank
#     
#     # すでに最高ランク
#     if current_rank >= 4:
#         return False, "すでに最高ランク（Rank 4: 王国）です"
#     
#     next_rank = current_rank + 1
#     required_kp = KINGDOM_RANKS[next_rank]['kp_required']
#     required_gifts = KINGDOM_RANKS[next_rank]['gifts_required']
#     
#     # KP不足
#     if st.session_state.kp < required_kp:
#         return False, f"KPが不足しています（必要: {required_kp} KP、所持: {st.session_state.kp} KP）"
#     
#     # ギフト不足
#     if st.session_state.completed_gifts < required_gifts:
#         return False, f"天運ギフトが不足しています（必要: {required_gifts}個、所持: {st.session_state.completed_gifts}個）"
#     
#     return True, f"ランクアップ可能！（消費: {required_kp} KP + ギフト{required_gifts}個）"

# # キングダムランクアップ実行
# def rankup_kingdom():
#     """キングダムをランクアップ"""
#     if not st.session_state.username:
#         return False
#     
#     # チェック
#     can_rankup, message = can_rankup_kingdom()
#     if not can_rankup:
#         st.error(message)
#         return False
#     
#     try:
#         next_rank = st.session_state.kingdom_rank + 1
#         required_kp = KINGDOM_RANKS[next_rank]['kp_required']
#         required_gifts = KINGDOM_RANKS[next_rank]['gifts_required']
#         
#         # KPとギフトを消費
#         st.session_state.kp -= required_kp
#         st.session_state.completed_gifts -= required_gifts
#         
#         # ランクアップ
#         st.session_state.kingdom_rank = next_rank
#         
#         # 保存
#         save_player_status()
#         
#         st.success(f"""
# 🏰 **キングダムがランクアップしました！**
# 
# {KINGDOM_RANKS[next_rank-1]['name']} → {KINGDOM_RANKS[next_rank]['name']}
# 
# 消費:
# - {required_kp} KP
# - 天運ギフト {required_gifts}個
# 
# 理想の拠点が、また一歩近づきました！
#         """)
#         
#         return True
#     except Exception as e:
#         st.error(f"ランクアップエラー: {e}")
#         return False


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
        
        # キングダムランク情報を取得
        essence_earth = calculate_essence_earth(st.session_state.birthdate)
        kingdom_info = get_kingdom_info(essence_earth, st.session_state.kingdom_rank)
        kingdom_rank_display = f"{kingdom_info['rank_emoji']} {kingdom_info['rank_display']}: {kingdom_info['rank_name']}"
        
        essence_human = getattr(st.session_state, 'essence_human', '?')
        essence_earth_val = getattr(st.session_state, 'essence_earth', '?')
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
- キングダムランク: {kingdom_rank_display}
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
- キングダム: {kingdom}（本質地運{essence_earth_val}）

■ 今年の攻略（13年周期）
- ミッション: {mission}（運命人運{destiny_human}）
- フィールド: {field}（運命地運{destiny_earth}）
- 報酬: {reward}（運命天運{destiny_heaven}）

■ 今月の攻略（28日周期）
- ステージ: {month_stage}（月天運{month_heaven}）
- ゾーン: {month_zone}（月地運{month_earth}）
- スキル: {month_skill}（月人運{month_human}）

【今月の詳細戦略】
STAGE: {get_month_stage_detail(month_heaven).get('english', '')} - {get_month_stage_detail(month_heaven).get('theme', '')}
→ {get_month_stage_detail(month_heaven).get('description', '')}

ZONE: {get_month_zone_detail(month_earth).get('english', '')}
制約: {get_month_zone_detail(month_earth).get('constraint', '')}
ヒント: {get_month_zone_detail(month_earth).get('hint', '')}

SKILL: {get_month_skill_detail(month_human).get('english', '')}
効果: {get_month_skill_detail(month_human).get('effect', '')}
行動: {get_month_skill_detail(month_human).get('action', '')}

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

**【重要】ラストパス（Last Pass）原則:**
あなたは一方的に話して会話を終わらせてはいけません。必ずプレイヤーに「選択」や「合意」を求める形でターンを終了してください。

❌ NG例（一方的な終了）:
「～なので、頑張ってくださいね！」

✅ OK例（ユーザーにパス）:
「～という攻略法があります。このクエストを受注しますか？」
「準備ができたら報告してください。いつでもお待ちしています。」
「他に相談したいことはありますか？」

**クエスト提案の形式:**
相談を受けたら、以下の形式で提案してください：

```
【あなたの状況分析】
（今月の運勢、アバター特性などを踏まえた分析）

【提案クエスト】
『具体的なタイトル』
（実行可能な具体的アクション）

プレイヤー様、この作戦（クエスト）を実行しますか？
```

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
    # スクロール制御用のグローバルCSS
    st.markdown("""
    <style>
        /* スムーズスクロールを有効化 */
        html {
            scroll-behavior: smooth;
        }
        
        /* チャット入力時のスクロール位置を保持 */
        .stChatInput {
            position: sticky;
            bottom: 0;
            background: white;
            z-index: 100;
        }
    </style>
    """, unsafe_allow_html=True)
    
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
            
            # 覚醒ドリンク（AP回復アイテム）
            if st.session_state.ap < st.session_state.max_ap:
                st.markdown("---")
                if st.button("⚡ 覚醒ドリンク（100 COIN）", use_container_width=True, type="secondary"):
                    success, message = use_energy_drink()
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                st.caption("💡 APを即座に全回復します")
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">レベル</div>
                <div class="level-badge">{AVATAR_LEVELS[st.session_state.avatar_level]['name']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Phase 4: レベル進捗バー
            if st.session_state.avatar_level < 5:
                current_level = st.session_state.avatar_level
                next_level = current_level + 1
                current_exp = st.session_state.exp
                current_threshold = AVATAR_LEVELS[current_level]['exp_required']
                next_threshold = AVATAR_LEVELS[next_level]['exp_required']
                
                exp_in_level = current_exp - current_threshold
                exp_needed = next_threshold - current_threshold
                exp_percentage = min(100, (exp_in_level / exp_needed) * 100) if exp_needed > 0 else 0
                
                st.markdown(f"""
                <div class="profile-info">
                    <div class="profile-label">次のレベルまで</div>
                    <div style="background: rgba(10, 1, 24, 0.6); border-radius: 10px; overflow: hidden; margin: 0.5rem 0;">
                        <div style="background: linear-gradient(90deg, #4a90e2, #63b3ed); height: 20px; width: {exp_percentage}%; transition: width 0.3s;"></div>
                    </div>
                    <div style="color: #c0c0c0; font-size: 0.85rem; text-align: center;">
                        {current_exp} / {next_threshold} EXP ({exp_percentage:.1f}%)
                    </div>
                    <div style="color: #63b3ed; font-size: 0.8rem; text-align: center; margin-top: 0.3rem;">
                        残り {next_threshold - current_exp} EXP で Lv.{next_level} へ！
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="profile-info">
                    <div style="color: #4a90e2; font-size: 0.9rem; text-align: center; font-weight: 600;">
                        👑 最高レベル到達！
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # キングダムランク表示（強化版）
            essence_earth = calculate_essence_earth(st.session_state.birthdate) if st.session_state.birthdate else 1
            kingdom_info = get_kingdom_info(essence_earth, st.session_state.kingdom_rank)
            progress = calculate_rank_progress(st.session_state.kp, st.session_state.kingdom_rank)
            
            st.markdown(f"""
            <div class="profile-info">
                <div class="profile-label">キングダムランク</div>
                <div class="level-badge">{kingdom_info['rank_emoji']} {kingdom_info['rank_display']}</div>
                <div style="margin-top: 0.8rem; color: #c0c0c0; font-size: 0.85rem;">
                    {kingdom_info['kingdom_name']} - {kingdom_info['kingdom_subtitle']}
                </div>
                <div style="margin-top: 0.5rem; color: #f4d16f; font-size: 0.9rem;">
                    {kingdom_info['rank_name']} ({kingdom_info['rank_english']})
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 進捗バー（最大ランク未満の場合のみ表示）
            if st.session_state.kingdom_rank < 4:
                st.markdown(f"""
                <div class="profile-info">
                    <div class="profile-label">ランクアップまでの進捗</div>
                    <div style="background: rgba(10, 1, 24, 0.6); border-radius: 10px; overflow: hidden; margin: 0.5rem 0;">
                        <div style="background: linear-gradient(90deg, #d4af37, #f4d16f); height: 20px; width: {progress['percentage']}%; transition: width 0.3s;"></div>
                    </div>
                    <div style="color: #c0c0c0; font-size: 0.85rem; text-align: center;">
                        {progress['current_kp']} / {progress['next_kp']} KP ({progress['percentage']:.1f}%)
                    </div>
                    <div style="color: #f4d16f; font-size: 0.8rem; text-align: center; margin-top: 0.3rem;">
                        残り {progress['remaining_kp']} KP で次のランクへ！
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="profile-info">
                    <div style="color: #d4af37; font-size: 0.9rem; text-align: center; font-weight: 600;">
                        🎉 キングダム完成！
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Phase 2: ランクアップボタン（旧システム - 削除予定）
            # if st.session_state.kingdom_rank < 4:
            #     can_rankup, message = can_rankup_kingdom()
            #     if can_rankup:
            #         if st.button("🏰 キングダムをランクアップ", use_container_width=True, type="primary"):
            #             if rankup_kingdom():
            #                 st.rerun()
            #     else:
            #         st.caption(message)
            
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
            
            # Phase 4: アバターレベル詳細
            with st.expander("⭐ アバターレベル詳細", expanded=False):
                st.markdown("### 全レベル一覧")
                
                current_level = st.session_state.avatar_level
                
                for level in range(6):
                    is_current = (level == current_level)
                    is_unlocked = (st.session_state.exp >= AVATAR_LEVELS[level]['exp_required'])
                    
                    emoji = LEVEL_UP_EMOJIS.get(level, "⭐")
                    
                    if is_current:
                        status = "✅ 現在のレベル"
                        border_color = "#4a90e2"
                    elif is_unlocked:
                        status = "🔓 到達済み"
                        border_color = "#4CAF50"
                    else:
                        status = "🔒 未到達"
                        border_color = "#666666"
                    
                    st.markdown(f"""
<div style="border: 2px solid {border_color}; border-radius: 10px; padding: 1rem; margin: 1rem 0; background: rgba(255,255,255,0.05);">

### {emoji} {AVATAR_LEVELS[level]['name']}
**{AVATAR_LEVELS[level]['english']}**

{status}

**必要EXP**: {AVATAR_LEVELS[level]['exp_required']} EXP  
**Max AP**: {AVATAR_LEVELS[level]['max_ap']}  
**COIN報酬**: {AVATAR_LEVELS[level]['coin_reward']} COIN

**説明**:  
{AVATAR_LEVELS[level]['description']}

</div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 💡 EXPの獲得方法")
                st.markdown("""
- **途中相談**: 10 EXP
- **相談完了**: 20 EXP
- **月の課題クリア**: 30-50 EXP（評価により変動）
- **クエスト完了**: 日数に応じて変動

レベルを上げることで、Max APが増加し、より多くのクエストに挑戦できるようになります。
                """)
            
            # 年間クエスト詳細表示（Phase 2: 新機能）
            with st.expander("🎯 年間クエスト詳細", expanded=False):
                st.markdown("### 今年の装備（道具）")
                
                # 年の装備の詳細情報
                equipment_num = (st.session_state.destiny_human - 1) % 13
                equipment = YEARLY_EQUIPMENT[equipment_num]
                
                st.markdown(f"""
**{equipment['name']}（{equipment['japanese']}）**

**機能**: {equipment['function']}

**説明**:  
{equipment['description']}

**使い方**:  
{equipment['usage']}
                """)
                
                st.markdown("---")
                st.markdown("### 今年のフィールド（攻略エリア）")
                
                # 年のフィールドの詳細情報
                field_num = (st.session_state.destiny_earth - 1) % 13
                field_detail = YEARLY_FIELD[field_num]
                
                st.markdown(f"""
**{field_detail['name']}（{field_detail['japanese']}）**

**状況**:  
{field_detail['situation']}

**クエスト内容**:  
{field_detail['quest']}
                """)
                
                st.markdown("---")
                st.markdown("### 今年の報酬（天運ギフト）")
                
                # 年の報酬の詳細情報
                gift_num = (st.session_state.destiny_heaven - 1) % 13
                gift_detail = YEARLY_GIFT[gift_num]
                
                st.markdown(f"""
**{gift_detail['name']}（{gift_detail['japanese']}）**

**概要**:  
{gift_detail['overview']}

**効果**:
""")
                for effect in gift_detail['effects']:
                    st.markdown(f"- {effect}")
                
                st.markdown(f"""
**建材としての役割**:  
{gift_detail['building_material']}
                """)
            
            # マンスリー・ストラテジー詳細表示
            with st.expander("📖 マンスリー・ストラテジー詳細", expanded=False):
                stage_detail = get_month_stage_detail(st.session_state.month_heaven)
                zone_detail = get_month_zone_detail(st.session_state.month_earth)
                skill_detail = get_month_skill_detail(st.session_state.month_human)
                
                st.markdown(f"""
                ### 🌅 STAGE: {st.session_state.month_stage}
                **{stage_detail.get('english', '')}** - {stage_detail.get('theme', '')}
                
                {stage_detail.get('description', '')}
                
                ---
                
                ### 🎯 ZONE: {st.session_state.month_zone}
                **{zone_detail.get('english', '')}**
                
                **制約**: {zone_detail.get('constraint', '')}
                
                **攻略ヒント**: {zone_detail.get('hint', '')}
                
                ---
                
                ### ⚔️ SKILL: {st.session_state.month_skill}
                **{skill_detail.get('english', '')}**
                
                **効果**: {skill_detail.get('effect', '')}
                
                **発動アクション**: {skill_detail.get('action', '')}
                
                ---
                
                ### 💡 今月の戦略
                
                **STAGE（{stage_detail.get('theme', '')}）** のテーマの中で、  
**ZONE（{zone_detail.get('constraint', '')}）** という制約条件があります。  
この環境で **SKILL（{skill_detail.get('effect', '')}）** を発動することが、今月の最適な攻略法です。
                
                アトリに相談して、具体的なアドバイスをもらいましょう！
                """)
            
            # Phase 3: 獲得したギフト一覧
            with st.expander("🎁 獲得したギフト履歴", expanded=False):
                gifts = get_user_gifts(include_used=True)
                
                if not gifts:
                    st.info("まだギフトを獲得していません。月の課題を5回クリアすると、天運ギフトが完成します！")
                else:
                    st.markdown(f"**獲得したギフト総数**: {len(gifts)}個")
                    st.markdown("---")
                    
                    for gift in gifts:
                        gift_detail = YEARLY_GIFT[gift['gift_number']]
                        status_icon = "✅" if gift['used_for_rankup'] else "🎁"
                        status_text = "使用済み" if gift['used_for_rankup'] else "保管中"
                        
                        st.markdown(f"""
### {status_icon} {gift['gift_japanese']}

**英語名**: {gift['gift_name']}  
**獲得年**: {gift['acquired_year']}年（{gift['acquired_age']}歳）  
**ステータス**: {status_text}

**概要**:  
{gift_detail['overview']}

**効果**:
""")
                        for effect in gift_detail['effects']:
                            st.markdown(f"- {effect}")
                        
                        st.markdown(f"""
**建材としての役割**:  
{gift_detail['building_material']}
                        """)
                        
                        if gift['used_for_rankup']:
                            st.caption(f"🏰 {gift['used_at'][:10]} にランクアップで使用されました")
                        
                        st.markdown("---")
            
            
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
        
        # ========== 新しいチャットベースUI ==========
        
        # チャット履歴の表示
        st.markdown("### 💬 アトリとの対話")
        
        # メッセージ履歴を表示
        chat_container = st.container()
        with chat_container:
            for i, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    # ユーザーメッセージ
                    ap_cost = message.get('ap_cost', 0)
                    cost_display = f" **[-{ap_cost} AP]**" if ap_cost > 0 else ""
                    st.markdown(f"**🧑 あなた**{cost_display}")
                    st.markdown(f"> {message['content']}")
                    st.markdown("")
                else:
                    # アトリのメッセージ
                    st.markdown(f"**✨ アトリ**")
                    st.markdown(message['content'])
                    st.markdown("")
        
        # 最新メッセージへのスクロール（アンカー）
        if len(st.session_state.messages) > 0:
            # スクロールが必要な場合のみJavaScriptを実行
            should_scroll = st.session_state.get('should_scroll', False)
            
            st.markdown("""
            <div id="latest-message" style="height: 1px;"></div>
            """, unsafe_allow_html=True)
            
            if should_scroll:
                # スクロール実行（複数回実行で確実に）
                st.markdown("""
                <script>
                    // 複数のタイミングでスクロール実行
                    function scrollToLatest() {
                        const element = document.getElementById('latest-message');
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'end' });
                        }
                    }
                    
                    // 即座に実行
                    scrollToLatest();
                    
                    // 複数のタイミングで再実行
                    setTimeout(scrollToLatest, 50);
                    setTimeout(scrollToLatest, 100);
                    setTimeout(scrollToLatest, 200);
                    setTimeout(scrollToLatest, 300);
                    setTimeout(scrollToLatest, 500);
                    setTimeout(scrollToLatest, 800);
                    setTimeout(scrollToLatest, 1000);
                    
                    // DOMContentLoaded後にも実行
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', scrollToLatest);
                    }
                    
                    // load後にも実行
                    window.addEventListener('load', scrollToLatest);
                </script>
                """, unsafe_allow_html=True)
                
                # フラグをリセット
                st.session_state.should_scroll = False
        
        # YESボタンの表示（pending_questがある場合）
        if st.session_state.get('waiting_for_yes', False) and st.session_state.pending_quest:
            st.markdown("---")
            quest = st.session_state.pending_quest
            
            st.info(f"""
📜 **クエスト提案**

{quest.get('title', 'クエスト')}

このクエストを受注しますか？
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ YES（やります）", key="accept_quest", use_container_width=True, type="primary"):
                    # クエスト作成
                    if create_quest(
                        quest_type=quest['type'],
                        title=quest['title'],
                        description=quest['description'],
                        advice=quest['advice'],
                        initial_cost=quest['initial_cost']
                    ):
                        # システムメッセージを追加
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "🎯 **【QUEST START】**\n\nステータス：進行中\n期限：7日以内\n\n準備ができたら報告してください。行き詰まった場合は、いつでも途中相談できます（-1 AP）。"
                        })
                        
                        st.session_state.pending_quest = None
                        st.session_state.waiting_for_yes = False
                        st.session_state.should_scroll = True  # スクロールフラグ
                        save_to_supabase()
                        st.rerun()
            
            with col2:
                if st.button("❌ NO（やめておく）", key="decline_quest", use_container_width=True):
                    # クエストを辞退
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "承知しました。他に相談したいことがあれば、いつでもお気軽にどうぞ。"
                    })
                    
                    st.session_state.pending_quest = None
                    st.session_state.waiting_for_yes = False
                    st.session_state.should_scroll = True  # スクロールフラグ
                    save_to_supabase()
                    st.rerun()
        
        # アクティブなクエストがある場合の表示
        if st.session_state.active_quest and not st.session_state.get('show_report_form', False):
            st.markdown("---")
            quest = st.session_state.active_quest
            created_at = datetime.fromisoformat(quest['created_at'].replace('Z', '+00:00'))
            days_elapsed = (datetime.now(created_at.tzinfo) - created_at).days
            
            initial_cost = quest.get('initial_cost', quest.get('ap_cost', 1))
            followup_count = quest.get('followup_count', 0)
            total_cost = initial_cost + followup_count
            
            expected_reward = initial_cost * 2 if days_elapsed <= 7 else initial_cost
            net_profit = expected_reward - total_cost
            
            status_color = "#4CAF50" if days_elapsed <= 7 else "#FFA500"
            
            st.markdown(f"""
            <div class="quest-card" style="border-color: {status_color};">
                <div class="quest-title">📜 進行中のクエスト</div>
                <div class="quest-cost">{quest['title']}</div>
                <p style="color: #c0c0c0; font-size: 0.9rem; margin: 0.5rem 0;">
                    {'💬 相談' if quest['quest_type'] == 'consultation' else '🎯 月の課題'} | 経過: {days_elapsed}日 / 7日
                </p>
                <div style="background: rgba(10, 1, 24, 0.6); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
                    <div style="color: #c0c0c0; font-size: 0.85rem;">
                        📊 <strong>AP収支</strong><br>
                        初期コスト: -{initial_cost} AP<br>
                        途中相談: {followup_count}回 (-{followup_count} AP)<br>
                        総コスト: <strong>-{total_cost} AP</strong><br>
                        期待報酬: <strong>+{expected_reward} AP</strong><br>
                        実質収支: <strong style="color: {'#4CAF50' if net_profit >= 0 else '#FFA500'};">{'+' if net_profit >= 0 else ''}{net_profit} AP</strong>
                    </div>
                </div>
                <p style="color: {status_color}; margin-top: 0.5rem;">
                    {'⚡ 期限内報告で2倍APボーナス！' if days_elapsed <= 7 else '⚠️ 期限超過（AP報酬は等倍）'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📝 行動を報告する", use_container_width=True, type="primary"):
                st.session_state.show_report_form = True
                st.rerun()
        
        # チャット入力欄
        if not st.session_state.get('waiting_for_yes', False):
            st.markdown("---")
            
            # AP不足の警告
            required_ap = 2 if st.session_state.active_quest is None else 1
            if st.session_state.ap < required_ap:
                st.error(f"⚠️ APが不足しています（必要: {required_ap} AP、所持: {st.session_state.ap} AP）")
            
# チャット入力
user_input = st.chat_input(
    "相談内容を入力(-1 AP)/ 「月の課題」と入力(-2 AP)" if not st.session_state.active_quest else "途中相談する(-1 AP)...",
    disabled=st.session_state.ap < required_ap
)

if user_input:
    # スクロールフラグを事前に設定
    st.session_state.should_scroll = True
    
    # APコスト判定
    if st.session_state.active_quest:
        # 途中相談
        cost = 1
        consultation_type = 'followup'
    else:
        # 新規相談 or 月の課題
        if is_monthly_challenge_request(user_input):
            cost = 2
            consultation_type = 'monthly'
        else:
            cost = 1
            consultation_type = 'consultation'
    
    # AP消費
    st.session_state.ap -= cost
    st.session_state.last_ap_cost = cost
    
    # 途中相談の場合、カウントをインクリメント
    if consultation_type == 'followup':
        increment_followup_count(st.session_state.active_quest['id'])
    
    # ユーザーメッセージを追加(AP消費情報付き)
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "ap_cost": cost
    })
    
    # プレイヤーステータスを保存
    save_player_status()
    
    # AIに送信
    with st.spinner("🌌 宇宙と対話中..."):
        try:
            # システムプロンプトを取得
            system_prompt = get_system_prompt()
            
            # 会話履歴を構築
            conversation = []
            for msg in st.session_state.messages:
                conversation.append(f"{'User' if msg['role'] == 'user' else 'Atori'}: {msg['content']}")
            
            # プロンプト作成
            full_prompt = f"""{system_prompt}

【会話履歴】
{chr(10).join(conversation)}

Atori:"""
            
            # AI応答を生成
            response = model.generate_content(full_prompt)
            ai_response = response.text
            
            # メッセージを追加
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })
            
            # クエスト提案の検出
            if ("受注しますか" in ai_response or "実行しますか" in ai_response) and not st.session_state.active_quest:
                # pending_questを作成
                quest_type = 'monthly_challenge' if consultation_type == 'monthly' else 'consultation'
                quest_title = extract_quest_title(ai_response)
                
                st.session_state.pending_quest = {
                    'type': quest_type,
                    'title': quest_title,
                    'description': user_input,
                    'advice': ai_response,
                    'initial_cost': cost
                }
                st.session_state.waiting_for_yes = True
            
            # 保存
            save_to_supabase()
            
            # rerun 前に少し待機(JavaScriptが実行される時間を確保)
            time.sleep(0.1)
            
            st.rerun()
            
        except Exception as e:
            st.error(f"エラー: {e}")
            # エラー時はAP返還
            st.session_state.ap += cost
            st.session_state.messages.pop()  # 最後のメッセージを削除
            save_player_status()
        
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
                st.info("""
💡 **ZONE適合度について**

AIがあなたの報告内容を分析し、今月のZONE制約に適った行動かどうかを自動評価します。

- 🌟 **Excellent** (150 KP): ZONE制約を完璧に理解・実行
- ✨ **Great** (100 KP): ZONE制約をよく理解・実行
- 👍 **Good** (50 KP): ZONE制約を部分的に実行
- 💧 **Poor** (10 KP): ZONE制約を無視した行動

※自己評価は参考として記録されますが、KP付与はAI評価に基づきます
                """)
                zone_eval = st.selectbox(
                    "自己評価（参考）",
                    options=['Good', 'Great', 'Excellent'],
                    help="あなた自身の評価を記録します（AI評価とは別）"
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
                        
                        if result and result[0]:  # success
                            success, ap_reward, kp_reward, exp_reward, days, ai_eval = result
                            
                            # AI評価メッセージ
                            eval_message = ""
                            if ai_eval:
                                eval_emoji = {
                                    'Excellent': '🌟',
                                    'Great': '✨',
                                    'Good': '👍',
                                    'Poor': '💧'
                                }
                                eval_message = f"\n\n**AI評価**: {eval_emoji.get(ai_eval, '')} {ai_eval}"
                            
                            st.success(f"""
✅ 報告完了！{eval_message}

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
                            
                            st.session_state.should_scroll = True  # スクロールフラグ
                            save_to_supabase()
                            
                            st.rerun()
                    else:
                        st.warning("報告内容を入力してください")
        
        # ユーザー入力を無効化（クエスト必須）
        if st.session_state.active_quest:
            st.info("💡 クエスト進行中です。行動完了後に報告してください。")
        else:
            st.info("""
💡 **下の入力欄から相談してください**

- **相談（小クエスト）**: 自由に相談内容を入力 → **-1 AP**
- **月の課題（メイン）**: 「月の課題」と入力 → **-2 AP**
            """)

if __name__ == "__main__":
    main()
    
    # フッター
    st.markdown("""
    <footer style='text-align: center; padding: 2rem 0; color: #c0c0c0; font-size: 0.8rem; opacity: 0.7;'>
        © 2024 THE PLAYER - Powered by Google Gemini AI
    </footer>
    """, unsafe_allow_html=True)

