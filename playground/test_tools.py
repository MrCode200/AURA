from langchain_core.tools import tool

@tool
def browse(url: str, browser: str) -> str:
    """Browse to a URL in the specified browser.
    This opens the first link found for the URL in the specified browser. (so URL=Search Query)

    Args:
        url: URL to browse to
        browser: Browser to use (e.g., 'chrome', 'firefox', 'edge')
    """
    return f"Browsing to {url} using {browser}"

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city.

    Args:
        city: City to get weather for
    """
    # (Placeholder implementation)
    return f"It's always sunny in {city}!"

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers together.

    Args:
        a: First integer
        b: Second integer
    """
    return a * b


tools = [browse, multiply]