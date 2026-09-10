"""
联网搜索工具(封装 Tavily API)
"""
import os

from langchain_core.tools import tool
from tavily import TavilyClient


@tool
def search_from_web(question: str):
    """
    联网查找相关技术栈


    Args:
        question: 需要查找的问题

    Returns:
        返回找到最相关的10条信息
    """
    tavily_client = TavilyClient(api_key=str(os.getenv("TAIL_API_KEY")))


    response = tavily_client.search(question, max_results=10)
    return response




