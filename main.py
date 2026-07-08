from app.config import agent
from app.rag.retriever import Retriever


def generate_answer(question: str):

    retriever = Retriever().retrieve(question)

    context_blocks = []
    for i, hit in enumerate(retriever, 1):
        text = hit['entity']['text']
        source = hit['entity'].get('source', 'unknown')
        score = hit['distance']

        print(f"[{i}] score: {score} source: {source}")
        print(text)
        print()

        context_blocks.append(f"source={source}\n{text}]")

    context = "\n\n".join(context_blocks)

    user_prompt = f"""
                        问题: {question}

                        上下文: {context}
                    """

    config = {
        "configurable": {
            "thread_id": "1",
        }
    }

    for chunk in agent.stream({
        "messages": [{
            "role": 'user',
            'content': user_prompt,
        }]
    }, config=config, stream_mode='messages'):
        print(chunk[0].content, end='', flush=True)


if __name__ == '__main__':
    while True:
        user_input = input("请输入问题：")
        if user_input == "exit":
            break
        generate_answer(user_input)





