'''Defines what model and embeddings used.'''

import dotenv
dotenv.load_dotenv(verbose=True)

from langchain_community.embeddings.ollama import OllamaEmbeddings

# OLLAMA_MODEL_NAME = "llama3"
# OLLAMA_MODEL_NAME = "gemma"
OLLAMA_MODEL_NAME = "wangshenzhi/llama3-8b-chinese-chat-ollama-q8"

# OLLAMA_EMBEDDING_NAME = "nomic-embed-text"
OLLAMA_EMBEDDING_NAME = "shaw/dmeta-embedding-zh"

from langchain_openai import OpenAIEmbeddings
OpenAI_MODEL_NAME = "gpt-3.5-turbo"
OpenAI_EMBEDDING_NAME = "text-embedding-3-small"


# EMBEDDING_PROVIDER = "Ollama"
EMBEDDING_PROVIDER = "OpenAI"


_EMBEDDING_MAP = {
    "Ollama": OllamaEmbeddings(
        model=OLLAMA_EMBEDDING_NAME,
        embed_instruction="文档：",
        query_instruction="询问："
    ),
    "OpenAI": OpenAIEmbeddings(
        model=OpenAI_EMBEDDING_NAME,
    )
}

_EMBEDDING_NAMES = {
    "Ollama": OLLAMA_EMBEDDING_NAME,
    "OpenAI": OpenAI_EMBEDDING_NAME,
}


EMBEDDING_NAME = _EMBEDDING_NAMES[EMBEDDING_PROVIDER]


def get_embedding_function():
    embeddings = _EMBEDDING_MAP[EMBEDDING_PROVIDER]
    return embeddings
