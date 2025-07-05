from helpers.input_sanitizer import sanitize_query_input, escape_discord_markdown, escape_query_param

def test_sanitize_query_trims_and_limits():
    query = "   Risk Legacy  " + "x" * 200
    result = sanitize_query_input(query)
    assert result.startswith("Risk Legacy")
    assert len(result) <= 100

def test_escape_markdown():
    raw = "*bold* _italic_ ~strike~"
    escaped = escape_discord_markdown(raw)
    assert escaped == r"\*bold\* \_italic\_ \~strike\~"

def test_escape_query_param():
    assert escape_query_param("Ticket to Ride: Europe") == "Ticket%20to%20Ride%3A%20Europe"
