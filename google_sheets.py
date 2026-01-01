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
def get_menu_data(user_name):
    try:
        client = get_client()
        sheet = client.open("LightMeal_Menu").sheet1
        
        # 👇 改动：不再只读第一列，而是读取所有数据
        all_records = sheet.get_all_values()
        
        # 👇 新增：过滤逻辑
        # 意思是：如果第一列(A列)的名字等于 user_name，就把第二列(B列)的菜取出来
        # all_records[1:] 是为了跳过第一行表头
        my_menu = [row[1] for row in all_records[1:] if len(row) > 1 and row[0] == user_name]
            
        return my_menu
    except Exception as e:
        return []

# --- 3. 写入新菜品函数 (就是缺了这个！) ---
# 👇 这里的括号里也多了 user_name
def add_new_food(user_name, food_name):
    try:
        client = get_client()
        sheet = client.open("LightMeal_Menu").sheet1
        
        # 👇 改动：写入的时候，把名字和菜名一起打包发过去
        sheet.append_row([user_name, food_name])
        return True
    except Exception as e:
        st.error(f"写入失败: {str(e)}")
        return False