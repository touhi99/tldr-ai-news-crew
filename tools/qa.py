import os
from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from llms import load_embedding

@tool("qa-tool", return_direct=False)
def get_qa(dates, query) -> str:
    """Search Chroma DB for top news information based on a query across multiple dates.
    
    Args:
        dates (list): List of dates as folder names
        query (str): The search query

    Returns:
        str: Aggregated news content from the top results
    """
    def retrieve_news(query, dates):
        all_retrieved = []
        for date in dates:
            vectorstore = Chroma(persist_directory="chroma_db/", collection_name=date, embedding_function=load_embedding())
            print(f"Querying for date: {date}")
            retriever = vectorstore.similarity_search(query, k=5)
            for r in retriever:
                all_retrieved.append(r.page_content)
        return all_retrieved

    # Perform the retrieval once for all dates
    all_retrieved_content = retrieve_news(query, dates)
    
    # Aggregate all results into a single string
    aggregated_content = '\n'.join(all_retrieved_content)
    return aggregated_content