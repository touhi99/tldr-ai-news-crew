import os
from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from llms import load_embedding

@tool("qa-tool", return_direct=False)
def get_qa(date, query) -> str:
    """Search Chroma DB answer similar to the query for the mentioned date. Once similar chunk is found, formulate the answer and return the answer."""
    vectorstore = Chroma(persist_directory="chroma_db/", collection_name = date, embedding_function=load_embedding())
    print(query)
    retriever = vectorstore.similarity_search(query, k=5)
    page_content = ''
    for r in retriever:
        page_content += r.page_content 
    return page_content