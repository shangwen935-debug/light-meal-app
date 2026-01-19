import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import pandas as pd
from datetime import datetime

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

# --- 4. ✨ 新增：历史打卡记录 ---
def log_history(user_name, food_name, tag):
    """
    记录用户的饮食行为
    tag: 例如 'AI推荐-推荐吃', 'AI推荐-慎吃', '随机-选中'
    """
    try:
        client = get_client()
        sh = client.open("LightMeal_Menu")
        
        # 尝试打开 'History' 表，如果不存在就自动创建
        try:
            worksheet = sh.worksheet("History")
        except:
            worksheet = sh.add_worksheet(title="History", rows="1000", cols="5")
            worksheet.append_row(["时间", "用户", "食物", "标签", "备注"]) # 表头
            
        # 写入数据：时间戳, 用户, 食物, 标签
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([time_str, user_name, food_name, tag, ""])
        return True
    except Exception as e:
        st.error(f"打卡失败: {e}")
        return False

# --- 5. ✨ 新增：获取统计数据 ---
def get_history_stats(user_name):
    try:
        client = get_client()
        # 如果表不存在，直接返回空
        try:
            worksheet = client.open("LightMeal_Menu").worksheet("History")
        except:
            return pd.DataFrame()
            
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # 筛选当前用户的数据
        if not df.empty:
            return df[df["用户"] == user_name]
        return df
    except Exception:
        return pd.DataFrame()

# --- 6. ✨ 新增：删除菜品函数 ---
def delete_food(user_name, food_name):
    try:
        client = get_client()
        sheet = client.open("LightMeal_Menu").sheet1
        
        # 获取所有数据来查找匹配的行
        all_records = sheet.get_all_values()
        
        # 寻找匹配 用户名 和 菜名 的行号
        # enumerate 从 0 开始，但 gspread 行号从 1 开始
        row_to_delete = 0
        for idx, row in enumerate(all_records):
            # row[0] is user, row[1] is food. idx=0 is header.
            if len(row) > 1 and row[0] == user_name and row[1] == food_name:
                row_to_delete = idx + 1 
                break 
        
        # 确保不删除表头 (row 1)
        if row_to_delete > 1:
            sheet.delete_rows(row_to_delete)
            return True
        return False
            
    except Exception as e:
        st.error(f"删除失败: {str(e)}")
        return False

# --- 7. ✨ 新增：用户认证系统 ---
def get_users_sheet():
    """获取或创建 Users 表"""
    client = get_client()
    sh = client.open("LightMeal_Menu")
    try:
        return sh.worksheet("Users")
    except:
        # 如果不存在，创建它，并写入表头
        ws = sh.add_worksheet(title="Users", rows="100", cols="2")
        ws.append_row(["Username", "Password"])
        return ws

def register_user(username, password):
    """注册新用户 (含查重)"""
    try:
        ws = get_users_sheet()
        # 获取第一列的所有用户名 (用于查重)
        existing_users = ws.col_values(1)
        
        if username in existing_users:
            return False, "❌ 用户名已被占用，请换一个！"
        
        # 存入账号密码 (明文存储，个人项目够用了)
        ws.append_row([username, password])
        return True, "✅ 注册成功！请切换到登录页登录。"
    except Exception as e:
        return False, f"❌ 系统错误: {e}"

def login_user(username, password):
    """验证登录"""
    try:
        ws = get_users_sheet()
        records = ws.get_all_records() # 获取所有数据
        
        for record in records:
            # 强转 string 避免数字类型的密码报错
            if str(record.get("Username")) == username and str(record.get("Password")) == password:
                return True, "✅ 登录成功"
        
        return False, "❌ 用户名或密码错误"
    except Exception as e:
        return False, f"❌ 登录失败: {e}"