import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_community.llms.openai import OpenAI

from model_and_embedding import get_embedding_function, OLLAMA_MODEL_NAME, OpenAI_MODEL_NAME

from update_database import DATASET_PATH

import time

PROMPT_TEMPLATE = """
作为精通中文的、专业的糖尿病问诊系统的虚拟医生，假设你有以下知识：
{context}
---

请用简体中文回答病人的提问：{question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def query_rag(query_text: str, option: int = 0):
    t0 = time.time()
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(
        persist_directory=DATASET_PATH,
        embedding_function=embedding_function
    )

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)
    for doc, _score in results:
        print(doc)
        print(f"score: {_score}")
    print('\n')

    relevant_docs = [doc.page_content for doc, _score in results if _score <= 100.0]
    if len(relevant_docs) != 0:
        context_text = "\n\n---\n\n".join(relevant_docs)
        
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
    else:
        prompt = query_text
    print(f"问题：\n{prompt}")

    if option == 0:
        model = Ollama(model="gemma")
    else:
        model = Ollama(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q8")
    # model = Ollama(model=OLLAMA_MODEL_NAME)
    # model = OpenAI(model=OpenAI_MODEL_NAME)
    response_text = model.invoke(prompt)
    response_text += "\n\n"
    print(f"回答：\n{response_text}")

    sources: list[str] = [doc.metadata.get("id", None) for doc, _score in results if _score <= 100.0]
    print(f"来源：{sources}")

    t1 = time.time()
    print(f"耗时：{t1 - t0}秒。")

    source_title_and_page: dict[str, list[str]] = {}
    for s in sources:
        source_info = s.split("：")
        title = source_info[0].strip(".pdf")
        page = source_info[1]
        if title not in source_title_and_page:
            source_title_and_page[title] = []
        source_title_and_page[title].append(page)
    source_list = []
    for k, v in source_title_and_page.items():
        # v = v.sort()
        src = k + "：" + "、".join(v)
        source_list.append(f"- _{src}_")

    if len(source_list) > 0:
        response_text += "_参考文档：_\n\n" + "\n\n".join(source_list)

    return response_text


if __name__ == "__main__":
    main()
