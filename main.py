import scrapy
from scrapy.crawler import CrawlerProcess
from email_scraper import scrape_emails
from scrapy import signals
import csv
import os
from settings import *

print ("Starting...")
class EmailSpider(scrapy.Spider):
    name = "email_search"
    allowed_domains = [DOMAIN]
    start_urls = [START_URL]

    def __init__(self, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)

        # Ensure the 'export' directory exists
        if not os.path.exists('export'):
            os.makedirs('export')

    def parse(self, response):

        # Handle large files by aborting processing
        if response.status == 400 and 'download size' in response.body.decode('utf-8'):
            return

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
                    #print(f"Found Email {email} at {response.url}")

        # Extract and follow links within the page
        for link in response.css("a::attr(href)").extract():

            # Filter out mailto links
            if "mailto:" in link:
                continue

            if link.startswith("/") or DOMAIN in link:
                yield response.follow(link, self.parse)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(EmailSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("Crawling finished!")

if __name__ == "__main__":
    process_settings = {
        'LOG_LEVEL': LOG_LEVEL,
        'AUTOTHROTTLE_ENABLED': AUTOTHROTTLE_ENABLED,
        'AUTOTHROTTLE_START_DELAY': AUTOTHROTTLE_START_DELAY,
        'AUTOTHROTTLE_MAX_DELAY': AUTOTHROTTLE_MAX_DELAY,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': AUTOTHROTTLE_TARGET_CONCURRENCY,
        'DOWNLOAD_MAXSIZE': DOWNLOAD_MAXSIZE,
        'DOWNLOAD_WARNSIZE': DOWNLOAD_WARNSIZE,
        'DOMAIN': DOMAIN,
        'START_URL': START_URL
    }
    process = CrawlerProcess(process_settings)
    process.crawl(EmailSpider)
    process.start()