import sys
from types import ModuleType, SimpleNamespace

stub = ModuleType("retrieval")
stub.retriever = SimpleNamespace(invoke=lambda query: [])
sys.modules["retrieval"] = stub

import agent
import knowledge_tool

OFF_TOPIC = "I can only help with small business and livelihood questions for Baguio City and Benguet."


def test_route_gives_url_for_extracted_passages_only(monkeypatch):
    docs = [
        SimpleNamespace(page_content="DTI text", metadata={"title": "01.2 DTI", "status": "VERIFIED"}),
        SimpleNamespace(page_content="RISE UP text", metadata={"title": "RISE UP", "status": "VERIFIED, AUTO-EXTRACTED", "url": "https://sbcorp.gov.ph/loans/"}),
    ]
    tool_message = SimpleNamespace(type="tool", name="search_knowledge_base", content="text", artifact=docs)
    monkeypatch.setattr(agent, "router", SimpleNamespace(invoke=lambda state: {"messages": [tool_message]}))
    monkeypatch.setattr(knowledge_tool, "retriever", SimpleNamespace(invoke=lambda query: docs))

    tool, context, sources = agent.route("loan for my business")

    assert sources == [
        {"title": "01.2 DTI", "status": "VERIFIED", "url": ""},
        {"title": "RISE UP", "status": "VERIFIED, AUTO-EXTRACTED", "url": "https://sbcorp.gov.ph/loans/"},
    ]


def router_replies(monkeypatch, message):
    monkeypatch.setattr(agent, "router", SimpleNamespace(invoke=lambda state: {"messages": [message]}))


def knowledge_base_has(monkeypatch, title):
    doc = SimpleNamespace(page_content=f"{title} text", metadata={"title": title, "status": "VERIFIED"})
    monkeypatch.setattr(knowledge_tool, "retriever", SimpleNamespace(invoke=lambda query: [doc]))


def test_pay_question_without_tool_call_still_searches_knowledge_base(monkeypatch):
    router_replies(monkeypatch, SimpleNamespace(type="ai", content=OFF_TOPIC))
    knowledge_base_has(monkeypatch, "10.9 Regular holidays in 2027")

    tool, context, sources = agent.route("What are the regular holidays in 2027?")

    assert tool == "search_knowledge_base"
    assert [s["title"] for s in sources] == ["10.9 Regular holidays in 2027"]


def test_off_topic_question_without_tool_call_is_still_refused(monkeypatch):
    router_replies(monkeypatch, SimpleNamespace(type="ai", content=OFF_TOPIC))
    knowledge_base_has(monkeypatch, "17.2 Baguio City Hall offices")

    assert agent.route("What is the weather in Baguio today?") == (None, "", [])


def test_web_search_without_news_cue_uses_knowledge_base(monkeypatch):
    web_result = SimpleNamespace(type="tool", name="web_search", content="web", artifact=[{"title": "Main Office | IPOPHL", "url": "https://www.ipophil.gov.ph/"}])
    router_replies(monkeypatch, web_result)
    knowledge_base_has(monkeypatch, "01.10 IPOPHL office in Baguio City")

    tool, context, sources = agent.route("Where is the IPOPHL office in Baguio City?")

    assert tool == "search_knowledge_base"
    assert [s["title"] for s in sources] == ["01.10 IPOPHL office in Baguio City"]


def test_news_question_keeps_web_search(monkeypatch):
    web_result = SimpleNamespace(type="tool", name="web_search", content="web", artifact=[{"title": "DTI news", "url": "https://www.dti.gov.ph/news/"}])
    router_replies(monkeypatch, web_result)
    knowledge_base_has(monkeypatch, "03.5 DTI programs")

    tool, context, sources = agent.route("What is the latest DTI news for small businesses?")

    assert tool == "web_search"
    assert sources == [{"title": "DTI news", "status": "WEB", "url": "https://www.dti.gov.ph/news/"}]


def test_knowledge_base_is_searched_with_the_full_question_not_the_router_query(monkeypatch):
    truncated = SimpleNamespace(type="tool", name="search_knowledge_base", content="Mayor text", artifact=[])
    router_replies(monkeypatch, truncated)
    queries = []
    monkeypatch.setattr(knowledge_tool, "retriever", SimpleNamespace(invoke=lambda query: queries.append(query) or []))

    agent.route("What are the requirements for a Mayor's Permit in Baguio?")

    assert queries == ["What are the requirements for a Mayor's Permit in Baguio?"]
