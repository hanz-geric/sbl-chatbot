from langchain.tools import tool
from langchain_core.tools import ToolException
from langchain_tavily import TavilySearch

WEB_RESULTS = 3
SEARCH_COUNTRY = "philippines"

tavily = TavilySearch(max_results=WEB_RESULTS, country=SEARCH_COUNTRY)


@tool(response_format="content_and_artifact", return_direct=True)
def web_search(query: str):
    """Search the web for current news and recent updates (this month, this year, new or latest programs, announcements) about small business and livelihood in the Philippines."""
    try:
        found = tavily.invoke({"query": query})
    except ToolException:
        return "", []
    # When nothing is found, Tavily returns a plain message string instead of a dict.
    if not isinstance(found, dict):
        return "", []
    results = found.get("results", [])
    context = "\n\n".join(f"### {r['title']}\n{r['content']}" for r in results)
    return context, results
