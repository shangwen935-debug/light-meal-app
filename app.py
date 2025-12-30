import streamlit as st
import random
import google_sheets  # 👈 核心变化：引入了你的新伙伴

# --- 1. 页面配置 ---
st.set_page_config(page_title="今日轻食 v2.0", page_icon="🥗", layout="centered")

# --- 2. CSS 样式 (保持不变) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
        height: 50px;
    }
    .success-card {
        padding: 20px;
        background-color: #e8f5e9;
        color: #1b5e20;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 数据初始化 ---
# 注意：这里不再写死菜单，而是问 google_sheets 要数据
if 'menu' not in st.session_state:
    st.session_state.menu = google_sheets.get_menu_data()
    
if 'decision' not in st.session_state:
    st.session_state.decision = None

# --- 4. 核心逻辑 ---
def make_choice():
    if st.session_state.menu:
        st.session_state.decision = random.choice(st.session_state.menu)

def add_food():
    if st.session_state.new_item:
        # 1. 先在前端显示出来
        st.session_state.menu.append(st.session_state.new_item)
        # 2. 调用后台尝试保存 (目前是打印日志，未来这里连接 API)
        google_sheets.add_new_food(st.session_state.new_item)
        # 3. 清空输入框
        st.session_state.new_item = "" 

def remove_food(item):
    st.session_state.menu.remove(item)
    if st.session_state.decision == item:
        st.session_state.decision = None

# --- 5. 界面布局 ---
st.title("🥗 今天吃点轻盈的？")
st.caption("架构升级版：UI与数据分离") # 改个标题庆祝一下

st.divider()

# 结果展示区
if st.session_state.decision:
    st.markdown(f"""
        <div class="success-card">
            <h3 style='margin:0'>🤖 AI 建议你吃</h3>
            <h1 style='margin:10px 0'>{st.session_state.decision}</h1>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🎲 不满意？再选一次"):
        make_choice()
else:
    if st.button("🎲 帮我决定！", type="primary"):
        make_choice()

st.divider()

# 菜单管理区
st.subheader("📋 你的菜单 (来自后端模块)")
st.text_input("添加新选项", key="new_item", on_change=add_food, placeholder="输入想吃的，回车添加...")

for item in st.session_state.menu:
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"**• {item}**")
    with col2:
        if st.button("✖️", key=item):
            remove_food(item)
            st.rerun()