"""
长期记忆管理 (读写 SQLite/JSON，管理 weak_points)
"""
import os

from dotenv import load_dotenv

load_dotenv(override=True)

from langgraph.store.postgres import PostgresStore


def InMemoryStore_PostgreSQL():

    with PostgresStore.from_conn_string(os.getenv('POSTGRESQL_URL')) as store:
        store.setup()

    return store

print(InMemoryStore_PostgreSQL())
