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

    assert [d.metadata["id"] for d in ranked][:3] == ["K106", "S00001", "S00002"]


def test_keyword_scores_rank_exact_rare_word_highest():
    texts = [
        "Every business in Baguio City and Benguet must register at BIR.",
        "Use ORUS, the BIR Online Registration and Update System, to register online.",
        "Business permits in Baguio City and Benguet are issued by the City Hall.",
    ] + [f"Program {n} for small businesses in Baguio City and Benguet." for n in range(20)]

    scores = retrieval.keyword_scores("How do I register with BIR ORUS in Baguio City and Benguet", [retrieval.tokenize(t) for t in texts])

    assert scores.index(max(scores)) == 1


def test_fuse_prefers_chunks_found_by_both_searches():
    meaning = [doc("K001"), doc("K002"), doc("K003")]
    keyword = [doc("K004"), doc("K002"), doc("K005")]

    fused = retrieval.fuse([meaning, keyword])

    assert [d.metadata["id"] for d in fused][:3] == ["K002", "K001", "K004"]


def test_search_finds_passage_by_exact_words():
    found = retrieval.search("Where can I register with the BIR online?")

    assert "K022" in [d.metadata["id"] for d in found]


def test_search_ignores_added_region_phrase():
    found = retrieval.search("Where can I register with the BIR online in Baguio City and Benguet?")

    assert "K022" in [d.metadata["id"] for d in found]


def test_search_keeps_document_list_for_ebpls_question():
    found = retrieval.search("What documents does the Baguio eBPLS portal ask for when applying for a new business permit?")

    assert "K048" in [d.metadata["id"] for d in found]


def test_search_finds_baguio_mayors_permit_requirements_not_other_towns():
    found = [d.metadata["id"] for d in retrieval.search("What are the requirements for a Mayor's Permit in Baguio?")]

    assert "K047" in found
    assert "K353" not in found


def test_search_finds_dti_fee_table_for_cost_question():
    found = [d.metadata["id"] for d in retrieval.search("How much does DTI business name registration cost?")]

    assert "K005" in found


def test_search_returns_nothing_when_no_passage_is_close():
    for message in ["hello", "good morning", "thanks!", "ok", "can you help me?", "hatdog", "asdfgh", "tell me a story"]:
        assert retrieval.search(message) == [], message


def test_search_still_finds_passages_for_the_weakest_real_questions():
    # The six test-set questions whose best match is furthest away (closest to MAX_DISTANCE).
    for question in [
        "What is a BMBE and what are its benefits?",
        "Saan ang opisina ng TESDA sa La Trinidad?",
        "Magsasara na ako ng negosyo, ano ang gagawin ko sa BIR?",
        "Ano ang OTOP Next Gen at para kanino ito?",
        "Saan ako pwedeng mag-training sa TESDA dito sa Baguio?",
        "magkano magpa register ng business bossing?",
    ]:
        assert retrieval.search(question) != [], question
