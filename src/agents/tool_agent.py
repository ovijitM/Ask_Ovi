from src.models.llm_factory import get_llm
from src.tools.calculator import multiply
from src.tools.search import internet_search
from src.tools.time import get_now_time
from src.tools.subprocess import run_shell_command
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from src.prompts.system_prompts import INTELLIGENT_SYSTEM_PROMPT
import sqlite3
import os
from typing import List, Optional

# Create global connection for persistent memory
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'memory.sqlite')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
memory = SqliteSaver(conn)


def get_default_tools() -> List:
    """Centralized tool registry so tool strategy is explicit and swappable."""
    return [multiply, internet_search, get_now_time, run_shell_command]


def create_general_agent(tools: Optional[List] = None, prompt: Optional[str] = None):
    llm = get_llm()
    selected_tools = tools or get_default_tools()
    selected_prompt = prompt or INTELLIGENT_SYSTEM_PROMPT
    return create_react_agent(
        llm,
        selected_tools,
        checkpointer=memory,
        prompt=selected_prompt,
    )
