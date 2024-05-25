import os 
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from llms import load_embedding
from langchain.tools import tool
from concurrent.futures import ThreadPoolExecutor, as_completed
import chromadb

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
            Chroma.from_documents(all_splits, embedding=load_embedding(), collection_name=date, persist_directory="chroma_db/")
            return f"Content stored for {date}"
        else:
            return f"No content to process for {date}"
    else:
        return f"Collection already exists for {date}"

@tool("embedder-tool", return_direct=True)
def embed_news_for_dates(dates):
    """
    Parallelize embedding news for multiple dates.

    Args:
        dates (list): List of dates as folder names

    Returns:
        list: A list of confirmation messages about the data store
    """
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(embed_news, date): date for date in dates}
        for future in as_completed(futures):
            date = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(f"Error processing {date}: {str(e)}")
    return results