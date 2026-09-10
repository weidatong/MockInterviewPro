"""
Streamlit 主程序 (聊天界面、文件上传)

启动方式：
    streamlit run app/ui/streamlit_app.py
"""
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from langchain_core.messages import HumanMessage
from app.graph import build_interview_graph, compile_graph
from app.memory.history_store import HistoryStore
from app.ui.components import (
    render_sidebar,
    render_chat_message,
    render_file_uploader,
    render_history_panel,
)


def init_session():
    """初始化 session state"""
    if "graph" not in st.session_state:
        # PostgreSQL history store
        try:
            st.session_state.history_store = HistoryStore()
            st.session_state.history_store_ok = True
        except Exception as e:
            st.session_state.history_store = None
            st.session_state.history_store_ok = False
            print(f"PostgreSQL 存储初始化失败: {e}")

        workflow = build_interview_graph()
        app = compile_graph(workflow)
        st.session_state.graph = app
        st.session_state.config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        st.session_state.interview_started = False
        st.session_state.interview_finished = False
        st.session_state.jd_text = ""
        st.session_state.cached_messages = []
        st.session_state.awaiting_input = False
        st.session_state.interview_history = _load_history_from_db()
        st.session_state.viewing_history_index = -1
        st.session_state.history_jd = ""
        st.session_state.processing = False
        st.session_state.pending_input = None


def do_start_interview():
    """执行面试启动（invoke 图），结果写入 session_state"""
    graph = st.session_state.graph
    config = st.session_state.config
    jd = st.session_state.jd_text

    initial_state = {
        "messages": [HumanMessage(content="你好，我准备好了，请开始面试。")],
        "jd": jd,
    }

    graph.invoke(initial_state, config)
    st.session_state.interview_started = True
    st.session_state.history_jd = jd

    snapshot = graph.get_state(config)
    _cache_messages(snapshot)


def do_resume_interview(user_input: str):
    """恢复面试执行"""
    graph = st.session_state.graph
    config = st.session_state.config

    graph.update_state(config, {"messages": [HumanMessage(content=user_input)]})
    graph.invoke(None, config)

    snapshot = graph.get_state(config)
    _cache_messages(snapshot)

    if hasattr(snapshot, 'next') and snapshot.next == ():
        st.session_state.interview_finished = True
        st.session_state.awaiting_input = False
        _save_to_history()
    else:
        st.session_state.awaiting_input = True


def do_quit_interview():
    """
    退出当前面试，保存历史记录，回到欢迎界面
    """
    if st.session_state.interview_started and not st.session_state.interview_finished:
        # 强制结束面试
        st.session_state.interview_finished = True
        st.session_state.awaiting_input = False
        _save_to_history()

    # 重置面试状态，回到欢迎界面
    st.session_state.interview_started = False
    st.session_state.interview_finished = False
    st.session_state.awaiting_input = False
    st.session_state.cached_messages = []
    st.session_state.jd_text = ""
    st.session_state.processing = False
    st.session_state.pending_input = None


def _load_history_from_db() -> list:
    """从 PostgreSQL 加载历史记录"""
    store = st.session_state.get("history_store")
    if store:
        try:
            return store.load_all()
        except Exception as e:
            print(f"从 PostgreSQL 加载历史记录失败: {e}")
    return []


def _save_history_to_db(record: dict):
    """将一条历史记录存入 PostgreSQL"""
    store = st.session_state.get("history_store")
    if not store:
        return
    try:
        new_id = store.append(record)
        record["id"] = new_id
    except Exception as e:
        print(f"保存历史记录到 PostgreSQL 失败: {e}")


def _save_to_history():
    """
    将当前面试保存到历史记录（PostgreSQL + session_state）
    """
    msgs = st.session_state.cached_messages
    if not msgs:
        return

    # 避免重复保存（已经保存过的就不再保存）
    jd = st.session_state.history_jd
    for record in st.session_state.interview_history:
        if record.get("jd") == jd and record.get("messages") == msgs:
            return

    # 提取 JD 摘要（取前 30 字）
    jd_summary = jd.strip()[:30] + "..." if len(jd.strip()) > 30 else jd.strip()

    # 从图状态获取薄弱点
    weak_points = []
    try:
        snap = st.session_state.graph.get_state(st.session_state.config)
        state_values = snap.values if hasattr(snap, 'values') else {}
        weak_points = state_values.get("weak_points", [])
    except Exception:
        weak_points = []

    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "jd": jd,
        "jd_summary": jd_summary,
        "messages": msgs.copy(),
        "weak_points": weak_points,
    }

    # 先写入 DB（获取自增 id），再追加到 session_state
    _save_history_to_db(record)  # 在 record 中设置 id
    if "id" not in record:
        record["id"] = len(st.session_state.interview_history) + 1
    st.session_state.interview_history.append(record)


def _cache_messages(snapshot):
    """从 snapshot 提取消息并缓存到 session_state"""
    values = snapshot.values if hasattr(snapshot, 'values') else {}
    msgs = values.get("messages", []) if isinstance(values, dict) else []
    result = []
    for msg in msgs:
        if isinstance(msg, HumanMessage):
            content = msg.content or ""
            if content == "你好，我准备好了，请开始面试。":
                continue
            result.append(("user", content))
        else:
            content = msg.content or ""
            if content:
                result.append(("assistant", content))
    st.session_state.cached_messages = result


def render_history_view():
    """
    在主区域渲染选中的历史对话
    """
    idx = st.session_state.get("viewing_history_index", -1)
    history = st.session_state.get("interview_history", [])
    if idx < 0 or idx >= len(history):
        return False

    record = history[idx]
    st.markdown("---")
    st.markdown(f"## 📖 历史对话 #{record['id']}")
    st.caption(f"📅 {record['date']}  |  📄 {record['jd_summary']}")

    if record.get("weak_points"):
        with st.expander("📌 薄弱知识点"):
            for wp in record["weak_points"]:
                st.warning(f"• {wp}")

    for role, content in record["messages"]:
        render_chat_message(role, content)

    if st.button("关闭历史对话"):
        st.session_state.viewing_history_index = -1
        st.rerun()

    return True


# ==== 页面主体 ====
st.set_page_config(page_title="MockInterview Pro", page_icon="🎯", layout="wide")
st.title("MockInterview Pro - 智能模拟面试官")

init_session()

# ===== 侧边栏 =====
with st.sidebar:
    # 退出面试按钮（只在面试进行中显示）
    if st.session_state.interview_started and not st.session_state.interview_finished:
        if st.button("🚪 退出面试", type="secondary", use_container_width=True):
            do_quit_interview()
            st.rerun()

    # 当前面试状态
    snapshot_values = {}
    if st.session_state.interview_started:
        try:
            snap = st.session_state.graph.get_state(st.session_state.config)
            snapshot_values = snap.values if hasattr(snap, 'values') else {}
        except Exception:
            snapshot_values = {}
    render_sidebar(snapshot_values)

    # 历史面试记录
    render_history_panel()

# ===== 主聊天区域 =====

# 优先显示历史对话查看
if render_history_view():
    pass

# 显示当前面试消息（缓存）
elif st.session_state.cached_messages:
    for role, content in st.session_state.cached_messages:
        render_chat_message(role, content)

    if st.session_state.get("processing"):
        # 用户消息已显示，展示思考动画后处理
        with st.chat_message("assistant"):
            st.markdown("🤔 **思考中...**")
        try:
            with st.spinner("正在评估回答..."):
                do_resume_interview(st.session_state.pending_input)
        except Exception as e:
            st.error(f"处理出错: {e}")
            st.session_state.interview_finished = True
            st.session_state.awaiting_input = False
        st.session_state.processing = False
        st.session_state.pending_input = None
        st.rerun()

    elif st.session_state.interview_finished:
        st.success("面试已结束！")
        if st.button("🔄 重新开始"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    elif st.session_state.awaiting_input:
        user_input = st.chat_input("请输入你的回答...")
        if user_input:
            # 立即显示用户消息，再交给 AI 处理
            st.session_state.cached_messages.append(("user", user_input))
            st.session_state.pending_input = user_input
            st.session_state.processing = True
            st.rerun()

# 面试未开始 → 欢迎界面
elif not st.session_state.interview_started:
    st.markdown("""
    ## 欢迎使用 MockInterview Pro 👋

    请上传岗位描述（JD）或直接粘贴到下方文本框，开始模拟面试。

    支持的输入方式：
    - **上传文件**：PDF / TXT / Markdown
    - **手动粘贴**：直接将 JD 文本粘贴到输入框
    """)

    uploaded_text = render_file_uploader()
    if uploaded_text:
        st.session_state.jd_text = uploaded_text

    jd_input = st.text_area(
        "粘贴 JD 文本",
        value=st.session_state.jd_text,
        height=200,
        placeholder="请粘贴岗位描述（JD）...",
        key="jd_input_area"
    )

    if st.button("🚀 开始面试", type="primary", disabled=not jd_input.strip()):
        if jd_input.strip():
            st.session_state.jd_text = jd_input.strip()
            try:
                with st.spinner("正在分析 JD 并生成面试计划..."):
                    do_start_interview()
            except Exception as e:
                st.error(f"启动面试失败: {e}")
                st.session_state.interview_started = False
                st.stop()
            st.session_state.awaiting_input = True
            st.rerun()
