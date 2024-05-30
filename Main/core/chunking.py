from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from Main.core.FileParser import File


def chunk_file(
        file: File, chunk_size: int, chunk_overlap: int = 0, model_name="gpt-3.5-turbo"
) -> File:
    """Chunks each document in a file into smaller documents
    according to the specified chunk size and overlap
    where the size is determined by the number of token for the specified model.
    """

    # split each document into chunks
    chunked_docs = []
    for doc in file.docs:
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name=model_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        # check size limit of content
        content = doc.page_content
        chunks = []
        # chunks content
        lines = content.split('\n')
        chunk = ""
        for line in lines:
            chunk = "\n".join([chunk, line])
            if len(chunk) > 50000: # max limit of characters getting chunked
                chunks.extend(text_splitter.split_text(chunk))  # splitter chunking by token
                chunk = ""
        if len(chunk) > 1:
            chunks.extend(text_splitter.split_text(chunk))

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page": doc.metadata.get("page", 1),
                    "chunk": i + 1,
                    "source": f"{doc.metadata.get('page', 1)}-{i + 1}",
                },
            )
            chunked_docs.append(doc)

    chunked_file = file.copy()
    chunked_file.docs = chunked_docs
    return chunked_file
