"""
web_search.py — free web research tool, no API key needed.
Uses duckduckgo-search, which is free and doesn't require signup.
"""
from duckduckgo_search import DDGS


def search_web(query, max_results=5):
    """Search the web and return a list of {title, snippet, url} results."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title"),
                    "snippet": r.get("body"),
                    "url": r.get("href")
                })
    except Exception as e:
        return [{"title": "Search failed", "snippet": str(e), "url": ""}]
    return results


def format_results_for_model(results):
    """Turn search results into a text block the LLM can read and reason over."""
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}\n{r['snippet']}\nSource: {r['url']}\n")
    return "\n".join(lines)


if __name__ == "__main__":
    # Quick manual test: python3 web_search.py
    res = search_web("current price of gold per gram")
    print(format_results_for_model(res))
