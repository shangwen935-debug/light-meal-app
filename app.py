import platform
import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import random
import google_sheets # 引用表格库

# ==========================================
# 1. 核心配置
# ==========================================
if platform.system() == "Windows":
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:15715"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:15715"
    print("🖥️ 检测到 Windows，已开启代理模式")
else:
    print("☁️ 检测到 Linux/云端，使用直连模式")

st.set_page_config(page_title="LightMeal 2.1", page_icon="🥗", layout="wide")

try:
    api_key = st.secrets["google_api_key"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("❌ 找不到 Key，请检查 secrets.toml")
    st.stop()

# ==========================================
# 2. 侧边栏导航
# ==========================================
with st.sidebar:
    st.title("🥗 LightMeal 菜单")
    page = st.radio(
        "功能导航", 
        ["📸 AI 营养师 (识图)", "🎲 帮我选饭 (随机)"],
    )
    st.divider()

# ==========================================
# 3. 功能 A：AI 营养师
# ==========================================
if page == "📸 AI 营养师 (识图)":
    st.title("🥗 AI 只有眼睛版")
    st.info("上传外卖菜单或食物照片，让 Gemini 帮你把把关。")

    uploaded_file = st.file_uploader("📸 上传图片...", type=["jpg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='已上传图片', width=400)

        if st.button("🔍 温柔分析 (Gemini 2.5)", type="primary"):
            status_box = st.empty()
            status_box.write("🤖 AI 正在思考中...")
            
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                my_prompt = """
                请仔细分析这张图片。
                1. **如果是菜单**：请帮我挑出 3 个比较健康、负担较小的菜作为推荐，并说明理由。
                2. **如果是食物**：请估算它的热量范围，并告诉我哪里吃得很好，哪里稍微注意一下（比如油盐）。
                **语气要求**：
                请做一个温柔、贴心的“饮食顾问”。
                多用鼓励的语气，不要太严肃教条。
                """
                response = model.generate_content([my_prompt, image])
                status_box.empty()
                st.success("✅ 分析完成！")
                st.markdown(response.text)
            except Exception as e:
                status_box.empty()
                st.error(f"❌ 出错啦：{e}")

# ==========================================
# 4. 功能 B：帮我选饭 (这里进行了 UX 升级！)
# ==========================================
elif page == "🎲 帮我选饭 (随机)":
    st.title("🎲 今天吃点啥？")

    # --- 💡 改进点 1: 这里的文案改了，强调“存档”概念 ---
    st.sidebar.markdown("### 👤 你的身份卡")
    user_name = st.sidebar.text_input(
        "请输入你的昵称/ID", 
        value="默认用户",
        help="⚠️ 记住这个名字！你的菜单会保存在云端，下次输入同样的名字就能找回数据。"
    )
    
    # --- 加载数据 ---
    if "menu" not in st.session_state:
        st.session_state.menu = []
    
    # 自动加载逻辑
    if not st.session_state.menu:
         st.session_state.menu = google_sheets.get_menu_data(user_name)

    # 刷新按钮
    if st.sidebar.button("🔄 同步云端数据"):
        st.session_state.menu = google_sheets.get_menu_data(user_name)
        st.sidebar.success("同步完成！")

    # --- 侧边栏加菜 ---
    with st.sidebar:
        st.divider()
        st.write(f"**📋 当前菜单 ({len(st.session_state.menu)})**")
        
        # 显示菜单列表
        for item in st.session_state.menu:
            st.caption(f"- {item}")
            
        st.markdown("---")
        new_item = st.text_input("📝 加个新菜", key="add_new")
        if st.button("➕ 添加到云端"):
            if new_item:
                if google_sheets.add_new_food(user_name, new_item):
                    st.toast(f"已把 {new_item} 存入云端表格！")
                    st.rerun()

    # --- 主界面逻辑 ---
    
    # 💡 改进点 2: 如果菜单是空的，显示“新手引导页”
    if not st.session_state.menu:
        st.warning("⚠️ 你的菜单现在是空的！")
        
        with st.container(border=True):
            st.markdown(f"""
            ### 👋 欢迎来到 LightMeal 选饭助手！
            
            看起来 **{user_name}** 还没有添加过任何菜单。
            
            **💡 如何开始：**
            1. 👈 **看左边**：在侧边栏输入你想吃的菜名（比如“黄焖鸡米饭”）。
            2. 👆 **点添加**：点击“添加到云端”按钮。
            3. ☁️ **自动保存**：数据会自动存到 Google 表格，**下次输入同一个名字就能找回来！**
            
            *快去添加几个菜，然后我来帮你做决定！*
            """)
            
    else:
        # 如果有菜，才显示大按钮
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("\n\n") # 稍微空几行
            if st.button("🎲 帮我决定！", type="primary", use_container_width=True):
                choice = random.choice(st.session_state.menu)
                st.balloons()
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
                    <h3>🤖 AI 经过慎重考虑，建议你吃：</h3>
                    <h1 style="color: #ff4b4b; font-size: 50px;">{choice}</h1>
                </div>
                """, unsafe_allow_html=True)