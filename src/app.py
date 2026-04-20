import os
import sys
import base64
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from dotenv import load_dotenv
from src.services.ai_service import AIService
from src.services.file_processor import FileProcessor
from src.services.session_manager import SessionManager

load_dotenv()

st.title("Intelligent AI Chat")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SESSION_DB_PATH = os.path.join(DATA_DIR, "chat_sessions.sqlite")

if "session_manager" not in st.session_state:
    st.session_state.session_manager = SessionManager(SESSION_DB_PATH)
if "ai_service" not in st.session_state:
    st.session_state.ai_service = AIService(st.session_state.session_manager)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "user_id" not in st.session_state:
    st.session_state.user_id = os.getenv("AI_USER_ID", os.getenv("USER", "default_user"))

loaded = st.session_state.session_manager.get_session(st.session_state.session_id)
if loaded:
    if "messages" not in st.session_state:
        st.session_state.messages = loaded.get("messages", [])
    if "mode" not in st.session_state:
        st.session_state.mode = loaded.get("mode", "Adaptive Agent (Tools+Memory)")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mode" not in st.session_state:
        st.session_state.mode = "Adaptive Agent (Tools+Memory)"

with st.sidebar:
    st.header("Settings")
    user_id = st.text_input("User ID (for long-term memory)", value=st.session_state.user_id)
    st.session_state.user_id = user_id.strip() or "default_user"

    mode = st.radio(
        "Mode:",
        ["Adaptive Agent (Tools+Memory)", "Adaptive Chat (No Tools)"],
        index=0 if st.session_state.mode == "Adaptive Agent (Tools+Memory)" else 1,
    )
    st.session_state.mode = mode
    
    st.header("Upload Info")
    uploaded_file = st.file_uploader("Upload Image or Text", type=["png", "jpg", "jpeg", "txt"])
    
    # State reset
    if st.button("Clear Memory"):
        st.session_state.messages = []
        st.session_state.session_manager.clear_session(st.session_state.session_id)
        st.rerun()

    if st.button("Clear Long-Term Memory"):
        st.session_state.session_manager.clear_user_memories(st.session_state.user_id)
        st.success("Long-term memory cleared for this user ID.")

# Show old messages
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("user"):
            st.markdown(msg["content"])
            image_b64 = msg.get("image_b64")
            if image_b64:
                st.image(base64.b64decode(image_b64))

# Input
user_input = st.chat_input("Ask anything...")

if user_input or uploaded_file:
    prompt = user_input or "Look at file."

    file_payload = FileProcessor.process_upload(uploaded_file)
    full_prompt = prompt + file_payload["prompt_suffix"]

    # Save user message
    msg_dict = {"role": "user", "content": prompt}
    if file_payload["image_b64"]:
        msg_dict["image_b64"] = file_payload["image_b64"]
    st.session_state.messages.append(msg_dict)

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
        if file_payload["image_b64"]:
            st.image(base64.b64decode(file_payload["image_b64"]))

    # Get AI response (handled via service layer with error handling)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if "Agent" in mode:
                ai_msg, is_error = st.session_state.ai_service.invoke_agent(
                    prompt=full_prompt,
                    thread_id=st.session_state.session_id,
                    user_id=st.session_state.user_id,
                    image_content=file_payload["agent_content"],
                )
            else:
                ai_msg, is_error = st.session_state.ai_service.invoke_chain(
                    full_prompt,
                    user_id=st.session_state.user_id,
                )

            if is_error:
                st.error(ai_msg)
            else:
                st.markdown(ai_msg)

            st.session_state.messages.append({"role": "assistant", "content": ai_msg})

    st.session_state.session_manager.save_session(
        session_id=st.session_state.session_id,
        mode=mode,
        messages=st.session_state.messages,
    )
