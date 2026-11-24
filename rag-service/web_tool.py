from langchain.tools import tool
from langchain_core.tools import ToolException
from langchain_tavily import TavilySearch

WEB_RESULTS = 3
# Tavily's country boost works only with topic "general", so it is not used with news.
SEARCH_TOPIC = "news"
SEARCH_TIME_RANGE = "month"
# Government agencies and Philippine news sites only, so foreign and social media pages are left out.
TRUSTED_SITES = [
    "dti.gov.ph",
    "dole.gov.ph",
    "dswd.gov.ph",
    "tesda.gov.ph",
    "sbcorp.gov.ph",
    "baguio.gov.ph",
    "benguet.gov.ph",
    "pna.gov.ph",
    "pia.gov.ph",
    "sunstar.com.ph",
    "inquirer.net",
    "mb.com.ph",
    "philstar.com",
]
# Added to every search so results from the Cordillera rank higher.
LOCAL_PLACES = "Baguio Benguet Cordillera"

tavily = TavilySearch(max_results=WEB_RESULTS)


@tool(response_format="content_and_artifact", return_direct=True)
def web_search(query: str):
    """Search the web for current news and recent updates (this month, this year, new or latest programs, announcements) about small business and livelihood in the Philippines."""
    try:
        found = tavily.invoke({"query": f"{query} {LOCAL_PLACES}", "topic": SEARCH_TOPIC, "time_range": SEARCH_TIME_RANGE, "include_domains": TRUSTED_SITES})
    except ToolException:
        return "", []
    # When nothing is found, Tavily returns a plain message string instead of a dict.
    if not isinstance(found, dict):
        return "", []
    results = [r for r in found.get("results", []) if r["title"].strip()]
    context = "\n\n".join(f"### {r['title']}\n{r['content']}" for r in results)
    return context, results
