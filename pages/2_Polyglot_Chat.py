import os
import openai
import sys
import streamlit as st
import time

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (PromptTemplate)
from langchain.memory import (ConversationBufferMemory)

sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

available_models = {"ChatGPT-3.5": "gpt-3.5-turbo", "ChatGPT-4": "gpt-4"}

st.title('Polyglot Chat')
with st.expander('Instructions'):
    st.markdown(':green[*either* ]:orange[ type any word or phrase into the chat below]')
    st.markdown(':green[*or* ]:orange[ type :blue["qs"] plus a word to discover the English meaning.]')
    st.caption(':orange[*for example, type :blue["qs villa"] to find out the definition of the word "villa."*]'
               ' :grey[*(qs = quid significat? "What does ... mean?")*]')

with st.sidebar:
    option = st.selectbox(
        'Choose a language:',
        ('Latin', 'Spanish', 'Mandarin')
    )

    if option == 'Latin':
        author_option = st.selectbox(
            'Choose an author for the AI to imitate:',
            ('Caesar', 'Cicero', 'Tacitus', 'Catullus', 'Lucretius', 'Ovid', 'Bede', 'John Gower')
        )
    elif option == "Spanish":
        author_option = st.selectbox(
            'Choose an author for the AI to imitate:',
            ('Borges', 'Paz', 'Neruda', 'Marquez', 'Cervantes', 'Lorca')
        )
    else:
        author_option = st.selectbox(
            'Choose an author for the AI to imitate:',
            ('Confucius', 'Lao Tse', 'Wang Wei', 'Luo Guanzhong', 'Lu Xun')
        )

    title_template = PromptTemplate(
        input_variables = ['concept'],
        partial_variables = {'language': option},
        template='Completely ignore the letters, "q" and "s" that {concept} begins with, then give the dictionary entry for the {language} word.'
    )

    script_template = PromptTemplate(
        input_variables = ['convo'],
        partial_variables = {'language': option, 'author': author_option},
        template='''
        Do not repeat {convo} when responding. If {convo} is in English, reply to it in {language}.  
        Reply in {language} to {convo} with no English translation.  
        Use the {language} in the style of {author}.  Be thorough and complete in your response.'''
    )

    with st.container(border=True):
        # Keep a dictionary of whether models are selected or not
        use_model = st.selectbox(':brain: Choose your model(s):',available_models.keys())
        use_model = available_models[use_model]

memoryS = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
model = ChatOpenAI(temperature=0, max_tokens=400, model_name=use_model)
chainT = LLMChain(llm=model, prompt=title_template, verbose=True, output_key='title')
chainS = LLMChain(llm=model, prompt=script_template, verbose=True, output_key='script', memory=memoryS)

with st.sidebar:
    # reset button
    if st.button("Clear Messages", type="primary"):
        # streamlit_js_eval(js_expressions="parent.window.location.reload()")
        st.session_state.messages.clear()
        memoryS.clear()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Format chat input and print it to screen
if input_text := st.chat_input("Quid agis?"):
    with st.chat_message("user"):
        st.markdown(input_text)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": input_text})

# Display the output if the the user gives an input - qs = define, else converse
if input_text and input_text[:2] == "qs":
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # moderate the post for harmful language
        from openai import OpenAI
        client = OpenAI()
        moderate_dict = client.moderations.create(input=input_text).model_dump()
        is_flagged = moderate_dict["results"][0]["flagged"]
        if is_flagged == True:
            st.write("There is something inappropriate about what you asked.")
        else:
            title = chainT.invoke(input_text)
            message_placeholder.markdown(title)
            st.session_state.messages.append({"role": "assistant", "content": title})

elif input_text:
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
                            memoryS.save_context({"input": question}, {"output": answer})
                script = chainS.invoke(input_text)
            for letter in script["script"]:
                full_response += letter + ("")
                time.sleep(0.02)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
