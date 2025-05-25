import re
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def valid_url(url, domain):
    parsed = urlparse(url)
    return parsed.scheme in {'http', 'https'} and parsed.netloc

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

def crawl(seed_url, max_pages=10):
    visited = set()
    to_visit = [seed_url]
    domain = urlparse(seed_url).netloc
    prepared_data = []

    while to_visit and len(prepared_data) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            cleaned_text = clean_text(text)

            if cleaned_text and len(cleaned_text.split()) > 20:
                prepared_data.append((url, cleaned_text))
                print(f"[{len(prepared_data)}/{max_pages}] Crawled: {url}")

            visited.add(url)

            for link_tag in soup.find_all('a', href=True):
                link = urljoin(url, link_tag['href'])
                if valid_url(link, domain) and link not in visited:
                    to_visit.append(link)

            time.sleep(1) # Slow down the crawling

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    return prepared_data

# def save_data(data, filename='prepared_data.txt'):
#     with open(filename, "w", encoding='utf-8') as file:
#         for url, text in data:
#             file.write(f"URL: {url}\n")
#             file.write(f"Content: \n{text}\n")
#             file.write("="*100 + "\n")

def save_data(data, filename='prepared_data.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

seed_url = "https://realpython.com/"
data = crawl(seed_url, max_pages=10)
save_data(data)

print(f"Crawled {len(data)} pages and saved to 'prepared_data.txt'")