from src.models.llm_factory import get_llm
from src.tools.calculator import multiply
from langchain.agents import create_agent

def create_math_agent():
    llm = get_llm()
    tools = [multiply]
    return create_agent(llm, tools)
