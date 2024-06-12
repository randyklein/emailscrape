import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
import os
from bs4 import BeautifulSoup
import fitz  # PyMuPDF for PDF

# List of text strings to search for
search_texts = ["for888565.com", "googie-anaiytics.com", "students who have demonstrated high levels of interest or involvement with ASTM Standards"]

# Log file to store URLs with matches
log_file = "export/matches.log"

print("Starting...")

class EmailSpider(scrapy.Spider):
    name = "text_search"
    allowed_domains = ["astm.org"]
    start_urls = ["https://www.astm.org/"]

    def __init__(self, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)

        # Ensure the 'export' directory exists
        if not os.path.exists('export'):
            os.makedirs('export')

    def parse(self, response):
        # Check for 'text/html' in the 'Content-Type' header to ensure it's an HTML response
        content_type = response.headers.get("Content-Type", b"").decode("utf-8")
        if "text/html" in content_type:
            page_content = response.text
            soup = BeautifulSoup(page_content, 'html.parser')
            text_found = False

            # Search for the specified texts in the page content
            for text in search_texts:
                if text in page_content:
                    with open(log_file, 'a') as log:
                        log.write(f"Found '{text}' on {response.url}\n")
                    text_found = True

            # Print the URL of each page crawled
            print(f"Crawled: {response.url}")

            # Extract and follow links within the page
            for link in response.css("a::attr(href)").extract():
                # Filter out mailto links
                if "mailto:" in link:
                    continue

                if link.startswith("/") or "astm.org" in link:
                    yield response.follow(link, self.parse)
        elif "application/pdf" in content_type:
            self.parse_pdf(response)
        elif "application/msword" in content_type or "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type:
            self.parse_doc(response)

    def parse_pdf(self, response):
        try:
            doc = fitz.open(stream=response.body, filetype='pdf')
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                for search_text in search_texts:
                    if search_text in text:
                        with open(log_file, 'a') as log:
                            log.write(f"Found '{search_text}' in PDF on {response.url}\n")
                        print(f"Found '{search_text}' in PDF on {response.url}")
                        break
        except Exception as e:
            print(f"Failed to parse PDF {response.url}: {e}")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(EmailSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("Crawling finished!")

if __name__ == "__main__":
    process_settings = {
        'LOG_LEVEL': 'INFO',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    }
    process = CrawlerProcess(process_settings)
    process.crawl(EmailSpider)
    process.start()
