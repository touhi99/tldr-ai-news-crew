## TLDR-ai-news-crew-agent

AI news going a bit faster to catch up? TLDR (tldr.tech) got it. Even, tldr's daily AI news is also overwhelming? The crew here got you. It's a learning repo with CrewAI to test agent capabilities, some features are just tested for fun and not for potential use.

Inspired from some examples:
- Based upon examples: https://mer.vin/2024/02/crewai-rag-using-tools/
- Streamlit courtesy: https://github.com/AbubakrChan/crewai-streamlit-UI-business-product-launch/

### Installation

```
pip install -r requirements.txt
```

### Usage

```
streamlit run main.py 
```
Give a date: YYYY-MM-DD format (i am lazy atm to validate)

### TODO

1. Crawl specific page by date (crew #1) (DONE, data_crawler)
2. visit all link -> each subject, content and url is one doc for a RAG system (crew #2) (DONE, data_engineer)
3. Summarize the top-k content and provide report (crew #3) (Halfway DONE, data_analyzer)
5. Use TTS (with some news background) (crew #4) (DONE for fun test)
6. audio available
7. Streamlit/API (DONE) (Yes, probably not the best cases to just read news running a streamlit, but somehow does the job now for learning)
8. Get range of news (last 3 days, last weeks)
9. Get personalized/preferred input news