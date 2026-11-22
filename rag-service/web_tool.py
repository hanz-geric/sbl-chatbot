import os
import uuid
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.tools import ToolException
from langchain_tavily import TavilySearch

load_dotenv()

WEB_RESULTS = 3
SEARCH_TOPIC = "news"
SEARCH_TIME_RANGE = "year"
SEARCH_DEPTH = "basic"
QUERY_SUFFIX = "Philippines"

tavily = TavilySearch(
    max_results = WEB_RESULTS,
    tavily_api_key = os.getenv("TAVILY_API_KEY"),
    topic = SEARCH_TOPIC,
    time_range = SEARCH_TIME_RANGE,
    search_depth = SEARCH_DEPTH,
)


def format_results(results: list[dict]) -> str:
    return "\n\n".join(f"### {r['title']}\n{r['content']}" for r in results)


@tool(response_format="content_and_artifact")
def web_search(query: str):
    """
        Search the internet for CURRENT news and recent updates about small business and livelihood in the Philippines: 
        new or latest programs, announcements, deadlines, and anything happening this month or this year. 
        Use this ONLY when the question is about something recent or new. Do NOT use it for 
        general questions about programs, requirements, eligibility, 
        or how to apply; the knowledge base answers those.
    """
    try:
        found = tavily.invoke({"query": f"{query} {QUERY_SUFFIX}"})
    except ToolException:
        return "", []
    results = found.get("results", [])
    return format_results(results), results


if __name__ == "__main__":

    QUERY = "DTI Cordillera news MSME"
    ID = str(uuid.uuid4())

    out = web_search.invoke({
            "name": "web_search", 
            "args": { "query": QUERY }, 
            "id": ID,
            "type": "tool_call"
        })

    print(out.content)
    print(out.artifact)