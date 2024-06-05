import streamlit as st
from PIL import Image
import pandas as pd

from Main.components.sidebar import sidebar
from Main.core.summary import generate_company_report
from Main.ui import (
    is_query_valid,
    is_open_ai_key_valid,
)

from Main.core.qa import get_query_answer, get_relevant_docs

VECTOR_STORE = "faiss"
MODEL = "openai"

# init
st.set_page_config(page_title="Doxter RAG", page_icon="📖", layout="wide")
# image
image = Image.open('Main/assets/logo.png')
st.image(image)
# Title
st.header("Doxter RAG")

# sidebar
sidebar()

openai_api_key = st.session_state.get("OPENAI_API_KEY")

if not openai_api_key:
    st.warning(
        "please Login to access the app!"
    )

# load API


uploaded_files = None
url = None

files = st.session_state.get("FILES")
selected_files = st.session_state.get("SELECTED_FILES")
folder_index = st.session_state.get("FOLDER_INDEX", None)

# wait for input
if (not url and not uploaded_files and st.session_state.get("FILES", None) == None) or not openai_api_key:
    st.stop()

if not is_open_ai_key_valid(openai_api_key):
    st.stop()
# check if vector DB loaded
if folder_index is None:
    st.stop()
# open chat area
with st.form(key="qa_form"):
    query = st.text_area("Ask a question about the SELECTED document")
    submit = st.form_submit_button("Submit")

# options to show more info
with st.expander("Advanced Options"):
    generate_report = st.button("Generate Report")

# generate report
if generate_report:
    with st.spinner("Generating Report... This may take a while⏳"):
        result = generate_company_report()
    st.download_button("Download Report", result)

# setup new chat
if not st.session_state.get("messages"):
    st.session_state.messages = []

# when chat sent
if submit:
    if not is_query_valid(query):
        st.stop()

    # get updated query
    search_query = query + ' \n '
    # if summary:
    #     search_query += get_query_answer(query, summary)
    summary = st.session_state.get("SUMMARY")
    search_query += get_query_answer(query, summary)

    result = get_relevant_docs(
        folder_index=folder_index,
        query=query,
        search_query=search_query,
    )
    # add answer
    st.session_state.get("messages").append({"role": "user", "content": query})
    st.session_state.get("messages").append({"role": "assistant", "content": result.answer})
    st.session_state["results"] = result.sources

if st.session_state.get("messages"):
    # Output Columns
    answer_col, sources_col = st.columns(2)
    with answer_col:
        st.markdown("#### Answer")
        for msg in reversed(st.session_state.get("messages")):
            message = f"""
            {msg["content"]}
            """
            st.chat_message(msg["role"]).write(message)
        # st.markdown(result.answer)

    with sources_col:
        st.markdown("#### Sources")
        for source in st.session_state.get("results", []):
            message = f"""
                        {source.page_content}
                        """
            st.write(message)
            st.markdown(source.metadata.get("file_name", "") + " : " + source.metadata.get("source", ""))
            st.markdown("---")
