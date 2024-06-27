# Doxter RAG - FrontEnd

---

## Project Structure:

* main.py 
* ui.py
* core/
  * api.py
  * chunking.py
  * debug.py
  * embedding.py
  * FileParser.py
  * prompts.py
  * qa.py
  * summary.py
* components/
  * faq.py
  * sidebar.py
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
