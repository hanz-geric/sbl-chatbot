import sys
from types import ModuleType, SimpleNamespace

stub = ModuleType("retrieval")
stub.retriever = SimpleNamespace(invoke=lambda query: [])
sys.modules["retrieval"] = stub

import knowledge_tool


def invoke(query):
    return knowledge_tool.search_knowledge_base.invoke(
        {
            "name": "search_knowledge_base",
            "args": {"query": query},
            "id": "test-call",
            "type": "tool_call",
        }
    )


def test_docs_become_cleaned_content_and_artifact(monkeypatch):
    docs = [
        SimpleNamespace(page_content="Fee is \u20b1200.\n(Status: VERIFIED)"),
        SimpleNamespace(
            page_content="DTI business name fees (01.2) apply only to sole proprietorships."
        ),
    ]
    monkeypatch.setattr(
        knowledge_tool, "retriever", SimpleNamespace(invoke=lambda query: docs)
    )
    out = invoke("business name fee")

    assert out.content == (
        "### Fee is \u20b1200.\n\n"
        "### DTI business name fees apply only to sole proprietorships."
    )
    assert out.artifact == docs


def test_question_is_passed_to_retriever_word_for_word(monkeypatch):
    seen = {}

    def fake_invoke(query):
        seen["query"] = query
        return []

    monkeypatch.setattr(knowledge_tool, "retriever", SimpleNamespace(invoke=fake_invoke))
    invoke("How do I register my business?")

    assert seen["query"] == "How do I register my business?"


def test_no_docs_give_empty_content(monkeypatch):
    monkeypatch.setattr(
        knowledge_tool, "retriever", SimpleNamespace(invoke=lambda query: [])
    )
    out = invoke("anything")

    assert out.content == ""
    assert out.artifact == []
