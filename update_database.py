import argparse
import os
import shutil
from langchain.document_loaders.pdf import PyPDFDirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from model_and_embedding import get_embedding_function, EMBEDDING_NAME
from langchain.vectorstores.chroma import Chroma


DATASET_PATH = "chroma_" + EMBEDDING_NAME
DOCUMENT_PATH = "documents"


def load_documents():
    # document_loader = PyMuPDFLoader("documents/成人糖尿病食养指南（2023年版）.pdf")
    document_loader = PyPDFDirectoryLoader(DOCUMENT_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
            "",
        ],
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    # 加载数据库。
    db = Chroma(
        persist_directory=DATASET_PATH, embedding_function=get_embedding_function()
    )

    # 计算页面ID。
    chunks_with_ids = calculate_chunk_ids(chunks)
    # print('\n\n'.join(str(d) for d in chunks_with_ids[:])); exit()

    # 读取现有文档。
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"数据库现有文档数量： {len(existing_ids)}")

    # 仅添加尚未存在于数据库中的文档。
    new_chunks = []
    for chunk in chunks_with_ids[:]:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 新增文档数量： {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
        print("✅ 添加完成。")
    else:
        print("✅ 没有需要添加的文档。")


def calculate_chunk_ids(chunks):
    # 文件ID格式： "documents/我是一个文件.pdf：第1页：2345"
    # 文件名：页数：起始位置

    # assert 0, "\n\n".join(str(ch) for ch in chunks[:5])

    # last_page_id = None
    # current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source").strip("documents/")
        page = chunk.metadata.get("page")
        start_index = chunk.metadata.get("start_index")
        current_page_id = f"{source}：第{page}页：{start_index}"

        # # If the page ID is the same as the last one, increment the index.
        # if current_page_id == last_page_id:
        #     current_chunk_index += 1
        # else:
        #     current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}"
        # last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(DATASET_PATH):
        shutil.rmtree(DATASET_PATH)


def main():
    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        clear_database()
        print("✨ 已清空数据库。")
        exit()

    # Create (or update) the data store.
    documents = load_documents()
    # assert 0, len(documents)
    # print(f"max: {max(len(pg.page_content) for pg in documents)}; min: {min(len(pg.page_content) for pg in documents)}")
    # print(f"aver: {sum(len(pg.page_content) for pg in documents)/len(documents)}")

    chunks = split_documents(documents)
    # assert 0, chunks[80]

    add_to_chroma(chunks)


if __name__ == "__main__":
    main()
