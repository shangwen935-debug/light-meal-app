import streamlit as st
import random
import google_sheets # 引用我们的后端库

# 把这段放在 import 下面
st.markdown("""
<style>
    /* 改变背景颜色 */
    .stApp {
        background-color: #f0f2f6;
    }
    /* 给所有按钮加个阴影 */
    div.stButton > button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("🎲 今天吃点啥？(多人版)")

# --- 1. 让用户输入名字 ---
# 在侧边栏增加一个输入框
user_name = st.sidebar.text_input("👤 请输入你的昵称/ID", value="默认用户")

if not user_name:
    st.warning("请先在左侧输入你的昵称！")
    st.stop() # 如果没有名字，停止运行下面的代码

# --- 2. 初始化 Session State ---
if "menu" not in st.session_state:
    st.session_state.menu = []

# --- 3. 加载属于这个用户的菜单 ---
# 注意：这里我们传入了 user_name
st.session_state.menu = google_sheets.get_menu_data(user_name)

# --- 4. 侧边栏：管理菜单 ---
with st.sidebar:
    st.header(f"📋 {user_name} 的菜单")
    
    # 显示当前菜单
    for item in st.session_state.menu:
        st.write(f"- {item}")
    
    # 添加新选项
    new_item = st.text_input("加个菜", key="new_item_input")
    if st.button("添加"):
        if new_item:
            # 写入时，同时传入 user_name 和 菜名
            if google_sheets.add_new_food(user_name, new_item):
                st.success("添加成功！")
                st.rerun()

# --- 5. 主界面：帮我决定 ---
if st.button("🎲 帮我决定！", type="primary"):
    if st.session_state.menu:
        choice = random.choice(st.session_state.menu)
        st.markdown(f"## 🤖 建议你吃：**{choice}**")
    else:
        st.warning("你的菜单是空的，先去左边添加一点吧！")