"""
检索器封装 (根据 Query 动态检索)
"""
import os

from app.config import embedding_model, Milvus_client


class Retriever:

    def retrieve(self, question, limit = 10):
        """
        输入用户问题，通过向量化从Milvus中找回最相关的limit个文本片段
        :param question: 用户问题
        :param limit: 返回数据限制
        :return:
        """
        query_vector = embedding_model.embed_query(question)

        results = Milvus_client.search(
            collection_name=str(os.getenv('COLLECTION_NAME')),
            data=[query_vector],
            limit=limit,
            output_fields=['text', 'source'],
        )
        return results[0]


