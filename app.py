import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date
from zoneinfo import ZoneInfo
import calendar
import gspread
from gspread.exceptions import WorksheetNotFound
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="電話対応ログ（大分）", layout="wide")

# =========================
# 日本時間設定
# =========================
JST = ZoneInfo("Asia/Tokyo")

def today_jst():
    return datetime.now(JST).date()

def now_jst_str():
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

def month_start_end(target_date):
    first_day = date(target_date.year, target_date.month, 1)
    last_day_num = calendar.monthrange(target_date.year, target_date.month)[1]
    last_day = date(target_date.year, target_date.month, last_day_num)
    return first_day, last_day

# =========================
# デザイン設定
# =========================
st.markdown("""
<style>
.stApp {
    background: #eef2f7 !important;
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

.section-card {
    background: #ffffff !important;
    color: #0f172a !important;
    padding: 22px 24px;
    border-radius: 20px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.10);
    border: 1px solid #dbe3ef;
    margin-bottom: 22px;
}

.section-card * {
    color: #0f172a;
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

.metric-card {
    background: #f8fafc !important;
    border: 1px solid #dbe3ef;
    border-radius: 18px;
    padding: 18px 18px;
    box-shadow: 0 5px 14px rgba(15, 23, 42, 0.06);
    min-height: 104px;
}

.metric-label {
    font-size: 13px;
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    font-weight: 800;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 28px;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-weight: 950;
    line-height: 1.25;
}

.metric-sub {
    font-size: 12px;
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    margin-top: 4px;
}

.admin-notice {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe;
    border-left: 6px solid #2563eb;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 16px;
    font-size: 14px;
    font-weight: 700;
}

html,
body,
.stApp,
div[data-testid="stAppViewContainer"],
div[data-testid="stMarkdownContainer"],
div[data-testid="stMarkdownContainer"] *,
div[data-testid="stWidgetLabel"],
div[data-testid="stWidgetLabel"] * {
    color: #0f172a !important;
}

label,
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

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #f8fafc !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    color: #0f172a !important;
    box-shadow: none !important;
    outline: none !important;
}

div[data-baseweb="select"] > div:hover,
div[data-baseweb="input"] > div:hover,
div[data-baseweb="textarea"] > div:hover {
    border-color: #2563eb !important;
}

input,
textarea,
div[data-baseweb="select"] input,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: #0f172a !important;
    background-color: #f8fafc !important;
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

input,
textarea,
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    border-color: #cbd5e1 !important;
    outline: none !important;
    box-shadow: none !important;
}

input:focus,
textarea:focus,
div[data-baseweb="select"] > div:focus,
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: #2563eb !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18) !important;
}

div[data-baseweb="select"],
div[data-baseweb="select"] *,
div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[data-baseweb="menu"],
div[data-baseweb="menu"] *,
ul[role="listbox"],
ul[role="listbox"] *,
li[role="option"],
li[role="option"] * {
    color: #0f172a !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #0f172a !important;
    opacity: 1 !important;
}

li[role="option"]:hover,
div[data-baseweb="menu"] li:hover {
    background-color: #eaf1ff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-testid="stRadio"] > div {
    gap: 12px;
}

div[data-testid="stRadio"] label {
    background: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    padding: 8px 12px !important;
    border-radius: 999px !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    opacity: 1 !important;
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

div[data-testid="stNumberInput"] {
    color: #0f172a !important;
}

div[data-testid="stNumberInput"] input {
    color: #0f172a !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #0f172a !important;
    opacity: 1 !important;
    outline: none !important;
    box-shadow: none !important;
}

div[data-testid="stNumberInput"] div[data-baseweb="input"] > div {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    color: #0f172a !important;
    outline: none !important;
    box-shadow: none !important;
}

div[data-testid="stNumberInput"] div[data-baseweb="input"] > div:focus-within {
    border-color: #2563eb !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18) !important;
}

div[data-testid="stNumberInput"] button {
    background-color: #e2e8f0 !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
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
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-testid="stNumberInput"] button:disabled {
    background-color: #f1f5f9 !important;
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
    border: 1px solid #cbd5e1 !important;
}

div[data-testid="stDateInput"] div[data-baseweb="input"] > div {
    border-color: #cbd5e1 !important;
    outline: none !important;
    box-shadow: none !important;
}

div[data-testid="stDateInput"] div[data-baseweb="input"] > div:focus-within {
    border-color: #2563eb !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18) !important;
}

div[data-baseweb="calendar"],
div[data-baseweb="calendar"] *,
div[data-baseweb="datepicker"],
div[data-baseweb="datepicker"] * {
    color: #0f172a !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #0f172a !important;
}

[disabled],
[aria-disabled="true"] {
    color: #475569 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #475569 !important;
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
    -webkit-text-fill-color: #ffffff !important;
    border: none !important;
    transform: translateY(-1px);
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.34);
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0px);
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
    -webkit-text-fill-color: #ffffff !important;
    border: none !important;
}

.log-row {
    background: #ffffff !important;
    border: 1px solid #dbe3ef;
    border-left: 6px solid #2563eb;
    border-radius: 16px;
    padding: 13px 15px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}

.log-main {
    font-weight: 850;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-size: 15px;
}

.log-sub {
    font-size: 13px;
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    margin-top: 5px;
    line-height: 1.5;
}

.total-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    color: #ffffff !important;
    border-radius: 20px;
    padding: 20px 24px;
    margin-top: 16px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.22);
}

.total-box,
.total-box *,
.total-label,
.total-value {
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

.total-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

@media (max-width: 700px) {
    .total-grid {
        grid-template-columns: 1fr;
    }
}

hr {
    margin-top: 1.2rem;
    margin-bottom: 1.2rem;
}

.stAlert,
.stAlert *,
div[data-testid="stAlert"],
div[data-testid="stAlert"] * {
    color: #0f172a !important;
    opacity: 1 !important;
}

div[role="dialog"],
div[role="dialog"] * {
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
}

div[role="dialog"] button,
div[role="dialog"] button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# タイトル
# =========================
st.markdown("""
<div class="app-header">
    <div class="app-title">📞 電話対応ログ</div>
    <div class="app-subtitle">大分営業所 / 受電記録管理</div>
</div>
""", unsafe_allow_html=True)

# =========================
# 大分版設定
# =========================
SPREADSHEET_KEY = "1yjuuTEPG8rsIr8Wctl6vtFmsU0cJy0rmsbvDnvpm934"

WORKSHEET_NAME = "logs"
KUMAMOTO_WORKSHEET_NAME = "logs_熊本"

STAFF_OPTIONS = ["吉田", "伊藤", "高木", "加藤", "加古", "長谷川"]

AREA_OPTIONS = ["大分", "熊本"]

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
        "佐々木",
        "松岡",
        "吉澤",
        "秋山",
        "斎藤",
        "桑原",
        "古賀",
        "一村",
        "遠藤",
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
def get_spreadsheet():
    creds_dict = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_KEY)

    return sheet

@st.cache_resource
def get_worksheet():
    sheet = get_spreadsheet()

    try:
        ws = sheet.worksheet(WORKSHEET_NAME)
    except WorksheetNotFound:
        ws = sheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=20)
        ws.append_row(HEADER_COLUMNS, value_input_option="USER_ENTERED")

    return ws

# =========================
# データ整形
# =========================
def normalize_log_df(df, source_name):
    if df.empty:
        df = pd.DataFrame(columns=HEADER_COLUMNS)

    if "用件" not in df.columns and "要件" in df.columns:
        df["用件"] = df["要件"]

    if "用件" in df.columns and "要件" in df.columns:
        df["用件"] = df["用件"].replace("", pd.NA).fillna(df["要件"])

    for col in HEADER_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[HEADER_COLUMNS].copy()

    df["対応時間（分）"] = pd.to_numeric(df["対応時間（分）"], errors="coerce").fillna(0).astype(int)
    df["番号"] = pd.to_numeric(df["番号"], errors="coerce")
    df["日付変換"] = pd.to_datetime(df["日付"], errors="coerce")
    df["受付側"] = source_name

    text_cols = ["担当者", "エリア", "相手", "用件", "備考", "登録日時"]
    for col in text_cols:
        df[col] = df[col].astype(str).replace("nan", "")

    return df

# =========================
# データ取得キャッシュ
# =========================
@st.cache_data(ttl=15)
def load_data():
    ws = get_worksheet()
    data = ws.get_all_records()
    df = pd.DataFrame(data)

    return normalize_log_df(df, "大分")

@st.cache_data(ttl=60)
def load_log_sheet_for_admin(worksheet_name, source_name):
    sheet = get_spreadsheet()

    try:
        ws = sheet.worksheet(worksheet_name)
    except WorksheetNotFound:
        return pd.DataFrame(columns=HEADER_COLUMNS + ["日付変換", "受付側"])

    data = ws.get_all_records()
    df = pd.DataFrame(data)

    return normalize_log_df(df, source_name)

@st.cache_data(ttl=60)
def load_optional_sheet(worksheet_name):
    sheet = get_spreadsheet()

    try:
        ws = sheet.worksheet(worksheet_name)
    except WorksheetNotFound:
        return pd.DataFrame()

    values = ws.get_all_values()

    if not values:
        return pd.DataFrame()

    max_cols = max(len(row) for row in values)
    normalized_values = []

    for row in values:
        normalized_values.append(row + [""] * (max_cols - len(row)))

    df = pd.DataFrame(normalized_values)

    return df

# =========================
# 共通表示部品
# =========================
def metric_card(label, value, sub_text=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def safe_dataframe(df, use_container_width=True, height=None):
    if df is None or df.empty:
        st.info("表示できるデータがありません")
    else:
        if height is None:
            st.dataframe(df, use_container_width=use_container_width)
        else:
            st.dataframe(df, use_container_width=use_container_width, height=height)

def format_minutes(total_minutes):
    total_minutes = int(total_minutes)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{total_minutes:,}分（{h}時間{m}分）"

def horizontal_bar_chart(df, label_col, value_col, title="", top_n=20):
    if df is None or df.empty:
        st.info("表示できるデータがありません")
        return

    chart_df = df[[label_col, value_col]].copy()
    chart_df[value_col] = pd.to_numeric(chart_df[value_col], errors="coerce").fillna(0)
    chart_df = chart_df.sort_values(value_col, ascending=False).head(top_n)

    if chart_df.empty:
        st.info("表示できるデータがありません")
        return

    height = max(260, min(720, 34 * len(chart_df) + 70))

    base = alt.Chart(chart_df).encode(
        y=alt.Y(
            f"{label_col}:N",
            sort=alt.SortField(field=value_col, order="descending"),
            title=None,
            axis=alt.Axis(labelLimit=220)
        ),
        x=alt.X(
            f"{value_col}:Q",
            title=value_col,
            axis=alt.Axis(format=",")
        ),
        tooltip=[
            alt.Tooltip(f"{label_col}:N", title=label_col),
            alt.Tooltip(f"{value_col}:Q", title=value_col, format=",")
        ]
    )

    bars = base.mark_bar(cornerRadiusEnd=4)

    text = base.mark_text(
        align="left",
        baseline="middle",
        dx=4,
        fontSize=12
    ).encode(
        text=alt.Text(f"{value_col}:Q", format=",")
    )

    chart = (bars + text).properties(
        title=title,
        height=height
    ).configure_title(
        fontSize=16,
        anchor="start"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )

    st.altair_chart(chart, use_container_width=True)

def reset_input_fields():
    st.session_state["input_mode"] = "通常入力"
    st.session_state["input_selected_date"] = today_jst()
    st.session_state["input_area"] = AREA_OPTIONS[0]
    st.session_state["input_partner"] = PARTNER_OPTIONS_BY_AREA[AREA_OPTIONS[0]][0]
    st.session_state["input_minutes"] = 1
    st.session_state["input_count"] = 1
    st.session_state["input_category"] = CATEGORY_OPTIONS[0]
    st.session_state["input_note"] = ""

# =========================
# 管理者集計画面
# =========================
def render_admin_dashboard():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">管理者集計</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="admin-notice">この画面を開いた時点で、logs と logs_熊本 を読み込んで集計します。</div>',
        unsafe_allow_html=True
    )

    today_for_month = today_jst()

    year_options = list(range(today_for_month.year - 2, today_for_month.year + 1))
    month_options = list(range(1, 13))

    col_y, col_m = st.columns(2)

    with col_y:
        selected_year = st.selectbox(
            "表示対象年",
            year_options,
            index=year_options.index(today_for_month.year)
        )

    with col_m:
        selected_month = st.selectbox(
            "表示対象月",
            month_options,
            index=today_for_month.month - 1,
            format_func=lambda x: f"{x}月"
        )

    target_month_date = date(selected_year, selected_month, 1)
    month_start, month_end = month_start_end(target_month_date)

    st.caption(
        f"対象期間：{month_start.strftime('%Y-%m-%d')} ～ {month_end.strftime('%Y-%m-%d')} / "
        f"最終表示時刻：{now_jst_str()}"
    )

    df_oita = load_log_sheet_for_admin(WORKSHEET_NAME, "大分")
    df_kumamoto = load_log_sheet_for_admin(KUMAMOTO_WORKSHEET_NAME, "熊本")

    df_all = pd.concat([df_oita, df_kumamoto], ignore_index=True)

    if df_all.empty:
        st.info("集計対象のデータがありません")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    df_all = df_all.dropna(subset=["日付変換"]).copy()

    df_month = df_all[
        (df_all["日付変換"].dt.date >= month_start) &
        (df_all["日付変換"].dt.date <= month_end)
    ].copy()

    if df_month.empty:
        st.info("対象月のデータがありません")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    df_today = df_all[df_all["日付変換"].dt.date == today_jst()].copy()

    admin_menu = st.radio(
        "表示内容",
        ["概要", "担当者", "エリア分析", "相手別分析", "用件分析", "月次サマリー", "詳細表"],
        horizontal=True
    )

    if admin_menu == "概要":
        st.markdown('<div class="section-title">概要</div>', unsafe_allow_html=True)

        today_count = len(df_today)
        today_minutes = int(df_today["対応時間（分）"].sum()) if not df_today.empty else 0
        month_count = len(df_month)
        month_minutes = int(df_month["対応時間（分）"].sum())

        oita_count = len(df_month[df_month["受付側"] == "大分"])
        kumamoto_count = len(df_month[df_month["受付側"] == "熊本"])

        oita_minutes = int(df_month[df_month["受付側"] == "大分"]["対応時間（分）"].sum())
        kumamoto_minutes = int(df_month[df_month["受付側"] == "熊本"]["対応時間（分）"].sum())

        oita_to_kumamoto = df_month[
            (df_month["受付側"] == "大分") &
            (df_month["エリア"] == "熊本")
        ]

        oita_to_kumamoto_count = len(oita_to_kumamoto)
        oita_to_kumamoto_minutes = int(oita_to_kumamoto["対応時間（分）"].sum())

        oita_receive_total = len(df_month[df_month["受付側"] == "大分"])
        oita_kumamoto_rate = (oita_to_kumamoto_count / oita_receive_total * 100) if oita_receive_total > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            metric_card("本日 総件数", f"{today_count:,}件", "今日登録された全体件数")
        with col2:
            metric_card("本日 総分数", format_minutes(today_minutes), "今日の対応時間合計")
        with col3:
            metric_card("今月 総件数", f"{month_count:,}件", "大分＋熊本の合計")
        with col4:
            metric_card("今月 総分数", format_minutes(month_minutes), "大分＋熊本の合計")

        st.write("")

        col5, col6, col7, col8 = st.columns(4)

        with col5:
            metric_card("大分受付 件数", f"{oita_count:,}件", format_minutes(oita_minutes))
        with col6:
            metric_card("熊本受付 件数", f"{kumamoto_count:,}件", format_minutes(kumamoto_minutes))
        with col7:
            metric_card("大分受付の熊本エリア件数", f"{oita_to_kumamoto_count:,}件", format_minutes(oita_to_kumamoto_minutes))
        with col8:
            metric_card("大分受付の熊本エリア比率", f"{oita_kumamoto_rate:.1f}%", "大分受付内の熊本エリア割合")

        st.write("")
        st.markdown('<div class="section-title">日別推移</div>', unsafe_allow_html=True)

        daily = (
            df_month
            .groupby(df_month["日付変換"].dt.strftime("%Y-%m-%d"))
            .agg(
                件数=("日付", "count"),
                分数=("対応時間（分）", "sum")
            )
            .reset_index()
        )

        daily = daily.rename(columns={"日付変換": "日付"})
        if "日付" not in daily.columns:
            daily = daily.rename(columns={daily.columns[0]: "日付"})

        daily = daily[["日付", "件数", "分数"]]
        chart_df = daily.set_index("日付")

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("日別 件数")
            st.line_chart(chart_df["件数"])

        with col_b:
            st.subheader("日別 分数")
            st.line_chart(chart_df["分数"])

        with st.expander("日別集計表を見る"):
            safe_dataframe(daily)

    elif admin_menu == "担当者":
        st.markdown('<div class="section-title">担当者別集計</div>', unsafe_allow_html=True)

        staff_summary = (
            df_month
            .groupby("担当者")
            .agg(
                件数=("日付", "count"),
                分数=("対応時間（分）", "sum")
            )
            .reset_index()
            .sort_values(["件数", "分数"], ascending=False)
        )

        staff_summary["平均分数"] = (staff_summary["分数"] / staff_summary["件数"]).round(1)

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("担当者別 件数")
            horizontal_bar_chart(staff_summary, "担当者", "件数", "担当者別 件数", top_n=20)

        with col_b:
            st.subheader("担当者別 分数")
            horizontal_bar_chart(staff_summary, "担当者", "分数", "担当者別 分数", top_n=20)

        st.subheader("担当者別一覧")
        safe_dataframe(staff_summary)

        st.markdown('<div class="section-title">受付側別 × 担当者</div>', unsafe_allow_html=True)

        staff_by_source = (
            df_month
            .groupby(["受付側", "担当者"])
            .agg(
                件数=("日付", "count"),
                分数=("対応時間（分）", "sum")
            )
            .reset_index()
            .sort_values(["受付側", "件数"], ascending=[True, False])
        )

        safe_dataframe(staff_by_source)

    elif admin_menu == "エリア分析":
        st.markdown('<div class="section-title">エリア分析</div>', unsafe_allow_html=True)

        area_cross_count = pd.pivot_table(
            df_month,
            index="受付側",
            columns="エリア",
            values="日付",
            aggfunc="count",
            fill_value=0,
            margins=True,
            margins_name="合計"
        )

        area_cross_minutes = pd.pivot_table(
            df_month,
            index="受付側",
            columns="エリア",
            values="対応時間（分）",
            aggfunc="sum",
            fill_value=0,
            margins=True,
            margins_name="合計"
        )

        oita_to_kumamoto = df_month[
            (df_month["受付側"] == "大分") &
            (df_month["エリア"] == "熊本")
        ]

        oita_to_kumamoto_count = len(oita_to_kumamoto)
        oita_to_kumamoto_minutes = int(oita_to_kumamoto["対応時間（分）"].sum())

        oita_receive_total = len(df_month[df_month["受付側"] == "大分"])
        oita_kumamoto_rate = (oita_to_kumamoto_count / oita_receive_total * 100) if oita_receive_total > 0 else 0

        col1, col2, col3 = st.columns(3)

        with col1:
            metric_card("大分が受けた熊本エリア件数", f"{oita_to_kumamoto_count:,}件", "受付側：大分 / エリア：熊本")
        with col2:
            metric_card("大分が受けた熊本エリア分数", format_minutes(oita_to_kumamoto_minutes), "受付側：大分 / エリア：熊本")
        with col3:
            metric_card("大分受付内の熊本エリア比率", f"{oita_kumamoto_rate:.1f}%", "大分受付のうち熊本エリア分")

        st.subheader("受付側 × 相手エリア：件数")
        safe_dataframe(area_cross_count.reset_index())

        st.subheader("受付側 × 相手エリア：分数")
        safe_dataframe(area_cross_minutes.reset_index())

        st.subheader("相手エリア別 件数・分数")
        area_summary = (
            df_month
            .groupby("エリア")
            .agg(
                件数=("日付", "count"),
                分数=("対応時間（分）", "sum")
            )
            .reset_index()
            .sort_values("件数", ascending=False)
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("相手エリア別 件数")
            horizontal_bar_chart(area_summary, "エリア", "件数", "相手エリア別 件数", top_n=20)

        with col_b:
            st.subheader("相手エリア別 分数")
            horizontal_bar_chart(area_summary, "エリア", "分数", "相手エリア別 分数", top_n=20)

        st.subheader("相手エリア別一覧")
        safe_dataframe(area_summary)

    elif admin_menu == "相手別分析":
        st.markdown('<div class="section-title">相手別分析</div>', unsafe_allow_html=True)

        partner_summary = (
            df_month
            .groupby("相手")
            .agg(
                件数=("日付", "count"),
                分数=("対応時間（分）", "sum")
            )
            .reset_index()
            .sort_values(["件数", "分数"], ascending=False)
        )

        partner_summary["平均分数"] = (partner_summary["分数"] / partner_summary["件数"]).round(1)

        st.markdown('<div class="section-title">相手別ランキング</div>', unsafe_allow_html=True)

        count_ranking = (
            partner_summary
            .sort_values(["件数", "分数"], ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
        count_ranking.insert(0, "順位", count_ranking.index + 1)

        minutes_ranking = (
            partner_summary
            .sort_values(["分数", "件数"], ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
        minutes_ranking.insert(0, "順位", minutes_ranking.index + 1)

        col_rank1, col_rank2 = st.columns(2)

        with col_rank1:
            st.subheader("件数ランキング TOP10")
            safe_dataframe(count_ranking[["順位", "相手", "件数", "分数", "平均分数"]])

        with col_rank2:
            st.subheader("分数ランキング TOP10")
            safe_dataframe(minutes_ranking[["順位", "相手", "分数", "件数", "平均分数"]])

        st.write("")
        st.markdown('<div class="section-title">相手別グラフ</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("相手別 件数")
            horizontal_bar_chart(partner_summary, "相手", "件数", "相手別 件数 上位20", top_n=20)

        with col_b:
            st.subheader("相手別 分数")
            horizontal_bar_chart(partner_summary, "相手", "分数", "相手別 分数 上位20", top_n=20)

        st.subheader("相手別一覧")
        safe_dataframe(partner_summary)

        st.markdown('<div class="section-title">受付側 × 相手</div>', unsafe_allow_html=True)

        source_partner_count = pd.pivot_table(
            df_month,
            index="相手",
            columns="受付側",
            values="日付",
            aggfunc="count",
            fill_value=0,
            margins=True,
            margins_name="合計"
        )

        st.subheader("受付側 × 相手：件数")
        safe_dataframe(source_partner_count.reset_index())

        source_partner_minutes = pd.pivot_table(
            df_month,
            index="相手",
            columns="受付側",
            values="対応時間（分）",
            aggfunc="sum",
            fill_value=0,
            margins=True,
            margins_name="合計"
        )

        st.subheader("受付側 × 相手：分数")
        safe_dataframe(source_partner_minutes.reset_index())

        st.markdown('<div class="section-title">相手 × 用件</div>', unsafe_allow_html=True)

        partner_category = pd.pivot_table(
            df_month,
            index="相手",
            columns="用件",
            values="日付",
            aggfunc="count",
            fill_value=0,
            margins=True,
            margins_name="合計"
        )

        st.subheader("相手 × 用件：件数")
        safe_dataframe(partner_category.reset_index())

    elif admin_menu == "用件分析":
        st.markdown('<div class="section-title">用件分析</div>', unsafe_allow_html=True)

        category_summary = (
            df_month
            .groupby("用件")
            .agg(
                件数=("日付", "count"),
                分数=("対応時間（分）", "sum")
            )
            .reset_index()
            .sort_values("件数", ascending=False)
        )

        category_summary["平均分数"] = (category_summary["分数"] / category_summary["件数"]).round(1)

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("用件別 件数")
            horizontal_bar_chart(category_summary, "用件", "件数", "用件別 件数", top_n=20)

        with col_b:
            st.subheader("用件別 分数")
            horizontal_bar_chart(category_summary, "用件", "分数", "用件別 分数", top_n=20)

        st.subheader("用件別一覧")
        safe_dataframe(category_summary)

        st.markdown('<div class="section-title">受付側 × 用件</div>', unsafe_allow_html=True)

        source_category = pd.pivot_table(
            df_month,
            index="用件",
            columns="受付側",
            values="日付",
            aggfunc="count",
            fill_value=0,
            margins=True,
            margins_name="合計"
        )

        safe_dataframe(source_category.reset_index())

    elif admin_menu == "月次サマリー":
        st.markdown('<div class="section-title">月次サマリー</div>', unsafe_allow_html=True)

        st.info("スプレッドシートの「月次サマリー」シートを、そのまま表示しています。")

        df_month_summary = load_optional_sheet("月次サマリー")
        safe_dataframe(df_month_summary, height=620)

    elif admin_menu == "詳細表":
        st.markdown('<div class="section-title">詳細表</div>', unsafe_allow_html=True)

        with st.expander("今月分の結合データを見る", expanded=True):
            show_cols = [
                "日付",
                "受付側",
                "担当者",
                "エリア",
                "相手",
                "対応時間（分）",
                "用件",
                "備考",
                "登録日時"
            ]
            safe_dataframe(
                df_month[show_cols].sort_values(["日付", "登録日時"], ascending=[False, False]),
                height=420
            )

        with st.expander("当日サマリー シートを表示"):
            df_today_summary = load_optional_sheet("当日サマリー")
            safe_dataframe(df_today_summary, height=320)

        with st.expander("月次サマリー シートを表示"):
            df_month_summary = load_optional_sheet("月次サマリー")
            safe_dataframe(df_month_summary, height=420)

        with st.expander("集計元 シートを表示"):
            df_base = load_optional_sheet("集計元")
            safe_dataframe(df_base, height=420)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ワークシート取得
# =========================
ws = get_worksheet()

# =========================
# 日付更新チェック
# =========================
today = str(today_jst())

if "last_date" not in st.session_state:
    st.session_state.last_date = today

if st.session_state.last_date != today:
    st.session_state.last_date = today
    load_data.clear()
    load_log_sheet_for_admin.clear()
    load_optional_sheet.clear()
    st.rerun()

# =========================
# 担当者選択
# =========================
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

# =========================
# メイン画面切替
# =========================
main_view = st.radio(
    "画面切替",
    ["電話ログ入力", "管理者集計"],
    horizontal=True,
    key="main_view"
)

if main_view == "管理者集計":
    render_admin_dashboard()
    st.stop()

# =========================
# ここから電話ログ入力画面
# =========================

# =========================
# データ取得
# =========================
df = load_data()

# =========================
# リセットフラグ
# =========================
if "reset_form" not in st.session_state:
    st.session_state["reset_form"] = False

if st.session_state["reset_form"]:
    reset_input_fields()
    st.session_state["reset_form"] = False

# =========================
# 入力初期値
# =========================
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

# =========================
# 入力エリア
# =========================
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
    load_log_sheet_for_admin.clear()
    load_optional_sheet.clear()

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

# =========================
# 履歴エリア
# =========================
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
                    load_log_sheet_for_admin.clear()
                    load_optional_sheet.clear()

                    st.rerun()

    total_minutes = int(df_view["対応時間（分）"].sum())
    total_count = int(len(df_view))
    h = total_minutes // 60
    m = total_minutes % 60

    st.markdown(
        f"""
        <div class="total-box">
            <div class="total-grid">
                <div>
                    <div class="total-label">表示日の合計件数</div>
                    <div class="total-value">{total_count}件</div>
                </div>
                <div>
                    <div class="total-label">表示日の合計対応時間</div>
                    <div class="total-value">{total_minutes}分（{h}時間{m}分）</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.info("この日のデータはありません")

st.markdown('</div>', unsafe_allow_html=True)
