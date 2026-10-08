"""Streamlit UI. Run from the repository root: python -m streamlit run app.py."""
import os
import streamlit as st
from chatbot import Conversation, respond

st.set_page_config(page_title="CSC-128 Course Assistant", page_icon="📚")
st.title("CSC-128 Course Assistant")
st.info("I am a software chatbot. I help with CSC-128 resources, concepts, assignment requirements, and logistics.")
st.caption("Coverage: supplied capstone instructions and labeled project study notes. Messages and selected source excerpts are sent to Groq when AI is enabled. Do not enter personal information or secrets.")


def setting(name, default=""):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except FileNotFoundError:
        return default


if "conversation" not in st.session_state:
    st.session_state.conversation = Conversation()
    st.session_state.messages = []

with st.sidebar:
    st.header("Start here")
    st.markdown("- Find a resource\n- Explain slot filling\n- Capstone requirements\n- When is the capstone due?")
    ai_enabled = st.toggle("Use Groq for wording", value=True)
    if st.button("Reset conversation"):
        st.session_state.conversation = Conversation()
        st.session_state.messages = []
        st.rerun()
    st.caption("Grades, extensions, and policy exceptions must go to your instructor.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about CSC-128", max_chars=1500):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Checking course sources…"):
            answer = respond(prompt, st.session_state.conversation,
                             setting("GROQ_API_KEY") if ai_enabled else "",
                             setting("GROQ_MODEL", "openai/gpt-oss-20b"))
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.messages = st.session_state.messages[-40:]
