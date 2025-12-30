import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

# 👇 注意这里：名字改回了 get_menu_data，这样 app.py 就能认识它了
def get_menu_data():
    # 1. 定义权限
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        # 2. 检查钥匙是否存在
        if "textkey" not in st.secrets:
            return ["❌ 严重错误: 后台没找到 textkey"]
        
        # 3. 尝试认证
        key_dict = json.loads(st.secrets["textkey"])
        creds = Credentials.from_service_account_info(key_dict, scopes=scope)
        client = gspread.authorize(creds)

        # 4. 尝试打开表格
        # ⚠️ 确保表格名字和你 Google Drive 里的一模一样
        sheet = client.open("LightMeal_Menu").sheet1
        
        # 5. 读取数据
        data = sheet.col_values(1)
        if not data:
            return ["⚠️ 提示: 表格连接成功，但里面是空的"]
            
        return data

    except Exception as e:
        # --- 🚨 捕捉并显示具体错误 ---
        return [f"❌ 抓到凶手了: {type(e).__name__}", f"详细信息: {str(e)}"]
