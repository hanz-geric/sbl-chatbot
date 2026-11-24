# SBL Assistant: System Context

Everything needed to build the whole system. Give this file to your AI agent together with #1 and your task issue (https://github.com/hanz-geric/sbl-chatbot/issues). If this file and an issue disagree, the issue wins; ask in the issue.

This is our **final project (Lab 5.2, "The Right Tool for the Job")** from the Ollama Lab Guide, with SBL as our topic. It must show what the labs teach (Ollama, LangChain RAG, a tool-using agent, prompt-injection defence, a Llama 3 vs Gemma 3 comparison). Where the lab manual uses something that no longer exists in current LangChain, we use its replacement (section 10).

---

## 1. What we are building

The **Small Business and Livelihood Development Knowledge Assistant** (University of Baguio group project). It answers small business and livelihood questions for **Baguio City and Benguet**: DTI business name registration, Baguio City business permits (Mayor's Permit, eBPLS), BIR, livelihood and loan programs (DOLE DILP, SB Corp, DSWD, TESDA, Negosyo Centers).

It is an **agent with two tools** (the Lab 5.2 architecture):
1. **`search_knowledge_base`** (RAG tool, Lab 2.1): searches 224 hand-checked passages plus 864 passages extracted automatically from official sites (issue #29).
2. **`web_search`** (Lab 3.1): Tavily web search for current news and updates.

A small model (llama3.2:3b) **decides which tool to use**. A second model (gemma3:4b) **writes the answer** only from what the tool returned. The page shows the answer with its **sources**.

### Ground rules of the product
- **Questions and answers are English only.**
- **Sources come from the tools, never from the model's text.**
- The model must not invent numbers (fees, rates, ages, dates), offices or approvals.
- Off-topic questions (weather, tourist spots, food, jokes) get one fixed sentence.
- Everything runs **locally on one laptop, CPU only**. The only thing that uses the internet is the web search tool (free Tavily key).

---

## 2. Architecture

```
Browser  http://127.0.0.1:5000/   templates/index.html + templates/messages.html (Jinja)
   │  fetch POST /ask (FormData), then GET /messages
   ▼
Flask    app.py ── saves messages ──► SQLite chat.db (table messages)
   │  route(question)
   ▼
Agent    agent.py: create_agent(llama3.2:3b, tools) picks ONE tool (or none = off-topic)
   ├─► knowledge_tool.py  search_knowledge_base ─► retrieval.py: Chroma + all-MiniLM-L6-v2 and BM25 keyword search, fused, top 5 (hand-checked preferred)
   └─► web_tool.py        web_search ─► Tavily (internet), top 3, Philippines boost
   │  tool text = CONTEXT, tool results = sources
   ▼
Answer   generator.py: RULES + CONTEXT ─► gemma3:4b (Ollama, localhost:11434)
```

Request flow for one question:
1. Browser POSTs the question to `/ask`. Flask saves the user message.
2. `route(question)` runs the agent. Both tools are `return_direct=True`, so the agent stops right after the tool runs (about 2 s). No tool call → off-topic.
3. Off-topic → `OFF_TOPIC_REPLY`. Tool returned nothing → `NO_RESULTS_REPLY`. Otherwise gemma3:4b answers from the tool's text with `RULES`.
4. Flask saves the bot message (answer + sources JSON + seconds) and returns `{"status": "success"}`.
5. Browser reloads the bubbles from `/messages`.

Why two models: llama3.2:3b supports tool calling but ignores the answer rules (it invented barangay clearance requirements and called DOLE DILP off-topic in testing). gemma3:4b has no tool calling in Ollama (`ollama show gemma3:4b` lists only completion and vision) but follows the answer rules well. Measured in testing: routing ~2 s, full answer ~13–20 s.

---

## 3. Environment

| Item | Value |
|---|---|
| OS | Windows (team laptops) |
| Python | 3.11, venv in `rag-service/.venv` |
| Ollama | `localhost:11434`; models `llama3.2:3b` (router, ~2 GB, has `tools`) and `gemma3:4b` (answers, ~3.4 GB) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` through `HuggingFaceEmbeddings` (downloads ~90 MB on first use, runs on CPU, not in Ollama) |
| Vector store | Chroma, folder `rag-service/chroma_db/`, collection `knowledge_base` |
| Web search | Tavily, free API key in the `TAVILY_API_KEY` environment variable; `country="philippines"` boosts Philippine pages |
| Chat history | SQLite file `rag-service/chat.db` (created by `app.py`) |
| Site URL | http://127.0.0.1:5000/ |

No XAMPP, PHP or MySQL.

### `rag-service/requirements.txt` (exactly)
```
langchain==1.5.2
langchain-ollama==1.1.0
langchain-huggingface==1.2.3
sentence-transformers==6.3.0
langchain-chroma==1.1.0
langchain-tavily==0.2.18
ollama==0.6.3
flask==3.1.3
pytest==9.1.1
pypdf==7.1.1
```
`sentence-transformers` is needed by `HuggingFaceEmbeddings` but is not installed with it, so it is listed. `pytest` is listed so the unit tests can be run from a clean checkout. `pypdf` lets `crawl.py` read official PDFs (issue #29, approved). `chromadb`, `langgraph`, `langchain-core`, `httpx` and `torch` come in as dependencies.

### Setup (per member)
```
ollama pull llama3.2:3b
ollama pull gemma3:4b
```
- Make a free account at https://tavily.com, copy the API key, then in cmd: `setx TAVILY_API_KEY "tvly-..."` and open a **new** terminal. Never commit the key.
- `cd rag-service`, `python -m venv .venv`, `.venv\Scripts\activate`, `pip install -r requirements.txt`, `python build_index.py`.

### Running
1. Ollama running.
2. `cd rag-service`, activate the venv, `python app.py`.
3. Open http://127.0.0.1:5000/

---

## 4. Repository layout (final)

```
sbl-chatbot/
├─ SYSTEM_CONTEXT.md
├─ docs/
│  ├─ design.pdf             2-page design document (Lab 5.2 Part 1)
│  ├─ test_questions.csv     60 test questions with expected facts
│  └─ score_sheet.xlsx       1-5 scoring rubric
└─ rag-service/
   ├─ .gitignore             .venv/  __pycache__/  chroma_db/  chat.db  crawl_cache/
   ├─ requirements.txt
   ├─ data/chunks.json       hand-checked, 285 passages
   ├─ data/scraped_chunks.json  1,114 passages written by crawl.py (do not edit by hand)
   ├─ scrape.py              extract_page, is_relevant, chunk_page, finalize, allowed, extract_links, is_useful_chunk
   ├─ crawl.py               crawls SEEDS → data/scraped_chunks.json (cache in crawl_cache/)
   ├─ build_index.py         chunks.json + scraped_chunks.json → Documents → MiniLM → Chroma
   ├─ retrieval.py           embeddings, vector_store, retriever
   ├─ search.py              debug printout of retrieval
   ├─ generator.py           RULES, clean_context, stream_answer (gemma3:4b)
   ├─ knowledge_tool.py      @tool search_knowledge_base
   ├─ web_tool.py            @tool web_search (Tavily)
   ├─ agent.py               create_agent router + route()
   ├─ ask.py                 terminal Q&A
   ├─ app.py                 Flask + SQLite chat
   ├─ templates/index.html   page, CSS, JS
   ├─ templates/messages.html  chat bubbles
   ├─ compare_models.py      Lab 5.1 comparison → model_comparison.md
   ├─ model_comparison.md    committed results
   ├─ injection_test.py      Lab 4.1/4.2 attacks
   ├─ injection_results.md   committed results
   ├─ evaluate.py            runs the 60 test questions
   └─ evaluation_results.md  answers + scores
```
Never commit `.venv/`, `__pycache__/`, `chroma_db/`, `chat.db`, or any API key.

---

## 5. Coding conventions (strict)

### General
- Touch only the files your issue names. Build exactly what is specified: no extra features, helpers, classes, config files, logging, retries, or error handling for cases not listed.
- Exact names, constants, strings, prompts, printed output and JSON keys as given.
- No new dependencies. No test framework, linter config, Docker, or README unless asked.
- Unclear? Ask in the issue. Do not invent a different design.

### Python
- 4 spaces, **double quotes**, f-strings.
- Imports in three groups (standard library / third-party / our files), blank line between, in the order the issue shows.
- `BASE = Path(__file__).parent`; open files with `encoding="utf-8"`.
- Settings as UPPER_CASE module constants at the top.
- Plain `snake_case` functions. **No classes.**
- **No type hints and no docstrings, except on `@tool` functions**: LangChain builds the tool's input from `query: str` and uses the docstring as the tool description the router model reads.
- No `typing`, `dataclass`, `argparse`, `logging`.
- Shared objects (`retriever`, `router`, `tavily`) are created once at module level.
- Scripts run at the top level; only `app.py` has `if __name__ == "__main__":`.

### HTML / JavaScript / CSS (`templates/`)
- 4 spaces. One `<style>` block in `<head>` of `index.html`, one `<script>` block at the bottom. No libraries, frameworks, or separate .js/.css files.
- Jinja: `{% for %}`, `{% if %}`, `{{ }}`, `{% include %}`. Jinja escapes `{{ }}` automatically; never use `|safe`.
- JS: `function name(){`, `const`/`let` (never `var`), `==`/`!=`, `fetch(...).then(...).catch(...)` (no async/await), `document.getElementById`. Text built in JS goes through `escapeHtml()`.

---

## 6. Knowledge base: `rag-service/data/chunks.json`

A JSON array of 285 objects, ids `K001`–`K197`, `K200`–`K230` and `K300`–`K356`. These were added on November 23, 2026 from official government pages: `K144`–`K165` (see `docs/kb_research_2026-11-23.md`), `K166`–`K182` (phase 2, see `docs/kb_research_phase2.md`) and `K200`–`K230` (phase 1, see `docs/kb_research_phase1.md`). New chunks sit next to their section in the file, so ids are not in file order. New sections: `04.5` agricultural loans, `04.6` OFW programs, `04.7` DOST SETUP, `10` hiring employees, `11` customer discounts (`11.2` senior citizen discount), `12` tourism businesses, `13` food businesses, `14` online selling, `15` closing a business, `16` transport livelihoods, `17` contact directory, `18` business-type checklists. `K183`–`K193` are hand-read passages from issue #29 (SEC, IPOPHL, DOLE, DTI; see `docs/kb_research_phase2.md`); `K194`–`K195` are Pag-IBIG employer registration and contributions (section `10.7`); `K196` and `K197` (08.3) say bank business loan rates and the barangay clearance fee are not covered (issue #30); `K198`–`K199` are unused. `K300`–`K356` come from a thorough hand-read pass of DTI, SEC, IPOPHL, DOLE, Pag-IBIG, FDA, OWWA, DOST-CAR, BIR and Benguet LGU sites (see `docs/kb_research_manual_pass.md`); new sections `02.9`–`02.11` Itogon, Tuba and Bokod permits, `10.8`–`10.10` Pag-IBIG remittance, DOLE pay rules and kasambahay, `14.6` Trustmark.

**Extracted passages: `rag-service/data/scraped_chunks.json`** (issue #29). Same fields plus `url` and `agency`; ids `S00001`…; `section` is the agency; text ends with `Source: <url> (checked <date>)` and `(Status: VERIFIED, AUTO-EXTRACTED)`. Written only by `crawl.py`: it reads the `SEEDS` list, obeys `robots.txt` (DTI blocks all crawlers), waits 1.5 s per request, caps 150 pages per site, reads up to 40 linked PDFs per site plus the `PDF_SEEDS` list with `pypdf` (skips PDFs dated before 2024, annual reports and CVs), filters pages (`is_relevant`) and passages (`is_useful_chunk`), and removes duplicates. Re-run with `python crawl.py` (uses `crawl_cache/`; delete it to re-download), then `python build_index.py`. Sites that block scripts (SEC, DOLE, IPOPHL, Pag-IBIG, DTI) are read by hand into `chunks.json` instead.
```json
{"id": "K004", "section": "01.2 ...", "title": "01.2 DTI Business Name Registration (Sole Proprietorship) > Who can register", "text": "..."}
```
- `title` starts with a section number (e.g. `01.2`, `02.1A`, `08.3`).
- `text` may contain **status labels**: `(Status: VERIFIED)`, `(Status: FOR VALIDATION, INTERVIEW-DERIVED)`, or inline `*(VERIFIED / INTERVIEW-DERIVED)*`.
- `text` may contain **cross-references**: `See 01.6`, `(see 02.3)`.
- Some chunks say "Not covered" and name an office to ask (section 08.3).

**Status of a chunk** = text inside the **last** `(Status: ...)` label, or `""`:
```python
found = re.findall(r"\(Status: ([^)]*)\)", text)
return found[-1] if found else ""
```

---

## 7. Python files (summary; the issues have the exact code)

| File | Main parts |
|---|---|
| `build_index.py` | `Document(page_content=title + "\n" + text, metadata={id, section, title, status})`; deletes `chroma_db/` with `shutil.rmtree`; `Chroma.from_documents(..., ids=chunk ids, collection_name="knowledge_base", persist_directory=...)`; loads `chunks.json` and, if present, `scraped_chunks.json`; metadata also has `url`; prints `Done. The collection has 1399 chunks (285 hand-checked + 1114 extracted).` |
| `retrieval.py` | `embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)`; `vector_store = Chroma(...)`; `retriever = SimpleNamespace(invoke=search)`: `search` fetches `CANDIDATES = 12` passages with `similarity_search_with_score`, subtracts `HAND_CHECKED_BONUS = 0.1` from the distance of hand-checked (`K…`) passages, and orders them (`rank`). Without the bonus, extracted pages crowded out hand-checked answers (e.g. "TESDA STEP"). It also runs BM25 keyword search (`keyword_scores`, plain Python, `BM25_K1 = 1.5`, `BM25_B = 0.75`) over all passages loaded from Chroma at start-up, takes the best `CANDIDATES`, and merges both lists by reciprocal rank fusion (`fuse`, `RRF_K = 60`), keeping `TOP_K = 5`. Before searching it removes the phrase "in Baguio City and Benguet" (`REGION_PHRASE`) that the router often adds, because every passage is about that area and the phrase pulled in directory and checklist passages (issue #30). |
| `generator.py` | `CHAT_MODEL = "gemma3:4b"`, `OFF_TOPIC_REPLY`, `NO_RESULTS_REPLY`, `RULES`, `clean_context(text)`, `stream_answer(question, context)` |
| `knowledge_tool.py` | `@tool(response_format="content_and_artifact", return_direct=True)` → returns `(context text, docs)` |
| `web_tool.py` | `tavily = TavilySearch(max_results=3, country="philippines")`; same decorator → returns `(context text, results)`; Tavily's `ToolException` (no results) → `("", [])` |
| `agent.py` | `ROUTER_MODEL = "llama3.2:3b"`, `ROUTER_PROMPT`, `router = create_agent(...)`, `route(question)` → `(tool name or None, context, sources)` |
| `app.py` | Flask routes `GET /`, `GET /messages`, `POST /ask`; SQLite `messages` table |

**Source format** (stored as JSON in `messages.sources`):
```python
{"title": "...", "status": "VERIFIED", "url": ""}        # knowledge base
{"title": "...", "status": "WEB", "url": "https://..."}  # web search
```

**Fixed replies**
```python
OFF_TOPIC_REPLY = "I can only help with small business and livelihood questions for Baguio City and Benguet."
NO_RESULTS_REPLY = "I could not find any information about that. Please try asking in a different way."
```

---

## 8. Database (SQLite, created by `app.py`)

```sql
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'bot')),
    content TEXT NOT NULL,
    sources TEXT,
    response_time REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
```
`sources` = JSON list (section 7) or NULL. Chat history is per browser: Flask's signed session cookie holds a random `sid` (`secrets.token_hex(16)`). Each member's `chat.db` is local and never committed. The Chroma index is rebuilt by `build_index.py` on each machine.

---

## 9. Decisions and why

| Decision | Why |
|---|---|
| Agent with RAG tool + web tool | Lab 5.2's proposed architecture |
| llama3.2:3b as router | has tool calling; fast on CPU (~2 s per route); llama3:8b/gemma3:12b from the manual are too slow on our CPUs |
| gemma3:4b writes the answers | follows the answer rules; reasoned correctly and completely on the Lab 1.4 puzzle in both prompt styles, where llama3.2:3b reached the right box through self-contradictory steps; no tool calling, so it can't route |
| Tools `return_direct=True` | the agent stops after the tool; gemma answers with our tested RULES |
| Off-topic = "no tool called" | tested: weather, tourist spots, jokes and "ignore your rules" prompts all got no tool call |
| all-MiniLM-L6-v2 embeddings | what Lab 2.1 teaches; English-only questions, so no multilingual model needed |
| Top 5 passages, hybrid search | Lab 2.1 used `k: 3`; with 1,397 passages the answer was often 4th or 5th. Hybrid search + top 5 raised the evaluation from 4.27 to 4.60 (4.75 with the passage fixes) (issue #30, `docs/evaluation_issue30.md`) for ~4 s more per answer |
| Status labels and "see 01.6" removed before the model sees text | the model copied them into answers; sources are shown separately |
| "(Answer in English.)" after the question | keeps gemma in English |
| Sources from tool results | the model can't make up sources |
| Flask + Jinja + SQLite | one language, one server, nothing to install beyond pip |
| Flask on 127.0.0.1 only | local demo |

---

## 10. Outdated parts of the lab manual and what we use instead

Checked against langchain 1.5.2 / langchain-community 0.4.2 (November 2026):

| Lab | Manual uses | Status | We use |
|---|---|---|---|
| 2.1 | `from langchain.chains import RetrievalQA` | removed from `langchain` 1.0; only in `langchain-classic`, deprecated, removal in 2.0. Its own notice says: build RAG with `create_agent` and a retrieval tool. | `create_agent` + `search_knowledge_base` tool |
| 2.1 | `from langchain.text_splitter import ...` | removed from `langchain` | not needed: our data is already split (`chunks.json`) |
| 2.1 | `from langchain_community.embeddings import HuggingFaceEmbeddings` | deprecated | `from langchain_huggingface import HuggingFaceEmbeddings` |
| 2.1 | `from langchain_community.vectorstores import Chroma` | deprecated | `from langchain_chroma import Chroma` |
| 2.1 | `from langchain_community.llms import Ollama` | deprecated | `from langchain_ollama import ChatOllama` |
| 3.1 | `TavilySearchResults` (langchain_community) | deprecated | `from langchain_tavily import TavilySearch` |
| 3.1 | agent prompt from LangChain Hub | `hub` moved to `langchain-classic` | our own `ROUTER_PROMPT` |
| 3.1 | hand-built LangGraph graph | still works | `create_agent` (builds the same model → tool graph on LangGraph) |
| 5.1 | llama3:8b vs gemma3:12b | still exist, too slow on CPU | llama3.2:3b vs gemma3:4b |

Still current and used as taught: the Ollama CLI and Python library (`ollama.chat`, `stream=True`), ChromaDB, chain-of-thought prompting, `<user_data>` markers (Lab 4.2).

---

## 11. Expected results (use for testing)

| Check | Expected |
|---|---|
| `python build_index.py` | ends `Done. The collection has 1399 chunks (285 hand-checked + 1114 extracted).` (also on re-run, ~15 s) |
| `search.py` default question | closest distance ≈ 0.464; retriever picks `K003, K031, K057` |
| `search.py "How much is the DTI business name registration fee?"` | ≈ 0.453; picks `K005, K035, K131` |
| `search.py "What is the weather in Baguio today?"` | ≈ 1.132 |
| DTI fee question | tool `search_knowledge_base`; ₱200 barangay, ₱500 city/municipality, ₱1,000 regional, ₱2,000 national, + ₱30 documentary stamp tax |
| "How much is the permit fee for a sari-sari store?" | no invented amount; says it doesn't have it and names an office |
| "Are there new livelihood grants announced this month?" | tool `web_search` |
| "How much is the CDA registration fee?" | no DTI fees used; "don't have that information", refers to CDA |
| "How much is the SEC registration fee?" | no DTI fees used; says it doesn't have it (in our test it named the City Treasurer's Office instead of SEC, a known weak spot) |
| weather / tourist spots / "Tell me a joke." | no tool, `OFF_TOPIC_REPLY`, ~2 s |
| Ollama down, web page | "Cannot reach Ollama. Is it running?" under the form |

---

## 12. Known limitations
- The router sometimes rewords the query, which can change which passages are found (the added "in Baguio City and Benguet" is now removed before searching).
- llama3.2:3b sometimes writes a malformed tool call (seen once in 10 tests); that question gets the off-topic reply.
- Prompt-injection defences only reduce attacks on a 4b model; they don't stop all of them (see `injection_results.md`).
- One CPU = one answer at a time.
- Each question is answered on its own; the model does not see earlier messages.

## 13. Build order (GitHub issues)
See #1.
