from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
from langchain.tools import tool
from concurrent.futures import ThreadPoolExecutor, as_completed

def setup_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    options.add_argument('--headless') 
    options.add_argument("--enable-javascript")
    options.add_argument('--no-sandbox')  # Add this to prevent issues in certain environments
    options.add_argument('--disable-dev-shm-usage')  
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_page_source(url, driver):
    driver.get(url)
    time.sleep(5)  # Adjust sleep time
    return driver.page_source

def save_to_text(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True) 
    with open(filepath, mode='w', encoding='utf-8') as file:
        if isinstance(data, list):
            data = '\n'.join(map(str, data))  # This converts list items to string and joins them with new lines
        file.write(data)

def extract_urls(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    urls = [link.get('href') for link in links if link.get('href') and "tldr.tech" not in link.get('href')]
    return set(urls)  # Using a set to avoid duplicate URLs


def crawl_page(url, date, driver):
    try:
        html = fetch_page_source(url, driver)
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        filepath = f"crawled_data/{date}/{os.path.basename(url).replace('/', '_')}.txt"
        save_to_text([url, text_content], filepath)
        print(f"Visited {url}, content saved under {filepath}")

        # Extract URLs from the fetched page
        return extract_urls(html), date, driver
    except Exception as e:
        print(f"Error visiting {url}: {str(e)}")
        return [], date, driver

def crawl_link(link, date, driver):
    try:
        link_html = fetch_page_source(link, driver)
        link_text = BeautifulSoup(link_html, 'html.parser').get_text(separator=' ', strip=True)
        link_path = f"crawled_data/{date}/linked_{os.path.basename(link).replace('/', '_')}.txt"
        save_to_text([link, link_text], link_path)
        print(f"Visited {link}, content saved under {link_path}")
    except Exception as e:
        print(f"Error visiting {link}: {str(e)}")

@tool("crawler-tool", return_direct=True)
def crawler_tool(dates: list[str]):
    """
    Crawl the data for the given list of dates.
    """
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for date in dates:
            data_dir = os.path.join('crawled_data', date)
            if os.path.exists(data_dir) and os.listdir(data_dir):
                print(f"Data already available for {date}")
                continue

            driver = setup_driver()
            url = f'https://tldr.tech/ai/{date}'
            futures.append(executor.submit(crawl_page, url, date, driver))

        for future in as_completed(futures):
            try:
                links, date, driver = future.result()
                # Crawl the extracted links in parallel
                link_futures = [executor.submit(crawl_link, link, date, driver) for link in links]
                for link_future in as_completed(link_futures):
                    link_future.result()
                driver.quit()
            except Exception as e:
                print(f"Error in main page crawling: {str(e)}")

    return "Crawled successfully"



#crawler_tool()
#crawler_tool(['2024-05-22', '2024-05-23', '2024-05-24'])