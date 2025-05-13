import streamlit as st
import requests
import json

# 页面设置
st.set_page_config(
    page_title="短视频文案仿写工具",
    page_icon="🎬",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
.markdown-box {
    background: #fff;
    border: 1px solid #ccc;
    padding: 16px;
    border-radius: 6px;
    white-space: normal;
    line-height: 1.6;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 初始化session状态
if 'last_generated' not in st.session_state:
    st.session_state.last_generated = ""

# 标题
st.title("🎬 短视频文案仿写与优化工具")

# 侧边栏 - API设置
with st.sidebar:
    st.header("API 设置")
    api_key = st.text_input("DeepSeek API Key", type="password", help="以 sk- 开头的API密钥")
    st.markdown("---")
    st.info("""
    使用说明：
    1. 输入参考文案和创作需求
    2. 点击分析或生成按钮
    3. 可对生成结果进行优化
    """)

# 主界面
tab1, tab2 = st.tabs(["文案生成", "文案优化"])

with tab1:
    # 第一部分：参考文案分析
    st.subheader("① 参考文案分析")
    reference_text = st.text_area(
        "粘贴你想参考的短视频文案：",
        height=200,
        placeholder="例如：很多人问我，30岁转行还来得及吗？其实我就是..."
    )
    
    if st.button("📊 拆解文案结构与网感", disabled=not (reference_text and api_key)):
        with st.spinner("正在分析文案结构与网感..."):
            prompt = f"""请帮我拆解以下短视频文案的内容结构与网感要素：

【原文案】：
{reference_text}

请输出以下内容：
1. 内容结构（开头吸引点 / 信息输出 / 结尾引导）
2. 文案风格特点（例如：亲切/犀利/反转/反常识）
3. 网感要素（冲突点、共鸣点、流行表达等）
请用清晰的小标题和 markdown 格式输出（如使用 **加粗**、- 项目符号等）。"""

            try:
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.5
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('choices') and data['choices'][0]:
                    st.markdown("### 文案结构与网感分析：")
                    st.markdown(data['choices'][0]['message']['content'], unsafe_allow_html=True)
                else:
                    st.error("分析失败：" + json.dumps(data, ensure_ascii=False))
            except Exception as e:
                st.error(f"请求出错：{str(e)}")

    # 第二部分：文案生成
    st.subheader("② 新文案生成")
    description = st.text_area(
        "输入你的视频创作需求：",
        height=150,
        placeholder="例如：我要写一个适合小红书分享的自律类文案，适合打工人，语气轻松自嘲..."
    )
    
    if st.button("✏️ 生成仿写文案", disabled=not (reference_text and description and api_key)):
        with st.spinner("正在生成新文案..."):
            prompt = f"""请参考以下短视频文案风格：
{reference_text}

根据下面的创作需求，模仿该文案的节奏与风格，创作一段新的短视频文案：
{description}

文案应包含吸引开头、清晰逻辑、网络语言风格，不要太夸张但要有代入感，请用 markdown 格式输出。"""

            try:
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.6
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('choices') and data['choices'][0]:
                    st.session_state.last_generated = data['choices'][0]['message']['content']
                    st.markdown("### 生成的新文案：")
                    st.markdown(st.session_state.last_generated, unsafe_allow_html=True)
                else:
                    st.error("生成失败：" + json.dumps(data, ensure_ascii=False))
            except Exception as e:
                st.error(f"请求出错：{str(e)}")

with tab2:
    st.subheader("③ 文案优化")
    if not st.session_state.last_generated:
        st.warning("请先在'文案生成'标签页生成文案")
    else:
        st.markdown("### 当前文案：")
        st.markdown(st.session_state.last_generated, unsafe_allow_html=True)
        
        feedback = st.text_area(
            "输入修改建议：",
            height=150,
            placeholder="例如：希望更轻松一点，更像聊天语气，少用"你知道吗"开头"
        )
        
        if st.button("🔁 优化文案", disabled=not (feedback and api_key)):
            with st.spinner("正在优化文案..."):
                prompt = f"""这是我刚刚生成的短视频文案：

{st.session_state.last_generated}

请根据以下反馈意见，修改文案内容，并重新调整表达方式与风格：

【反馈】：
{feedback}

请输出优化后的完整文案，保持清晰、自然、有节奏，使用 markdown 格式输出。"""

                try:
                    response = requests.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.6
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('choices') and data['choices'][0]:
                        st.session_state.last_generated = data['choices'][0]['message']['content']
                        st.markdown("### 优化后的文案：")
                        st.markdown(st.session_state.last_generated, unsafe_allow_html=True)
                    else:
                        st.error("优化失败：" + json.dumps(data, ensure_ascii=False))
                except Exception as e:
                    st.error(f"请求出错：{str(e)}")