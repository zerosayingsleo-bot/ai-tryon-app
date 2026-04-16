import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import random

# --- 1. 页面配置 ---
st.set_page_config(page_title="AI 虚拟试穿工作流", layout="centered", page_icon="👕")

# --- 2. 侧边栏：API 深度配置 ---
with st.sidebar:
    st.title("⚙️ 配置中心")
    api_key = st.text_input("输入 Gemini API Key", type="password")
    
    st.markdown("""
    **🔧 当前底层配置：**
    - **API 版本**: `v1` (稳定版)
    - **传输协议**: `REST` (防断连)
    - **视觉模型**: `1.5-Flash-8B` (高频免费)
    """)
    
    if api_key:
        try:
            # 【最核心防御】强制切断 v1beta 路由，使用纯净的 REST 协议和 v1 稳定版接口
            genai.configure(
                api_key=api_key, 
                transport='rest',
                client_options={'api_version': 'v1'}
            )
            st.success("✅ API 底层环境已就绪")
        except Exception as e:
            st.error(f"❌ 配置异常: {e}")

st.title("👕 AI 数字人模特试穿系统")
st.markdown("上传衣服照片，利用极速版 Gemini 识别特征并一键生成 AI 数字人穿搭指令。")

# --- 3. 核心功能区 ---
uploaded_file = st.file_uploader("第一步：上传衣服照片", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 预览图片
    image = Image.open(uploaded_file)
    st.image(image, caption="已上传的原始衣服", use_container_width=True)

    # 用户要求输入框
    user_requirement = st.text_area(
        "第二步：描述模特和场景",
        placeholder="例如：一名 25 岁的亚洲女性模特，在极简主义摄影棚内，阳光明媚，电影级光影..."
    )

    # 触发按钮
    if st.button("🚀 开始生成工作流"):
        if not api_key:
            st.warning("⚠️ 请先在左侧边栏配置您的 API Key")
        else:
            with st.status("正在启动极速 AI 工作流...", expanded=True) as status:
                try:
                    # --- 1. 强制绑定高频模型 ---
                    # 彻底放弃智能探测，强制使用专为高频免费打造的 8b 轻量级模型
                    target_model = 'gemini-1.5-flash-8b'
                    status.write(f"已锁定免封锁模型: `{target_model}`")
                    model = genai.GenerativeModel(target_model)

                    # --- 2. 构造分析 Prompt ---
                    prompt_content = [
                        f"你是一名时尚摄影专家。分析图中衣服款式、材质，并结合要求：'{user_requirement}'。输出格式：\n1. 衣服细节描述：\n2. 英文AI绘图Prompt：",
                        image
                    ]

                    # --- 3. 稳健的请求机制 (带重试逻辑) ---
                    status.write("正在发送多模态分析请求...")
                    
                    response = None
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            # 基础防御：请求前微小随机延迟，防止并发被墙
                            time.sleep(1 + random.random()) 
                            response = model.generate_content(prompt_content)
                            if response:
                                break # 成功则跳出循环
                                
                        except Exception as inner_e:
                            if "429" in str(inner_e) and attempt < max_retries - 1:
                                wait_sec = (attempt + 1) * 8 # 遇到 429 阶梯等待: 8秒 -> 16秒
                                status.write(f"⚠️ 服务器拥堵 (429)，正在自动规避，{wait_sec} 秒后重试...")
                                time.sleep(wait_sec)
                            else:
                                raise inner_e # 抛出非 429 错误或最后一次失败的错误

                    # --- 4. 结果解析与展示 ---
                    if response and response.text:
                        status.update(label="✨ 生成成功！", state="complete", expanded=True)
                        st.success("多模态分析与指令生成完毕：")
                        
                        full_text = response.text
                        col1, col2 = st.columns(2)
                        
                        # 简单的文本切割逻辑，分离“描述”与“英文提示词”
                        with col1:
                            st.subheader("📝 细节分析")
                            analysis_text = full_text.split("2.")[0].replace("1.", "")
                            st.write(analysis_text)
                            
                        with col2:
                            st.subheader("🎨 绘图指令 (Prompt)")
                            prompt_text = full_text.split("2.")[-1] if "2." in full_text else full_text
                            st.code(prompt_text.strip(), language="markdown")
                            
                    else:
                        status.update(label="❌ 无法生成内容", state="error")
                        st.error("模型未能返回有效结果，请确认图片格式正确或图片未违规。")

                except Exception as e:
                    err_msg = str(e)
                    status.update(label="❌ 发生底层错误", state="error")
                    st.error(f"详细拒绝原因: {err_msg}")
                    
                    # 针对可能残留的 404 给出最后的退路提示
                    if "404" in err_msg:
                        st.info("💡 如果依然报 404，请将代码第 48 行的模型 ID 改为 `'gemini-1.5-flash-002'` 尝试。")

# --- 4. 底部声明 ---
st.markdown("---")
st.caption("⚡ 终极稳定版工作流 | 强制定向 v1 接口 | Powered by Gemini 1.5 Flash 8B")
