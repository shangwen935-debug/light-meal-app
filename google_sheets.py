import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

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
        
        # --- 🛠️ 核心修复区：自动清洗数据 ---
        raw_key = st.secrets["textkey"]
        
        # 这一步是为了防止 Streamlit 网页框把 \n 转义成了真正的换行
        # 我们尝试把 "非法换行" 自动修补回来
        try:
            # 方案 A: 尝试开启“宽容模式”解析
            key_dict = json.loads(raw_key, strict=False)
        except json.JSONDecodeError:
            # 方案 B: 如果还是报错，说明可能 \n 真的变成了回车
            # 我们手动把 "真回车" 替换成 JSON 能读的 "\n" 吗？
            # 风险较大，但我们先试试简单的替换控制符
            fixed_key = raw_key.replace('\n', '\\n') 
            # 注意：这可能会破坏外层结构，所以我们只作为备选
            # 如果上面 strict=False 没过，大概率是数据彻底乱了
            return ["❌ 密钥格式被破坏", "请尝试手动修改 secrets.json 的 formatting"]

        # 3. 尝试认证
        creds = Credentials.from_service_account_info(key_dict, scopes=scope)
        client = gspread.authorize(creds)

        # 4. 尝试打开表格
        sheet = client.open("LightMeal_Menu").sheet1
        
        # 5. 读取数据
        data = sheet.col_values(1)
        if not data:
            return ["⚠️ 提示: 表格是空的"]
            
        return data

    except Exception as e:
        return [f"❌ 依然报错: {type(e).__name__}", f"详细: {str(e)}"]
