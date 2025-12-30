import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

def get_google_sheet_data():
    # 1. 定义我们需要的权限范围 (Scope)
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        # 2. 读取 Secrets (钥匙)
        # 这里的 "textkey" 必须和你 Streamlit 后台 Secrets 里的名字一模一样
        if "textkey" not in st.secrets:
            return ["错误：Streamlit后台未配置 textkey"]
        
        # 加载 JSON 字符串
        key_dict = json.loads(st.secrets["textkey"])
        
        # 3. 登录 Google
        creds = Credentials.from_service_account_info(key_dict, scopes=scope)
        client = gspread.authorize(creds)

        # 4. 打开表格
        # 确保这个名字和你 Google Drive 里的表格名字完全一致
        sheet = client.open("LightMeal_Menu").sheet1
        
        # 5. 读取数据
        data = sheet.col_values(1)  # 读取第一列
        
        if not data:
            return ["提示：表格是空的，快去添加吧！"]
            
        return data

    except Exception as e:
        # --- 🚨 关键修改：这里会把具体的英文报错直接显示在屏幕上 ---
        return [f"❌ 发生错误: {str(e)}", "请截图发给 Gemini 帮忙分析"]

# 如果直接运行这个文件进行测试
if __name__ == "__main__":
    print(get_google_sheet_data())