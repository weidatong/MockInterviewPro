"""
生成最终复盘报告
"""
from langchain_core.messages import AIMessage, HumanMessage

from app.config import llm
from app.prompts.review_prompt import REVIEW_SYSTEM_PROMPT, REVIEW_HUMAN_TEMPLATE
from app.state import InterviewState


def review_node(state: InterviewState):
    """
    复盘节点：面试结束后，结合薄弱点生成深度复盘报告
    :param state: 当前状态（包含完整消息历史、薄弱点列表）
    :return: 包含复盘报告的 AI 消息
    """
    messages = state["messages"]
    qa_records = _extract_qa_pairs(messages, state.get("interview_plan", []))
    weak_points = state.get("weak_points", [])

    if not qa_records:
        qa_records = [{"question": "未记录问题", "answer": ""}]

    qa_text = "\n\n".join([
        f"**问题 {i + 1}**: {qa['question']}\n**回答**: {qa['answer'] or '（未回答）'}"
        for i, qa in enumerate(qa_records)
    ])
    weak_points_text = "\n".join([f"- {wp}" for wp in weak_points]) if weak_points else "（无显著薄弱点）"

    prompt = REVIEW_HUMAN_TEMPLATE.format(
        jd=state.get("jd", "（未提供）"),
        qa_records=qa_text,
        weak_points_text=weak_points_text,
    )

    response = llm.invoke([
        {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    report_content = response.content if hasattr(response, 'content') else str(response)

    return {
        "messages": [AIMessage(content=f"## 📋 面试复盘报告\n\n{report_content}")],
        "current_stage": "review",
    }


def _extract_qa_pairs(messages, interview_plan):
    """
    从消息历史中提取 QA 对
    """
    qa_pairs = []
    last_question = ""

    for msg in messages:
        if isinstance(msg, AIMessage):
            content = msg.content or ""
            if "问题：" in content:
                last_question = content.replace("问题：", "").strip()
            elif "追问：" in content:
                last_question = content.replace("追问：", "").strip()
        elif isinstance(msg, HumanMessage):
            content = msg.content or ""
            if content in ("你好，我准备好了，请开始面试。",):
                continue
            if last_question:
                qa_pairs.append({"question": last_question, "answer": content})
                last_question = ""

    if not qa_pairs and interview_plan:
        human_msgs = [m for m in messages if isinstance(m, HumanMessage)
                      and m.content not in ("你好，我准备好了，请开始面试。",)]
        for i, q in enumerate(interview_plan):
            answer = human_msgs[i].content if i < len(human_msgs) else ""
            qa_pairs.append({"question": q, "answer": answer})

    return qa_pairs
