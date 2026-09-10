"""
评估回答质量的 Prompt (含结构化输出 Schema)
"""
from typing import List, Optional

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


class EvaluationResult(BaseModel):
    """评估候选人回答的结构化输出"""
    is_correct: bool = Field(description="回答是否基本正确")
    need_deep_probe: bool = Field(description="是否需要基于 JD 进行深度追问")
    need_tool_call: bool = Field(description="是否需要调用工具(如执行代码/搜索)")
    tool_name: str = Field(default="", description="需要调用的工具名称，如 execute_python_code / search_web")
    feedback: str = Field(description="对候选人回答的简短评价")


class EvaluateOutput(BaseModel):
    """LLM 分析 JD 后的结构化输出"""
    interview_plan: List[str] = Field(description="针对 JD 生成的 5 个核心面试问题")
    knowledge_points: List[str] = Field(description="每个问题对应的知识点（与 interview_plan 一一对应）")


EVALUATE_SYSTEM_PROMPT = """你是一位严格的面试官。请评估候选人的回答质量。

评估标准：
1. 候选人的回答是否正确、完整
2. 是否需要基于回答进行深度追问（如果回答流于表面）
3. 是否需要调用工具来验证（涉及代码、数据或需要查证的信息）
4. 给出简短且有建设性的反馈

注意：仅根据当前问题和回答进行评估，不要引入外部知识。"""


def get_evaluate_prompt_template() -> ChatPromptTemplate:
    """获取评估 Prompt 模板"""
    return ChatPromptTemplate.from_messages([
        ("system", EVALUATE_SYSTEM_PROMPT),
        ("human", "问题：{question}\n\n候选人回答：{answer}")
    ])
