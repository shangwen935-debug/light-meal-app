import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import random
import platform
import pandas as pd
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
    
    # ==========================================
    # 🔐 核心升级：用户门禁系统
    # ==========================================
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    # 如果未登录，显示登录/注册面板
    if not st.session_state.current_user:
        st.info("👋 请先登录以同步你的数据")
        tab_login, tab_reg = st.tabs(["🔑 登录", "📝 注册"])
        
        with tab_login:
            l_user = st.text_input("用户名", key="login_u")
            l_pass = st.text_input("密码", type="password", key="login_p")
            if st.button("登录", type="primary", use_container_width=True):
                success, msg = google_sheets.login_user(l_user, l_pass)
                if success:
                    st.session_state.current_user = l_user
                    st.rerun()
                else:
                    st.error(msg)

        with tab_reg:
            r_user = st.text_input("新用户名", key="reg_u")
            r_pass = st.text_input("设置密码", type="password", key="reg_p")
            if st.button("注册新账号", use_container_width=True):
                if r_user and r_pass:
                    success, msg = google_sheets.register_user(r_user, r_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("账号密码不能为空")
        
        st.divider()
        st.warning("🔒 请登录后使用功能")
        st.stop() # 🛑 没登录就停止运行下面的代码
    
    # 如果已登录
    user_name = st.session_state.current_user
    st.success(f"👤 欢迎, **{user_name}**")
    if st.button("退出登录", type="secondary"):
        st.session_state.current_user = None
        st.rerun()
        
    st.divider()

    # 导航栏
    page = st.radio(
        "功能导航", 
        ["🤔 能不能吃? (决策辅助)", "🎲 帮我选饭 (随机)", "🏆 个人成就 (数据看板)"]
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
    
    # 初始化 session_state 用于暂存 AI 结果
    if "ai_result_text" not in st.session_state:
        st.session_state.ai_result_text = None

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
                
                # 存入 session_state
                st.session_state.ai_result_text = response.text
                status_box.empty()
                st.success("✅ 评估结束！")
                
            except Exception as e:
                status_box.empty()
                st.error(f"❌ 出错啦：{e}")

    # --- 如果有分析结果，显示结果和录入表单 ---
    if st.session_state.ai_result_text:
        st.markdown(st.session_state.ai_result_text)
        
        st.divider()
        with st.container(border=True):
            st.markdown("### 📝 饮食打卡")
            c1, c2 = st.columns(2)
            ai_cal = c1.number_input("预估热量 (kcal)", min_value=0, step=10, help="根据 AI 的分析填入大概数值")
            ai_note = c2.text_input("备注", placeholder="例如：没吃米饭，只吃了菜")
            
            if st.button("✅ 确认记录", type="primary", use_container_width=True):
                current_user = user_name if user_name else "访客"
                if google_sheets.log_history(current_user, "AI评估餐食", "AI决策", calories=ai_cal, comment=st.session_state.ai_result_text + f"\n用户备注: {ai_note}"):
                    st.balloons()
                    st.success(f"已记录！热量: {ai_cal} kcal")
                    # 清空状态，准备下一次
                    st.session_state.ai_result_text = None
                    st.rerun()

# ==========================================
# 4. 功能 B：帮我选饭 (✨ 这里的逻辑升级了！)
# ==========================================
elif page == "🎲 帮我选饭 (随机)":
    st.title("🎲 今天吃点啥？")

    # 初始化 session_state 用于暂存随机结果
    if "random_choice" not in st.session_state:
        st.session_state.random_choice = None

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
        
        # 显示菜单列表 (带删除按钮)
        for item in st.session_state.menu:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.caption(f"- {item}")
            with c2:
                if st.button("✖️", key=f"del_{item}", help="删除此菜品"):
                    if google_sheets.delete_food(user_name, item):
                        st.toast(f"🗑️ 已删除 {item}")
                        st.session_state.menu = google_sheets.get_menu_data(user_name)
                        st.rerun()
            
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
                st.session_state.random_choice = random.choice(st.session_state.menu)
                st.rerun() # 刷新页面以显示结果

        # --- 如果有随机结果，显示结果卡片和录入表单 ---
        if st.session_state.random_choice:
            choice = st.session_state.random_choice
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 20px;">
                <h3>🤖 AI 建议你吃：</h3>
                <h1 style="color: #ff4b4b; font-size: 50px;">{choice}</h1>
            </div>
            """, unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("### 📝 决定吃这个了？完善一下数据吧")
                c1, c2 = st.columns(2)
                r_cal = c1.number_input("预估热量 (kcal)", min_value=0, step=50, key="r_cal")
                r_note = c2.text_input("备注", placeholder="例如：去皮吃，少放辣", key="r_note")
                
                if st.button("✅ 确认打卡", type="primary", use_container_width=True):
                    if google_sheets.log_history(user_name, choice, "随机-选中", calories=r_cal, comment=r_note):
                        st.balloons()
                        st.toast(f"已记录：{choice}")
                        # 清空选择
                        st.session_state.random_choice = None
                        st.rerun()
            
            if st.button("🔄 不想吃这个，重选", use_container_width=True):
                st.session_state.random_choice = None
                st.rerun()

# ==========================================
# 5. 功能 C：数据看板 (✨ 响应你的需求)
# ==========================================
elif page == "🏆 个人成就 (数据看板)":
    st.title("🏆 你的饮食成就")
    
    # 简单的登录框（复用侧边栏逻辑，或者在这里单独再问一次）
    # 直接使用当前登录的用户
    query_name = user_name
    st.caption(f"正在查看 **{query_name}** 的数据档案")
    
    if query_name:
        df = google_sheets.get_history_stats(query_name)
        
        if not df.empty:
            # --- 🛡️ 容错处理：补全缺失列 (防止表格表头不全导致报错) ---
            for col in ["Date", "Time", "Food", "Calories", "Tag", "Comment"]:
                if col not in df.columns:
                    df[col] = "未知" if col == "Tag" else ""

            # ✨ 小动画：弹出提示
            st.toast(f"已同步 {query_name} 的最新数据！", icon="🚀")

            # --- 🎮 游戏化计算 ---
            xp = len(df) * 10  # 每次打卡 10 XP
            level = int(xp / 100) + 1
            next_level_xp = level * 100
            current_level_xp = xp % 100
            
            # --- 1. 玩家状态栏 (UI 优化版) ---
            with st.container(border=True):
                c_avatar, c_info = st.columns([1, 4])
                with c_avatar:
                    st.markdown("<div style='font-size: 60px; text-align: center;'>🦸</div>", unsafe_allow_html=True)
                with c_info:
                    st.subheader(f"{query_name}")
                    st.caption(f"🏅 Lv.{level} 健康美食家 | ✨ 总经验: {xp} XP")
                    # 进度条
                    st.progress(current_level_xp / 100, text=f"🔥 冲鸭！距离下一级还差 {100 - current_level_xp} XP")
            
            # --- 2. 核心属性 (Metrics) ---
            st.write("") # 空一行
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🍽️ 累计用餐", f"{len(df)} 次", delta="坚持记录")
            with col2:
                # 找出吃得最多的食物
                top_food = df["Food"].value_counts().idxmax() # 👈 修正：读取 Food
                st.metric("❤️ 本命食物", top_food, delta="真爱")
            with col3:
                # 找出最多的标签 (AI推荐 vs 随机)
                fav_style = df["Tag"].value_counts().idxmax() # 👈 修正：读取 Tag
                clean_style = fav_style.split('-')[0] if '-' in fav_style else fav_style
                st.metric("🎭 决策流派", clean_style, delta="风格")
            
            st.divider()
            
            # --- 3. 可视化图表 (装备栏) ---
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("📊 饮食偏好 (Top 5)")
                # 统计食物出现频率
                food_counts = df["Food"].value_counts().head(5) # 👈 修正
                # 🎨 优化配色：使用温暖的橙色代替刺眼的红
                st.bar_chart(food_counts, color="#FF9F36")
                
            with c2:
                st.subheader("⚖️ 决策来源")
                # 统计标签 (AI vs 随机)
                tag_counts = df["Tag"].value_counts() # 👈 修正
                # 🎨 优化配色：使用专业的蓝色代替刺眼的绿
                st.bar_chart(tag_counts, color="#36A2EB")

            # --- 4. 历史卷轴 ---
            with st.expander("📜 查看详细历史记录"):
                st.dataframe(
                    df[["Date", "Time", "Food", "Calories", "Tag", "Comment"]].sort_values("Date", ascending=False), # 👈 修正：显示所有英文列
                    use_container_width=True,
                    hide_index=True
                )
                
        else:
            st.info("🧊 还没有数据哦，快去使用【AI 决策】或【随机选饭】功能并打卡吧！")