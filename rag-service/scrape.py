import re
from html.parser import HTMLParser
from io import BytesIO
from urllib.parse import unquote, urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

from pypdf import PdfReader

SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "button", "select", "iframe", "template"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BLOCK_TAGS = {"p", "li", "td", "th", "dd", "dt", "div", "section", "br", "tr", "table", "ul", "ol", "blockquote", "pre"} | HEADING_TAGS
MAIN_TAGS = {"main", "article"}
VOID_TAGS = {"br", "img", "hr", "input", "meta", "link", "source", "wbr", "col", "area", "base", "embed", "param", "track"}
SKIP_WORDS = ["bid", "procurement", "vacanc", "career", "hiring-for", "gallery", "photo", "video", "transparency", "award", "tender", "canvass", "rfq", "quotation", "job-opening", "jobs", "recruitment", "saln", "annual-report", "audit-report", "privacy-policy", "sitemap", "login", "wp-admin", "feed", "news", "press-release", "events", "governance", "scorecard", "graduates", "accomplishment", "report", "funeral", "death", "sickness", "maternity", "retirement", "pension", "salary-loan", "calamity-loan", "unemployment", "survivor", "coa-aar", "audit", "magazine", "newsletter", "journal", "sinag", "available-slots", "list-of-qualifications", "circular"]
KEYWORDS = ["business", "registration", "register", "permit", "license", "fee", "loan", "grant", "livelihood", "training", "msme", "micro", "enterprise", "entrepreneur", "negosyo", "tax", "employer", "contribution", "discount", "consumer", "complaint", "cooperative", "corporation", "requirement", "apply", "application", "financing", "capital", "seed", "assistance", "program", "scholarship", "farmer", "trademark", "product", "export", "price", "wage"]
MIN_PAGE_CHARS = 300
MIN_PDF_YEAR = 2024
ANNUAL_REPORT = r"[-_]ar[-_\d]|(?:^|[-_/])cv[-_.]"
YEAR = r"(?<!\d)(?:19|20)\d{2}(?!\d)"
MIN_KEYWORD_HITS = 3
MIN_CHUNK_CHARS = 400
MAX_CHUNK_CHARS = 800
MIN_LAST_CHUNK_CHARS = 100
STATUS = "VERIFIED, AUTO-EXTRACTED"
MIN_USEFUL_CHARS = 150
MIN_BUSINESS_HITS = 2
LIST_MIN_ITEMS = 10
LIST_MAX_AVERAGE_CHARS = 20
BUSINESS_WORDS = ["business", "enterprise", "msme", "entrepreneur", "negosyo", "permit", "registration", "register", "loan", "financing", "grant", "livelihood", "employer", "tax", "fee", "license", "cooperative", "corporation", "trademark", "discount", "consumer", "training", "scholarship", "farmer", "seller"]
USER_AGENT = "sbl-chatbot-research/1.0"
FILE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".mp4", ".mp3")


def extract_page(html):
    state = {"skip": 0, "main": 0, "title": False, "heading": False}
    title = []
    buffer = []
    lines = []

    def flush():
        text = " ".join("".join(buffer).split())
        buffer.clear()
        if text:
            lines.append((state["heading"], state["main"] > 0, text))

    def start(tag, attrs):
        if tag in VOID_TAGS and tag != "br":
            return
        if tag in SKIP_TAGS:
            state["skip"] += 1
        elif tag in MAIN_TAGS:
            state["main"] += 1
        elif tag == "title":
            state["title"] = True
        if tag in BLOCK_TAGS:
            flush()
            if tag in HEADING_TAGS:
                state["heading"] = True

    def end(tag):
        if tag in BLOCK_TAGS:
            flush()
            if tag in HEADING_TAGS:
                state["heading"] = False
        if tag in SKIP_TAGS:
            state["skip"] = max(0, state["skip"] - 1)
        elif tag in MAIN_TAGS:
            state["main"] = max(0, state["main"] - 1)
        elif tag == "title":
            state["title"] = False

    def data(text):
        if state["title"]:
            title.append(text)
        elif state["skip"] == 0:
            buffer.append(text)

    parser = HTMLParser(convert_charrefs=True)
    parser.handle_starttag = start
    parser.handle_endtag = end
    parser.handle_data = data
    parser.feed(html)
    parser.close()
    flush()

    if any(in_main for _, in_main, _ in lines):
        lines = [line for line in lines if line[1]]

    sections = []
    heading = ""
    body = []
    for is_heading, _, text in lines:
        if is_heading:
            if body:
                sections.append((heading, "\n".join(body)))
                body = []
            heading = text
        else:
            body.append(text)
    if body:
        sections.append((heading, "\n".join(body)))
    return " ".join("".join(title).split()), sections


def is_relevant(url, title, text):
    label = (url + " " + title).lower().replace(" ", "-")
    if any(word in label for word in SKIP_WORDS):
        return False
    if re.search(ANNUAL_REPORT, label):
        return False
    if any(0x1D400 <= ord(char) <= 0x1D7FF for char in title):
        return False
    if len(text) < MIN_PAGE_CHARS:
        return False
    lowered = text.lower()
    return sum(1 for word in KEYWORDS if word in lowered) >= MIN_KEYWORD_HITS


def split_long(line):
    if len(line) <= MAX_CHUNK_CHARS:
        return [line]
    pieces = []
    current = ""
    for sentence in line.replace(". ", ".\n").split("\n"):
        if current and len(current) + 1 + len(sentence) > MAX_CHUNK_CHARS:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return [piece[:MAX_CHUNK_CHARS] for piece in pieces]


def pack(lines):
    groups = []
    current = []
    for line in lines:
        if current and len("\n".join(current + [line])) > MAX_CHUNK_CHARS:
            groups.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        groups.append(current)
    if len(groups) > 1 and len("\n".join(groups[-2] + groups[-1])) <= MAX_CHUNK_CHARS:
        groups[-2] = groups[-2] + groups.pop()
    return groups


def chunk_page(url, title, sections, agency, checked):
    name = title.split(" | ")[0].strip()
    chunks = []
    pending = []
    pending_heading = ""

    def add(heading, lines):
        chunk_title = f"{name} > {heading}" if heading and heading != name else name
        body = "\n".join(lines)
        chunks.append({
            "section": agency,
            "title": chunk_title,
            "text": f"{body}\nSource: {url} (checked {checked})\n(Status: {STATUS})",
            "url": url,
            "agency": agency,
        })

    for heading, body in sections:
        lines = [piece for line in body.split("\n") for piece in split_long(line)]
        if pending:
            lines = pending + lines
            heading = pending_heading
            pending = []
        groups = pack(lines)
        if len("\n".join(groups[-1])) < MIN_CHUNK_CHARS:
            pending = groups.pop()
            pending_heading = heading
        for group in groups:
            add(heading, group)
    if pending and len("\n".join(pending)) >= MIN_LAST_CHUNK_CHARS:
        add(pending_heading, pending)
    return chunks


def finalize(chunks):
    seen = set()
    out = []
    for chunk in chunks:
        body = chunk["text"].split("\nSource: ")[0]
        key = " ".join(body.lower().split())
        if key in seen:
            continue
        seen.add(key)
        out.append({"id": f"S{len(out) + 1:05d}", **chunk})
    return out


def allowed(robots_text, url):
    robots = RobotFileParser()
    robots.parse(robots_text.splitlines())
    return robots.can_fetch(USER_AGENT, url)


def collect_hrefs(html):
    found = []

    def start(tag, attrs):
        href = dict(attrs).get("href")
        if tag == "a" and href:
            found.append(href)

    parser = HTMLParser(convert_charrefs=True)
    parser.handle_starttag = start
    parser.feed(html)
    parser.close()
    return found


def extract_links(html, base_url, prefixes):
    found = collect_hrefs(html)
    host = urlparse(base_url).netloc
    links = []
    for href in found:
        url = urldefrag(urljoin(base_url, href))[0]
        parts = urlparse(url)
        if parts.scheme not in ("http", "https") or parts.netloc != host:
            continue
        if parts.path.lower().endswith(FILE_EXTENSIONS):
            continue
        if not any(parts.path.startswith(prefix) for prefix in prefixes):
            continue
        if url not in links:
            links.append(url)
    return links


def is_useful_chunk(body):
    if len(body) < MIN_USEFUL_CHARS:
        return False
    items = [item for item in re.split(r"\n| \| ", body) if item.strip()]
    if len(items) >= LIST_MIN_ITEMS and sum(len(item) for item in items) / len(items) < LIST_MAX_AVERAGE_CHARS:
        return False
    lowered = body.lower()
    return sum(1 for word in BUSINESS_WORDS if word in lowered) >= MIN_BUSINESS_HITS


def extract_pdf_links(html, base_url):
    found = collect_hrefs(html)
    host = urlparse(base_url).netloc
    links = []
    for href in found:
        url = urldefrag(urljoin(base_url, href))[0]
        parts = urlparse(url)
        if not parts.path.lower().endswith(".pdf"):
            continue
        if parts.netloc != host and not parts.netloc.endswith(".gov.ph"):
            continue
        if url not in links:
            links.append(url)
    return links


def extract_pdf(data):
    reader = PdfReader(BytesIO(data))
    title = (reader.metadata.title if reader.metadata and reader.metadata.title else "").strip()
    sections = []
    for page in reader.pages:
        lines = [" ".join(line.split()) for line in (page.extract_text() or "").splitlines()]
        body = "\n".join(line for line in lines if line)
        if body:
            sections.append(("", body))
    return title, sections


def is_recent_pdf(url):
    years = [int(year) for year in re.findall(YEAR, unquote(url))]
    return not years or max(years) >= MIN_PDF_YEAR
