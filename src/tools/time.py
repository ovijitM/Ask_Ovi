from datetime import datetime
from langchain_core.tools import tool

@tool
def get_now_time() -> str:
    """Get current date and time."""
    return datetime.now().isoformat()
