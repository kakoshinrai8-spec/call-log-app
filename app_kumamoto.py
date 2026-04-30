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
# タイトル
# =========================
st.title("📞 電話対応ログ（熊本）")

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
        "佐々木",
        "松岡",
        "吉澤",
        "秋山",
        "斎藤",
        "桑原",
        "古賀",
        "一村",
        "遠藤",
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
    ]
}

CATEGORY_OPTIONS = [
    "注文",
    "商品問合せ",
    "納期依頼",
    "見積依頼",
    "返品依頼",
    "伝票確認",
    "在庫確認",
    "請求書関連",
    "その他"
]

HEADER_COLUMNS = ["日付", "番号", "担当者", "エリア", "相手", "対応時間（分）", "要件", "備考", "登録日時"]

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

# =========================
# 日付更新チェック
# =========================
today = str(today_jst())

if "last_date" not in st.session_state:
    st.session_state.last_date = today

if st.session_state.last_date != today:
    st.session_state.last_date = today
    load_data.clear()
    st.rerun()

# =========================
# 担当者選択
# =========================
if "staff" not in st.session_state:
    st.session_state.staff = ""

if st.session_state.staff == "":
    staff = st.selectbox("あなたの名前を選択", STAFF_OPTIONS)

    if st.button("決定"):
        st.session_state.staff = staff
        st.rerun()

    st.stop()

staff = st.session_state.staff
st.success(f"担当者：{staff}")

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
st.subheader("入力")

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
    category = st.selectbox("要件", CATEGORY_OPTIONS, key="input_category")
    note = st.text_input("備考", key="input_note")

# =========================
# メッセージ表示エリア
# =========================
message_area = st.empty()

# =========================
# 追加処理
# =========================
if st.button("追加"):
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

# =========================
# 追加メッセージ表示
# =========================
if st.session_state.get("added"):
    added_count = st.session_state.get("added_count", 1)
    message_area.success(f"✅ {added_count}件追加しました")
    st.session_state["added"] = False
    st.session_state["added_count"] = 1

# =========================
# 区切り
# =========================
st.divider()

# =========================
# 履歴エリア
# =========================
st.subheader("履歴")

view_date = st.date_input("表示する日付", value=today_jst(), key="view_date")
view_date_str = str(view_date)

df_view = df[df["日付"] == view_date_str]

if not df_view.empty:
    df_display = df_view.sort_index(ascending=False).reset_index()

    with st.container(height=260):
        for i, row in df_display.iterrows():
            col1, col2 = st.columns([8, 1])

            with col1:
                registered_at = row["登録日時"] if pd.notna(row["登録日時"]) else ""
                st.write(
                    f"{row['日付']} | {row['担当者']} | {row['エリア']} | {row['相手']} | {int(row['対応時間（分）'])}分 | {row['要件']} | {registered_at}"
                )

            with col2:
                if st.button("削除", key=f"del_{i}"):
                    ws.delete_rows(int(row["index"]) + 2)
                    load_data.clear()
                    st.rerun()

    total = int(df_view["対応時間（分）"].sum())
    h = total // 60
    m = total % 60

    st.subheader("合計")
    st.write(f"{total}分（{h}時間{m}分）")

else:
    st.info("この日のデータはありません")
