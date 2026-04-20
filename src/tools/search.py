import http.client
import urllib.parse
from langchain_core.tools import tool

@tool
def internet_search(query: str) -> str:
    """Search internet for query."""
    conn = http.client.HTTPSConnection("google.serper.dev")
    encoded_query = urllib.parse.quote(query)
    conn.request("GET", f"/search?q={encoded_query}&apiKey=4c9dd1c6f2a600df3d9b694e558fe32f305a5a91", '', {})
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")
