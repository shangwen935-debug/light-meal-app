import streamlit as st
import random

# --- 1. 页面配置 ---
st.set_page_config(page_title="今日轻食", page_icon="🥗", layout="centered")

# --- 2. CSS 样式 (让界面变圆润优雅) ---
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
if 'menu' not in st.session_state:
    # 这里是你定制的“永久”菜单
    st.session_state.menu = [
        "南谷稻香中式减脂菜", 
        "窑鸡王", 
        "小谷姐姐麻辣拌 (自加牛肉版)", 
        "广式滋补蒸鸡", 
        "粒栗皆饭团", 
        "猪肚鸡汤饭",
        "张家小板凳麻辣拌 (自加牛肉少酱版)",
        "任意轻食外卖"
    ]
if 'decision' not in st.session_state:
    st.session_state.decision = None

# --- 4. 核心逻辑 ---
def make_choice():
    if st.session_state.menu:
        st.session_state.decision = random.choice(st.session_state.menu)

def add_food():
    if st.session_state.new_item:
        st.session_state.menu.append(st.session_state.new_item)
        st.session_state.new_item = "" 

def remove_food(item):
    st.session_state.menu.remove(item)
    if st.session_state.decision == item:
        st.session_state.decision = None

# --- 5. 界面布局 ---
st.title("🥗 今天吃点轻盈的？")
st.caption("把做饭的时间省下来，去写更优雅的代码。")

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
st.subheader("📋 你的菜单")
st.text_input("添加新选项", key="new_item", on_change=add_food, placeholder="输入想吃的，回车添加...")

# 优雅的列表展示
for item in st.session_state.menu:
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"**• {item}**")
    with col2:
        if st.button("✖️", key=item, help="删除"):
            remove_food(item)
            st.rerun()