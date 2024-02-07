import pandas as pd
import streamlit as st
from classes import get_primer, format_question, run_request
import warnings

warnings.filterwarnings("ignore")
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_icon="chat2vis.png", layout="wide", page_title="Chat2VIS")

st.markdown("<h1 style='text-align: center; font-weight:bold; padding-top: 0rem;'> \
            Data Visualization with OpenAI</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;padding-top: 0rem;'>Creating Visualisations using Natural Language</h2>", unsafe_allow_html=True)

# For additional citation referencing: st.sidebar.markdown(
#    '<a style="text-align: center;padding-top: 0rem;" href="https://blog.streamlit.io/chat2vis-ai-driven-visualisations-with-streamlit-and-natural-language">Blog </a> by Paula Maddigan',
#    unsafe_allow_html=True)

available_models = {"ChatGPT-4": "gpt-4", "ChatGPT-3.5": "gpt-3.5-turbo"}

# List to hold datasets
if "datasets" not in st.session_state:
    datasets = {}
    # Preload datasets
    datasets["Movies"] = pd.read_csv("movies.csv")
    datasets["Housing"] = pd.read_csv("housing.csv")
    datasets["Cars"] = pd.read_csv("cars.csv")
    datasets["Colleges"] = pd.read_csv("colleges.csv")
    datasets["Customers & Products"] = pd.read_csv("customers_and_products_contacts.csv")
    datasets["Department Store"] = pd.read_csv("department_store.csv")
    datasets["Energy Production"] = pd.read_csv("energy_production.csv")
    st.session_state["datasets"] = datasets
else:
    # use the list already loaded
    datasets = st.session_state["datasets"]

with st.sidebar:
    # First we want to choose the dataset, but we will fill it with choices once we've loaded one
    dataset_container = st.empty()

    # Add facility to upload a dataset
    try:
        with st.container(border=True):
            uploaded_file = st.file_uploader(":computer: Load a CSV file:", type="csv")
            index_no = 0
            if uploaded_file:
                # Read in the data, add it to the list of available datasets. Give it a nice name.
                file_name = uploaded_file.name[:-4].capitalize()
                datasets[file_name] = pd.read_csv(uploaded_file)
                # We want to default the radio button to the newly added dataset
                index_no = len(datasets) - 1
    except Exception as e:
        st.error("File failed to load. Please select a valid CSV file.")
        print("File failed to load.\n" + str(e))

    # Radio buttons for dataset choice
    chosen_dataset = dataset_container.radio(":bar_chart: Choose your data:", datasets.keys(),
                                             index=index_no)  # ,horizontal=True,)
    # Check boxes for model choice
    with st.container(border=True):
        st.write(":brain: Choose your model(s):")
        # Keep a dictionary of whether models are selected or not
        use_model = {}
        for model_desc, model_name in available_models.items():
            label = f"{model_desc} ({model_name})"
            key = f"key_{model_desc}"
            use_model[model_desc] = st.checkbox(label, value=True, key=key)

    with st.container(border=True):
        st.write("Citation:")
        st.markdown("<h4  style='text-align: center;font-size:small;color:grey;padding-top: 0rem;padding-bottom: .2rem;'>Chat2VIS: Generating Data \
            Visualisations via Natural Language using ChatGPT, Codex and GPT-3 \
            Large Language Models </h4>", unsafe_allow_html=True)

        st.caption("(https://doi.org/10.1109/ACCESS.2023.3274199)")

# Text area for query
question = st.text_area(":eyes: What would you like to visualize?", height=10)
go_btn = st.button("Go...")

# Make a list of the models which have been selected
selected_models = [model_name for model_name, choose_model in use_model.items() if choose_model]
model_count = len(selected_models)

# Execute chatbot query
if go_btn and model_count > 0:
    # Place for plots depending on how many models
    plots = st.columns(model_count)
    # Get the primer for this dataset
    primer1, primer2 = get_primer(datasets[chosen_dataset], 'datasets["' + chosen_dataset + '"]')
    # Create model, run the request and print the results
    for plot_num, model_type in enumerate(selected_models):
        with plots[plot_num]:
            st.subheader(model_type)
            try:
                # Format the question
                question_to_ask = format_question(primer1, primer2, question, model_type)
                # Run the question
                answer = ""
                answer = run_request(question_to_ask, available_models[model_type])

                # the answer is the completed Python script so add to the beginning of the script to it.
                answer = primer2 + answer
                print("Model: " + model_type)
                print(answer)
                plot_area = st.empty()
                plot_area.pyplot(exec(answer))

            except Exception as error:
                st.error(error)

# Display the datasets in a list of tabs
# Create the tabs
tab_list = st.tabs(datasets.keys())

# Load up each tab with a dataset
for dataset_num, tab in enumerate(tab_list):
    with tab:
        # Can't get the name of the tab! Can't index key list. So convert to list and index
        dataset_name = list(datasets.keys())[dataset_num]
        st.subheader(dataset_name)
        st.dataframe(datasets[dataset_name], hide_index=True)

# Insert footer to reference dataset origin
footer = """<style>.footer {position: fixed;left: 0;bottom: 0;width: 100%;text-align: center;}</style><div class="footer">
<p> <a style='display: block; text-align: center;'> Datasets courtesy of NL4DV, nvBench and ADVISor </a></p></div>"""
st.caption("Datasets courtesy of NL4DV, nvBench and ADVISor")

# Hide menu and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)