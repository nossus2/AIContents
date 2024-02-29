import os
import openai
import sys
import streamlit as st
import time

from langchain_openai import ChatOpenAI

from langchain.chains import LLMChain
from langchain.prompts import (PromptTemplate)
from langchain.memory import (ConversationSummaryMemory)

sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.environ['OPENAI_API_KEY']

available_models = {"ChatGPT-3.5": "gpt-3.5-turbo", "ChatGPT-4": "gpt-4"}

st.title('Debate AI')
with st.expander('Instructions'):
    st.markdown(':blue[1. type a topic to debate in the sidebar]')
    st.markdown(':orange[2. choose the ai role in the debate]')
    st.markdown(':green[3. choose the grade level to debate at]')

with st.sidebar:
    topic = st.text_input("Type the topic you would like to debate. ")

    role = st.selectbox(
        """Select the AI's role in the debate.  
        It will argue either pro/for the topic stated above or con/against the topic stated above. """,
        ("pro/for", "con/against")
    )

    option = st.selectbox(
        'Choose a grade level:',
        ("4", "5", "6", "7", "8", "9", "10", "11", "12")
    )

    with st.container(border=True):
        # Keep a dictionary of whether models are selected or not
        use_model = st.selectbox(':brain: Choose your model(s):',available_models.keys())
        # Assign temperature for AI
        use_model = available_models[use_model]
        aiTemp = st.slider(':sparkles: Choose AI variance or creativity:', 0.0, 1.0, 0.0, 0.1)


# AI template which passes framework for response
script_template = PromptTemplate(
    input_variables=['convo'],
    partial_variables={'topic': topic, 'grade_level': option, 'role': role},
    template='''
        You are a persuasive expert at debating and rhetoric.  The premise of the debate is {topic}.  
        You are arguing {role} the {topic}.  
        Your response to the user should include critique of their {convo} and evidence to support your own arguments.
        Your response should be tailored to someone in grade {grade_level}.
        Be sure to take into account what was said previously: {history} - before responding
        Limit the response to 500 tokens.'''
)

model_mem = ChatOpenAI(temperature=0, max_tokens=250, model_name=use_model)
model = ChatOpenAI(temperature=aiTemp, max_tokens=500, model_name=use_model)
memorySt = ConversationSummaryMemory(llm=model_mem, memory_key='history', return_messages=True)
chainSt = LLMChain(llm=model, prompt=script_template, verbose=True, output_key='script', memory=memorySt)

with st.sidebar:
    # reset button
    if st.button("Clear Messages", type="primary"):
        # streamlit_js_eval(js_expressions="parent.window.location.reload()")
        st.session_state.messages.clear()
        memorySt.clear()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Format chat input and print it to screen
if input_text := st.chat_input("Type Here:"):
    with st.chat_message("user"):
        st.markdown(input_text)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": input_text})

# Display the output if the the user types any input
if input_text:
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # moderate the post for harmful language
        from openai import OpenAI

        client = OpenAI()
        moderate_dict = client.moderations.create(input=input_text).model_dump()
        is_flagged = moderate_dict["results"][0]["flagged"]

        if is_flagged == True:
            st.write("There is something inappropriate about what you asked.")

        else:
            with st.spinner("Thinking..."):
                if st.session_state.messages:
                    for i in range(len(st.session_state.messages)):
                        if "content" in st.session_state.messages[i] and st.session_state.messages[i]["role"] == "user":
                            question = st.session_state.messages[i]["content"]
                        if "content" in st.session_state.messages[i] and st.session_state.messages[i][
                            "role"] == "assistant":
                            answer = st.session_state.messages[i]["content"]
                            memorySt.save_context({"input": question}, {"output": answer})
                script = chainSt.invoke(input_text)
            for letter in script["script"]:
                full_response += letter + ("")
                time.sleep(0.02)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})