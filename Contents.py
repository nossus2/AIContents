import streamlit as st

st.set_page_config(
    page_title="AI Activities",
    page_icon="👋",
)

st.write("# Welcome to IMS AI Activities! 👋")

st.sidebar.success("Select an activity above.")

st.markdown(
    """
    These activities are intended for educational use.
    Remember that these LLM AI's can provide non-factual statements.
    The higher your value for the AI's variance, the greater chance you will see these.
    If you encounter any bugs, errors, or invalid responses, please report them to edtech@indianmountain.org.
    
    **Famous PenPal** allows you to ask questions of a famous historical or fictional person
    You will receive responses in the form of a letter.
    
    **Polyglot Chat** allows you to interact with an author in their native language.
    You can also find the definition of words or characters.  Be sure to read the instructions!
    
    **Data Visualization** allows you to use an existing .csv or to upload your own.
    You can then use natural language to plot the data.
    
    **Debate AI** provides a format for you to debate with the AI on a topic of your devising.
"""
)