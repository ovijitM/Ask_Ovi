import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src.chains.basic_chain import create_intelligent_chain
from src.agents.tool_agent import create_general_agent
from src.utils.logger import get_logger

load_dotenv()
log = get_logger()

def main():
    log.info("App start.")
    while True:
        print("\nModes:\n1. Adaptive Chat (No Tools)\n2. Adaptive Agent (Tools+Memory)\n3. Exit")
        choice = input("Pick (1/2/3): ")
        
        if choice == '3':
            break
            
        elif choice == '1':
            chain = create_intelligent_chain()
            user_input = input("Chat prompt: ")
            print(">>>", chain.invoke({"input": user_input}))
            
        elif choice == '2':
            agent = create_general_agent()
            print("Adaptive Agent ready. Type 'back' to change mode.")
            config = {"configurable": {"thread_id": "session_1"}}
            while True:
                user_input = input("Agent prompt: ")
                if user_input.lower() == 'back':
                    break
                response = agent.invoke({"messages": [("user", user_input)]}, config=config)
                
                if "messages" in response and response["messages"]:
                    print(">>>", response["messages"][-1].content)

if __name__ == "__main__":
    main()
