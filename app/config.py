"""
全局配置 (加载 .env，初始化 LLM、Embeddings 模型实例)
"""
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from pymilvus import MilvusClient
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import OllamaEmbeddings

load_dotenv(override=True)

# ===== Checkpointer (短期记忆) =====
checkpoint = InMemorySaver()

# ===== LLM 实例 =====
# 主要聊天模型 (用于结构化输出等)
llm = init_chat_model(model='deepseek-chat')

# DeepSeek 模型 (用于 Agent)
deepseek_model = ChatDeepSeek(
    model=str(os.getenv('CHAT_MODEL', 'deepseek-chat'))
)

# ===== Embedding 模型 =====
embedding_model = OllamaEmbeddings(
    model=str(os.getenv('EMBEDDING_MODEL', 'qwen3-embedding:8b')),
    base_url=str(os.getenv('EMBEDDING_HOST', 'http://localhost:11434'))
)

# ===== Milvus 向量数据库 =====
Milvus_client = MilvusClient(uri=os.getenv('MILVUS_URI', 'http://localhost:19530'))

db_name = str(os.getenv('DB_NAME', 'mock_interview_pro'))
existing_databases = Milvus_client.list_databases()

if db_name not in existing_databases:
    Milvus_client.create_database(db_name)

Milvus_client.use_database(db_name=db_name)
