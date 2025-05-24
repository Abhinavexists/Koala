import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def valid_url(url, domain):
    parsed = urlparse(url)
    return parsed.scheme in {'http', 'https'} and parsed.netloc

def crawl(seed_url, max_pages=10):
    visited = set()
    to_visit = [seed_url]
    domain = urlparse(seed_url).netloc
    crawled_data = []

    while to_visit and len(crawled_data) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            crawled_data.append((url, text))
            visited.add(url)
            print(f"[{len(visited)}/{max_pages}] Crawled: {url}")

            for link_tag in soup.find_all('a', href=True):
                link = urljoin(url, link_tag['href'])
                if valid_url(link, domain) and link not in visited:
                    to_visit.append(link)

            time.sleep(1) # Slow down the crawling

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    return crawled_data

def save_data(data, filename='crawled_data.txt'):
    with open(filename, "w", encoding='utf-8') as file:
        for url, text in data:
            file.write(f"URL: {url}\n")
            file.write(f"Content: \n{text}\n")
            file.write("="*100 + "\n")

seed_url = ""
data = crawl(seed_url, max_pages=10)
save_data(data)

print(f"Crawled {len(data)} pages and saved to 'crawled_data.txt'")