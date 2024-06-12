# This script is a modified version of main.py
#this script searches for all instances of text in the search_text list across the listed domain.
#to run, run this script directly instead of main

import scrapy
from scrapy.crawler import CrawlerProcess
from email_scraper import scrape_emails
from scrapy import signals
import csv
import os
from settings import *
from bs4 import BeautifulSoup

# List of text strings to search for
search_texts = ["for888565.com", "googie-anaiytics.com", "astm.org/get-involved/membership.html"]

# Log file to store URLs with matches
log_file = "matches.log"

print ("Starting...")
class EmailSpider(scrapy.Spider):
    name = "text_search"
    allowed_domains = [DOMAIN]
    start_urls = [START_URL]

    def __init__(self, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)

        # Ensure the 'export' directory exists
        if not os.path.exists('export'):
            os.makedirs('export')

    def parse(self, response):

        # Check for 'text/html' in the 'Content-Type' header to ensure it's an HTML response
        content_type = response.headers.get("Content-Type", b"").decode("utf-8")
        if "text/html" not in content_type:
            return

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
        'DOMAIN': DOMAIN,
        'START_URL': START_URL
    }
    process = CrawlerProcess(process_settings)
    process.crawl(EmailSpider)
    process.start()