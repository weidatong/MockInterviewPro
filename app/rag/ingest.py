"""
文档加载、切分、向量化入库逻辑
"""
import os
from langchain_community.document_loaders import (
    TextLoader,
    PDFPlumberLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import embedding_model, Milvus_client


class RAGIngestor:
    def __init__(self, data_dir: str, collection_name: str):
        self.data_dir = data_dir
        self.collection_name = collection_name

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000,
            chunk_overlap=200,
            add_start_index=True,
        )
        if not Milvus_client.has_collection(collection_name):
            Milvus_client.create_collection(collection_name, dimension=4096, metric_type='COSINE', auto_id=True)

    # 自动选择 loader
    def load_single_file(self, file_path: str):
        ext = file_path.lower().split(".")[-1]

        if ext == "txt":
            loader = TextLoader(file_path, encoding="utf-8")
        elif ext == "md":
            loader = UnstructuredMarkdownLoader(file_path)
        elif ext == "pdf":
            loader = PDFPlumberLoader(file_path)
        elif ext in ("doc", "docx"):
            loader = UnstructuredWordDocumentLoader(file_path)
        else:
            print(f"Unsupported file type: {file_path}")
            return []

        return loader.load()

    # 加载目录下所有文件
    def load_docs(self):
        docs = []
        for root, _, files in os.walk(self.data_dir):
            for f in files:
                file_path = os.path.join(root, f)
                docs.extend(self.load_single_file(file_path))
        return docs

    # 分割单个文档
    def process_single_doc(self, doc):
        chunks = self.splitter.split_documents([doc])
        vectors = embedding_model.embed_documents(
            [chunk.page_content for chunk in chunks]
        )

        return [
            {
                "vector": vectors[i],
                "text": chunks[i].page_content,
                "source": chunks[i].metadata.get("source", "unknown"),
            }
            for i in range(len(vectors))
        ]

    def insert_to_milvus(self, rows):
        Milvus_client.insert(collection_name=self.collection_name, data=rows)
        Milvus_client.flush(collection_name=self.collection_name)

    def run(self):
        docs = self.load_docs()
        total = 0

        for doc in docs:
            rows = self.process_single_doc(doc)
            self.insert_to_milvus(rows)
            total += len(rows)

        print(f"Inserted {total} rows into {self.collection_name}.")


if __name__ == "__main__":
    collection_name = str(os.getenv('COLLECTION_NAME'))
    ingestor = RAGIngestor(data_dir="../../data/jds", collection_name=collection_name)
    ingestor.run()















