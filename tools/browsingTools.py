import trafilatura
from ddgs import DDGS

from tools import tool_registry, logger
from tools.toolResponse import ToolResponse

MAX_CHARS_TOTAL: int = 12000  # TODO: Move to settings
MIN_CHARS_WARNING: int = 500  # Warn if extracted content per page is below this


# Improve using scores based on:
# 1. paragraph length
# 2. overlap of query words with words in paragraph
# 3. (find more ...)

def extract_content(url: str, max_chars: int) -> str:
    """Fetches and extracts main content from a URL using Trafilatura."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        logger.warning(f"Failed to fetch URL: {url}")
        return ""

    # USE favor_recall
    # If parts of your documents are missing, try this preset to take more elements into account.
    result = trafilatura.extract(downloaded, favor_recall=True, include_comments=False)

    # USE favor_precision
    # If your results contain too much noise, prioritize precision to focus on the most central and relevant elements.
    if not result:
        result = trafilatura.extract(downloaded, favor_precision=True)

    content = result[:max_chars]
    return content


def find_links(queries: list[str], top_k: int) -> list[dict[str, any]]:
    """
    Searches DuckDuckGo for links using multiple queries.

    Divides the top_k results between the queries to get a more diverse set of results.
    :param queries: List of queries to search for
    :param top_k: Number of results to return
    """

    results: list[dict[str, str]] = []
    with DDGS() as ddgs:
        for i, q in enumerate(queries):
            if len(queries) == 1:
                max_results = top_k
            elif i == len(queries) - 1:
                max_results = top_k - int(top_k / len(queries)) * i
            else:
                max_results = int(top_k / len(queries))

            res = ddgs.text(q, safesearch="off", max_results=max_results)
            results.extend(res)

    return results


@tool_registry.register_function()
def browse(query: str | list[str], top_k: int = 3) -> dict:
    """
    Browses the web for information. Be precise with the query to exclude irrelevant results.
    Use this tool only if you don't have any information.
    If the user is unsatisfied with the results he will tell you to search.

    You can use DuckDuckGo search operators to refine results:
        - `cats dogs` → Results about cats **or** dogs
        - `"cats and dogs"` → Exact phrase match
        - `cats -dogs` → Exclude results containing "dogs"
        - `cats +dogs` → Boost results containing "dogs"
        - `dogs site:example.com` → Results from a specific site
        - `intitle:dogs` → Pages with "dogs" in the title
        - `inurl:cats` → Pages with "cats" in the URL

    :param query: The query to browse the web for
    :param top_k: The number of results to return
    """
    if isinstance(query, str):
        query = [query]

    browse_results: list[dict[str, str]] = []
    try:
        results = find_links(query, top_k)
        if not results:
            return ToolResponse(
                status="success",
                message=f"No results found for {query}",
                metadata={"results": []}
            ).model_dump()

        chars_per_page = int(MAX_CHARS_TOTAL / len(results))
        for r in results:
            href = r.get("href") or r.get("url")
            title = r.get("title") or ""
            content = extract_content(href, chars_per_page)

            # Absolute warning if truncated content is too small
            if len(content) == 0:
                logger.warning(f"No content extracted for {href}")
                continue

            elif len(content) < MIN_CHARS_WARNING:
                logger.warning(
                    f"Content truncated or too short ({len(content)=} chars < {MIN_CHARS_WARNING=} chars) due to MAX_CHARS_TOTAL.")

            browse_results.append({
                "href": href,
                "title": title,
                "content": content,
            })

        return ToolResponse(
            status="success",
            message=f"{query} browsed successfully",
            metadata={"results": browse_results}
        ).model_dump()
    except Exception as e:
        return ToolResponse(
            status="error",
            message=f"Failed to browse {query}",
            metadata={"results": browse_results},
            error=str(e)
        ).model_dump()
