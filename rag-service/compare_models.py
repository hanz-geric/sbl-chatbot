import time
from pathlib import Path

import ollama

BASE = Path(__file__).parent
MODELS = ["llama3.2:3b", "gemma3:4b"]
RESULTS_PATH = BASE / "model_comparison.md"
PUZZLE = (
    "I have three boxes, one labeled 'Apples', one labeled 'Oranges', and one labeled 'Apples and Oranges'. "
    "I know that every single box is mislabeled. I am allowed to pick only one fruit from only one box "
    "to determine the correct labels for all three. Which box should I pick from?"
)
TASKS = [
    ("Reasoning, zero-shot", PUZZLE),
    ("Reasoning, chain-of-thought", "Solve the following logic puzzle: " + PUZZLE + "\n\nThink step-by-step before providing the final answer."),
    (
        "Code generation",
        "Write a Python function that takes a list of integers and returns the second-largest number in the list. "
        "The function should handle unusual cases like empty lists or lists with duplicate numbers.",
    ),
    (
        "SBL answer from context",
        "Answer only from this context, in 2 to 5 sentences.\n\nCONTEXT:\n"
        "DTI business name registration fees: Barangay scope ₱200, City/Municipality ₱500, Regional ₱1,000, "
        "National ₱2,000, plus ₱30 documentary stamp tax. Registration is valid for 5 years.\n\n"
        "QUESTION: How much does it cost to register a business name for one sari-sari store in one barangay?",
    ),
    (
        "SBL rule: number not in context",
        "Answer only from this context. If the answer is not in the context, say you don't have that information.\n\n"
        "CONTEXT:\nA Mayor's Permit is needed to operate a business in Baguio City. Apply online through eBPLS or at the "
        "Permits and Licensing Division, Baguio City Hall.\n\n"
        "QUESTION: How much is the Mayor's Permit fee for a sari-sari store?",
    ),
]

lines = ["# Model comparison (Lab 5.1)", ""]
rows = []
for model in MODELS:
    capabilities = ollama.show(model).capabilities
    for name, prompt in TASKS:
        print(f"{model}: {name}...", flush=True)
        start = time.time()
        reply = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}], options={"temperature": 0.1})
        seconds = round(time.time() - start, 1)
        rows.append(f"| {model} | {name} | {seconds} s |")
        lines += [f"## {model}: {name} ({seconds} s)", "", reply["message"]["content"], ""]
    rows.append(f"| {model} | Capabilities | {', '.join(capabilities)} |")

lines[2:2] = ["| Model | Task | Result |", "|---|---|---|"] + rows + [""]
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Saved {RESULTS_PATH.name}")