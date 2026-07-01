import os
import json
import datetime
import uuid

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖")
st.title("🤖 AI Assistant")

if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None


def generate_title(prompt: str) -> str:
    text = " ".join(prompt.split()).strip()
    if not text:
        return "New chat"
    words = text.split()
    title = " ".join(words[:5])
    if len(words) > 5:
        title += "..."
    return title[:40]


def ensure_active_chat():
    if not st.session_state.conversations:
        new_chat = {
            "id": uuid.uuid4().hex,
            "title": "New chat",
            "messages": [],
            "session_memory": "",
        }
        st.session_state.conversations.append(new_chat)
        st.session_state.active_chat_id = new_chat["id"]
    elif st.session_state.active_chat_id is None or not any(
        chat["id"] == st.session_state.active_chat_id for chat in st.session_state.conversations
    ):
        st.session_state.active_chat_id = st.session_state.conversations[0]["id"]


ensure_active_chat()


def get_active_chat():
    for chat in st.session_state.conversations:
        if chat["id"] == st.session_state.active_chat_id:
            return chat
    return st.session_state.conversations[0]


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("hf_api_key")
)

MODEL_CANDIDATES = [
    os.getenv("HF_MODEL", "Qwen/Qwen2.5-3B-Instruct"),
    "Qwen/Qwen2.5-7B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
]


def build_request_messages(chat, system_prompt: str):
    messages = []

    if chat["session_memory"]:
        messages.append({"role": "system", "content": f"Session memory:\n{chat['session_memory']}"})

    messages.append({"role": "system", "content": system_prompt})

    for message in chat["messages"]:
        role = message.get("role", "user")
        content = message.get("content", "")
        if role not in {"system", "user", "assistant"}:
            role = "user"
        if not isinstance(content, str):
            content = str(content)
        messages.append({"role": role, "content": content})

    return messages


def get_model_response(messages, max_tokens, stream=True):
    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            return client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                stream=stream,
            )
        except Exception as exc:
            last_error = exc
            continue

    raise last_error

with st.sidebar:
    st.header("Chats")

    if st.button("➕ New chat", use_container_width=True):
        new_chat = {
            "id": uuid.uuid4().hex,
            "title": "New chat",
            "messages": [],
            "session_memory": "",
        }
        st.session_state.conversations.insert(0, new_chat)
        st.session_state.active_chat_id = new_chat["id"]
        st.rerun()

    st.markdown("---")

    if not st.session_state.conversations:
        st.caption("No chats yet")
    else:
        for chat in st.session_state.conversations:
            if st.button(chat["title"], key=f"chat_{chat['id']}", use_container_width=True):
                st.session_state.active_chat_id = chat["id"]
                st.rerun()

    st.markdown("---")
    st.header("Options")
    if st.button("Clear current chat", use_container_width=True):
        active_chat = get_active_chat()
        active_chat["messages"] = []
        active_chat["session_memory"] = ""
        active_chat["title"] = "New chat"
        st.rerun()

    st.header("Settings")
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful assistant.",
        height=100,
    )
    max_tokens = st.number_input("Max Tokens", 100, 4096, 1024)

    st.text_area(
        "Session Memory",
        value=get_active_chat()["session_memory"] or "No memory yet.",
        height=140,
        disabled=True,
    )

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt", "xlsx"])

active_chat = get_active_chat()

if uploaded_file is not None:
    try:
        content = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        content = uploaded_file.read().decode("utf-8", errors="ignore")

    with st.chat_message("assistant"):
        st.markdown("📄 File content")
        st.text(content)

for message in active_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What would you like to know?")

if prompt:
    active_chat["messages"].append({"role": "user", "content": prompt})

    if active_chat["title"] == "New chat":
        active_chat["title"] = generate_title(prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    request_messages = build_request_messages(active_chat, system_prompt)

    with st.chat_message("assistant"):
        assistant_chunks = []

        def stream_response(response_stream):
            for chunk in response_stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    assistant_chunks.append(delta)
                    yield delta

        try:
            response_stream = get_model_response(request_messages, max_tokens, stream=True)
            st.write_stream(stream_response(response_stream))
        except Exception as exc:
            st.error(f"Response error: {exc}")
            assistant_chunks = ["Sorry, I could not generate a response right now."]

    assistant_message = "".join(assistant_chunks)
    active_chat["messages"].append({"role": "assistant", "content": assistant_message})

    memory_parts = []
    if active_chat["session_memory"]:
        memory_parts = [part.strip() for part in active_chat["session_memory"].split("\n\n") if part.strip()]

    memory_parts.append(f"User: {prompt}\nAssistant: {assistant_message}")
    if len(memory_parts) > 3:
        memory_parts = memory_parts[-3:]

    active_chat["session_memory"] = "\n\n".join(memory_parts)

    if active_chat["messages"]:
        conversation_json = json.dumps(active_chat["messages"], indent=2)
        st.download_button(
            label="Download chat JSON",
            data=conversation_json,
            file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

st.markdown(
    """
    <style>
        .stChatMessage {
            padding: 1rem;
            border-radius: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)