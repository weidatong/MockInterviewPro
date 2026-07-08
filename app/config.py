"""
全局配置 (加载 .env，初始化 LLM、Embeddings 模型实例)
"""
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from pymilvus import MilvusClient
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import OllamaEmbeddings

from app.memory.long_term import InMemoryStore_PostgreSQL
from app.prompts.init_prompt import system_prompt

load_dotenv(override=True)

checkpoint = InMemorySaver()

store = InMemoryStore_PostgreSQL()

deepseek_model = ChatDeepSeek(
    model=str(os.getenv('CHAT_MODEL'))
)

embedding_model = OllamaEmbeddings(
    model=str(os.getenv('EMBEDDING_MODEL')),
    base_url=str(os.getenv('EMBEDDING_HOST'))
)


agent = create_agent(
    model=deepseek_model,
    tools=[],
    store=store,
    # checkpointer=checkpoint,
    system_prompt=system_prompt,
)

Milvus_client = MilvusClient(uri=os.getenv('MILVUS_URI'))

existed_databases = Milvus_client.list_databases()

if str(os.getenv('DB_NAME')) not in existed_databases:
    Milvus_client.create_database(str(os.getenv('DB_NAME')))

Milvus_client.use_database(db_name=str(os.getenv('DB_NAME')))




