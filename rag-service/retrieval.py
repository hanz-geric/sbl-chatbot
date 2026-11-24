import math
import re
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE = Path(__file__).parent
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_PATH = BASE / "chroma_db"
COLLECTION = "knowledge_base"
TOP_K = 5
CANDIDATES = 12
HAND_CHECKED_BONUS = 0.1
BM25_K1 = 1.5
BM25_B = 0.75
RRF_K = 60
REGION_PHRASE = r"\s*\b(?:in|for|within)\s+(?:the\s+)?Baguio(?:\s+City)?\s*(?:and|,|&)\s*(?:the\s+)?(?:province\s+of\s+)?Benguet(?:\s+province)?\b"

embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
vector_store = Chroma(
    collection_name=COLLECTION,
    embedding_function=embeddings,
    persist_directory=str(DB_PATH),
)


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def keyword_scores(query, doc_tokens):
    query_tokens = set(tokenize(query))
    count = len(doc_tokens)
    average_length = sum(len(tokens) for tokens in doc_tokens) / count
    counters = [Counter(tokens) for tokens in doc_tokens]
    doc_freq = {word: sum(1 for c in counters if word in c) for word in query_tokens}
    scores = []
    for tokens, counter in zip(doc_tokens, counters):
        score = 0.0
        for word in query_tokens:
            freq = counter[word]
            if freq:
                idf = math.log((count - doc_freq[word] + 0.5) / (doc_freq[word] + 0.5) + 1)
                score += idf * freq * (BM25_K1 + 1) / (freq + BM25_K1 * (1 - BM25_B + BM25_B * len(tokens) / average_length))
        scores.append(score)
    return scores


def fuse(rankings):
    scores = {}
    docs = {}
    for ranking in rankings:
        for position, doc in enumerate(ranking):
            chunk_id = doc.metadata["id"]
            docs[chunk_id] = doc
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (RRF_K + position + 1)
    return [docs[chunk_id] for chunk_id in sorted(scores, key=scores.get, reverse=True)]


def rank(results):
    def adjusted(result):
        doc, distance = result
        return distance - HAND_CHECKED_BONUS if doc.metadata["id"].startswith("K") else distance

    return [doc for doc, _ in sorted(results, key=adjusted)]


def keyword_search(query):
    scores = keyword_scores(query, all_tokens)
    best = sorted(range(len(all_docs)), key=lambda i: scores[i], reverse=True)[:CANDIDATES]
    return [all_docs[i] for i in best if scores[i] > 0]


def search(query):
    query = re.sub(REGION_PHRASE, "", query, flags=re.I).strip()
    meaning = rank(vector_store.similarity_search_with_score(query, k=CANDIDATES))
    return fuse([meaning, keyword_search(query)])[:TOP_K]


stored = vector_store.get(include=["documents", "metadatas"])
all_docs = [Document(page_content=text, metadata=metadata) for text, metadata in zip(stored["documents"], stored["metadatas"])]
all_tokens = [tokenize(doc.page_content) for doc in all_docs]


retriever = SimpleNamespace(invoke=search)
