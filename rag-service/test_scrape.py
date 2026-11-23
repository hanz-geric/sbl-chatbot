import scrape

PAGE = """<html><head><title>Business Name Registration | DTI</title>
<script>var x = 1;</script><style>p {color: red}</style></head>
<body>
<header><a href="/">Home</a> <a href="/about">About Us</a></header>
<nav><ul><li>Programs</li><li>Contact</li></ul></nav>
<main>
<h1>Business Name Registration</h1>
<p>Any Filipino at least 18 years old can register a business name.</p>
<h2>Fees</h2>
<ul><li>Barangay: PHP 200</li><li>National: PHP 2,000</li></ul>
</main>
<footer>Copyright 2026. All rights reserved.</footer>
</body></html>"""


def test_extract_page_keeps_main_text_under_headings():
    title, sections = scrape.extract_page(PAGE)

    assert title == "Business Name Registration | DTI"
    assert sections == [
        ("Business Name Registration", "Any Filipino at least 18 years old can register a business name."),
        ("Fees", "Barangay: PHP 200\nNational: PHP 2,000"),
    ]


RELEVANT_TEXT = (
    "To register a business name, apply online through BNRS. The registration fee depends on the "
    "territorial scope. Micro, small and medium enterprises can also get help from Negosyo Centers "
    "for business permits, loans, trainings and livelihood programs. " * 2
)


def test_is_relevant_keeps_business_pages_and_drops_noise():
    assert scrape.is_relevant("https://www.dti.gov.ph/business/registration/", "Business Name Registration", RELEVANT_TEXT)
    assert not scrape.is_relevant("https://www.dti.gov.ph/bids-and-awards/invitation-to-bid-2026/", "Invitation to Bid", RELEVANT_TEXT)
    assert not scrape.is_relevant("https://www.dti.gov.ph/careers/", "Job Vacancies: Administrative Aide", RELEVANT_TEXT)
    assert not scrape.is_relevant("https://www.dti.gov.ph/business/fees/", "Fees", "Registration fee: PHP 200.")
    assert not scrape.is_relevant("https://www.dti.gov.ph/news/sports-fest/", "DTI Sports Fest", "Employees joined the annual sports fest held at the main office. " * 10)


def test_chunk_page_makes_sized_passages_with_source_and_status():
    line = "Applicants must submit the accomplished form and a valid government ID to the office."
    sections = [
        ("Who can apply", "\n".join([line] * 6)),
        ("Requirements", "\n".join([line] * 14)),
    ]
    chunks = scrape.chunk_page("https://sbcorp.gov.ph/loans/", "RISE UP Loans | SB Corporation", sections, "SB Corp", "November 24, 2026")

    bodies = [c["text"].split("\nSource: ")[0] for c in chunks]
    assert all(400 <= len(b) <= 800 for b in bodies)
    assert "".join(bodies).count(line) == 20
    assert chunks[0]["title"] == "RISE UP Loans > Who can apply"
    assert chunks[-1]["title"] == "RISE UP Loans > Requirements"
    assert chunks[0]["text"].endswith(
        "\nSource: https://sbcorp.gov.ph/loans/ (checked November 24, 2026)\n(Status: VERIFIED, AUTO-EXTRACTED)"
    )
    assert chunks[0]["section"] == "SB Corp"
    assert chunks[0]["agency"] == "SB Corp"
    assert chunks[0]["url"] == "https://sbcorp.gov.ph/loans/"


def test_finalize_drops_duplicate_passages_and_numbers_the_rest():
    shared = "Negosyo Centers help MSMEs register their business and find financing."
    chunks = [
        {"title": "A", "text": f"{shared}\nSource: https://a.gov.ph/ (checked X)\n(Status: S)"},
        {"title": "B", "text": f"{shared}  \nSource: https://b.gov.ph/ (checked X)\n(Status: S)"},
        {"title": "C", "text": "Another passage.\nSource: https://c.gov.ph/ (checked X)\n(Status: S)"},
    ]
    out = scrape.finalize(chunks)

    assert [c["title"] for c in out] == ["A", "C"]
    assert [c["id"] for c in out] == ["S00001", "S00002"]


def test_allowed_follows_robots_txt():
    robots = "User-agent: *\nDisallow: /wp-admin/\nDisallow: /private\n"

    assert scrape.allowed(robots, "https://www.dti.gov.ph/business/registration/")
    assert not scrape.allowed(robots, "https://www.dti.gov.ph/wp-admin/edit.php")
    assert not scrape.allowed(robots, "https://www.dti.gov.ph/private/files")
    assert scrape.allowed("", "https://www.dti.gov.ph/anything/")


def test_extract_links_keeps_same_site_pages_under_prefixes():
    html = """<a href="/dti-business-center/permits/">Permits</a>
<a href="https://www.dti.gov.ph/dti-business-center/loans/#top">Loans</a>
<a href="/dti-careers/">Careers</a>
<a href="https://www.facebook.com/DTI">Facebook</a>
<a href="/dti-business-center/brochure.jpg">Image</a>
<a href="mailto:ask@dti.gov.ph">Email</a>"""
    links = scrape.extract_links(html, "https://www.dti.gov.ph/dti-business-center/", ["/dti-business-center/"])

    assert links == [
        "https://www.dti.gov.ph/dti-business-center/permits/",
        "https://www.dti.gov.ph/dti-business-center/loans/",
    ]


def test_is_relevant_drops_news_reports_and_member_benefit_pages():
    assert not scrape.is_relevant("https://sbcorp.gov.ph/corporate-governance-scorecard-2022/", "Corporate Governance Scorecard 2022", RELEVANT_TEXT)
    assert not scrape.is_relevant("https://www.tesda.gov.ph/About/TESDA/list-of-graduates", "List of Graduates", RELEVANT_TEXT)
    assert not scrape.is_relevant("https://ati2.da.gov.ph/ati-main/news/agrilink-2026", "AgriLink 2026 news", RELEVANT_TEXT)
    assert not scrape.is_relevant("https://www.sss.gov.ph/funeral-benefit/", "FUNERAL BENEFIT", RELEVANT_TEXT)


def test_is_useful_chunk_needs_length_and_business_words():
    assert scrape.is_useful_chunk("Micro enterprises can apply for a business loan of up to PHP 300,000 with a business permit and DTI registration. " * 2)
    assert not scrape.is_useful_chunk("Learn more | Visit an SSS Branch | Find a branch near you.")
    assert not scrape.is_useful_chunk("Did the Audit Committee meet at least four times during the year? Y | Board of Directors resumes | Atty. Juan dela Cruz | " * 3)


def test_is_relevant_drops_social_media_style_posts():
    assert not scrape.is_relevant("https://ati2.da.gov.ph/ati-main/content/article/50-interns", "\U0001d7f1\U0001d7ec \U0001d5d9\U0001d5ec\U0001d5d9\U0001d5dc\U0001d5e3\U0001d5e7 Interns", RELEVANT_TEXT)


def test_is_useful_chunk_drops_link_and_archive_lists():
    archive = "May 2022 (1) | April 2022 (1) | February 2022 (2) | January 2022 (1) | November 2021 (4) | business loan registration | " * 3
    assert not scrape.is_useful_chunk(archive)
