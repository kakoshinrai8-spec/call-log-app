import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="電話対応ログ", layout="wide")

# =========================
# タイトル
# =========================
st.title("📞 電話対応ログ")

# =========================
# 日付更新チェック
# =========================
today = str(date.today())

if "last_date" not in st.session_state:
    st.session_state.last_date = today

if st.session_state.last_date != today:
    st.session_state.last_date = today
    st.rerun()

# =========================
# 更新ボタン（上に配置）
# =========================
colA, colB = st.columns([8,2])

with colB:
    if st.button("🔄 更新"):
        st.rerun()

# =========================
# 認証
# =========================
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
data = ws.get_all_records()
df = pd.DataFrame(data)

if df.empty:
    df = pd.DataFrame(columns=["日付","番号","担当者","エリア","相手","対応時間（分）","要件","備考"])

df["対応時間（分）"] = pd.to_numeric(df["対応時間（分）"], errors="coerce").fillna(0)

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

if st.button("追加"):
    number = df["番号"].max() + 1 if not df.empty else 1

    ws.append_row([
        str(selected_date),
        number,
        staff,
        area,
        partner,
        minutes,
        category,
        note
    ])

    st.success("追加しました")
    st.rerun()

# =========================
# 区切り
# =========================
st.divider()

# =========================
# 履歴エリア
# =========================
st.subheader("履歴")

# 👉ここに移動（重要）
view_date = st.date_input("表示する日付", value=date.today())
view_date_str = str(view_date)

df_view = df[df["日付"] == view_date_str]

if not df_view.empty:

    df_display = df_view.sort_index(ascending=False).reset_index()

    with st.container(height=220):
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
    total = int(df_view["対応時間（分）"].sum())
    h = total // 60
    m = total % 60

    st.subheader("合計")
    st.write(f"{total}分（{h}時間{m}分）")

    staff_summary = df_view.groupby("担当者")["対応時間（分）"].sum().reset_index()
    st.dataframe(staff_summary)

else:
    st.info("この日のデータはありません")
