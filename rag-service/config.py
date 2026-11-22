"""Model names and the LLM provider switch, shared by agent.py and generator.py."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE.parent / ".env")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").strip().lower()
if LLM_PROVIDER not in ("groq", "local"):
    raise ValueError("LLM_PROVIDER must be 'groq' or 'local'")

if LLM_PROVIDER == "local":
    ROUTER_MODEL = os.getenv("ROUTER_MODEL", "llama3.2:3b")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gemma4:12b")
else:
    ROUTER_MODEL = os.getenv("ROUTER_MODEL", "openai/gpt-oss-20b")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-oss-120b")
