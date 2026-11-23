from pathlib import Path
from types import SimpleNamespace

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE = Path(__file__).parent
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_PATH = BASE / "chroma_db"
COLLECTION = "knowledge_base"
TOP_K = 3
CANDIDATES = 12
HAND_CHECKED_BONUS = 0.1

embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
vector_store = Chroma(
    collection_name=COLLECTION,
    embedding_function=embeddings,
    persist_directory=str(DB_PATH),
)


def rank(results):
    def adjusted(result):
        doc, distance = result
        return distance - HAND_CHECKED_BONUS if doc.metadata["id"].startswith("K") else distance

    return [doc for doc, _ in sorted(results, key=adjusted)[:TOP_K]]


def search(query):
    return rank(vector_store.similarity_search_with_score(query, k=CANDIDATES))


retriever = SimpleNamespace(invoke=search)
