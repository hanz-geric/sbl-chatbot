import json
import re
import shutil
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE = Path(__file__).parent
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_PATH = BASE / "chroma_db"
COLLECTION = "knowledge_base"


def get_status(text):
    found = re.findall(r"\(Status: ([^)]*)\)", text)
    return found[-1] if found else ""


with open(BASE / "data" / "chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)
print(f"Loaded {len(chunks)} chunks")

documents = [
    Document(
        page_content=c["title"] + "\n" + c["text"],
        metadata={"id": c["id"], "section": c["section"], "title": c["title"], "status": get_status(c["text"])},
    )
    for c in chunks
]

shutil.rmtree(DB_PATH, ignore_errors=True)

embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    ids=[c["id"] for c in chunks],
    collection_name=COLLECTION,
    persist_directory=str(DB_PATH),
)

print(f"Done. The collection has {len(vector_store.get()['ids'])} chunks.")