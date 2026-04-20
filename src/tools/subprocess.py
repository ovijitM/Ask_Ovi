import subprocess
from langchain_core.tools import tool

@tool
def run_shell_command(command: str) -> str:
    """Execute shell command. Return output or error."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)
