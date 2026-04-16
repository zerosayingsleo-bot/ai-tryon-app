import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import random

# --- 1. 页面配置 ---
st.set_page_config(page_title="AI 虚拟试穿系统", layout="centered", page_icon="👕")

# --- 2. 侧边栏 API 配置 ---
with st.sidebar:
    st.title("⚙️ 配置中心")
    api_key = st.text_input("输入新的 Gemini API Key", type="password")
    st.info("💡 提示：如果您遇到了 429 报错，请尝试切换 VPN 节点（推荐美国或新加坡）。")
    
    if api_key:
        try:
            # 使用 rest 模式在 Streamlit 部署环境中更稳定
            genai.configure(api_key=api_key, transport='rest')
            st.success("API 配置已就绪")
        except Exception as e:
            st.error(f"配置失败: {e}")

st.title("👕 AI 数字人模特试穿系统")
st.markdown("上传衣服照片，利用 Gemini 识别特征并一键生成 AI 数字人穿搭指令。")

# --- 3. 核心功能 ---
uploaded_file = st.file_uploader("第一步：上传衣服照片", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="已上传的原始衣服", use_container_width=True)

    user_requirement = st.text_area(
        "第二步：描述模特和场景",
        placeholder="例如：一名 25 岁的女性模特，在极简主义摄影棚内，阳光明媚..."
    )

    # 按钮点击逻辑
    if st.button("🚀 开始生成工作流"):
        if not api_key:
            st.warning("⚠️ 请先在侧边栏配置 API Key")
        else:
            with st.status("正在启动 AI 工作流...", expanded=True) as status:
                try:
                    # --- 1. 暴力指定模型 (绝不让它用 2.0) ---
                    status.write("正在强制唤醒 gemini-1.5-flash 模型...")
                    # 直接写死，跳过权限检测
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    # --- 2. 构造 Prompt ---
                    prompt_content = [
                        f"你是一名时尚摄影专家。分析图中衣服款式、材质，并结合要求：'{user_requirement}'。输出格式：\n1. 衣服细节描述：\n2. 英文AI绘图Prompt：",
                        image
                    ]

                    # --- 3. 执行请求 ---
                    status.write("正在发送分析请求...")
                    # 仅保留一次基础延迟防止并发
                    time.sleep(1.5) 
                    
                    response = model.generate_content(prompt_content)

                    # --- 4. 结果展示 ---
                    if response and response.text:
                        status.update(label="✨ 生成成功！", state="complete", expanded=True)
                        st.success("分析与指令生成完毕：")
                        
                        full_text = response.text
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("📝 细节分析")
                            st.write(full_text.split("2.")[0].replace("1.", ""))
                        with col2:
                            st.subheader("🎨 绘图指令 (Prompt)")
                            prompt_text = full_text.split("2.")[-1] if "2." in full_text else full_text
                            st.code(prompt_text.strip(), language="markdown")
                    else:
                        status.update(label="❌ 无法生成内容", state="error")
                        st.error("模型未能返回结果，请检查图片是否清晰。")

                except Exception as e:
                    err_msg = str(e)
                    status.update(label="❌ 发生错误", state="error")
                    st.error(f"底层拒绝详情: {err_msg}")
                    # --- 3. 带重试机制的请求执行 (对抗 429) ---
                    status.write("正在分析并生成内容（如遇拥堵将自动重试）...")
                    
                    response = None
                    max_retries = 3
                    for i in range(max_retries):
                        try:
                            # 每次请求前随机微调等待时间，避免并发
                            time.sleep(1 + random.random()) 
                            response = model.generate_content(prompt_content)
                            if response:
                                break
                        except Exception as e:
                            if "429" in str(e) and i < max_retries - 1:
                                wait_sec = (i + 1) * 10 # 第一次等10秒，第二次等20秒
                                status.write(f"⚠️ 服务器繁忙，正在等待 {wait_sec} 秒后进行第 {i+2} 次重试...")
                                time.sleep(wait_sec)
                            else:
                                raise e # 抛出最终错误

                    # --- 4. 结果展示 ---
                    if response and response.text:
                        status.update(label="✨ 生成成功！", state="complete", expanded=True)
                        st.success("分析与指令生成完毕：")
                        
                        full_text = response.text
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("📝 细节分析")
                            st.write(full_text.split("2.")[0].replace("1.", ""))
                        with col2:
                            st.subheader("🎨 绘图指令 (Prompt)")
                            prompt_text = full_text.split("2.")[-1] if "2." in full_text else full_text
                            st.code(prompt_text.strip(), language="markdown")
                    else:
                        status.update(label="❌ 无法生成内容", state="error")
                        st.error("模型未能返回结果，请检查图片是否清晰。")

                except Exception as e:
                    err_msg = str(e)
                    if "429" in err_msg:
                        status.update(label="❌ 配额限制", state="error")
                        st.error("您当前的 API 免费额度已耗尽。请：1. 彻底等待 1 分钟后再试；2. 切换 VPN 节点到美国；3. 在 AI Studio 确认是否为付费版限制。")
                    else:
                        status.update(label="❌ 发生错误", state="error")
                        st.error(f"具体错误信息: {err_msg}")

# --- 4. 页脚 ---
st.markdown("---")
st.caption("⚡ 2026 稳定版工作流 | 自动重试机制已开启")
