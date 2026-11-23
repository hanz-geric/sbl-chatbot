import sys
from types import ModuleType, SimpleNamespace

stub = ModuleType("retrieval")
stub.retriever = SimpleNamespace(invoke=lambda query: [])
sys.modules["retrieval"] = stub

import agent


def test_route_gives_url_for_extracted_passages_only(monkeypatch):
    docs = [
        SimpleNamespace(metadata={"title": "01.2 DTI", "status": "VERIFIED"}),
        SimpleNamespace(metadata={"title": "RISE UP", "status": "VERIFIED, AUTO-EXTRACTED", "url": "https://sbcorp.gov.ph/loans/"}),
    ]
    tool_message = SimpleNamespace(type="tool", name="search_knowledge_base", content="text", artifact=docs)
    monkeypatch.setattr(agent, "router", SimpleNamespace(invoke=lambda state: {"messages": [tool_message]}))

    tool, context, sources = agent.route("loan for my business")

    assert sources == [
        {"title": "01.2 DTI", "status": "VERIFIED", "url": ""},
        {"title": "RISE UP", "status": "VERIFIED, AUTO-EXTRACTED", "url": "https://sbcorp.gov.ph/loans/"},
    ]
