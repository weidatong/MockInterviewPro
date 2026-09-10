"""
评估回答，决定路由 (追问/换题/调工具/结束)
"""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.config import llm
from app.prompts.evaluate_prompt import EvaluationResult
from app.state import InterviewState

# 绑定结构化输出
structured_evaluator = llm.with_structured_output(EvaluationResult)


def evaluate_answer_node(state: InterviewState):
    """
    评估节点：根据候选人回答质量决定下一步路由
    :param state: 当前状态
    :return: 更新后的状态字段（含路由决策）
    """
    # 获取当前问题索引
    idx = state.get("current_question_index", 0)
    plan = state["interview_plan"]
    knowledge_points = state.get("knowledge_points", [])

    current_question = plan[idx] if idx < len(plan) else "面试已结束"
    current_kp = knowledge_points[idx] if idx < len(knowledge_points) else []
    kp_text = "、".join(current_kp) if isinstance(current_kp, list) else str(current_kp)

    # 获取候选人最新回答
    human_msgs = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    last_answer = human_msgs[-1].content if human_msgs else ""

    # 检查是否有工具返回结果，附加到 prompt 中
    tool_msgs = [m for m in state["messages"] if isinstance(m, ToolMessage)]
    tool_context = ""
    if tool_msgs:
        last_tool = tool_msgs[-1]
        tool_context = f"\n\n工具执行结果({last_tool.name}):\n{last_tool.content[:1000]}"

    # 调用 LLM 进行结构化评估
    prompt = f"问题：{current_question}\n\n候选人回答：{last_answer}{tool_context}"
    result = structured_evaluator.invoke(prompt)

    # 更新薄弱点
    weak_points = state.get("weak_points", [])
    if not result.is_correct and kp_text:
        if kp_text not in weak_points:
            weak_points = list(weak_points) + [kp_text]

    # 如果是工具返回后的再次评估，强制走正常判断（避免死循环）
    if tool_msgs:
        if result.is_correct:
            all_asked = idx >= len(plan) - 1
            if all_asked:
                return {
                    "messages": [AIMessage(content=result.feedback or "验证通过，所有问题已答完。")],
                    "current_stage": "evaluate",
                    "weak_points": weak_points,
                    "route_decision": "review",
                }
            else:
                return {
                    "messages": [AIMessage(content=result.feedback or "验证通过，我们继续下一题。")],
                    "current_stage": "evaluate",
                    "current_question_index": idx + 1,
                    "weak_points": weak_points,
                    "route_decision": "ask",
                }
        else:
            return {
                "messages": [AIMessage(content=result.feedback or "验证未通过，需要进一步探讨。")],
                "current_stage": "evaluate",
                "weak_points": weak_points,
                "route_decision": "probe",
            }

    # 决定路由（非工具场景）
    all_asked = idx >= len(plan) - 1

    if result.need_tool_call:
        tool_name = result.tool_name or "execute_python_code"
        return {
            "messages": [AIMessage(content=f"需要调用工具({tool_name})进行验证。")],
            "current_stage": "evaluate",
            "weak_points": weak_points,
            "route_decision": "tools",
            "tool_name": tool_name,
        }
    elif result.need_deep_probe or not result.is_correct:
        return {
            "messages": [AIMessage(content=result.feedback)],
            "current_stage": "evaluate",
            "weak_points": weak_points,
            "route_decision": "probe",
        }
    else:
        # 回答正确
        if all_asked:
            return {
                "messages": [AIMessage(content=result.feedback or "所有问题已答完，准备复盘。")],
                "current_stage": "evaluate",
                "weak_points": weak_points,
                "route_decision": "review",
            }
        else:
            return {
                "messages": [AIMessage(content=result.feedback or "回答不错，我们继续下一题。")],
                "current_stage": "evaluate",
                "current_question_index": idx + 1,
                "weak_points": weak_points,
                "route_decision": "ask",
            }


def route_after_evaluation(state: InterviewState) -> str:
    """
    根据评估结果的路由决策，决定下一步走向
    :param state: 当前状态
    :return: 下一个节点名称
    """
    decision = state.get("route_decision", "ask")
    return decision
