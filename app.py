import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 页面配置 ---
st.set_page_config(page_title="AI 虚拟试穿工作流", layout="centered")

# --- 侧边栏：配置 API Key ---
with st.sidebar:
    st.title("设置")
    api_key = st.text_input("请输入 Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    st.info("该工作流使用 Gemini 1.5 Flash 进行图像分析与 Prompt 生成。")

st.title("👕 AI 数字人模特试穿系统")
st.markdown("上传衣服照片，Gemini 将自动为您设计数字人形象并生成穿搭提示词。")

# --- 第一步：上传图片 ---
uploaded_file = st.file_uploader("选择衣服图片...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 显示上传的图片
    image = Image.open(uploaded_file)
    st.image(image, caption="已上传的衣服", use_column_width=True)

    # --- 第二步：输入自定义要求 ---
    user_requirement = st.text_area(
        "数字人及场景要求",
        placeholder="例如：一名在北欧森林里的金发女性模特，阳光明媚，电影感画面..."
    )

    if st.button("🚀 开始生成工作流"):
        if not api_key:
            st.error("请先在侧边栏输入 API Key！")
        else:
            with st.spinner("Gemini 正在分析图片并编写提示词..."):
                try:
                    # 初始化 Gemini 2.0 Flash (多模态能力强且免费额度高)
                    model = genai.GenerativeModel('gemini-2.0-flash')

                    # 构造 Prompt 给 Gemini
                    system_prompt = f"""
                    你是一名顶尖的 AI 绘图提示词专家和时尚造型师。
                    任务：分析这张图片中的衣服（款式、颜色、材质、纹理），并结合用户的要求："{user_requirement}"。
                    输出：
                    1. 衣服的详细特征描述（中文）。
                    2. 一段用于 Stable Diffusion 或 Midjourney 的英文高清绘图提示词（Prompt）。
                    要求提示词包含：数字人的五官、肤色、姿势、光影效果、环境细节，以及确保衣服与人体结合自然。
                    """

                    # 发送图片和文字给 Gemini
                    response = model.generate_content([system_prompt, image])

                    # --- 第三步：展示结果 ---
                    st.success("分析完成！")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("分析报告")
                        st.write(response.text)

                    with col2:
                        st.subheader("AI 绘图指令")
                        # 将生成的 Prompt 放入代码框，方便用户复制
                        st.code(response.text.split("Prompt")[-1].strip(), language="markdown")

                    # --- 第四步：模拟/调用生成环节 ---
                    st.divider()
                    st.info(
                        "提示：您可以将上述 Prompt 复制到 Stable Diffusion 或 Midjourney 中。目前 Gemini API 正在逐步开放 Imagen 3 原生绘图接口。")

                except Exception as e:
                    st.error(f"发生错误: {str(e)}")

# --- 底部页脚 ---
st.markdown("---")
st.caption("基于 Google Gemini API | 免费部署于 Streamlit Cloud")
