import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="電話対応ログ", layout="wide")
st.title("電話対応ログ")

# ===== 今日の日付 =====
today = str(date.today())

# ===== 日付変化検知（1日1回自動更新）=====
if "last_date" not in st.session_state:
    st.session_state.last_date = today

if st.session_state.last_date != today:
    st.session_state.last_date = today
    st.rerun()

# ===== 手動更新 =====
if st.button("🔄 更新"):
    st.rerun()

# ===== 入力モード =====
mode = st.radio("入力モード", ["通常入力", "過去入力"], horizontal=True)

if mode == "通常入力":
    selected_date = date.today()
else:
    selected_date = st.date_input("日付選択", value=date.today())

# ===== 認証 =====
creds_dict = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

client = gspread.authorize(creds)

SPREADSHEET_ID = "1yjuuTEPG8rsIr8Wctl6vtFmsU0cJy0rmsbvDnvpm934"
sheet = client.open_by_key(SPREADSHEET_ID)
ws = sheet.worksheet("logs")

# =========================
# 担当者（最初だけ）
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
st.write(f"担当者：{staff}")

# =========================
# データ取得
# =========================
data = ws.get_all_records()
df = pd.DataFrame(data)

if df.empty:
    df = pd.DataFrame(columns=["日付","番号","担当者","エリア","相手","対応時間（分）","要件","備考"])

df["対応時間（分）"] = pd.to_numeric(df["対応時間（分）"], errors="coerce").fillna(0)

# =========================
# 入力フォーム
# =========================
col1, col2 = st.columns(2)

with col1:
    area = st.selectbox("エリア", ["大分", "熊本"])

    partner = st.selectbox(
        "相手",
        ["得意先", "岡崎", "小薮", "美濃", "鶴岡", "椎葉", "倉庫配送", "内線", "その他"]
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
            "その他"
        ]
    )

    note = st.text_input("備考")

# =========================
# 追加
# =========================
if st.button("追加"):
    number = df["番号"].max() + 1 if not df.empty else 1

    new_row = [
        str(selected_date),
        number,
        staff,
        area,
        partner,
        minutes,
        category,
        note
    ]

    ws.append_row(new_row)
    st.rerun()

# =========================
# 当日データ
# =========================
df_today = df[df["日付"] == today]

# =========================
# スクロール＋削除
# =========================
if not df_today.empty:
    st.subheader("本日の入力履歴（削除できます）")

    df_display = df_today.sort_index(ascending=False).reset_index()

    with st.container(height=200):
        for i, row in df_display.iterrows():
            col1, col2 = st.columns([8,1])

            with col1:
                st.write(
                    f"{row['日付']} | {row['担当者']} | {row['エリア']} | {row['相手']} | {row['対応時間（分）']}分 | {row['要件']}"
                )

            with col2:
                if st.button("削除", key=f"del_{i}"):
                    ws.delete_rows(int(row["index"]) + 2)
                    st.rerun()

    # ===== 集計 =====
    total = int(df_today["対応時間（分）"].sum())
    h = total // 60
    m = total % 60

    st.subheader("本日合計")
    st.write(f"{total}分（{h}時間{m}分）")

    staff_summary = df_today.groupby("担当者")["対応時間（分）"].sum().reset_index()
    st.subheader("担当者別（本日）")
    st.dataframe(staff_summary)

else:
    st.info("本日のデータはまだありません")
