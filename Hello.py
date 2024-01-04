import streamlit as st

st.set_page_config(
    page_title="AI Activities",
    page_icon="👋",
)

st.write("# Welcome to IMS AI Activities! 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    These activities are intended for educational use.
    They use GPT 3.5 Turbo as the AI.
    If you encounter any bugs, errors, or invalid responses, please report them to edtech@indianmountain.org.
"""
)