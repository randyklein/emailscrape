import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from email_scraper import scrape_emails
from scrapy import signals
import re
import csv
import os

print ("Starting...")
class AstmEmailSpider(scrapy.Spider):
    name = "astm_email"
    allowed_domains = ["astm.org"]
    start_urls = ["https://www.astm.org/"]

    def __init__(self, *args, **kwargs):
        super(AstmEmailSpider, self).__init__(*args, **kwargs)

        # Ensure the 'export' directory exists
        if not os.path.exists('export'):
            os.makedirs('export')

    def parse(self, response):

        # Check for 'text/html' in the 'Content-Type' header to ensure it's an HTML response
        content_type = response.headers.get("Content-Type", b"").decode("utf-8")
        if "text/html" not in content_type:
            return

        emails = scrape_emails(response.text)

        # If emails found, write them to CSV
        if emails:
            with open("export/emails.csv", "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                for email in emails:
                    writer.writerow([response.url, email])
                    print(f"Found Email {email} at {response.url}")

        # Extract and follow links within the page
        for link in response.css("a::attr(href)").extract():

            # Filter out mailto links
            if "mailto:" in link:
                continue

            if link.startswith("/") or "astm.org" in link:
                yield response.follow(link, self.parse)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AstmEmailSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("Crawling finished!")

if __name__ == "__main__":
    settings = {
        "LOG_LEVEL": "INFO",
        "AUTOTHROTTLE_ENABLED": False,
        "AUTOTHROTTLE_START_DELAY": 5,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0
    }
    process = CrawlerProcess(settings)
    process.crawl(AstmEmailSpider)
    process.start()