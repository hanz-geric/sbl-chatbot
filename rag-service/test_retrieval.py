import importlib
import sys
from types import SimpleNamespace

sys.modules.pop("retrieval", None)
retrieval = importlib.import_module("retrieval")


def doc(chunk_id):
    return SimpleNamespace(metadata={"id": chunk_id})


def test_rank_prefers_hand_checked_chunks_when_close():
    results = [(doc("S00001"), 0.70), (doc("S00002"), 0.72), (doc("K106"), 0.78), (doc("S00003"), 0.80), (doc("K050"), 0.95)]

    ranked = retrieval.rank(results)

    assert [d.metadata["id"] for d in ranked] == ["K106", "S00001", "S00002"]
