"""
RAG 检索器工具
"""
from langchain_core.tools import tool

from app.rag.retriever import Retriever


@tool
def rag_search(query: str) -> str:
    """
    根据查询问题返回相关文档
    :param query: 查询问题
    :return: 相关文档
    """
    retriever = Retriever()
    return retriever.retrieve(query)






