import json

import httpx
import pytest

import app
from app import format_answer


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(app, "DB_PATH", tmp_path / "chat.db")
    app.create_table()
    return app.app.test_client()


def bot_messages():
    with app.get_db() as db:
        return [dict(row) for row in db.execute("SELECT * FROM messages WHERE role = 'bot'").fetchall()]


def test_markdown_bullets_and_bold_become_html_list():
    assert format_answer("You need:\n*   Barangay clearance\n* **Police** clearance") == \
        "You need:\n<ul><li>Barangay clearance</li><li><strong>Police</strong> clearance</li></ul>"


def test_html_in_answer_is_escaped():
    assert format_answer("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_ask_streams_answer_and_saves_it_with_sources_and_seconds(client, monkeypatch):
    sources = [{"title": "01.2 DTI", "status": "VERIFIED", "url": ""}]
    monkeypatch.setattr(app, "route", lambda question: ("search_knowledge_base", "DTI text", sources))
    monkeypatch.setattr(app, "stream_answer", lambda question, context: iter(["Register ", "with DTI", "."]))

    response = client.post("/ask", data={"question": "How do I register my business name?"})

    assert response.mimetype == "text/plain"
    assert response.get_data(as_text=True) == "Register with DTI."
    [bot] = bot_messages()
    assert bot["content"] == "Register with DTI."
    assert json.loads(bot["sources"]) == sources
    assert bot["response_time"] is not None


def test_ask_sends_off_topic_reply_as_one_piece(client, monkeypatch):
    monkeypatch.setattr(app, "route", lambda question: (None, "", []))

    response = client.post("/ask", data={"question": "Who won the NBA finals?"})

    assert response.mimetype == "text/plain"
    assert response.get_data(as_text=True) == app.OFF_TOPIC_REPLY
    [bot] = bot_messages()
    assert bot["content"] == app.OFF_TOPIC_REPLY
    assert bot["sources"] is None


def test_ask_returns_json_error_when_ollama_is_down(client, monkeypatch):
    def ollama_down(question, context):
        raise httpx.ConnectError("connection refused")
        yield

    monkeypatch.setattr(app, "route", lambda question: ("search_knowledge_base", "DTI text", []))
    monkeypatch.setattr(app, "stream_answer", ollama_down)

    response = client.post("/ask", data={"question": "How do I register my business name?"})

    assert response.get_json() == {"status": "failed", "message": "Cannot reach Ollama. Is it running?"}
    assert bot_messages() == []
