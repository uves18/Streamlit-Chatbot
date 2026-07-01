from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
import os
load_dotenv()
import json
import datetime
# st.title("Echo bot")

# if "messages" not in st.session_state:
#     st.session_state.messages=[]

# #display chat messages from history i.e session_state
# # prompt= st.chat_input("type something")
# # if prompt:
# #     st.write(f"User has sent the following-> {prompt}")

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input("What's up?"):
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     st.session_state.messages.append({"role":"user", "content":prompt})

# response=f"Echo: {prompt}"
# #display assistant message in the chat container
# with st.chat_message("assistant"):
# #add assistant response to the chat history
#     st.session_state.messages.append({"role":"assiatnt", "content":prompt})

#------------------------------------------------------------------------------------------------
# import random
# import time

# def response_generator():
#     response=random.choice(
#         [
#             "hello hi there, how can i assit you today",
#             "ha bol",
#             "pareshan mat kar",
#         ]
#     )
#     for word in response.split():
#         yield word + " "
#         time.sleep(0.05)



# if"messages" not in st.session_state:
#     st.session_state.messages=[]

# #intitalize the chat history
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# #accept the user
# if prompt :=st.chat_input("What's up?"):
# #display the messgae in the chat message container 
#     with st.chat_message("user"):
#         st.markdown(prompt)
# #add the user to the chat history
# st.session_state.messages.append({"role":"user", "content":prompt})

# with st.sidebar:
#     st.title("options")
#     if st.button("clear chat history"):
#         st.session_state.message=[]
#         st.rerun

#---------------------------------------------------------------------------------
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖")
st.title("🤖 AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("hf_api_key")
)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What would you like to know?"):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("thinking..."):

            response = client.chat.completions.create(
                model="Qwen/Qwen3.5-9B",
                messages=st.session_state.messages,
                max_tokens=1024
            )

            assistant_message = response.choices[0].message.content
            st.markdown(assistant_message)

    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_message
    })

with st.sidebar:
    st.title("Options")
    if st.button("clear the history"):
        st.session_state.messages=[]
        st.rerun()



#uploading files to the streamlit web app
with st.sidebar:
    file=st.file_uploader("Choose a file",
                         type=["csv","txt","xlxs"] )

if file is not None:
    content= file.read().decode("utf-8")
    with st.chat_message("assistant"):
        st.markdown("📄File Content:")
        st.text(content)


#day9 System Prompts & Settings
with st.sidebar:
    st.title("Settings")
    system_prompt=st.text_area(
        "System Prompt",
        value="You are a helpful assistant",
        height=100
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    max_tokens = st.number_input("Max Tokens", 100, 4096, 1024)
    st.write("-----------------------------------------------")
    if st.button:
        if st.session_state.messages:
            conversation_json=json.dumps(
                st.session_state.messages,
                indent=2
            )
            st.download_button(
                label="Download JSON",  # Added comma here
                data=conversation_json, # Added comma here
                file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                 mime="application/json"
            )
st.markdown("""
    <style>
            .stChatMessage{
                padding:1 rem
                border.radius: 1 rem
            </style>
""", unsafe_allow_html=True)