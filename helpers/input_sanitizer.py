import re
from urllib.parse import quote

MAX_QUERY_LENGTH = 100

def sanitize_query_input(query: str) -> str:
    """
    Cleans user input for search queries:
    - Strips whitespace
    - Escapes Discord markdown
    - Enforces a max length
    """
    query = query.strip()

    # Enforce max length
    if len(query) > MAX_QUERY_LENGTH:
        query = query[:MAX_QUERY_LENGTH]

    return escape_discord_markdown(query)

def escape_discord_markdown(text: str) -> str:
    """
    Escapes common Discord markdown characters.
    """
    escape_chars = r"*_~`>|"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def escape_query_param(query: str) -> str:
    """
    Escapes a string to be safely used as a URL query parameter.
    """
    return quote(query)
