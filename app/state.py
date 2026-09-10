"""
LangGraph State 定义 (InterviewState TypedDict)
"""
import operator
from typing import TypedDict, Annotated, Sequence, Literal

from langchain_core.messages import BaseMessage


class InterviewState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    interview_plan: list              # 面试问题计划列表
    current_stage: str                # 当前阶段: init / ask / evaluate / probe / review / finish
    current_question_index: int       # 当前面试问题索引（用于正确追踪到哪一题）
    weak_points: list                 # 长期记忆：薄弱知识点列表
    knowledge_points: list            # 知识点列表（与 interview_plan 一一对应）
    jd: str                           # 岗位描述原文
    route_decision: Literal["ask", "probe", "review", "tools"]  # 评估后的路由决策
    tool_name: str                        # 需要调用的工具名称（tools 路由时使用）
