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


def test_message_with_nothing_to_look_up_gets_no_results_reply_without_sources(client, monkeypatch):
    monkeypatch.setattr(app, "route", lambda question: ("search_knowledge_base", "", []))

    response = client.post("/ask", data={"question": "hello"})

    assert response.get_data(as_text=True) == app.NO_RESULTS_REPLY
    [bot] = bot_messages()
    assert bot["content"] == app.NO_RESULTS_REPLY
    assert bot["sources"] is None


def test_decline_is_saved_without_sources(client, monkeypatch):
    sources = [{"title": "08.3 Topics not covered", "status": "VERIFIED", "url": ""}]
    for answer in ["I don't have that information. Ask the Negosyo Center.",
                   "I don\u2019t have that information. Ask the Negosyo Center.",
                   "No current announcements were found. Please ask the DTI Cordillera (CAR) office."]:
        monkeypatch.setattr(app, "route", lambda question: ("search_knowledge_base", "text", sources))
        monkeypatch.setattr(app, "stream_answer", lambda question, context, answer=answer: iter([answer]))

        client.post("/ask", data={"question": "How much is the CDA fee?"}).get_data()

    assert [bot["sources"] for bot in bot_messages()] == [None, None, None]


def test_ask_returns_json_error_when_ollama_is_down(client, monkeypatch):
    def ollama_down(question, context):
        raise httpx.ConnectError("connection refused")
        yield

    monkeypatch.setattr(app, "route", lambda question: ("search_knowledge_base", "DTI text", []))
    monkeypatch.setattr(app, "stream_answer", ollama_down)

    response = client.post("/ask", data={"question": "How do I register my business name?"})

    assert response.get_json() == {"status": "failed", "message": "Cannot reach Ollama. Is it running?"}
    assert bot_messages() == []


def test_question_box_is_limited_to_max_question_length(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "DB_PATH", tmp_path / "chat.db")
    app.create_table()
    html = app.app.test_client().get("/").get_data(as_text=True)
    assert f'maxlength="{app.MAX_QUESTION_LENGTH}"' in html


def test_response_time_is_labelled(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "DB_PATH", tmp_path / "chat.db")
    app.create_table()
    client = app.app.test_client()
    with client.session_transaction() as s:
        s["sid"] = "test"
    app.save_message("test", "bot", "Hello", None, 12.3)
    html = client.get("/messages").get_data(as_text=True)
    assert "Answered in 12.3 s" in html
