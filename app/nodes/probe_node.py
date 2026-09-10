"""
深度追问节点(结合RAG)
"""
import logging

from langchain_core.messages import AIMessage, HumanMessage

logging.getLogger("pymilvus").setLevel(logging.WARNING)

from app.config import llm
from app.prompts.probe_prompt import PROBE_SYSTEM_PROMPT, PROBE_HUMAN_TEMPLATE
from app.state import InterviewState
from app.tools.rag_search import rag_search


def probe_node(state: InterviewState):
    """
    深度追问节点：根据候选人回答中的薄弱点，生成针对性追问
    :param state: 当前状态
    :return: 包含追问问题的 AI 消息
    """
    # 获取当前问题索引
    idx = state.get("current_question_index", 0)
    plan = state["interview_plan"]
    knowledge_points = state.get("knowledge_points", [])

    current_question = plan[idx] if idx < len(plan) else ""
    current_kp_raw = knowledge_points[idx] if idx < len(knowledge_points) else []
    current_kp = "、".join(current_kp_raw) if isinstance(current_kp_raw, list) else str(current_kp_raw)

    # 获取候选人最新回答
    human_msgs = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    last_answer = human_msgs[-1].content if human_msgs else ""

    # 获取薄弱点
    weak_points = state.get("weak_points", [])

    # 构建追问对话历史（让 LLM 了解已经问过什么，避免重复或跑题）
    conversation_history_lines = []
    for msg in state["messages"]:
        if isinstance(msg, AIMessage):
            content = msg.content or ""
            if content.startswith("追问：") or content.startswith("追问"):
                conversation_history_lines.append(f"面试官追问：{content.replace('追问：', '').strip()}")
        elif isinstance(msg, HumanMessage):
            content = msg.content or ""
            if content and content not in ("你好，我准备好了，请开始面试。", last_answer):
                conversation_history_lines.append(f"候选人回答：{content[:200]}")
    conversation_history = "\n".join(conversation_history_lines[-6:]) or "暂无"

    # 尝试用 RAG 检索相关知识，生成更深入的追问
    rag_context = ""
    try:
        rag_result = rag_search.invoke(current_question)
        rag_context = str(rag_result)[:500]
    except Exception:
        rag_context = ""

    # 构造追问 prompt
    probe_prompt = PROBE_HUMAN_TEMPLATE.format(
        question=current_question,
        answer=last_answer,
        weak_points="、".join(weak_points) if weak_points else "回答不够深入",
        knowledge_points=current_kp if current_kp else "",
        conversation_history=conversation_history,
        rag_context=rag_context,
    )

    # 调用 LLM 生成追问
    response = llm.invoke([
        {"role": "system", "content": PROBE_SYSTEM_PROMPT},
        {"role": "user", "content": probe_prompt},
    ])

    probe_question = response.content if hasattr(response, 'content') else str(response)

    return {
        "messages": [AIMessage(content=f"追问：{probe_question}")],
        "current_stage": "probe",
    }
