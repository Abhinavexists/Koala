import re
import time
import json
import requests
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Tuple, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Crawler:
    def __init__(self, user_agent: str = "KoalaBot/1.0"):
        self.visited: Set[str] = set()
        self.to_visit: List[Tuple[str, int]] = []
        self.data = []
        self.seen_content_hashes: Set[str] = set()
        self.headers = {"User-Agent": user_agent}
        
    def is_allowed(self, url: str, robots_rules: Dict[str, List[str]]) -> bool:
        domain = urlparse(url).netloc
        path = urlparse(url).path
        
        if domain not in robots_rules:
            return True
            
        return True
        
    def get_robots_txt(self, url: str) -> List[str]:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        disallowed = []
        
        try:
            response = requests.get(robots_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                lines = response.text.split('\n')
                for line in lines:
                    if line.lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path and path != '/':
                            disallowed.append(path)
        except Exception as e:
            logging.warning(f"Error fetching robots.txt for {parsed.netloc}: {e}")
            
        return disallowed
        
    def valid_url(self, url: str, domain: str) -> bool:
        parsed = urlparse(url)
        
        if not (parsed.scheme in {'http', 'https'} and parsed.netloc):
            return False
            
        if domain and domain not in parsed.netloc:
            return False
            
        skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml', '.zip'}
        if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
            return False
            
        skip_patterns = ['#', 'javascript:', 'mailto:', 'tel:']
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
            
        return True
                
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        text = text.strip()
        return text
        
    def extract_main_content(self, soup: BeautifulSoup) -> str:
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
            
        main_content = ""
        
        content_selectors = [
            'main', 'article', '.content', '#content', '.post', '.entry',
            '.article-body', '.post-content', '.entry-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem.get_text(separator='\n', strip=True)
                break
                
        if not main_content:
            for elem in soup.find_all(['nav', 'sidebar', 'menu', 'footer', 'header']):
                elem.decompose()
            main_content = soup.get_text(separator='\n', strip=True)
            
        return self.clean_text(main_content)
        
    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        metadata = {
            "url": url,
            "title": "",
            "description": "",
            "keywords": [],
            "last_modified": None
        }
        
        title_tag = soup.find('title')
        if title_tag:
            metadata["title"] = self.clean_text(title_tag.get_text())
            
        meta_desc = soup.find('meta', attrs={"name": "description"}) or \
                   soup.find('meta', attrs={"property": "og:description"})
        if meta_desc and meta_desc.get('content'):
            metadata["description"] = self.clean_text(meta_desc['content'])
            
        meta_keywords = soup.find('meta', attrs={"name": "keywords"})
        if meta_keywords and meta_keywords.get('content'):
            metadata["keywords"] = [k.strip() for k in meta_keywords['content'].split(',')]
            
        return metadata
    
    def crawl_page(self, url: str, robots_rules: Dict[str, List[str]]) -> Tuple[Optional[Dict], List[str]]:
        if not self.is_allowed(url, robots_rules):
            logging.info(f"Robots.txt disallows crawling: {url}")
            return None, []
        
        new_urls = []
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logging.info(f"Skipping {url}: not HTML content ({content_type})")
                return None, []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content = self.extract_main_content(soup)
            
            word_count = len(content.split())
            if not content or word_count < 10:  # Reduced from 20 to 10
                logging.info(f"Skipping {url}: content too short ({word_count} words)")
                return None, []
                
            content_sample = content[:500] if len(content) > 500 else content
            content_hash = hashlib.md5(content_sample.encode()).hexdigest()
            
            if content_hash in self.seen_content_hashes:
                logging.info(f"Skipping {url}: similar content detected")
                return None, []
                
            self.seen_content_hashes.add(content_hash)
            
            metadata = self.extract_metadata(soup, url)
            metadata["content"] = content
            metadata["word_count"] = word_count
            
            domain = urlparse(url).netloc
            for link_tag in soup.find_all('a', href=True):
                href = link_tag.get('href', '').strip()
                if not href:
                    continue
                    
                full_url = urljoin(url, href)
                
                parsed = urlparse(full_url)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"
                
                if (self.valid_url(clean_url, domain) and 
                    clean_url not in self.visited and 
                    clean_url != url):
                    new_urls.append(clean_url)
                    
            new_urls = list(set(new_urls))
            
            return metadata, new_urls
            
        except requests.RequestException as e:
            logging.error(f"Request error crawling {url}: {e}")
            return None, []
        except Exception as e:
            logging.error(f"Error crawling {url}: {e}")
            return None, []
            
    def crawl(self, seed_url: str, max_pages: int = 50, max_depth: int = 2) -> List[Dict]:
        self.to_visit = [(seed_url, 0)]
        domain = urlparse(seed_url).netloc
        
        robots_rules = {domain: self.get_robots_txt(seed_url)}
        logging.info(f"Starting crawl from {seed_url}")
        logging.info(f"Max pages: {max_pages}, Max depth: {max_depth}")
        
        pages_crawled = 0
        
        while self.to_visit and pages_crawled < max_pages:
            url, depth = self.to_visit.pop(0)
            
            if url in self.visited or depth > max_depth:
                continue
            
            self.visited.add(url)
            
            logging.info(f"Crawling [{pages_crawled + 1}/{max_pages}] (depth {depth}): {url}")
            
            page_data, new_urls = self.crawl_page(url, robots_rules)
            
            if page_data:
                self.data.append(page_data)
                pages_crawled += 1
                logging.info(f"✓ Successfully crawled: {url} ({page_data['word_count']} words)")
                
                if depth < max_depth:
                    for new_url in new_urls[:10]:
                        if new_url not in self.visited:
                            self.to_visit.append((new_url, depth + 1))
            else:
                logging.info(f"✗ No data extracted from {url}")
            
            time.sleep(0.5)
                
        logging.info(f"Crawling completed. Successfully crawled {len(self.data)} pages")
        return self.data
        
    def save_data(self, filename: str = 'prepared_data.json'):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)
        logging.info(f"Data saved to {filename}")

if __name__ == "__main__":
    pass