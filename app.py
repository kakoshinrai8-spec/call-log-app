import streamlit as st
import pandas as pd
from datetime import date, datetime
from zoneinfo import ZoneInfo
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="電話対応ログ", layout="wide")

# =========================
# タイトル
# =========================
st.title("📞 電話対応ログ")

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
    return sheet.worksheet("logs")

# =========================
# データ取得キャッシュ
# =========================
@st.cache_data(ttl=15)
def load_data():
    ws = get_worksheet()
    data = ws.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=["日付", "番号", "担当者", "エリア", "相手", "対応時間（分）", "要件", "備考", "登録日時"])

    for col in ["日付", "番号", "担当者", "エリア", "相手", "対応時間（分）", "要件", "備考", "登録日時"]:
        if col not in df.columns:
            df[col] = ""

    df["対応時間（分）"] = pd.to_numeric(df["対応時間（分）"], errors="coerce").fillna(0)
    df["番号"] = pd.to_numeric(df["番号"], errors="coerce")

    return df

ws = get_worksheet()

# =========================
# 日付更新チェック
# =========================
today = str(date.today())

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
    staff = st.selectbox(
        "あなたの名前を選択",
        ["吉田", "伊藤", "高木", "加藤", "加古"]
    )

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
# 入力エリア
# =========================
st.subheader("入力")

mode = st.radio("入力モード", ["通常入力", "過去入力"], horizontal=True)

if mode == "通常入力":
    selected_date = date.today()
else:
    selected_date = st.date_input("入力日付", value=date.today())

col1, col2 = st.columns(2)

with col1:
    area = st.selectbox("エリア", ["大分", "熊本"])

    partner = st.selectbox(
        "相手",
        ["得意先", "岡崎", "小薮", "美濃", "鶴岡", "椎葉", "細水", "中野", "倉庫配送", "内線", "その他"]
    )

    minutes = st.number_input("対応時間（分）", min_value=1, step=1)

with col2:
    category = st.selectbox(
        "要件",
        [
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
    )

    note = st.text_input("備考")

# =========================
# メッセージ表示エリア
# =========================
message_area = st.empty()

# =========================
# 追加処理
# =========================
if st.button("追加"):
    max_number = pd.to_numeric(df["番号"], errors="coerce").max()
    number = int(max_number) + 1 if pd.notna(max_number) else 1

    created_at = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")

    ws.append_row([
        selected_date.strftime("%Y-%m-%d"),
        int(number),
        str(staff),
        str(area),
        str(partner),
        int(minutes),
        str(category),
        note if note else "",
        created_at
    ])

    load_data.clear()
    st.session_state["added"] = True
    st.rerun()

# =========================
# 追加メッセージ表示
# =========================
if st.session_state.get("added"):
    message_area.success("✅ 追加しました")
    st.session_state["added"] = False

# =========================
# 区切り
# =========================
st.divider()

# =========================
# 履歴エリア
# =========================
st.subheader("履歴")

view_date = st.date_input("表示する日付", value=date.today(), key="view_date")
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

    staff_summary = df_view.groupby("担当者")["対応時間（分）"].sum().reset_index()
    st.dataframe(staff_summary, use_container_width=True)

else:
    st.info("この日のデータはありません")
