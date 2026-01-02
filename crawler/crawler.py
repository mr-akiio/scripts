import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import json
import time

class WebCrawler:
    def __init__(self, start_url, max_depth=2, delay=1):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.visited = set()
        self.max_depth = max_depth
        self.delay = delay
        self.output_file = start_url
        self.robot_parser = RobotFileParser()
        self.setup_robots()

    def setup_robots(self):
        
        robots_url = urljoin(self.start_url, '/robots.txt')
        self.robot_parser.set_url(robots_url)
        try:
            
            self.robot_parser.read()
            print(f"Loaded robots.txt from {robots_url}")
            
        except Exception as e:
            print(f"Could not read robots.txt: {e}")

    def can_fetch(self, url):
        return self.robot_parser.can_fetch("*", url)

    def fetch_links(self, url):
        try:
            time.sleep(self.delay)
            
            response = requests.get(url, timeout=10, headers={'User-Agent': 'JustASimpleCrawler/1.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            links = set()
            
            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href'])
                parsed = urlparse(link)
                if parsed.netloc == self.domain and parsed.scheme in ("http", "https"):
                    links.add(link.split('#')[0])

            return links
        
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return set()

    def crawl(self, url=None, depth=0):
        if url is None:
            url = self.start_url
            
        if depth > self.max_depth:
            return
        
        if url in self.visited:
            return
        
        if not self.can_fetch(url):
            print(f"Disallowed by robots.txt: {url}")
            return

        print(f"Visiting: {url}")
        
        self.visited.add(url)
        links = self.fetch_links(url)

        for link in links:
            self.crawl(link, depth + 1)

    def save_to_json(self):
        
        data = {
            "start_url": self.start_url,
            "domain": self.domain,
            "total_pages": len(self.visited),
            "urls": sorted(self.visited),
        }
        
        try:
            
            with open(f"crawler_out/{self.domain}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"\nCrawl results saved to crawler_out/{self.domain}.json")
            
        except Exception as e:
            print(f"Failed to save JSON: {e}")

        
if __name__ == "__main__":
    start = input("Enter the start: ").strip()
    crawler = WebCrawler(start, max_depth=2, delay=1)
    crawler.crawl()
    print("\nCrawl complete")
    crawler.save_to_json()


