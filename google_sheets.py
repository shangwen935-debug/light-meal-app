import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import json

# --- 1. 配置权限范围 ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# --- 2. 智能认证 (自动识别是本地还是云端) ---
try:
    # 优先尝试读取本地文件 (secrets.json)
    creds = ServiceAccountCredentials.from_json_keyfile_name("secrets.json", scope)
    client = gspread.authorize(creds)
    # print("正在使用本地 secrets.json 进行连接...") # 调试用

except FileNotFoundError:
    # 如果找不到文件，说明可能在 Streamlit 云端
    try:
        # 从 Streamlit 的云端机密里读取 (我们稍后会配置这个)
        key_dict = json.loads(st.secrets["textkey"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        # print("正在使用云端 Secrets 进行连接...") # 调试用
    except Exception as e:
        client = None
        print(f"严重错误：找不到任何密钥。详情: {e}")

# --- 3. 连接表格 ---
# ⚠️ 重要：这里必须和你 Google Sheets 左上角的名字一模一样！
SHEET_NAME = "LightMeal_Menu" 

def get_menu_data():
    """
    从 Google Sheets 读取菜单
    """
    if client is None:
        return ["错误：无法连接到数据库"]

    try:
        sheet = client.open(SHEET_NAME).sheet1  # 打开第一张表
        data = sheet.col_values(1)  # 读取第一列所有数据
        
        # 如果第一行是表头 "Menu"，把它去掉
        if data and (data[0] == "Menu" or data[0] == "菜单"):
            return data[1:]
        
        # 如果表格是空的，为了防止报错，返回一个默认提示
        if not data:
            return ["表格是空的，快去添加吧！"]
            
        return data
    except Exception as e:
        return [f"连接出错: {str(e)}", "请检查表格名称是否正确"]

def add_new_food(food_name):
    """
    把新菜名写入 Google Sheets
    """
    if client is None:
        return False

    try:
        sheet = client.open(SHEET_NAME).sheet1
        sheet.append_row([food_name]) # 在最后一行追加
        return True
    except Exception as e:
        print(f"写入失败: {e}")
        return False