import os
import openai
import sys
import streamlit as st
import time

from langchain.chat_models import ChatOpenAI

from langchain.chains import LLMChain
from langchain.prompts import (PromptTemplate)
from langchain.memory import (ConversationSummaryMemory)

sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.environ['OPENAI_API_KEY']

st.title('Famous Pen Pals')
with st.expander('Instructions'):
    st.markdown(':blue[1. type your name in the sidebar]')
    st.markdown(':orange[2. choose a famous historical person, literary figure, or author]')
    st.markdown(':green[3. ask them a question and they will reply in a letter to you]')

with st.sidebar:
    option = st.selectbox(
        'Choose a category:',
        ('Historical Figure', 'Fictional Figure', 'Author')
    )

    if option == 'Historical Figure':
        author_option = st.selectbox(
            'Choose a historical figure for the AI to imitate:',
            ('Martin Luther King, Jr.', 'Amelia Earhart', 'Winston Churchill', 'Anna May Wong', 'Nelson Mandela',
             'Marie Curie', 'Wolfgang Amadeus Mozart', 'Karl Marx', 'Gautama Buddha', 'Leonardo da Vinci',
             'Jerry Garcia', 'Dali Llama', 'Carl Jung', 'Vladek Spiegelman', 'Artie Spiegelman')
        )
    elif option == "Fictional Figure":
        author_option = st.selectbox(
            'Choose a literary figure for the AI to imitate:',
            ('Hermione Granger', 'Nancy Drew', "Prince Hamlet", 'Atticus Finch', 'Willy Wonka',
             'Gandalf', 'Captain Ahab', 'Columbo', 'Superman', 'George Costanza')
        )
    else:
        author_option = st.selectbox(
            'Choose an author for the AI to imitate:',
            ('Homer', 'Jane Austen', 'Leo Tolstoy', 'Emily Dickinson', 'Franz Kafka', 'William Shakespeare',
             'Maya Angelou', 'Edgar Allan Poe')
        )

    userName = st.text_input("Type your name: ")

# AI template which passes framework for response
script_template = PromptTemplate(
    input_variables=['convo'],
    partial_variables={'author': author_option, 'name': userName},
    template='''{history}
    Reply to {convo} as if you are {author}.  You reply in the same style that {author} would write in.  
    Always respond in English.  Reply as if composing a letter to {name} with the closing and signature on its own line.  
    Do not write a poem or an essay.  
    Limit the response to 500 tokens.'''
)

model_mem = ChatOpenAI(temperature=0, max_tokens=250, model_name="gpt-3.5-turbo")
model = ChatOpenAI(temperature=0, max_tokens=500, model_name="gpt-3.5-turbo")
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
                        if "content" in st.session_state.messages[i] and st.session_state.messages[i]["role"] == "assistant":
                            answer = st.session_state.messages[i]["content"]
                            memorySt.save_context({"input": question}, {"output": answer})
                script = chainSt.invoke(input_text)
            for letter in script["script"]:
                full_response += letter + ("")
                time.sleep(0.03)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

