"""Build the router and answer models for LLM_PROVIDER (groq or local)."""

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from config import CHAT_MODEL, LLM_PROVIDER, ROUTER_MODEL


def build_model(model):
    if LLM_PROVIDER == "local":
        return ChatOllama(model=model, temperature=0.1, num_ctx=4096, num_predict=300)
    return ChatGroq(model=model, temperature=0.1, max_tokens=300)


router_model = build_model(ROUTER_MODEL)
chat_model = build_model(CHAT_MODEL)
