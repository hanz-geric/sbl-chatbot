# Knowledge Base Research, Phase 2 — November 23, 2026

Phase 2 covers official sites that the automated fetcher could not read in the first round (bot checks, JavaScript-only pages, images). They were read in a real browser on **November 23, 2026**. Nothing is filled in from memory.

Result: **17 new passages (`K166`–`K182`)** and 3 updated ones (`K028`, `K135`, `K165`). Phase 1 runs separately and uses `K200`–`K299`.

## Added

| Section | Passages | Source |
|---|---|---|
| 01.7 FDA: License to Operate (who, how, fees, validity and penalties), product registration (CPR), free BBMSMEs training | K166–K171 | https://www.fda.gov.ph/faqs/ ; https://www.fda.gov.ph/bbmsmes/ (brochure images) |
| 04.6 Programs for OFWs: OWWA BPBH (₱20,000), OWWA–Landbank EDLP loan (₱100,000–₱2M, 7.5%), ELAP livelihood (₱15,000) | K172–K174 | https://owwa.gov.ph/balik-pinas-balik-hanapbuhay-program-bpbh/ ; https://owwa.gov.ph/ofw-enterprise-development-and-loan-program-formerly-p2b-ofw-reintegration-program/ ; https://owwa.gov.ph/education-and-livelihood-assistance-program-elap-2/ |
| 04.7 DOST SETUP: what it gives, priority sectors, PSTO-Benguet contact | K175–K176 | https://car.dost.gov.ph/technology-transfer-and-commercialization-innovation-system-support/ ; https://car.dost.gov.ph/contact-us/ |
| 07.4 DTI sales promotion permits (IRegIS, NegosyoKonek) | K177 | https://www.dti.gov.ph/dti-consumer-space/dti-newly-accredited-licensed-business/dti-sales-promotion-application |
| 09.3 How to file a DTI complaint (CAReS); which agency handles which complaint | K178–K179 | https://www.dti.gov.ph/dti-consumer-space/dti-complaints |
| 11.2 Senior citizen discount: what to give, proof and promos, tax deduction | K180–K182 | https://www.ncsc.gov.ph/post/what-are-the-rights-and-privileges-of-senior-citizens ; https://www.ncsc.gov.ph/post/pahayag-ng-ncsc-sa-no-double-discount-ruling-ng-korte-suprema |

Updated:
- `K028` (01.7): now points to the FDA passages; status VERIFIED.
- `K135` (08.3 "Not covered"): narrowed from "FDA fees and processing times" to **CPR fees only**, since LTO fees are now covered. Otherwise the answer model would decline LTO fee questions.
- `K165` (11.1): the "senior discount not covered" line now points to 11.2.

`knowledge_tool.py`: the tool description now lists senior citizen discounts, FDA licensing, OFW programs and consumer complaints.

## Checks

- `python build_index.py`: 182 chunks. `pytest`: 11 passed.
- Reference searches in `SYSTEM_CONTEXT.md` unchanged (0.464 / 0.453 / 1.169, same picks).
- Off-topic routing unchanged: capital of France declined 6/6; NBA, cooking, weather and tourist spots declined.
- End-to-end answers (router + gemma3:4b) correct and grounded for: FDA LTO fee for a small manufacturer; home-made peanut butter in La Trinidad; returning OFW financing; senior discount in a Baguio restaurant; senior discount on top of a sale; raffle promo permit; equipment for food processing; defective appliance complaint.
- **Retrieval lesson (again):** the router rewrites questions and adds "in Baguio City and Benguet". The OWWA and DOST passages lost to general chunks until their titles used plain words ("financial help for returning OFWs", "help to buy equipment") and named Baguio City and Benguet.

## Not added

- **BIR:** the useful material (EOPT flyer, Citizen's Charter 2026, online seller and delivery rider registration guides) is all PDF downloads from `bir-cdn.bir.gov.ph`. Not downloaded without permission. The HTML page https://www.bir.gov.ph/penalties quotes old Tax Code text (20% interest) and does not reflect the EOPT reductions for small taxpayers, so it was **not** used.
- **DTI sales promo checklist:** PDF only.
- **Blocked by bot checks / CAPTCHA** (need a person to pass the check in the browser pane once): SEC (sec.gov.ph), DOLE (dole.gov.ph, ble.dole.gov.ph), IPOPHL (ipophil.gov.ph), Pag-IBIG (pagibigfund.gov.ph).
- **DOST SETUP amounts and repayment terms:** not on the DOST-CAR page.
