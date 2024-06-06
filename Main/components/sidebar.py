import pandas as pd
import streamlit as st
from streamlit_tags import st_tags_sidebar

from Main.components.faq import faq
from dotenv import load_dotenv
import os

from Main.core.api import BackendAPI
from Main.core.embedding import embed_files

load_dotenv()


def sidebar():
    with st.sidebar:
        backend_api = st.session_state.get("BACKEND_API", None)
        # case not logged in
        if not st.session_state.get('online', False):
            st.markdown(
                "## How to use\n"
                "1. Enter your password below🔑\n"  # noqa: E501
                "2. Upload a pdf, docx, or txt file📄\n"
                "3. Ask a question about the document💬\n"
            )
            username = st.text_input("username",
                                     placeholder="username")
            password = st.text_input(
                "Password",
                type="password",
                placeholder="password",
                help="you can send us an email at https://www.synapse-analytics.io/contact to get access",  # noqa: E501
                value=None
            )
            login_btn = st.button('login')

            if login_btn:
                if not backend_api:
                    backend_api = BackendAPI()
                    st.session_state["BACKEND_API"] = backend_api
                # create api
                success = backend_api.login(username, password)
                if success:
                    st.session_state["online"] = True
                    st.session_state["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", None)
                    update_files()


        # case logged in
        else:
            st.markdown(
                f"## Welcome {backend_api.user}\n"
                "1. Upload a pdf, docx, or txt file📄\n"
                "2. Ask a question about the document💬\n"
            )
            st.markdown("## Upload New Files:")
            uploaded_files = st.file_uploader(
                "Upload file of the following format: pdf, docx, pptx, xlsx or txt",
                type=["pdf", "docx", "txt", "pptx", "xlsx"],
                accept_multiple_files=False
            )
            if uploaded_files:
                tags = st_tags_sidebar(
                    label='',
                    text='File Tags...',
                    value=[],
                    maxtags=4,
                    key='1')
                col1, col2 = st.columns([1, 1])
                with col1:
                    upload_btn = st.button('Upload')
                with col2:
                    upload_ocr_btn = st.button('Upload OCR')
                if upload_btn:
                    # upload file to DB
                    # for file in uploaded_files:
                    file = uploaded_files
                    backend_api.upload(file.name, file, tags=tags)
                    update_files()
                if upload_ocr_btn:
                    # upload file to DB using OCR
                    # for file in uploaded_files:
                    file = uploaded_files
                    backend_api.upload(file.name, file, tags=tags, ocr=True)
                    update_files()

            st.markdown("## Your Files:")
            filter_tags = st_tags_sidebar(
                label='',
                text='Filter Tags...',
                value=[],
                maxtags=4,
                key='2')
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                update = st.button('update')
            with col2:
                load = st.button('load')
            with col3:
                load_all = st.button('load all')
            files = st.session_state.get('FILES', None)

            if update:
                update_files()
            if load:
                load_files()
            if load_all:
                load_files(all=True)
            if files:
                displayed_files = [file for file in files if set(filter_tags) <= set(file.get('tags', []))]
                df = pd.DataFrame(
                    displayed_files
                )
                Files = st.data_editor(df)
                # update cache of dataframe
                # st.session_state['FILES'] = list(Files.to_dict('index').values())
                # get loaded files
                st.session_state['LOADED'] = [id for id, loaded in zip(Files.id, Files.Load) if loaded]

            delete_selected = st.button('delete selected', type="primary")
            if delete_selected:
                delete_files()
                update_files()
        st.markdown("---")
        st.markdown("# About")
        st.markdown(
            "📖Doxter RAG allows you to ask questions about your "
            "documents and get accurate answers with instant citations. "
        )
        st.markdown("---")

        faq()


def update_files():
    API = st.session_state.get("BACKEND_API", None)
    loaded = st.session_state.get('LOADED', [])
    if not API:
        return None
    files = API.get_files()
    if files is None or files is False:
        return None
    for file in files:
        file['Load'] = file['id'] in loaded
    st.session_state['FILES'] = files
    st.rerun()


def delete_files():
    # chunked_files = st.session_state.get("CHUNKED_FILES")
    api = st.session_state.get("BACKEND_API")
    # get all files
    chunked_files = []
    files = st.session_state.get('FILES')
    selected_files = st.session_state.get('LOADED', [])
    for file in files:
        if file['id'] not in selected_files:
            continue
        api.delete(file['id'])


def load_files(all=False):
    openai_key = st.session_state.get('OPENAI_API_KEY')
    # get updated chunked files
    with st.spinner("fetching documents"):
        chunked_files = get_new_chunksed_files(all)
        get_summary()

    # save chunks to temp db
    with st.spinner("Indexing document... This may take a while⏳"):
        folder_index = embed_files(
            files=chunked_files,
            embedding="openai",
            vector_store="faiss",
            openai_api_key=openai_key,
            model="text-embedding-3-small"
        )
    st.session_state["FOLDER_INDEX"] = folder_index


def get_new_chunksed_files(all=False):
    # chunked_files = st.session_state.get("CHUNKED_FILES")
    api = st.session_state.get("BACKEND_API")
    # get all files
    chunked_files = []
    files = st.session_state.get('FILES')
    selected_files = st.session_state.get('LOADED', [])

    for file in files:
        if file['status_display'] != "Complete":
            continue
        if not all and file['id'] not in selected_files:
            continue

        file_chunk = api.load(file['id'])
        chunked_files.append(file_chunk)
    # st.session_state["CHUNKED_FILES"] = chunked_files
    return chunked_files


def get_summary(all=False):
    files = st.session_state.get('FILES')
    selected_files = st.session_state.get('LOADED', [])
    file_summary = {}
    for file in files:
        if file['status_display'] != "Complete":
            continue
        if not all and file['id'] not in selected_files:
            continue

        file_summary[file['name']] = file['summary']
    summary = f"The following are the loaded files and their description: \n {file_summary}"
    st.session_state["SUMMARY"] = summary
