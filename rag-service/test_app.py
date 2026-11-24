import app as chat_app
from app import format_answer


def test_markdown_bullets_and_bold_become_html_list():
    assert format_answer("You need:\n*   Barangay clearance\n* **Police** clearance") == \
        "You need:\n<ul><li>Barangay clearance</li><li><strong>Police</strong> clearance</li></ul>"


def test_html_in_answer_is_escaped():
    assert format_answer("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_question_box_is_limited_to_max_question_length(tmp_path, monkeypatch):
    monkeypatch.setattr(chat_app, "DB_PATH", tmp_path / "chat.db")
    chat_app.create_table()
    html = chat_app.app.test_client().get("/").get_data(as_text=True)
    assert f'maxlength="{chat_app.MAX_QUESTION_LENGTH}"' in html


def test_response_time_is_labelled(tmp_path, monkeypatch):
    monkeypatch.setattr(chat_app, "DB_PATH", tmp_path / "chat.db")
    chat_app.create_table()
    client = chat_app.app.test_client()
    with client.session_transaction() as s:
        s["sid"] = "test"
    chat_app.save_message("test", "bot", "Hello", None, 12.3)
    html = client.get("/messages").get_data(as_text=True)
    assert "Answered in 12.3 s" in html
