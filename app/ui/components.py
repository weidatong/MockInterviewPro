"""
自定义 UI 组件（折叠面板展示 Agent 思考过程、状态可视化等）
"""
import streamlit as st


def render_sidebar(state: dict):
    """
    渲染侧边栏：展示面试状态、知识图谱、薄弱点等
    :param state: 当前图状态 values
    """
    st.sidebar.title("MockInterview Pro")

    # 当前阶段
    current_stage = state.get("current_stage", "未开始")
    st.sidebar.subheader("当前阶段")
    stage_map = {
        "init": "📄 初始化",
        "ask": "❓ 提问中",
        "evaluate": "📊 评估中",
        "probe": "🔍 深度追问",
        "review": "📋 生成复盘",
        "tools": "🛠️ 执行工具",
        "finish": "✅ 已结束",
    }
    st.sidebar.info(stage_map.get(current_stage, current_stage))

    # 进度
    plan = state.get("interview_plan", [])
    idx = state.get("current_question_index", 0)
    if plan:
        st.sidebar.subheader("面试进度")
        st.sidebar.progress(min(idx / len(plan), 1.0))
        st.sidebar.caption(f"第 {min(idx + 1, len(plan))}/{len(plan)} 题")

    # 薄弱知识点
    weak_points = state.get("weak_points", [])
    if weak_points:
        st.sidebar.subheader("📌 薄弱知识点")
        for wp in weak_points:
            st.sidebar.warning(f"• {wp}")

    # 面试问题计划（可折叠）
    if plan:
        with st.sidebar.expander("📋 面试问题计划", expanded=False):
            for i, q in enumerate(plan):
                done = i < idx
                prefix = "✅" if done else "⏳"
                st.markdown(f"{prefix} **Q{i + 1}**: {q}")

    # 消息统计
    messages = state.get("messages", [])
    st.sidebar.subheader("对话统计")
    st.sidebar.metric("消息总数", len(messages))


def render_chat_message(role: str, content: str):
    """
    统一渲染聊天消息
    :param role: 'user' 或 'assistant'
    :param content: 消息内容
    """
    with st.chat_message(role):
        if "复盘报告" in content or "##" in content:
            st.markdown(content)
        else:
            st.write(content)


def render_file_uploader():
    """
    渲染文件上传组件，支持上传 JD 和简历 PDF
    :return: 上传的文件内容（文本）
    """
    uploaded_file = st.file_uploader(
        "上传 JD 或简历 (支持 PDF/TXT/MD)",
        type=["pdf", "txt", "md"],
        key="jd_uploader"
    )
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            try:
                from langchain_community.document_loaders import PDFPlumberLoader
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                loader = PDFPlumberLoader(tmp_path)
                docs = loader.load()
                os.unlink(tmp_path)
                return "\n".join([d.page_content for d in docs])
            except Exception as e:
                st.error(f"PDF 解析失败: {e}")
                return uploaded_file.getvalue().decode("utf-8", errors="ignore")
        else:
            return uploaded_file.getvalue().decode("utf-8", errors="ignore")
    return None


def render_history_panel():
    """
    渲染历史面试记录面板（侧边栏）
    显示过往面试列表，点击可查看对话详情
    """
    history = st.session_state.get("interview_history", [])

    with st.sidebar.expander("📜 历史面试记录", expanded=False):
        if not history:
            st.caption("暂无历史记录")
            return

        for i, record in enumerate(history):
            label = f"#{i + 1} {record.get('jd_summary', '未知')}"
            if st.button(label, key=f"history_{i}", use_container_width=True):
                st.session_state.viewing_history_index = i
                st.rerun()

    # 如果正在查看某条历史记录，显示其对话
    viewing_idx = st.session_state.get("viewing_history_index", -1)
    if viewing_idx >= 0 and viewing_idx < len(history):
        record = history[viewing_idx]
        _render_history_detail(record)


def _render_history_detail(record: dict):
    """
    渲染单条历史记录的详情
    :param record: 历史记录字典
    """
    with st.sidebar.container():
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### 📖 历史对话 #{record.get('id', '?')}")
        st.sidebar.caption(f"📅 {record.get('date', '')}")
        st.sidebar.caption(f"📄 {record.get('jd_summary', '')}")

        if record.get("weak_points"):
            with st.sidebar.expander("📌 薄弱知识点"):
                for wp in record["weak_points"]:
                    st.sidebar.warning(f"• {wp}")

        # 展开查看完整对话
        with st.sidebar.expander("💬 查看完整对话", expanded=False):
            msgs = record.get("messages", [])
            for role, content in msgs:
                if role == "user":
                    st.markdown(f"**🧑 你**: {content[:200]}{'...' if len(content) > 200 else ''}")
                else:
                    st.markdown(f"**🤖 面试官**: {content[:200]}{'...' if len(content) > 200 else ''}")
                st.markdown("---")

        if st.button("关闭", key=f"close_history_{record.get('id', '')}"):
            st.session_state.viewing_history_index = -1
            st.rerun()
