# Doxter RAG - FrontEnd

---

## Project Structure:

* main.py | *main file responsible for streamlit UI components*
* ui.py | *ui components*
* core/ 
  * api.py | *class interface for backend api*
  * debug.py | *debug class*
  * embedding.py | *class for embedding docs in vectorDB*
  * FileParser.py | *Base File class for retaining parsed info and serialization*
  * qa.py | *functions for question and answering tasks*
  * summary.py | *functions for summarization and analysis tasks*
* components/
  * faq.py | *general FAQ in the sidebar*
  * sidebar.py | *streamlit sidebar components for handling app state*
* assets/

## Project Setup:

Install dependencies:
> poetry init

Setup environment variables:
> export OPENAI_API_KEY = Your_API_key

Run Streamlit App:
> streamlit run Main/main.py

## Setup on streamlit
* Save project to a public github repository
* Login to your streamlit account
* Create new Streamlit App
* Connect the app to your github repo
* set run option to Main/main.py
* Setup Advanced Options:
  * set python version to 3.11
  * add environment variables in secrets
    * OPENAI_API_KEY = "Your_API_key"
* Save and run project
