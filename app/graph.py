"""
LangGraph 核心编排 (定义节点、边、条件路由、编译 Graph)
"""
import uuid

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, END
from app.nodes.init_node import interview_init_node, ask_question_node
from app.nodes.evaluate_node import evaluate_answer_node, route_after_evaluation
from app.nodes.probe_node import probe_node
from app.nodes.review_node import review_node
from app.state import InterviewState
from app.tools.code_executor import execute_python_code
from app.tools.web_search import search_from_web


def tool_execution_node(state: InterviewState):
    """
    工具执行节点：根据 tool_name 调用相应工具，结果以 ToolMessage 返回
    """
    tool_name = state.get("tool_name", "")

    # 获取候选人最新回答作为工具输入
    human_msgs = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    last_answer = human_msgs[-1].content if human_msgs else ""

    tool_map = {
        "execute_python_code": execute_python_code,
        "python": execute_python_code,
        "search_from_web": search_from_web,
        "search_web": search_from_web,
        "web_search": search_from_web,
    }

    tool_fn = tool_map.get(tool_name)
    if not tool_fn:
        return {
            "messages": [ToolMessage(
                content=f"未知工具: {tool_name}，请选择可用工具: execute_python_code, search_from_web",
                name=tool_name
            )],
        }

    try:
        result = tool_fn.invoke(last_answer)
        result_str = str(result)
        # 截断过长的返回
        if len(result_str) > 3000:
            result_str = result_str[:3000] + "\n...(truncated)"
        return {
            "messages": [ToolMessage(content=result_str, name=tool_name)],
            "current_stage": "tools",
        }
    except Exception as e:
        return {
            "messages": [ToolMessage(content=f"工具执行出错: {type(e).__name__}: {e}", name=tool_name)],
        }


def build_interview_graph() -> StateGraph:
    """构建面试状态机图"""
    workflow = StateGraph(InterviewState)

    # 添加节点
    workflow.add_node("init", interview_init_node)
    workflow.add_node("ask", ask_question_node)
    workflow.add_node("evaluate", evaluate_answer_node)
    workflow.add_node("probe", probe_node)
    workflow.add_node("tools", tool_execution_node)
    workflow.add_node("review", review_node)

    # 设置入口
    workflow.set_entry_point("init")

    # 边：init → ask → evaluate
    workflow.add_edge("init", "ask")
    workflow.add_edge("ask", "evaluate")

    # 条件边：根据评估结果决定下一步
    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "ask": "ask",          # 回答合格 → 下一题
            "probe": "probe",      # 需要深挖 → 追问
            "tools": "tools",      # 需要调工具 → 执行工具
            "review": "review",    # 面试完成 → 复盘
        }
    )

    # probe / tools 执行完回到 evaluate
    workflow.add_edge("probe", "evaluate")
    workflow.add_edge("tools", "evaluate")

    # review 完成后结束
    workflow.add_edge("review", END)

    return workflow


def compile_graph(workflow: StateGraph):
    """编译图，配置 checkpointer 和中断"""
    app = workflow.compile(
        checkpointer=InMemorySaver(),
        interrupt_after=["ask", "probe"],  # 在 ask 或 probe 之后中断，等待用户输入
    )
    return app


def run_cli():
    """CLI 交互主循环"""
    workflow = build_interview_graph()
    app = compile_graph(workflow)

    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }

    jd_input = input('请输入JD：\n')
    initial_state = {
        "messages": [HumanMessage(content="你好，我准备好了，请开始面试。")],
        "jd": jd_input
    }

    # 第一次调用：执行 init → ask，然后中断等待回答
    app.invoke(initial_state, config)

    while True:
        snapshot = app.get_state(config)

        if snapshot.next == ():
            print('\n面试结束!')
            break

        # 显示 AI 最后一条消息（问题或追问）
        messages = snapshot.values.get("messages", [])
        if messages:
            last_msg = messages[-1]
            print(f"\n{last_msg.content}")

        user_input = input('\n候选人回答 (输入 quit 退出): ')
        if user_input.lower() == "quit":
            break

        # 注入用户输入到 state 并恢复执行
        app.update_state(config, {"messages": [HumanMessage(content=user_input)]})
        app.invoke(None, config)


if __name__ == '__main__':
    run_cli()
