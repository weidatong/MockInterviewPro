"""
长期记忆管理 (读写 SQLite/JSON，管理 weak_points)
"""
import os

from dotenv import load_dotenv
from langgraph.store.postgres import PostgresStore

load_dotenv(override=True)


def get_postgres_store():
    """获取 PostgreSQL store 实例（作为长期记忆存储）"""
    connection_string = os.getenv('POSTGRESQL_URL')
    if not connection_string:
        raise ValueError("POSTGRESQL_URL 环境变量未设置")

    store = PostgresStore.from_conn_string(connection_string)
    store.setup()
    return store
