import csv
import time
from pathlib import Path

from agent import route
from generator import NO_RESULTS_REPLY, OFF_TOPIC_REPLY, stream_answer

BASE = Path(__file__).parent
QUESTIONS_PATH = BASE.parent / "docs" / "test_questions.csv"
RESULTS_PATH = BASE / "evaluation_results.md"

with open(QUESTIONS_PATH, encoding="utf-8", newline="") as f:
    questions = list(csv.DictReader(f))
print(f"Loaded {len(questions)} questions")

table = ["| ID | Tool | Seconds | Score (1-5) |", "|---|---|---|---|"]
details = []
for q in questions:
    print(f"{q['id']}: {q['question']}", flush=True)
    start = time.time()
    tool, context, sources = route(q["question"])
    if tool is None:
        answer = OFF_TOPIC_REPLY
    elif not context:
        answer = NO_RESULTS_REPLY
    else:
        answer = "".join(stream_answer(q["question"], context)).strip()
    seconds = round(time.time() - start, 1)

    table.append(f"| {q['id']} | {tool or 'none'} | {seconds} |  |")
    details += [
        f"## {q['id']}: {q['question']}",
        "",
        f"**Expected:** {q['expected']}",
        "",
        f"**Tool:** {tool or 'none'} ({seconds} s)",
        "",
        answer,
        "",
        "**Sources:** " + ("; ".join(s["title"] for s in sources) or "none"),
        "",
    ]

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(["# Evaluation results", ""] + table + [""] + details))
print(f"Saved {RESULTS_PATH.name}")
