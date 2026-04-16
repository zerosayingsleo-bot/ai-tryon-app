import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- 1. 页面配置 ---
st.set_page_config(page_title="AI 虚拟试穿系统", layout="centered", page_icon="👕")

# --- 2. 侧边栏 API 配置 ---
with st.sidebar:
    st.title("⚙️ 配置中心")
    api_key = st.text_input("输入 Gemini API Key", type="password")
    st.info("💡 提示：如果遇到 429 报错，请检查网络节点并等待 1 分钟。")
    
    if api_key:
        try:
            # 强制使用 rest 传输协议，在某些地区更稳定
            genai.configure(api_key=api_key, transport='rest')
            st.success("API 配置已就绪")
        except Exception as e:
            st.error(f"配置失败: {e}")

st.title("👕 AI 数字人模特试穿系统")
st.markdown("上传衣服照片，利用 Gemini 自动分析并生成 AI 数字人穿搭指令。")

# --- 3. 核心功能 ---
uploaded_file = st.file_uploader("第一步：上传衣服照片", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="已上传的原始衣服", use_container_width=True)

    user_requirement = st.text_area(
        "第二步：描述模特和场景",
        placeholder="例如：一名 25 岁的女性模特，在极简主义摄影棚内，阳光明媚..."
    )

    if st.button("🚀 开始生成工作流"):
        if not api_key:
            st.warning("⚠️ 请先在侧边栏配置 API Key")
        else:
            with st.status("正在通信中...", expanded=True) as status:
                try:
                    # --- 动态探测可用模型 (解决 404 问题) ---
                    status.write("正在探测您的 API 权限...")
                    available_models = [
                        m.name for m in genai.list_models() 
                        if 'generateContent' in m.supported_generation_methods
                    ]
                    
                    # 优先级：2.0-flash > 1.5-flash > 任意包含 flash 的模型 > 第一个可用模型
                    target_model = ""
                    if "models/gemini-2.0-flash" in available_models:
                        target_model = "models/gemini-2.0-flash"
                    elif "models/gemini-1.5-flash" in available_models:
                        target_model = "models/gemini-1.5-flash"
                    else:
                        # 找任何带 flash 的
                        flash_models = [m for m in available_models if "flash" in m]
                        target_model = flash_models[0] if flash_models else available_models[0]
                    
                    status.write(f"已匹配最佳模型: `{target_model}`")
                    model = genai.GenerativeModel(target_model)

                    # --- 构造 Prompt ---
                    prompt_content = [
                        f"你是一名时尚摄影专家。分析图中衣服款式、材质，并结合要求：'{user_requirement}'。输出：1.衣服细节描述；2.一段详细的英文AI绘图Prompt（包含模特五官、环境、光影、材质感）。",
                        image
                    ]

                    # --- 执行生成 (解决 429 问题) ---
                    status.write("正在分析图片并生成指令...")
                    # 稍微延迟一下，避开瞬时频率限制
                    time.sleep(1) 
                    response = model.generate_content(prompt_content)
                    
                    # 检查是否有内容返回
                    if response.text:
                        status.update(label="✨ 生成成功！", state="complete", expanded=True)
                        st.success("分析与指令生成完毕：")
                        
                        res_text = response.text
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("📝 细节分析")
                            st.write(res_text.split("2.")[0])
                        with col2:
                            st.subheader("🎨 绘图指令")
                            prompt_box = res_text.split("2.")[-1] if "2." in res_text else res_text
                            st.code(prompt_box.strip(), language="markdown")
                    else:
                        status.update(label="⚠️ 未能生成内容", state="error")
                        st.error("模型返回了空结果，请尝试更换图片或描述。")

                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str:
                        status.update(label="❌ 频率限制", state="error")
                        st.error("您当前的免费额度已达上限或操作过快。请等待 1 分钟后再试，或前往 Google AI Studio 检查配额。")
                    elif "404" in err_str:
                        status.update(label="❌ 模型不存在", state="error")
                        st.error(f"找不到模型 {target_model}。请尝试在 AI Studio 重新创建一个 API Key。")
                    else:
                        status.update(label="❌ 错误", state="error")
                        st.error(f"发生错误: {err_str}")

# --- 4. 页脚 ---
st.markdown("---")
st.caption("⚡ 自适应工作流 v2.5 | 自动模型匹配技术")
