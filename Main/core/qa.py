import os
from typing import Any, List

from openai import OpenAI

from langchain.docstore.document import Document
from Main.core.embedding import FolderIndex
from pydantic.v1 import BaseModel


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

class AnswerWithSources(BaseModel):
    answer: str
    sources: List[Document]


def get_relevant_docs(query: str, search_query: str, folder_index: FolderIndex) -> AnswerWithSources:
    """
    get the query to be answered, a search query used for searching the vector DB, and the Vector DB.
    Get relevant docs from the VectorDB using the search query, and answer the query using these results.
    :param query: base query to be answered
    :param search_query: key words to be used to search the vector DB
    :param folder_index: VectorDB to be used for searching and reference
    :return: Object Class containing answer and source documents list
    """

    relevant_docs = folder_index.index.similarity_search(search_query)

    messages = [
        {"role": "system",
         "content": "Create a final answer to the given questions using the provided document excerpts(in no particular order) as references. \n"
                    f"The context is the following: {relevant_docs}"
         },
        {"role": "user", "content": f"question: {query}"}
    ]
    # f"some key topics to cover are {topics.keys()} described as follows {topics}."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0,
    )
    answer = ""
    for choice in response.choices:
        answer += choice.message.content

    return AnswerWithSources(answer=answer, sources=relevant_docs)


def get_sources(answer: str, folder_index: FolderIndex) -> List[Document]:
    """Retrieves the docs that were used to answer the question the generated answer."""

    source_keys = [s for s in answer.split("SOURCES: ")[-1].split(", ")]

    source_docs = []
    for file in folder_index.files:
        for doc in file.docs:
            if doc.metadata["source"] in source_keys:
                source_docs.append(doc)

    return source_docs


def get_relevant_keywords(query, summary):
    """
    gets a query about a topic, a summary of said topic, and returns keywords that would help search for answers for that query.
    :param query: Question about a certain topic
    :param summary: summary of the files stored in the vector DB
    :return: Keywords to search for in the vector DB
    """
    messages = [
        {"role": "system",
         "content": "You are an answer generator for a search engine, you will be given a question and you'll return a list of relevant keywords to look for. \n"
                    "ex: Q: 'what is the net operational profit in 2022?', A: 'Buisness data, gross profit, operating expenses, net sales, revenue, cost of sales, etc.' "
                    f"Context: {summary}"
         },
        {"role": "user", "content": f"question: {query}"}
    ]
    # f"some key topics to cover are {topics.keys()} described as follows {topics}."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )
    answer = ""
    for choice in response.choices:
        answer += choice.message.content
    return answer
