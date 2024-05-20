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

![Image](./fig/screenshot.png)

### TODO

1. Get range of news (last 3 days, last weeks)
2. Get personalized/preferred input news
3. Add validation for crawling error