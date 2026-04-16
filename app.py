import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- 1. 基础页面设置 ---
st.set_page_config(page_title="AI 虚拟试穿系统", layout="centered", page_icon="👕")

# --- 2. 侧边栏 API 配置 ---
with st.sidebar:
    st.title("⚙️ 配置中心")
    api_key = st.text_input("输入 Gemini API Key", type="password")
    st.info("💡 建议：如果 429 报错，请等待 1 分钟后重试。")
    if api_key:
        genai.configure(api_key=api_key)

st.title("👕 AI 数字人模特试穿系统")
st.markdown("上传衣服照片，利用 Gemini 识别特征并生成 AI 数字人穿搭指令。")

# --- 3. 核心功能逻辑 ---
uploaded_file = st.file_uploader("第一步：上传衣服照片", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 转换图片
    image = Image.open(uploaded_file)
    st.image(image, caption="已上传的原始衣服", use_container_width=True)

    user_requirement = st.text_area(
        "第二步：描述模特和场景",
        placeholder="例如：一名 25 岁的亚洲女性模特，站在极简主义工作室中，柔和光影..."
    )

    # 按钮点击逻辑
    if st.button("🚀 生成数字人穿搭工作流"):
        if not api_key:
            st.warning("⚠️ 请先在侧边栏配置 API Key")
        else:
            # 建立状态提示，防止重复点击
            with st.status("正在识别衣服并分析提示词...", expanded=True) as status:
                try:
                    # 获取当前账户下可用的 Flash 模型 ID
                    # 优先选择 2.0，如果失败则回退到 1.5
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                    except:
                        model = genai.GenerativeModel('gemini-pro-vision')

                    # 构造 2026 标准 Prompt
                    prompt_text = f"""
                    你是一名顶尖的 AI 虚拟模特摄影师。
                    请根据图片中的衣服（款式、面料、颜色）以及用户要求："{user_requirement}"。
                    执行以下任务：
                    1. 详细描述衣服在数字人身上的穿着细节。
                    2. 提供一段高质量的英文 AI 绘图提示词 (Prompt)，用于生成该衣服的虚拟试穿大片。
                    提示词要求：包含模特外貌、相机参数、环境光影、衣服褶皱感。
                    """

                    # 发起请求
                    # 免费层级建议增加一个微小的延迟防止并发
                    time.sleep(0.5) 
                    response = model.generate_content([prompt_text, image])
                    
                    # 成功后更新状态
                    status.update(label="✨ 生成成功！", state="complete", expanded=True)
                    
                    # 展示结果
                    st.success("分析与指令生成完毕：")
                    
                    res_text = response.text
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📝 衣服细节分析")
                        # 截取前半段描述
                        st.write(res_text.split("2.")[0] if "2." in res_text else res_text)
                        
                    with col2:
                        st.subheader("🎨 绘图指令 (Prompt)")
                        # 将英文 Prompt 单独提取到代码框中
                        prompt_part = res_text.split("2.")[-1] if "2." in res_text else res_text
                        st.code(prompt_part.strip(), language="markdown")

                    st.divider()
                    st.info("💡 提示：将右侧指令复制到 Stable Diffusion 或 Midjourney 即可出图。")

                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg:
                        status.update(label="❌ 触发频率限制", state="error")
                        st.error("操作太快了！Gemini 免费版每分钟限制调用次数。请等待 60 秒后再试。")
                    elif "404" in error_msg:
                        status.update(label="❌ 模型未找到", state="error")
                        st.error("当前 API Key 无法访问指定的模型版本，请检查 Google AI Studio 权限。")
                    else:
                        status.update(label="❌ 发生未知错误", state="error")
                        st.error(f"具体错误：{error_msg}")

# --- 4. 底部声明 ---
st.markdown("---")
st.caption("⚡ 2026 Gemini Workflow | Powered by Google Generative AI")
