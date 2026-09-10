"""
解析JD，生成面试计划
"""
from langchain_core.messages import AIMessage

from app.config import llm
from app.prompts.evaluate_prompt import EvaluateOutput
from app.state import InterviewState

structured_llm = llm.with_structured_output(EvaluateOutput)


def interview_init_node(state: InterviewState):
    """
    初始化节点：解析 JD，生成面试计划
    :param state: 当前状态（包含 jd 字段）
    :return: 更新后的状态字段
    """
    plan = analyze_jd(state['jd'])
    print("面试计划生成完毕:", plan.interview_plan)

    return {
        "messages": [AIMessage(content="你好，我已经读取你的JD，准备开始面试。")],
        "interview_plan": plan.interview_plan,
        "knowledge_points": plan.knowledge_points,
        "current_stage": "init",
        "current_question_index": 0,
        "weak_points": [],
    }


def ask_question_node(state: InterviewState):
    """
    提问节点：从 interview_plan 中取出当前问题并提问
    :param state: 当前状态
    :return: 更新后的状态字段
    """
    plan = state["interview_plan"]
    idx = state.get("current_question_index", 0)

    if idx >= len(plan):
        return {
            "messages": [AIMessage(content="所有问题已问完，准备生成复盘报告。")],
            "current_stage": "finish",
        }

    question = plan[idx]

    return {
        "messages": [AIMessage(content=f"问题：{question}")],
        "current_stage": "ask",
    }


def analyze_jd(jd: str) -> EvaluateOutput:
    """
    调用 LLM 分析 JD，生成面试问题和对应知识点
    :param jd: 岗位描述文本
    :return: 结构化输出（问题列表 + 知识点列表）
    """
    prompt = f"""
    请分析下面的JD，生成5个核心面试问题，并标注每个问题考察的知识点。

    JD: {jd}
    """
    result = structured_llm.invoke(prompt)
    return result
