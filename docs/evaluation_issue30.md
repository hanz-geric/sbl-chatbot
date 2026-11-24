# Evaluation: Retrieval Fix (issue #30)

**Date:** November 24, 2026
**System:** gemma3:4b answers, llama3.2:3b router, all-MiniLM-L6-v2 embeddings, Chroma.
**Knowledge base:** 1,397 passages (283 hand-checked + 1,114 extracted), the same in both runs.
**Questions:** the original 60 (T01–T50, H01–H10) and the 20 from v5 (V01–V20).
**Scoring:** the same 1–5 rubric as v1–v5. One rater (Claude). Answers are in `docs/evaluation_issue30_baseline_results.md` (baseline) and `docs/evaluation_issue30_results.md` (#30). Scores and notes are in `docs/scores_issue30.csv`.

## What changed

| | Baseline | #30 |
|---|---|---|
| Search | meaning only (12 candidates, hand-checked bonus 0.1) | meaning + BM25 keyword search, merged by reciprocal rank fusion |
| Router's "in Baguio City and Benguet" | searched as typed | removed before searching |
| Passages given to gemma | 3 | 5 |

BM25 is written in plain Python in `retrieval.py`. It needs no new package, so `rank_bm25` was not added.

## Results

| | Baseline | #30 |
|---|---|---|
| Original 60, average | 4.27 | **4.60** |
| Original 60, answers scored 5 | 40 | 45 |
| New 20, average | 4.35 | 4.35 |
| Average seconds per answer (original 60) | 19.8 | 24.1 |

For comparison, v4 scored 4.82 and v5 scored 4.40 (`evaluation_v5.md`). The baseline run (4.27) is v5's setup plus the merged hand-read pass and PDF passages. Those additions did not change the scores.

**Fixed by #30:**
- T07 (SEC for corporations, 1 → 5)
- T17 (eBPLS document list, 1 → 5)
- T19 (25% + 2% penalty, 1 → 5)
- V09 (no DOLE fee stated, 1 → 5)
- T09 (BIR timing, 2 → 5)
- T13 (ORUS, 2 → 5)
- T04 (who can register, 3 → 5)
- T33 (app.sbcorp.ph, 3 → 5)
- T49 (3 → 5)
- V15 (SSS deadline, 3 → 5)

Most of these are the "crowding" failures from v5. The keyword search finds exact words such as ORUS, eBPLS, SB Corp and Rule 1020. Removing the region phrase keeps directory and checklist passages from winning.

**Worse:**
- V03 (5 → 1): the stock-corporation fee rule was given as the partnership fee.
- Small losses of one point each (detail left out or wording): T18, T20, T30, T48, H04, V01, V07, V13.

**Still failing:**
- **Numbers attached to the wrong item:**
  - H09: CDA name reservation fee given as the registration fee.
  - V03: see above.
  - V20: SB Corp RISE UP rate given as Landbank's rate.
- **Wrong office:**
  - H06: City Tourism for barangay clearance.
  - H10: DTI or SB Corp for a BDO loan.
- **T40 ("free help"):** the DSWD SLP and DOLE DILP passages are still not retrieved for this wording.

## Numbers rule: tried, not kept

A stricter rule 2 was tested. It added: "a fee for a name reservation is not a registration fee, a fee for a stock corporation is not a fee for a partnership, and one bank's or program's interest rate is not another bank's rate."

The test used 10 fee questions, each answered twice with the old rule and twice with the new one, on the same passages. H09, V03 and V20 gave the same wrong numbers with both rules. The new rule also made T32 worse ("PHP 300.0 thousand"). The prompt was left unchanged.

These errors come from the 4b model mixing up items that sit close together in a passage. Rewording the rule does not stop it.

## Passage fixes for the number errors

Because the rule did not help, the passages were reworded so the warning sits next to the number:

- **K146 (CDA):** the title and text now say that ₱100–₱300 is the **name reservation fee only, not the registration fee**, and that the registration fee is not covered.
- **K184 (SEC):** the title and text now say the fees are for **stock corporations only**, and that partnership fees are not covered (use eSPARC or 1-4SEC).
- **K173 (OWWA–Landbank EDLP):** the 7.5% is now marked as only for the EDLP, not Landbank's other loans.
- **New K196 (08.3):** says interest rates of bank business loans (Landbank, BDO, BPI and others) are not covered. It also says the program rates in 04.2, 04.5 and 04.6 are not bank rates. The user is told to ask the bank.

End-to-end check (router + gemma3:4b), each question asked twice:

| Question | Before | After (2 of 2) |
|---|---|---|
| H09 CDA registration fee | gave the name reservation fee | says it doesn't have it; ask the CDA |
| V03 SEC partnership fee | gave the stock-corporation rule | not covered; eSPARC or 1-4SEC |
| V20 Landbank loan rate | gave SB Corp's 8–12% | doesn't have it; ask the bank |
| H10 BDO loan rate | sent the user to SB Corp | doesn't have it; ask the bank |

Fee and rate questions that should be answered were still answered: V01, T48, T32, V13, V17, T08, the EDLP rate (7.5%) and the RISE UP rates. With 284 hand-checked passages the index has 1,398 passages. The full 80 questions were not re-run after this change.

## Next steps

1. Re-run the 80 questions to confirm the passage fixes in a full run.
2. Make T40 retrieve the free-help programs (DSWD SLP, DOLE DILP), for example by adding the words "free help" and "no money" to the 08.2 passage.
3. A group member should re-score a sample, as for v1–v4.
