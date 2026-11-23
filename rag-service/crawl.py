import hashlib
import json
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import httpx

from scrape import USER_AGENT, allowed, chunk_page, extract_links, extract_page, finalize, is_relevant, is_useful_chunk

BASE = Path(__file__).parent
CACHE_DIR = BASE / "crawl_cache"
OUT_PATH = BASE / "data" / "scraped_chunks.json"
MAX_PAGES_PER_SITE = 150
DELAY_SECONDS = 1.5
TIMEOUT_SECONDS = 20
SEEDS = [
    ("DTI", "https://www.dti.gov.ph/dti-business-center/", ["/dti-business-center/"]),
    ("DTI", "https://www.dti.gov.ph/dti-consumer-space/", ["/dti-consumer-space/"]),
    ("DTI", "https://bnrs.dti.gov.ph/faq", ["/faq"]),
    ("SB Corp", "https://sbcorp.gov.ph/programs-and-services/msme-financing-programs/", ["/"]),
    ("CDA", "https://cda.gov.ph/services/regulatory-services/registration/", ["/services/"]),
    ("FDA", "https://www.fda.gov.ph/faqs/", ["/faqs/"]),
    ("DSWD", "https://livelihood.dswd.gov.ph/", ["/"]),
    ("TESDA", "https://www.tesda.gov.ph/About/TESDA/1279", ["/About/TESDA/"]),
    ("DOST", "https://car.dost.gov.ph/", ["/"]),
    ("DA", "https://ati2.da.gov.ph/ati-main/content/training_services", ["/ati-main/content/"]),
    ("DA", "https://acpc.gov.ph/", ["/"]),
    ("DBP", "https://www.dbp.ph/developmental-banking/micro-small-and-medium-enterprises/", ["/developmental-banking/"]),
    ("OWWA", "https://owwa.gov.ph/programs-and-services/", ["/"]),
    ("SSS", "https://www.sss.gov.ph/employer-er/", ["/"]),
    ("PhilHealth", "https://www.philhealth.gov.ph/members/", ["/members/", "/partners/employers/"]),
    ("NCDA", "https://ncda.gov.ph/disability-laws/republic-acts/republic-act-no-10754-an-act-expanding-the-benefits-and-privileges-of-persons-with-disability-pwd/", ["/disability-laws/"]),
    ("NCSC", "https://www.ncsc.gov.ph/post/what-are-the-rights-and-privileges-of-senior-citizens", ["/post/"]),
    ("NWPC", "https://nwpc.dole.gov.ph/car/", ["/car/"]),
    ("Baguio City", "https://ebpls.baguio.gov.ph/", ["/"]),
]

CACHE_DIR.mkdir(exist_ok=True)
today = date.today()
checked = f"{today:%B} {today.day}, {today.year}"
client = httpx.Client(headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=TIMEOUT_SECONDS)
robots_cache = {}


def fetch(url):
    cached = CACHE_DIR / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ".html")
    if cached.exists():
        return cached.read_text(encoding="utf-8")
    time.sleep(DELAY_SECONDS)
    try:
        response = client.get(url)
    except httpx.HTTPError as error:
        print(f"  failed {url}: {error.__class__.__name__}")
        return ""
    if response.status_code != 200 or "text/html" not in response.headers.get("content-type", ""):
        print(f"  skipped {url}: {response.status_code} {response.headers.get('content-type', '')}")
        return ""
    cached.write_text(response.text, encoding="utf-8")
    return response.text


def robots_for(url):
    parts = urlparse(url)
    root = f"{parts.scheme}://{parts.netloc}"
    if root not in robots_cache:
        try:
            response = client.get(root + "/robots.txt")
            robots_cache[root] = response.text if response.status_code == 200 else ""
        except httpx.HTTPError:
            robots_cache[root] = ""
    return robots_cache[root]


chunks = []
seen = set()
for agency, start_url, prefixes in SEEDS:
    queue = [start_url]
    pages = 0
    kept = 0
    while queue and pages < MAX_PAGES_PER_SITE:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        if not allowed(robots_for(url), url):
            print(f"  robots.txt disallows {url}")
            continue
        html = fetch(url)
        if not html:
            continue
        pages += 1
        queue.extend(link for link in extract_links(html, url, prefixes) if link not in seen)
        title, sections = extract_page(html)
        text = "\n".join(body for _, body in sections)
        if is_relevant(url, title, text):
            kept += 1
            chunks.extend(c for c in chunk_page(url, title, sections, agency, checked) if is_useful_chunk(c["text"].split("\nSource: ")[0]))
    print(f"{agency}: {start_url} -> {pages} pages read, {kept} relevant")

chunks = finalize(chunks)
OUT_PATH.write_text(json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Done. Saved {len(chunks)} extracted chunks to {OUT_PATH.name}.")
