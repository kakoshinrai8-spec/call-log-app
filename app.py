import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ===== Secretsから認証 =====
creds_dict = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

client = gspread.authorize(creds)

# ===== シート =====
SPREADSHEET_NAME = "電話対応ログ"
SHEET_NAME = "logs"

sheet = client.open(SPREADSHEET_NAME)
ws = sheet.worksheet(SHEET_NAME)

st.title("📞 電話ログアプリ")

col1, col2 = st.columns(2)

with col1:
    担当者 = st.selectbox("担当者", ["吉田", "伊藤", "高木", "加藤", "加古"])

with col2:
    エリア = st.text_input("エリア")

相手 = st.text_input("相手")
対応時間 = st.number_input("対応時間（分）", min_value=0)
要件 = st.selectbox("要件", ["問い合わせ", "伝票確認", "在庫確認", "その他"])
備考 = st.text_area("備考")

if st.button("登録"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([now, 担当者, エリア, 相手, 対応時間, 要件, 備考])
    st.success("登録しました！")

data = ws.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    st.dataframe(df)
