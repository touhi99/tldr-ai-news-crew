import os 
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from llms import load_embedding
from langchain.tools import tool

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
    for filename in os.listdir(path):
        all_splits = []
        if filename.endswith(".txt"): 
            file_path = os.path.join(path, filename)
            with open(file_path, 'r') as file: 
                print(file)
                loader = TextLoader(file)
                docs = loader.load()

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                splits = text_splitter.split_documents(docs)
                all_splits.extend(splits)  # Accumulate splits from all articles

    if all_splits:
        Chroma.from_documents(all_splits, embedding=load_embedding(), persist_directory="../chroma_db/"+ date)
        #retriever = vectorstore.similarity_search(query)
        return "Content stored"
    else:
        return "No content available for processing."
    
@tool("retriever-tool", return_direct=True)
def get_news(date, query) -> str:
    """Search Chroma DB for relevant news information based on a query."""
    vectorstore = Chroma(persist_directory="../chroma_db/"+date, embedding_function=load_embedding())
    retriever = vectorstore.similarity_search(query)
    return retriever