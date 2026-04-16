import streamlit as st
from google import genai
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
    - **核心 SDK**: `google-genai` (2026 最新官方库)
    - **视觉模型**: `Gemini 2.5 Flash` (原生支持)
    """)

st.title("👕 AI 数字人模特试穿系统")
st.markdown("上传衣服照片，利用全新一代 Gemini 识别特征并一键生成 AI 数字人穿搭指令。")

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
            with st.status("正在启动全新 2.5 代 AI 工作流...", expanded=True) as status:
                try:
                    # 【核心更新 1】使用全新的 Client 初始化方式
                    client = genai.Client(api_key=api_key)
                    
                    # 锁定刚刚在你的探测列表中确认存在的模型
                    target_model = 'gemini-2.5-flash'
                    status.write(f"已锁定最新生产模型: `{target_model}`")

                    # 构造分析 Prompt
                    prompt_text = f"你是一名时尚摄影专家。分析图中衣服款式、材质，并结合要求：'{user_requirement}'。输出格式：\n1. 衣服细节描述：\n2. 英文AI绘图Prompt："

                    status.write("正在发送多模态分析请求...")
                    
                    # 【核心更新 2】使用全新的 API 调用语法
                    response = None
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            time.sleep(1 + random.random()) 
                            response = client.models.generate_content(
                                model=target_model,
                                contents=[prompt_text, image]
                            )
                            if response and response.text:
                                break
                                
                        except Exception as inner_e:
                            if "429" in str(inner_e) and attempt < max_retries - 1:
                                wait_sec = (attempt + 1) * 5
                                status.write(f"⚠️ 服务器排队中，正在等待 {wait_sec} 秒后重试...")
                                time.sleep(wait_sec)
                            else:
                                raise inner_e

                    # --- 4. 结果解析与展示 ---
                    if response and response.text:
                        status.update(label="✨ 生成成功！", state="complete", expanded=True)
                        st.success("多模态分析与指令生成完毕：")
                        
                        full_text = response.text
                        col1, col2 = st.columns(2)
                        
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
                        st.error("模型未能返回有效结果。")

                except Exception as e:
                    status.update(label="❌ 发生底层错误", state="error")
                    st.error(f"详细错误: {str(e)}")

# --- 4. 底部声明 ---
st.markdown("---")
st.caption("⚡ 2026 全新重构版工作流 | Powered by Gemini 2.5 Flash")
