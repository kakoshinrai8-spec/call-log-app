import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread
from gspread.exceptions import WorksheetNotFound
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="電話対応ログ（熊本）", layout="wide")

# =========================
# 日本時間設定
# =========================
JST = ZoneInfo("Asia/Tokyo")

def today_jst():
    return datetime.now(JST).date()

def now_jst_str():
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

# =========================
# デザイン設定
# =========================
st.markdown("""
<style>
.stApp {
    background: #e8eef5 !important;
    color: #0f172a !important;
}

.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2rem;
    max-width: 1180px;
}

.app-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 48%, #334155 100%) !important;
    color: #ffffff !important;
    padding: 26px 30px;
    border-radius: 22px;
    margin-bottom: 22px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.25);
}

.app-header,
.app-header *,
.app-title,
.app-subtitle {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.app-title {
    font-size: 32px;
    font-weight: 900;
    letter-spacing: 0.03em;
}

.app-subtitle {
    font-size: 14px;
    opacity: 0.84;
    margin-top: 7px;
}

.staff-badge {
    display: inline-block;
    background: #e0e7ff !important;
    color: #312e81 !important;
    -webkit-text-fill-color: #312e81 !important;
    padding: 9px 16px;
    border-radius: 999px;
    font-weight: 800;
    margin-bottom: 14px;
    border: 1px solid #a5b4fc;
}

.section-card:empty {
    display: none !important;
}

.section-card {
    background: #ffffff !important;
    color: #0f172a !important;
    padding: 22px 24px;
    border-radius: 20px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.10);
    border: 1px solid #dbe3ef;
    margin-bottom: 22px;
}

.section-title {
    font-size: 20px;
    font-weight: 850;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    margin-bottom: 14px;
    border-left: 6px solid #2563eb;
    padding-left: 10px;
}

.help-text {
    font-size: 13px;
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    margin-top: -6px;
    margin-bottom: 14px;
}

label,
div[data-testid="stWidgetLabel"],
div[data-testid="stWidgetLabel"] *,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stRadio"] label,
div[data-testid="stTextArea"] label {
    font-weight: 800 !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    opacity: 1 !important;
}

/* 入力欄そのものとBaseWeb外枠の両方へ枠を指定する */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #f8fbff !important;
    border: 2.5px solid #475569 !important;
    border-radius: 12px !important;
    color: #0f172a !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.10) !important;
    outline: none !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stDateInput"] div[data-baseweb="input"],
div[data-testid="stNumberInput"] div[data-baseweb="input"] {
    background-color: #f8fbff !important;
    border: 2.5px solid #475569 !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.10) !important;
    overflow: hidden !important;
}

div[data-baseweb="select"] > div:hover,
div[data-baseweb="input"] > div:hover,
div[data-baseweb="textarea"] > div:hover,
div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover,
div[data-testid="stTextInput"] div[data-baseweb="input"]:hover,
div[data-testid="stDateInput"] div[data-baseweb="input"]:hover,
div[data-testid="stNumberInput"] div[data-baseweb="input"]:hover {
    border-color: #1e293b !important;
}

div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within,
div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within,
div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
div[data-testid="stDateInput"] div[data-baseweb="input"]:focus-within,
div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: #2563eb !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.20) !important;
}

input,
textarea,
div[data-baseweb="select"] input,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: #0f172a !important;
    background-color: #f8fbff !important;
    font-weight: 650 !important;
    -webkit-text-fill-color: #0f172a !important;
    opacity: 1 !important;
    outline: none !important;
    box-shadow: none !important;
}

input::placeholder,
textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #64748b !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[data-baseweb="menu"],
div[data-baseweb="menu"] *,
ul[role="listbox"],
ul[role="listbox"] *,
li[role="option"],
li[role="option"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    opacity: 1 !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
li[role="option"] {
    background-color: #ffffff !important;
}

li[role="option"]:hover,
div[data-baseweb="menu"] li:hover {
    background-color: #eaf1ff !important;
}

div[data-testid="stNumberInput"] input {
    color: #0f172a !important;
    background-color: #f8fbff !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-testid="stNumberInput"] div[data-baseweb="input"] > div {
    background-color: #f8fbff !important;
    border: 0 !important;
    border-radius: 10px !important;
}

div[data-testid="stNumberInput"] button {
    background-color: #dbe4ee !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border-left: 1px solid #94a3b8 !important;
    box-shadow: none !important;
}

div[data-testid="stNumberInput"] button svg,
div[data-testid="stNumberInput"] button svg path {
    color: #0f172a !important;
    fill: #0f172a !important;
    stroke: #0f172a !important;
}

div[data-testid="stNumberInput"] button:hover {
    background-color: #cbd5e1 !important;
}

div[data-testid="stDateInput"] div[data-baseweb="input"] > div {
    background-color: #f8fbff !important;
    border: 0 !important;
}

div[data-baseweb="calendar"],
div[data-baseweb="calendar"] *,
div[data-baseweb="datepicker"],
div[data-baseweb="datepicker"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-testid="stRadio"] > div {
    gap: 12px;
}

div[data-testid="stRadio"] label {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    padding: 8px 12px !important;
    border-radius: 999px !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-testid="stRadio"] *,
div[role="radiogroup"],
div[role="radiogroup"] *,
div[data-baseweb="radio"],
div[data-baseweb="radio"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    opacity: 1 !important;
}

.stButton > button[kind="primary"] {
    border-radius: 14px;
    font-weight: 900;
    min-height: 44px;
    border: none !important;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.28);
}

.stButton > button[kind="primary"] *,
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    color: #ffffff !important;
    border: none !important;
    transform: translateY(-1px);
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.34);
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0);
}

.stButton > button[kind="secondary"] {
    border-radius: 12px;
    font-weight: 800;
    min-height: 40px;
    border: none !important;
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    box-shadow: 0 6px 14px rgba(220, 38, 38, 0.25);
}

.stButton > button[kind="secondary"] *,
.stButton > button[kind="secondary"] p,
.stButton > button[kind="secondary"] span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
    color: #ffffff !important;
    border: none !important;
}

.log-row {
    background: #ffffff;
    border: 1px solid #dbe3ef;
    border-left: 6px solid #2563eb;
    border-radius: 16px;
    padding: 13px 15px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}

.log-main {
    font-weight: 850;
    color: #0f172a;
    font-size: 15px;
}

.log-sub {
    font-size: 13px;
    color: #475569;
    margin-top: 5px;
    line-height: 1.5;
}

.total-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    border-radius: 20px;
    padding: 20px 24px;
    margin-top: 16px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.22);
}

.total-box,
.total-box * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.total-label {
    font-size: 13px;
    opacity: 0.78;
}

.total-value {
    font-size: 28px;
    font-weight: 900;
    margin-top: 5px;
}

hr {
    margin-top: 1.2rem;
    margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# タイトル
# =========================
st.markdown("""
<div class="app-header">
    <div class="app-title">📞 電話対応ログ</div>
    <div class="app-subtitle">熊本営業所 / 受電記録管理</div>
</div>
""", unsafe_allow_html=True)

# =========================
# 熊本版設定
# =========================
WORKSHEET_NAME = "logs_熊本"

STAFF_OPTIONS = ["實取", "濵田", "岩木", "木下", "松本"]

AREA_OPTIONS = ["熊本", "大分"]

PARTNER_OPTIONS_BY_AREA = {
    "大分": [
        "得意先",
        "岡崎",
        "小薮",
        "美濃",
        "鶴岡",
        "椎葉",
        "細水",
        "中野",
        "三井所",
        "倉庫配送",
        "内線",
        "その他"
    ],
    "熊本": [
        "得意先",
        "佐々木(良)",
        "松岡",
        "吉澤",
        "秋山",
        "斎藤",
        "桑原",
        "古賀",
        "一村",
        "遠藤",
        "北島",
        "岡崎",
        "小薮",
        "美濃",
        "鶴岡",
        "椎葉",
        "細水",
        "中野",
        "三井所",
        "佐々木(惇)",
        "倉庫配送",
        "内線",
        "その他"
    ]
}

CATEGORY_OPTIONS = [
    "注文",
    "商品問合せ",
    "納期確認",
    "見積依頼",
    "返品関連",
    "伝票確認",
    "在庫確認",
    "請求書関連",
    "その他"
]

HEADER_COLUMNS = ["日付", "番号", "担当者", "エリア", "相手", "対応時間（分）", "用件", "備考", "登録日時"]

# =========================
# 接続キャッシュ
# =========================
@st.cache_resource
def get_worksheet():
    creds_dict = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key("1yjuuTEPG8rsIr8Wctl6vtFmsU0cJy0rmsbvDnvpm934")

    try:
        ws = sheet.worksheet(WORKSHEET_NAME)
    except WorksheetNotFound:
        ws = sheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=20)
        ws.append_row(HEADER_COLUMNS, value_input_option="USER_ENTERED")

    return ws

# =========================
# データ取得キャッシュ
# =========================
@st.cache_data(ttl=15)
def load_data():
    ws = get_worksheet()
    data = ws.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=HEADER_COLUMNS)

    if "用件" not in df.columns and "要件" in df.columns:
        df["用件"] = df["要件"]

    if "用件" in df.columns and "要件" in df.columns:
        df["用件"] = df["用件"].replace("", pd.NA).fillna(df["要件"])

    for col in HEADER_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df["対応時間（分）"] = pd.to_numeric(df["対応時間（分）"], errors="coerce").fillna(0)
    df["番号"] = pd.to_numeric(df["番号"], errors="coerce")

    return df

def reset_input_fields():
    st.session_state["input_mode"] = "通常入力"
    st.session_state["input_selected_date"] = today_jst()
    st.session_state["input_area"] = AREA_OPTIONS[0]
    st.session_state["input_partner"] = PARTNER_OPTIONS_BY_AREA[AREA_OPTIONS[0]][0]
    st.session_state["input_minutes"] = 1
    st.session_state["input_count"] = 1
    st.session_state["input_category"] = CATEGORY_OPTIONS[0]
    st.session_state["input_note"] = ""

ws = get_worksheet()

today = str(today_jst())

if "last_date" not in st.session_state:
    st.session_state.last_date = today

if st.session_state.last_date != today:
    st.session_state.last_date = today
    load_data.clear()
    st.rerun()

if "staff" not in st.session_state:
    st.session_state.staff = ""

if st.session_state.staff == "":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">担当者選択</div>', unsafe_allow_html=True)
    staff = st.selectbox("あなたの名前を選択", STAFF_OPTIONS)

    if st.button("決定", type="primary", use_container_width=True):
        st.session_state.staff = staff
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

staff = st.session_state.staff
st.markdown(f'<div class="staff-badge">担当者：{staff}</div>', unsafe_allow_html=True)

df = load_data()

if "reset_form" not in st.session_state:
    st.session_state["reset_form"] = False

if st.session_state["reset_form"]:
    reset_input_fields()
    st.session_state["reset_form"] = False

if "input_mode" not in st.session_state:
    st.session_state["input_mode"] = "通常入力"
if "input_selected_date" not in st.session_state:
    st.session_state["input_selected_date"] = today_jst()
if "input_area" not in st.session_state:
    st.session_state["input_area"] = AREA_OPTIONS[0]
if "input_partner" not in st.session_state:
    st.session_state["input_partner"] = PARTNER_OPTIONS_BY_AREA[AREA_OPTIONS[0]][0]
if "input_minutes" not in st.session_state:
    st.session_state["input_minutes"] = 1
if "input_count" not in st.session_state:
    st.session_state["input_count"] = 1
if "input_category" not in st.session_state:
    st.session_state["input_category"] = CATEGORY_OPTIONS[0]
if "input_note" not in st.session_state:
    st.session_state["input_note"] = ""

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">入力</div>', unsafe_allow_html=True)
st.markdown('<div class="help-text">通常入力は本日分、過去入力は日付を指定して登録できます。</div>', unsafe_allow_html=True)

mode = st.radio("入力モード", ["通常入力", "過去入力"], horizontal=True, key="input_mode")

if mode == "通常入力":
    selected_date = today_jst()
    st.session_state["input_selected_date"] = selected_date
else:
    selected_date = st.date_input("入力日付", value=st.session_state["input_selected_date"], key="input_selected_date")

col1, col2 = st.columns(2)

with col1:
    area = st.selectbox("エリア", AREA_OPTIONS, key="input_area")

    current_partner_options = PARTNER_OPTIONS_BY_AREA[area]
    if st.session_state["input_partner"] not in current_partner_options:
        st.session_state["input_partner"] = current_partner_options[0]

    partner = st.selectbox("相手", current_partner_options, key="input_partner")
    minutes = st.number_input("対応時間（分）", min_value=1, step=1, key="input_minutes")
    count = st.number_input("件数", min_value=1, step=1, key="input_count")

with col2:
    category = st.selectbox("用件", CATEGORY_OPTIONS, key="input_category")
    note = st.text_input("備考", key="input_note")

message_area = st.empty()

if st.button("＋ 追加する", type="primary", use_container_width=True):
    max_number = pd.to_numeric(df["番号"], errors="coerce").max()
    start_number = int(max_number) + 1 if pd.notna(max_number) else 1

    created_at = now_jst_str()

    rows_to_add = []
    for i in range(int(count)):
        rows_to_add.append([
            selected_date.strftime("%Y-%m-%d"),
            start_number + i,
            str(staff),
            str(area),
            str(partner),
            int(minutes),
            str(category),
            note if note else "",
            created_at
        ])

    ws.append_rows(rows_to_add, value_input_option="USER_ENTERED")

    load_data.clear()
    st.session_state["added"] = True
    st.session_state["added_count"] = int(count)
    st.session_state["reset_form"] = True
    st.rerun()

if st.session_state.get("added"):
    added_count = st.session_state.get("added_count", 1)
    message_area.success(f"✅ {added_count}件追加しました")
    st.session_state["added"] = False
    st.session_state["added_count"] = 1

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">履歴</div>', unsafe_allow_html=True)

view_date = st.date_input("表示する日付", value=today_jst(), key="view_date")
view_date_str = str(view_date)

df_view = df[df["日付"] == view_date_str]

if not df_view.empty:
    df_display = df_view.sort_index(ascending=False).reset_index()

    with st.container(height=300):
        for i, row in df_display.iterrows():
            col1, col2 = st.columns([9, 1])

            with col1:
                registered_at = row["登録日時"] if pd.notna(row["登録日時"]) else ""
                note_text = row["備考"] if pd.notna(row["備考"]) and str(row["備考"]).strip() != "" else "なし"

                st.markdown(
                    f"""
                    <div class="log-row">
                        <div class="log-main">
                            {row['日付']} ｜ {row['担当者']} ｜ {row['エリア']} → {row['相手']} ｜ {int(row['対応時間（分）'])}分
                        </div>
                        <div class="log-sub">
                            用件：{row['用件']}　｜　備考：{note_text}　｜　登録日時：{registered_at}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("削除", key=f"del_{i}"):
                    ws.delete_rows(int(row["index"]) + 2)
                    load_data.clear()
                    st.rerun()

    total = int(df_view["対応時間（分）"].sum())
    h = total // 60
    m = total % 60

    st.markdown(
        f"""
        <div class="total-box">
            <div class="total-label">表示日の合計対応時間</div>
            <div class="total-value">{total}分（{h}時間{m}分）</div>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.info("この日のデータはありません")

st.markdown('</div>', unsafe_allow_html=True)
