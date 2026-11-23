# Knowledge Base Research: Phase 1 (November 23, 2026)

Phase 1 of the knowledge base expansion adds sections 12 to 18 to `rag-service/data/chunks.json` as `K200`–`K230` (31 passages). Phase 2 (sites with bot checks: OWWA, FDA, BIR consumer rules, DOST, Pag-IBIG, DOLE, SEC, IPOPHL, senior discount) uses `K166`–`K199` and is done separately.

All facts were read on official government pages on **November 23, 2026**. Nothing is filled in from memory. Where an official page did not give a fee, document list or contact, the passage says so and tells the chatbot to refer the user to the named office.

## Passages added

| Section | Ids | Passages |
|---|---|---|
| 12 Tourism businesses | K200–K204 | 12.1 DOT accreditation mandatory vs optional; 12.2 primary enterprises (homestays, inns, tour guides, tour operators); 12.3 secondary enterprises (restaurants, shops, agri-tourism farms); 12.4 how to apply (DOT portal); 12.5 Baguio City VISITA registration |
| 13 Food businesses | K205–K207 | 13.1 sanitary permit; 13.2 health certificates for food handlers; 13.3 carinderias, food stalls and home-based food in Baguio City |
| 14 Online selling | K208–K212 | 14.1 do online sellers need to register; 14.2 BIR registration channels and documents; 14.3 duties after BIR registration; 14.4 selling on e-marketplaces (Shopee, Lazada, TikTok Shop); 14.5 withholding tax on platform payouts |
| 15 Closing a business | K213–K216 | 15.1 overview; 15.2 retiring the Mayor's Permit (RA 7160 Sec. 145, Baguio City); 15.3 BIR Form 1905 closure checklist; 15.4 cancelling the DTI business name (links to 01.2) |
| 16 Transport livelihoods | K217 | 16.1 tricycle franchise (LGU power under RA 7160; no Baguio/Benguet procedure found) |
| 17 Contact directory | K218–K225 | 17.1 DTI; 17.2 Baguio City Hall offices; 17.3 SSS; 17.4 PhilHealth; 17.5 Pag-IBIG (not found); 17.6 BIR; 17.7 TESDA; 17.8 DOLE (FOR VALIDATION) |
| 18 Business-type checklists | K226–K230 | 18.1 sari-sari store; 18.2 food stall/carinderia; 18.3 homestay/small inn; 18.4 online shop; 18.5 home-based service |

Section 07.5 (Internet Transactions Act) and 01.2 (BNRS cancellation grounds) were read and not repeated; the new passages point to them. Section 14 does not repeat 01.6's general BIR rules; 15.3 overlaps with K027 on purpose because K027 cites a PwC alert while 15.3 cites the BIR checklist itself.

Cross-references in the new passages are written as `(see 02.3)` so `clean_context` strips them before the answer model sees the text.

## Sources read (all checked November 23, 2026)

| Source | Used for |
|---|---|
| https://mirror.officialgazette.gov.ph/2009/11/10/implementing-rules-and-regulations-of-republic-act-no-9593/ (RA 9593 IRR) | 12.1–12.3: primary/secondary enterprises, compulsory vs voluntary accreditation, DOT accreditation before LGU permit |
| https://accreditation.tourism.gov.ph/ (DOT Accreditation Portal) | 12.4: online application; page shows only the sign-in screen |
| https://visita.baguio.gov.ph/auth/register (VISITA data privacy undertaking) | 12.5: Ordinance No. 20, s. 2026; what is collected; sharing with BPLO and DOT |
| https://visita.baguio.gov.ph/accommodations | 12.5: listing includes homestays, transient houses, boarding houses, condo units |
| https://visita.baguio.gov.ph/contact | 12.5, 17.2: City Tourism, Culture and Arts Office contact |
| https://www.officialgazette.gov.ph/1975/12/23/presidential-decree-no-856-s-1975/ (Code on Sanitation) | 13.1–13.3, 18.5: Sec. 14 sanitary permit, Sec. 15 and 19 health certificates, Sec. 16 food sources, Chapter XII barbers and beauty parlors |
| https://www.officialgazette.gov.ph/1991/10/10/republic-act-no-7160/ (Local Government Code) | 15.2: Sec. 145 retirement of business; 16.1: Sec. 447/458 tricycle franchises |
| https://ebpls.baguio.gov.ph/ | 15.2, 17.2: eBPLS services (no retirement service listed), bizpass@baguio.gov.ph |
| https://bir-cdn.bir.gov.ph/BIR/pdf/CDR%20-%202025%20(1).pdf (BIR checklists, revised July 2025) | 14.1: online sellers, vloggers, content creators register as self-employed (CDR F1101); 15.3: closure checklist (CDR F1105C); 16.1: franchise documents for common carriers |
| https://bir-cdn.bir.gov.ph/BIR/pdf/TAXPAYERS%20GUIDE%20FOR%20ONLINE%20SELLERS.pdf | 14.2–14.3: registration channels, documents, ₱30 DST, invoices, books |
| https://bir-cdn.bir.gov.ph/BIR/pdf/RR%2016-2023.pdf | 14.4–14.5: register before selling on a platform, COR to platform, 1% on half of gross remittances, ₱500,000 threshold |
| https://bir-cdn.bir.gov.ph/BIR/pdf/PR41JUL1624.pdf (BIR press release) | 14.5: withholding starts July 15, 2024; credited against income tax |
| https://bir-cdn.bir.gov.ph/BIR/pdf/Annex%202%20(RMC%20No.%2010-2025).pdf (BIR FOI receiving offices) | 17.6: RDO No. 8 Baguio City, RDO No. 9 La Trinidad, RR2-CAR addresses and phones |
| https://bnrs.dti.gov.ph/faq | 14.1: business name needed if not using your true name; 15.4: call DTI office first, DTI-initiated cancellation |
| https://www.dti.gov.ph/dti-regions/dti-car | 17.1: DTI-CAR regional office address and email |
| https://www.dti.gov.ph/wp-content/uploads/2025/06/25June_DTIDirectoryofKeyOfficials.pdf | 17.1: DTI Benguet Provincial Office address, phones, email; DTI-CAR telefax |
| https://member.sss.gov.ph/member/sss/branchloc (SSS branch locator, Luzon) | 17.3: Baguio and La Trinidad branches |
| https://www.sss.gov.ph/contact-us/ | 17.3: hotline 1455 |
| https://www.philhealth.gov.ph/about_us/directory/ | 17.4: PRO CAR, LHIO Baguio City, LHIO La Trinidad |
| https://car.tesda.gov.ph/tesdacar/contact/ | 17.7: TESDA CAR, Benguet PO, CSITE executive office, Benguet PTC |

## Blocked or not usable

| Site | Problem | Effect |
|---|---|---|
| https://www.baguio.gov.ph/ | TLS certificate error (name mismatch) | No official Baguio City page for the City Health Services Office, business retirement, or tricycle franchises |
| https://latrinidad.gov.ph/ | TLS certificate error (certificate is for another domain) | La Trinidad Negosyo Center and tricycle pages not read |
| https://car.dole.gov.ph/contact-us/ | Cloudflare bot check (HTTP 403) | 17.8 uses the search engine's copy of the page; marked FOR VALIDATION |
| https://www.pagibigfund.gov.ph/ | reCAPTCHA browser check | 17.5 has no Pag-IBIG address; left for phase 2 |
| https://pia.gov.ph/ (news article on Baguio sanitary permits) | Cloudflare bot check (HTTP 403) | Not used |
| https://beta.tourism.gov.ph/ (DOT news: accreditation goes digital, fee waiver) | Navigation refused | Fee waiver status unknown; 12.4 gives no fee |
| https://www.tourism.gov.ph/downloadable%20files/StreamlinedDocumentaryRequirements2017.pdf | 404 | No DOT document list |
| https://ecommerce.dti.gov.ph/faqs/ | Navigation refused | Not used; 07.5 already covers RA 11967 |
| https://negosyocenter.dti.gov.ph/ | Page loads empty ("NCOP") | No Benguet Negosyo Center directory |
| https://www.pna.gov.ph/articles/1239160, /1156537 | 404 | Not used |
| quarantine.doh.gov.ph (health card, sanitary permit pages) | Loaded in search only; these are for ports and airports, not LGUs | Not used for Baguio rules |

No CAPTCHA or bot check was solved or bypassed.

## Gaps that need interviews or office visits

- **Baguio City Health Services Office:** sanitary permit fee and documents; health certificate tests, validity and fee; whether a home kitchen selling food needs a sanitary permit; office phone and hours.
- **Baguio City Permits and Licensing Division / City Treasurer:** documents and fees to retire a business permit; whether BIR closure must come first.
- **DOT (Cordillera regional office):** current accreditation documents, inspection, fees, and whether the fee waiver still applies; DOT accreditation of tour guides in Baguio City.
- **City Tourism, Culture and Arts Office:** what VISITA registration requires from homestay owners; whether it replaces or adds to DOT accreditation.
- **Baguio City and La Trinidad tricycle franchising:** which office handles it (franchising board or council committee), requirements, fees.
- **Pag-IBIG Baguio branch** contact, and **DOLE Baguio–Benguet** contact (confirm the details in 17.8).
- **Negosyo Centers in Benguet:** list and addresses per municipality.
- **SSS, PhilHealth, Pag-IBIG:** steps to close an employer account when a business closes.
- Office hours for all offices in section 17 (none of the pages listed them).

## Retrieval and routing checks

- No change to `ROUTER_PROMPT` or the `search_knowledge_base` docstring was needed: all 14 test questions on the new topics routed to `search_knowledge_base` with a new passage in the top 3, and the off-topic set (weather, tourist spots, "What is the capital of France?" six times, NBA, cooking adobo) got no tool call.
- Full answers checked (route + gemma3:4b): homestay DOT accreditation (K228, K203, K200), carinderia health certificates (K206), platform withholding (K212), retiring a Baguio business permit (K214), tricycle franchise in La Trinidad (K217), SSS Baguio address (K220), sari-sari store steps (K226). All grounded in the new passages; no invented fees.
- Weak spot: "What do I need to close my BIR registration?" retrieves K054, K023 and K027, not K215. K027 answers it, so the answer is still correct.
- Weak spot: the tricycle question also pulls K221 (PhilHealth contacts) as its 2nd source, because both mention La Trinidad.
- `search.py` reference values: default question 0.464 (K003, K031, K057) and DTI fee question 0.453 (K005, K131, K035) are unchanged; the weather question's closest distance moved from 1.169 to 1.132 (K218, a contact-directory passage that names Baguio City).
