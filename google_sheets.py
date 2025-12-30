import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

# --- 1. 核心连接函数 (公用的) ---
def get_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # 如果之前加了 strict=False 解决了问题，这里保持加上
    # 如果没加也能跑，这行代码也是安全的
    key_dict = json.loads(st.secrets["textkey"], strict=False)
    creds = Credentials.from_service_account_info(key_dict, scopes=scope)
    return gspread.authorize(creds)

# --- 2. 读取菜单函数 ---
def get_menu_data():
    try:
        client = get_client()
        sheet = client.open("LightMeal_Menu").sheet1
        # 读取第一列所有数据
        data = sheet.col_values(1)
        
        # 简单过滤：如果第一行是表头 "Menu"，把它去掉
        if data and data[0] == "Menu":
            return data[1:]
            
        return data
    except Exception as e:
        return [f"读取失败: {str(e)}"]

# --- 3. 写入新菜品函数 (就是缺了这个！) ---
def add_new_food(food_name):
    try:
        client = get_client()
        sheet = client.open("LightMeal_Menu").sheet1
        # 在表格末尾追加一行
        sheet.append_row([food_name])
        return True
    except Exception as e:
        st.error(f"写入失败: {str(e)}")
        return False
