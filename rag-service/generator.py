import re

import ollama

CHAT_MODEL = "gemma3:4b"
OFF_TOPIC_REPLY = "I can only help with small business and livelihood questions for Baguio City and Benguet."
NO_RESULTS_REPLY = "I could not find any information about that. Please try asking in a different way."
RULES = """You are the Small Business and Livelihood Assistant for Baguio City and Benguet, Philippines.
Rules:
1. Use ONLY the facts in CONTEXT. Do not use outside knowledge.
2. Numbers rule: state an amount, fee, rate, age, or date ONLY if CONTEXT gives it for the exact agency, program, and item the user asked about. Never move a number from one agency or program to another. If the exact number is not in CONTEXT, say you don't have that information and name the office to ask.
3. Only if a CONTEXT entry about the exact topic asked says "Not covered", say you don't have it and refer the user to the office named there. Otherwise answer from CONTEXT normally.
4. When you refer the user to an office, name only offices that appear in CONTEXT.
5. Never promise that a loan, grant, or application will be approved; say approval is decided by the agency.
6. Only for renewal schedules that change every year, tell the user to check the current advisory.
7. Be brief: 2 to 5 sentences or a short list. Do not write citations or section numbers; the sources are shown to the user separately.

CONTEXT:
"""


def clean_context(text):
    text = re.sub(r"\n?\(Status:[^)]*\)", "", text)
    text = re.sub(r"\*?\((?:VERIFIED|FOR VALIDATION|INTERVIEW-DERIVED|UNVERIFIED|PENDING|GENERAL GUIDANCE)[^)]*\)\*?", "", text)
    text = re.sub(r"\(\s*see [^)]*\)", "", text, flags=re.I)
    text = re.sub(r"\(\s*\d\d\.\d[^)]*\)", "", text)
    text = re.sub(r"^.*?(?:->|\u2192)[ \t]*$\n?", "", text, flags=re.M)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"[ \t]+([;,.])", r"\1", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def stream_answer(question, context):
    stream = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": RULES + context},
            {"role": "user", "content": question + "\n\n(Answer in English.)"},
        ],
        stream=True,
        options={"temperature": 0.1, "num_predict": 300, "num_ctx": 4096},
    )
    for part in stream:
        yield part["message"]["content"]