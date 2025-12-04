import os
from dotenv import dotenv_values
import streamlit as st
from groq import Groq

# Streamlit page config
st.set_page_config(
    page_title="The Tech Buddy 🧑‍💻",
    page_icon="🤖",
    layout="centered"
)

# Load secrets
try:
    secrets = dotenv_values(".env")  # For local testing
    GROQ_API_KEY = secrets["GROQ_API_KEY"]
except:
    secrets = st.secrets  # For Streamlit deployment
    GROQ_API_KEY = secrets["GROQ_API_KEY"]

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

INITIAL_RESPONSE = secrets["INITIAL_RESPONSE"]
INITIAL_MSG = secrets["INITIAL_MSG"]
CHAT_CONTEXT = secrets["CHAT_CONTEXT"]

# Initialize Groq client
client = Groq()

# Initialize chat history in session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE}
    ]

# Display page title
st.title("Welcome Buddy!")
st.caption("Helping You Level Up Your Coding Game")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar='🤖' if message["role"]=="assistant" else "🗨️"):
        st.markdown(message["content"])

# User input
user_prompt = st.chat_input("Ask me")

def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

# Handle user input
if user_prompt:
    with st.chat_message("user", avatar="🗨️"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Prepare messages
    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        {"role": "assistant", "content": INITIAL_MSG},
        *st.session_state.chat_history
    ]

    # Stream assistant response
    with st.chat_message("assistant", avatar='🤖'):
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Replace with your chosen model if needed
            messages=messages,
            stream=True
        )
        response = st.write_stream(parse_groq_stream(stream))
    st.session_state.chat_history.append({"role": "assistant", "content": response})
