import sys
import time

from agent import route
from generator import NO_RESULTS_REPLY, OFF_TOPIC_REPLY, stream_answer


def ask(question):
    start = time.time()
    tool, context, sources = route(question)
    routed = time.time() - start

    if tool is None:
        print(f"\nAnswer: {OFF_TOPIC_REPLY}")
        print(f"\n(off-topic: no tool chosen, {routed:.1f} s)")
        return

    print(f"\nTool: {tool} (chosen in {routed:.1f} s)")
    if not context:
        print(f"\nAnswer: {NO_RESULTS_REPLY}")
        return

    print("\nAnswer: ", end="", flush=True)
    first = None
    for piece in stream_answer(question, context):
        if first is None:
            first = time.time() - start
        print(piece, end="", flush=True)
    total = time.time() - start

    print("\n\nSources:")
    for source in sources:
        line = f"  - {source['title']}"
        if source["status"]:
            line += f"  [{source['status']}]"
        if source["url"]:
            line += f"  {source['url']}"
        print(line)
    print(f"\n(first words after {first:.1f} s, full answer in {total:.1f} s)")


if len(sys.argv) > 1:
    ask(" ".join(sys.argv[1:]))
else:
    print("Small Business and Livelihood Assistant. Type a question, or press Enter to quit.")
    while True:
        question = input("\nYou: ").strip()
        if not question:
            break
        ask(question)
