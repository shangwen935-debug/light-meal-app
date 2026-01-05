import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import random
import platform
import google_sheets # 引用我们的后端库

# ==========================================
# 1. 核心配置 (保留你的完美设置)
# ==========================================
st.set_page_config(page_title="LightMeal 3.0", page_icon="🥗", layout="wide")


# 自动判断系统 (Windows 开代理，云端直连)
if platform.system() == "Windows":
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:15715"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:15715"
    print("🖥️ Windows模式：代理已开启")
else:
    print("☁️ 云端模式：直连开启")

# 验证 API Key
try:
    api_key = st.secrets["google_api_key"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("❌ 找不到 Key，请检查 secrets.toml")
    st.stop()
    # ... (上面是 import 和 set_page_config, 还有 API Key 配置) ...

# ==========================================
# ✨ 新增：高大上的封面页 (Landing Page)
# ==========================================

# 1. 初始化门禁状态
if "page_state" not in st.session_state:
    st.session_state.page_state = "landing" # 默认是封面状态

# 2. 如果还在封面状态，显示这一页
if st.session_state.page_state == "landing":
    
    # 搞点排版，把内容居中
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.write("\n\n") # 空几行，让它垂直居中一点
        st.markdown("""
        # LightMeal 3.2 🥗
        ### 你的私人 AI 饮食决策顾问
        
        这不是一个简单的菜单。  
        这是一个懂你身体状态、能听懂你碎碎念的智能管家。
        
        ---
        **核心功能：**
        * 📸 **AI 慧眼**：拍张照，告诉我能不能吃
        * 🚦 **状态决策**：生理期、熬夜、减脂？我帮你判断
        * 🎲 **治愈纠结**：不知道吃啥？存入云端，我帮你选
        """)
        
        st.write("\n")
        
        # 那个“进入 App”的按钮
        if st.button("🚀 开启健康之旅", type="primary", use_container_width=True):
            st.session_state.page_state = "app" # 改状态
            st.rerun() # 立即刷新页面，进入正题

    # 🛑 关键：如果是封面页，运行到这里就直接停止！
    # 这样后面的侧边栏、主功能代码统统不会被加载，屏幕就是干干净净的。
    st.stop()

# ==========================================
# 下面是你原来的 sidebar 代码...
# with st.sidebar:
# ...

# ==========================================
# 2. 侧边栏：状态输入 (✨ Day 3 核心升级)
# ==========================================
with st.sidebar:
    st.title("🥗 LightMeal 助手")
    
    # 导航栏
    page = st.radio(
        "功能导航", 
        ["🤔 能不能吃? (决策辅助)", "🎲 帮我选饭 (随机)"]
    )
    st.divider()

    # --- ✨ 新增逻辑：只有在 AI 页面才显示这些选项 ---
    user_context_instruction = "" # 初始化变量，防止报错
    
    if page == "🤔 能不能吃? (决策辅助)":
        st.header("🚦 今日状态录入")
        st.caption("AI 会根据你的状态，决定是否推荐你吃这顿饭。")
        
        # 1. 身体感受 (多选)
        status_tags = st.multiselect(
            "身体感觉怎么样？",
            ["😴 熬夜/没睡好", "🩸 生理期", "😵 肠胃不适", "🔥 上火/喉咙痛", "🏃‍♀️ 刚运动完", "🧠 压力大/用脑过度", "😀 我感觉非常好"],
            default=[]
        )
        
        # 2. 饮食目标 (单选)
        diet_goal = st.radio(
            "当前目标是？",
            ["📉 严格减脂", "🍎 控糖/抗炎", "💪 增肌/补充能量", "😋 只要好吃就行"],
            index=1 # 默认选控糖
        )
        
        # 3. 把选项拼成一句话，准备喂给 AI
        status_text = "、".join(status_tags) if status_tags else "身体状态正常"
        
        # 拼凑成一段“系统指令”
        user_context_instruction = f"""
        **【用户当前画像】**
        - 身体状态：{status_text}
        - 饮食目标：{diet_goal}
        
        **【你的任务】**
        不要只报热量！请结合用户的【身体状态】和【饮食目标】进行决策判断。
        
        **【输出格式要求】**
        1. **决策结论**：用 Emoji 开头（✅ 推荐 / ⚠️ 慎吃 / ❌ 达咩）。
        2. **贴心提醒**：温柔地解释原因，多站在用户身体舒服的角度考虑（例如：“生理期吃太凉可能会加重不适，抱抱你，我们换热饮好吗？”）。
        3. **补救建议**：如果非要吃，怎么吃比较好（例如：“把皮去掉”、“只吃一半”）。
        4. **营养速查**：最后再简单列一下热量和营养素。
        """

# ==========================================
# 3. 功能 A：AI 决策辅助 (✨ 逻辑已升级)
# ==========================================
if page == "🤔 能不能吃? (决策辅助)":
    st.title("🤔 帮我看看：这顿能吃吗？")
    
    # 在主界面展示一下刚才选的状态
    if 'status_tags' in locals() and status_tags:
        st.info(f"🎯 当前设定：**{status_text}** + **{diet_goal}**")
    else:
        st.info("🧘 当前设定：身体倍儿棒，吃嘛嘛香")

    uploaded_file = st.file_uploader("📸 拍张照/传菜单...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='待评估的食物', width=400)

        if st.button("⚖️ 评估开始", type="primary"):
            status_box = st.empty()
            status_box.write("🤖 AI 正在结合你的身体状况思考...")
            
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 关键点：把“用户状态指令”和“图片”一起发给 AI
                response = model.generate_content([user_context_instruction, image])
                
                status_box.empty()
                st.success("✅ 评估结束！")
                st.markdown(response.text)
                
            except Exception as e:
                status_box.empty()
                st.error(f"❌ 出错啦：{e}")

# ==========================================
# 4. 功能 B：帮我选饭 (✨ 这里的逻辑升级了！)
# ==========================================
elif page == "🎲 帮我选饭 (随机)":
    st.title("🎲 今天吃点啥？")

    # --- 身份卡 (门禁系统) ---
    st.sidebar.markdown("### 👤 你的身份卡")
    
    # 💡 改动 1: 默认值改为空字符串 ""，并增加 placeholder 提示
    user_name = st.sidebar.text_input(
        "请输入你的昵称/ID", 
        value="", 
        placeholder="例如：麦当劳一级爱好者", 
        help="⚠️ 你的菜单会绑定在这个名字上，下次输入同样的名字就能找回数据。"
    )

    # 💡 改动 2: 如果名字是空的，直接停止运行后续代码
    if not user_name:
        st.warning("👈 请先在左侧输入一个昵称，开启你的专属菜单！")
        st.info("💡 **为什么要输入昵称？**\n\n我们使用云端数据库保存你的菜单。输入一个独特的 ID，可以防止你的菜单和别人的混在一起。")
        st.stop() # 🛑 这是一个“红灯”，程序运行到这里就会暂停，直到用户输入名字

    # --- 只有输入了名字，下面的代码才会运行 ---
    
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
        st.write(f"**📋 {user_name} 的菜单 ({len(st.session_state.menu)})**") # 标题也加上名字
        
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
    if not st.session_state.menu:
        st.warning(f"👋 欢迎 **{user_name}**！你的菜单现在是空的。")
        with st.container(border=True):
            st.markdown(f"""
            ### 💡 如何开始：
            1. 👈 **看左边**：在侧边栏输入你想吃的菜名。
            2. 👆 **点添加**：点击“添加到云端”按钮。
            3. ☁️ **自动保存**：数据会自动存到 Google 表格。
            """)
    else:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("\n\n")
            if st.button("🎲 帮我决定！", type="primary", use_container_width=True):
                choice = random.choice(st.session_state.menu)
                st.balloons()
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
                    <h3>🤖 AI 建议你吃：</h3>
                    <h1 style="color: #ff4b4b; font-size: 50px;">{choice}</h1>
                </div>
                """, unsafe_allow_html=True)