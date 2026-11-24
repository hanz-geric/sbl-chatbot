# Evaluation v5: Bulk Knowledge Base (issue #29)

**Date:** November 23–24, 2026
**System:** gemma3:4b answers, llama3.2:3b router, all-MiniLM-L6-v2 embeddings, Chroma. Retrieval fetches 12 candidates and prefers hand-checked passages (distance bonus 0.1), top 3.
**Knowledge base (v5):** 224 hand-checked passages (`chunks.json`, K001–K193 and K200–K230) + 864 extracted passages (`scraped_chunks.json`). Not included in this run: Pag-IBIG passages K194–K195, the PDF crawl, and the thorough hand-read pass (K300–K356).
**Questions:** the original 60 (T01–T50, H01–H10) plus 20 new ones for the new topics (V01–V20, `docs/test_questions_v5.csv`).
**Scoring:** same 1–5 rubric as v1–v4 (`evaluation_v1_baseline.md`), one rater (Claude). Answers: `docs/evaluation_v5_results.md` (v5) and `docs/evaluation_control_results.md` (control). Scores and notes for v4, control and v5: `docs/scores_v5.csv`.

## Results

The **control** run used the same 80 questions on the knowledge base just before #29 (`feature/kb-phase2`: 213 hand-checked passages, no extracted passages, plain top-3 retrieval, same models).

| | v4 | Control (before #29) | v5 (#29) |
|---|---|---|---|
| Original 60, average | **4.82** | **4.28** | **4.40** |
| New 20, average | — | 4.00 | 4.40 |
| Answers scored 5 (of the original 60) | 52 | 37 | 37 |
| Average seconds per answer, original 60 (v5) | — | — | 19.6 |

**#29 did not cause the drop from v4; it improved on the system it started from** (+0.12 on the original 60, +0.40 on the new 20). The drop from 4.82 happened before #29. v4 (`evaluation_v1_to_v4.md`) used **bge-m3 embeddings with hybrid BM25 keyword search and an agency filter**. The current app uses **all-MiniLM-L6-v2 meaning search only**, and the knowledge base had grown in phases 1 and 2.

- **v5 better than control:** T03; T07; T34 (control invented a ₱1,000,000 ceiling); H08 (control invented "BFP charges no fee"); H10; and most new questions (SEC fees, trademarks, TUPAD, Rule 1020, SSS payment deadline).
- **v5 worse than control:** T01, T10, T25, T46, H09.

Two "decline" items are now answerable because the knowledge base grew: **T48** (SEC fee, K184) and **H07** (minimum wage, K163). They were scored on correctness; their expected answers in `test_questions.csv` are outdated.

## Remaining problems (v5)

1. **Crowding by general passages.** Checklists and online-selling passages from phase 1 (18.4, 14.1) and extracted pages win retrieval for general questions, pushing out the passage with the answer: T09 (BIR timing → online-seller text), T13 (ORUS missing), T17 (eBPLS documents not listed), T33 (where to apply for SB Corp), T40 (free help → only Negosyo Centers), T04 (who can register → "what it is"). T09, T13, T17, T33 and T40 fail the same way in the control, so they predate #29.
2. **Numbers attached to the wrong item.** gemma3:4b sometimes copies a nearby number: H09 (CDA name reservation fee given as the registration fee), V09 (DTI business name fees given as the DOLE Rule 1020 fee), V20 (EDLP rate given as Landbank's loan rate). This breaks the numbers rule and is the most serious failure type.
3. **"Not covered" passages still pulled in.** T19 retrieved the 08.3 Baguio business tax entry instead of the 25% + 2% penalty passage.
4. **Wrong office in referrals.** T01 (CPDO for permits), H06 (City Tourism for barangay clearance), V06 (SEC for patents).

## Next steps

1. **Fix retrieval.** The biggest gap to v4 is the retrieval stack. Options: bring back hybrid keyword search (needs `rank_bm25`), an agency filter when the question names an agency, and/or give the answer model more passages (top 5).
2. Tighten the numbers rule for fee questions (answer only if the passage names the same agency and item), and re-check H09, V09 and V20.
3. Re-run v5 after merging the filtered PDF passages and the thorough hand-read pass (K300–K356).
4. Update the outdated expected answers for T48 and H07.
5. A group member should re-score a sample, as for v1–v4.
