from langchain_core.output_parsers import StrOutputParser
from src.models.llm_factory import get_llm
from src.prompts.system_prompts import INTELLIGENT_PROMPT

def create_intelligent_chain(prompt_template=INTELLIGENT_PROMPT, temperature=0.7):
    llm = get_llm(temperature=temperature)
    return prompt_template | llm | StrOutputParser()


def create_caveman_chain():
    # Backward-compatible alias for existing callers.
    return create_intelligent_chain()
