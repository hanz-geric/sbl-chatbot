import json
import secrets
import sqlite3
import time
from pathlib import Path

import httpx
import ollama
from flask import Flask, jsonify, render_template, request, session

from agent import route
from generator import NO_RESULTS_REPLY, OFF_TOPIC_REPLY, stream_answer

BASE = Path(__file__).parent
DB_PATH = BASE / "chat.db"
SECRET_KEY = "sbl-chatbot-local"
MAX_QUESTION_LENGTH = 500

app = Flask(__name__)
app.secret_key = SECRET_KEY


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def create_table():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'bot')),
                content TEXT NOT NULL,
                sources TEXT,
                response_time REAL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_message(session_id, role, content, sources=None, response_time=None):
    with get_db() as db:
        db.execute(
            "INSERT INTO messages(session_id, role, content, sources, response_time) VALUES(?,?,?,?,?)",
            (session_id, role, content, sources, response_time),
        )


def get_messages(session_id):
    with get_db() as db:
        rows = db.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,)).fetchall()
    messages = [dict(row) for row in rows]
    for message in messages:
        message["sources"] = json.loads(message["sources"]) if message["sources"] else []
    return messages


def get_session_id():
    if "sid" not in session:
        session["sid"] = secrets.token_hex(16)
    return session["sid"]


@app.get("/")
def index():
    return render_template("index.html", messages=get_messages(get_session_id()))


@app.get("/messages")
def messages():
    return render_template("messages.html", messages=get_messages(get_session_id()))


@app.post("/ask")
def ask():
    session_id = get_session_id()
    question = request.form.get("question", "").strip()
    if not question:
        return jsonify({"status": "failed", "message": "Please type a question."})
    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({"status": "failed", "message": f"Please keep your question under {MAX_QUESTION_LENGTH} characters."})

    save_message(session_id, "user", question)
    start = time.time()
    try:
        tool, context, sources = route(question)
        if tool is None:
            answer, sources = OFF_TOPIC_REPLY, []
        elif not context:
            answer = NO_RESULTS_REPLY
        else:
            answer = "".join(stream_answer(question, context)).strip()
    except ollama.ResponseError as e:
        return jsonify({"status": "failed", "message": f"The model returned an error: {e.error}"})
    except (ConnectionError, httpx.ConnectError):
        return jsonify({"status": "failed", "message": "Cannot reach Ollama. Is it running?"})

    seconds = round(time.time() - start, 2)
    save_message(session_id, "bot", answer, json.dumps(sources) if sources else None, seconds)
    return jsonify({"status": "success"})


create_table()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
