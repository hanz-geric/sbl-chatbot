from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE = Path(__file__).parent
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_PATH = BASE / "chroma_db"
COLLECTION = "knowledge_base"
TOP_K = 3

embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
vector_store = Chroma(
    collection_name=COLLECTION,
    embedding_function=embeddings,
    persist_directory=str(DB_PATH),
)
retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K})