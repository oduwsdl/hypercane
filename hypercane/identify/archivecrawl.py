import logging
import scrapy

from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from requests.utils import parse_header_links

module_logger = logging.getLogger('hypercane.identify.archivecrawl')

class WaybackSpiderInitializationException(Exception):
    pass

class StorageObject:
    # TODO: make this work with an on-disk database

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

    custom_settings = {
        'DEPTH_LIMIT': 1 # 0 means no depth limit
    }

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

            module_logger.warning("Failed to get Link header from {}".format(response.url))

        if retrieved_link_headers is True:
            # Mementos should have Link headers and we only crawl Mementos
            module_logger.info("extracting URI-R and URI-T from {}".format(response.url))
            urit, urir = return_urit_and_urir(link_headers.decode())

            self.link_storage.add( (urit, urir) )

            for sel in response.xpath('//a'):
    
                href = sel.xpath('@href').extract()
                href = extract_href_string(href)
    
                if href is not None:
                    if href != "":
                        yield response.follow(href, self.parse)

def crawl_mementos(link_storage, urims, crawl_depth):
    process = CrawlerProcess()
        
    module_logger.info("custom_settings: {}".format(WaybackSpider.custom_settings))

    WaybackSpider.custom_settings = {
        'DEPTH_LIMIT': int(crawl_depth)
    }

    allowed_domains = []

    for uri in urims:
        o = urlparse(uri)
        
        if ':' in o.netloc:
            host, port = o.netloc.split(':')
        else:
            host = o.netloc

        if o.netloc not in allowed_domains:
            allowed_domains.append(o.netloc)

    module_logger.info("Starting crawl of Mementos")
    process.crawl(
        WaybackSpider, start_urls=urims, link_storage=link_storage, allowed_domains=allowed_domains
        )
    process.start()
    module_logger.info("Crawl complete")
