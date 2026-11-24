import os
from types import SimpleNamespace

from langchain_core.tools import ToolException

os.environ.setdefault("TAVILY_API_KEY", "test-key")

import web_tool


def invoke(query):
    return web_tool.web_search.invoke(
        {
            "name": "web_search",
            "args": {"query": query},
            "id": "test-call",
            "type": "tool_call",
        }
    )


def test_results_become_content_and_artifact(monkeypatch):
    results = [{"title": "DTI news", "content": "New MSME program."}]
    seen = {}

    def fake_invoke(args):
        seen.update(args)
        return {"results": results}

    monkeypatch.setattr(web_tool, "tavily", SimpleNamespace(invoke=fake_invoke))
    out = invoke("MSME loans")

    assert out.content == "### DTI news\nNew MSME program."
    assert out.artifact == results
    assert seen["query"].startswith("MSME loans")


def test_empty_results_give_empty_content(monkeypatch):
    monkeypatch.setattr(
        web_tool, "tavily", SimpleNamespace(invoke=lambda args: {"results": []})
    )
    out = invoke("no hits")

    assert out.content == ""
    assert out.artifact == []


def test_no_results_message_gives_empty_content(monkeypatch):
    # TavilySearch returns a plain string, not a dict, when nothing is found.
    message = "No search results found for 'What is the capital of France?'. Suggestions: Try a more detailed search."
    monkeypatch.setattr(web_tool, "tavily", SimpleNamespace(invoke=lambda args: message))
    out = invoke("What is the capital of France?")

    assert out.content == ""
    assert out.artifact == []


def test_search_error_returns_empty_result(monkeypatch):
    def failing_invoke(args):
        raise ToolException("quota exceeded")

    monkeypatch.setattr(web_tool, "tavily", SimpleNamespace(invoke=failing_invoke))
    out = invoke("anything")

    assert out.content == ""
    assert out.artifact == []


def test_searches_only_this_months_news(monkeypatch):
    seen = {}

    def fake_invoke(args):
        seen.update(args)
        return {"results": []}

    monkeypatch.setattr(web_tool, "tavily", SimpleNamespace(invoke=fake_invoke))
    invoke("new livelihood grants this month")

    assert seen["topic"] == "news"
    assert seen["time_range"] == "month"


def test_searches_only_trusted_sites(monkeypatch):
    seen = {}

    def fake_invoke(args):
        seen.update(args)
        return {"results": []}

    monkeypatch.setattr(web_tool, "tavily", SimpleNamespace(invoke=fake_invoke))
    invoke("latest DOLE livelihood news")

    assert "dole.gov.ph" in seen["include_domains"]
    assert "facebook.com" not in seen["include_domains"]


def test_search_adds_local_place_names(monkeypatch):
    seen = {}

    def fake_invoke(args):
        seen.update(args)
        return {"results": []}

    monkeypatch.setattr(web_tool, "tavily", SimpleNamespace(invoke=fake_invoke))
    invoke("new DTI programs this year")

    assert seen["query"] == "new DTI programs this year Baguio Benguet Cordillera"


def test_results_without_a_title_are_skipped(monkeypatch):
    kept = {"title": "DTI news", "content": "New MSME program."}
    results = [{"title": "", "content": "Untitled page."}, kept]
    monkeypatch.setattr(
        web_tool, "tavily", SimpleNamespace(invoke=lambda args: {"results": results})
    )
    out = invoke("MSME loans")

    assert out.content == "### DTI news\nNew MSME program."
    assert out.artifact == [kept]
