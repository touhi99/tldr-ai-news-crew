import os 
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from llms import load_embedding
from langchain.tools import tool
import chromadb

@tool("embedder-tool", return_direct=False)
def embed_news(date):
    """Given date, find the data of that date news and embed them to vector store

    Args:
        date (str): the date as the folder name

    Returns:
        str: A confirmation about the data store
    """
    base_path = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
    path = os.path.join(base_path, 'crawled_data', date)
    client = chromadb.PersistentClient(path="chroma_db/")
    if date not in [c.name for c in client.list_collections()]:
        all_splits = []
        for filename in os.listdir(path):
            if filename.endswith(".txt"): 
                file_path = os.path.join(path, filename)
                loader = TextLoader(file_path)
                docs = loader.load()

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                splits = text_splitter.split_documents(docs)
                all_splits.extend(splits)  # Accumulate splits from all articles

        if all_splits:
            Chroma.from_documents(all_splits, embedding=load_embedding(), collection_name = date, persist_directory="chroma_db/")
            return "Content stored"
        else:
            return "No content to process"
    else:
        return "Collection already exists"
    
@tool("retriever-tool", return_direct=False)
def get_news(date, query) -> str:
    """Search Chroma DB for top news information based on a query. If a query returns null try similarly alternating query until it's not empty.
    Once top news has been found, summarize it and return as a reporter describing it."""
    vectorstore = Chroma(persist_directory="chroma_db/", collection_name = date, embedding_function=load_embedding())
    retriever = vectorstore.similarity_search("Summarize top 5 latest AI news", k=10)
    page_content = ''
    for r in retriever:
        page_content += r.page_content 
    return page_content