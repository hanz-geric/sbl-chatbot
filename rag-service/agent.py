from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from knowledge_tool import search_knowledge_base
from web_tool import web_search

ROUTER_MODEL = "llama3.2:3b"
ROUTER_PROMPT = """You are the Small Business and Livelihood Assistant for Baguio City and Benguet, Philippines.
Tools:
- search_knowledge_base: use it for questions about registering a business, permits, taxes, loans, grants, livelihood programs, trainings and offices.
- web_search: use it only, with the user's question word for word, when the user asks for current or recent news, updates or announcements.
Rules:
1. If the question is not about business, livelihood, permits, taxes, loans, training, or hiring employees (for example weather, tourist spots, food, news, or general knowledge), do not use any tool and reply with exactly this sentence: "I can only help with small business and livelihood questions for Baguio City and Benguet."
2. Answer ONLY from the tool results. Do not use outside knowledge. If the results do not have the answer, say you don't have that information.
3. Never invent amounts, fees, rates, dates or offices.
4. Never promise that a loan, grant, or application will be approved.
5. Answer in English, in 2 to 5 sentences or a short list."""

router = create_agent(
    model=ChatOllama(model=ROUTER_MODEL, temperature=0.1, num_ctx=4096, num_predict=300),
    tools=[search_knowledge_base, web_search],
    system_prompt=ROUTER_PROMPT,
)


def route(question):
    result = router.invoke({"messages": [{"role": "user", "content": question}]})
    last = result["messages"][-1]
    if last.type != "tool":
        return None, "", []
    if last.name == "search_knowledge_base":
        sources = [{"title": d.metadata["title"], "status": d.metadata["status"], "url": d.metadata.get("url", "")} for d in last.artifact]
    else:
        sources = [{"title": r["title"], "status": "WEB", "url": r["url"]} for r in last.artifact]
    return last.name, last.content, sources
