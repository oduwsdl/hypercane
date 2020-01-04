import logging
import scrapy

from scrapy.crawler import CrawlerProcess

module_logger = logging.getLogger('hypercane.identify.archivecrawl')

import scrapy
import sys
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin
import logging

from requests.utils import parse_header_links

module_logger = logging.getLogger()

class WaybackSpiderInitializationException(Exception):
    pass

class StorageObject:

    def __init__(self):

        self.storage = []


    def add(self, item):

        if item not in self.storage:
            self.storage.append(item)

def extract_href_string(href):

    if type(href) == list:
  
        if len(href) > 0:
  
            href = href[0]
  
            if type(href) == list:
  
                if len(href) > 0:
  
                     href = href[0]

    return href

def return_urit_and_urir(link_headers):

    header_links = parse_header_links(link_headers) 

    for item in header_links:

        if item['rel'] == 'timemap':
            urit = item['url']

        if 'original' in item['rel']:
            # handles original latest-version and similar
            urir = item['url']

    return (urit, urir)

class WaybackSpider(scrapy.Spider):
  
    def __init__(self, *args, **kwargs):

        try:
            self.start_urls = kwargs['start_urls']
            self.allowed_domains = kwargs['allowed_domains']
            self.link_storage = kwargs['link_storage']
        except KeyError as e:
            msg = "Failed to supply argument to WaybackSpider, details: {}".format(e)
            module_logger.exception(msg)
            raise WaybackSpiderInitializationException(msg)

    def parse(self, response):

        retrieved_link_headers = False

        try:

            link_headers = response.headers["link"]
            retrieved_link_headers = True

        except KeyError:

            print("Failed to get Link header from {}".format(response.url))


        if retrieved_link_headers is True:
            # Mementos should have Link headers and we only crawl Mementos

            urit, urir = return_urit_and_urir(link_headers.decode())

            self.link_storage.add( (urit, urir) )

            for sel in response.xpath('//a'):
    
                href = sel.xpath('@href').extract()
                href = extract_href_string(href)
    
                if href is not None:
                    if href != "":
                        yield response.follow(href, self.parse)

process = CrawlerProcess()

starting_url = sys.argv[1]
depth_limit = sys.argv[2]

WaybackSpider.custom_settings = {
    'DEPTH_LIMIT': int(depth_limit)
}

link_storage = StorageObject()

print("starting crawl with {}".format(starting_url))

print("link storage has {} items to start".format(len(link_storage.storage)))

#process.crawl(ShawnSpider, start_urls=[starting_url], link_storage=link_storage)
process.crawl(WaybackSpider, start_urls=[starting_url], link_storage=link_storage, allowed_domains=['wayback.archive-it.org'])

process.start()

print("link storage has {} items now".format(len(link_storage.storage)))

with open("output.txt", 'w') as f:

    for entry in link_storage.storage:
        f.write("{}\n".format(entry))

print("done crawling")
