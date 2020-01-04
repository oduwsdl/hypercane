import logging
import scrapy

from scrapy.crawler import CrawlerProcess

module_logger = logging.getLogger('hypercane.identify.archivecrawl')

def extract_href_string(href):

    if type(href) == list:
    
        if len(href) > 0:
    
            href = href[0]
    
            if type(href) == list:
    
                if len(href) > 0:
    
                     href = href[0]

    return href

class WaybackSpiderInitializationException(Exception):
    pass

class WaybackSpider(scrapy.Spider):
    
    def __init__(self, *args, **kwargs):

        try:
            self.start_urls = kwargs['start_urls']
            self.allowed_domains = kwargs['allowed_domains']
            self.custom_settings = {
                'DEPTH_LIMIT': kwargs['depth_limit']
            }
            self.link_storage = kwargs['link_storage']
        except KeyError as e:
            msg = "Failed to supply argument to WaybackSpider, details: {}".format(e)
            module_logger.exception(msg)
            raise WaybackSpiderInitializationException(msg)
`
    def parse(self, response):

        for sel in response.xpath('//a'):

            href = sel.xpath('@href').extract()

            href = extract_href_string(href)

            if href is not None:
                if href != "":
                    self.link_storage.add(href)

        for sel in response.xpath('//a'):

            href = sel.xpath('@href').extract()

            href = extract_href_string(href)

            if href is not None:
                if href != "":
                    yield response.follow(href, self.parse)

# import scrapy
# import sys
# from scrapy.crawler import CrawlerProcess
# from urllib.parse import urljoin
# import logging

# module_logger = logging.getLogger()

# class WaybackSpiderInitializationException(Exception):
#     pass

# #class IkeaItem(scrapy.Item):
# #
# #    name = scrapy.Field()
# #    link = scrapy.Field()


# #class IkeaSpider(scrapy.Spider):
# #    name = 'ikea'
# #
# #    allowed_domains = ['www.ikea.com']
# #
# #    start_urls = ['http://www.ikea.com/']
# #
# #    def parse(self, response):
# #        for sel in response.xpath('//tr/td/a'):
# ##            item = IkeaItem()
# ##            item['name'] = sel.xpath('text()').extract()
# ##            item['link'] = sel.xpath('@href').extract()
# #
# #            yield sel.xpath('@href').extract()

# class StorageObject:

#     def __init__(self):

#         self.storage = []


#     def add(self, item):

#         if item not in self.storage:
#             self.storage.append(item)

# def extract_href_string(href):

#     if type(href) == list:
    
#         if len(href) > 0:
    
#             href = href[0]
    
#             if type(href) == list:
    
#                 if len(href) > 0:
    
#                      href = href[0]

#     return href

# class ShawnSpider(scrapy.Spider):

#     name = 'shawnspider'

#     allowed_domains = ['wayback.archive-it.org']

#     custom_settings = {
#         'DEPTH_LIMIT': 1
#     }

#     def __init__(self, *args, **kwargs):

#         super(ShawnSpider, self).__init__(*args, **kwargs)

#         self.start_urls = kwargs['start_urls']
#         self.link_storage = kwargs.get('link_storage')

#         if not self.start_urls:
#             raise Exception("Need start_urls for crawler!!!")

#         if not self.link_storage:
#             raise Exception("Need link storage object for crawler!!!")

#     def parse(self, response):

#         for sel in response.xpath('//a'):

#             href = sel.xpath('@href').extract()

#             href = extract_href_string(href)

#             if href is not None:
#                 if href != "":
#                     self.link_storage.add(urljoin(response.url, href))
#                     yield response.follow(href, self.parse)    

# class WaybackSpider(scrapy.Spider):
    
#     def __init__(self, *args, **kwargs):

#         try:
#             self.start_urls = kwargs['start_urls']
#             self.allowed_domains = kwargs['allowed_domains']
# #            self.custom_settings = {
# #                'DEPTH_LIMIT': kwargs['depth_limit']
# #            }
#             self.link_storage = kwargs['link_storage']
#         except KeyError as e:
#             msg = "Failed to supply argument to WaybackSpider, details: {}".format(e)
#             module_logger.exception(msg)
#             raise WaybackSpiderInitializationException(msg)

#     def parse(self, response):

#         for sel in response.xpath('//a'):

#             href = sel.xpath('@href').extract()

#             href = extract_href_string(href)

#             if href is not None:
#                 if href != "":
#                     self.link_storage.add(href)

#         for sel in response.xpath('//a'):

#             href = sel.xpath('@href').extract()

#             href = extract_href_string(href)

#             if href is not None:
#                 if href != "":
#                     yield response.follow(href, self.parse)

# process = CrawlerProcess()

# starting_url = sys.argv[1]

# WaybackSpider.custom_settings = {
#     'DEPTH_LIMIT': 1
# }

# link_storage = StorageObject()

# print("starting crawl with {}".format(starting_url))

# print("link storage has {} items to start".format(len(link_storage.storage)))

# #process.crawl(ShawnSpider, start_urls=[starting_url], link_storage=link_storage)
# process.crawl(WaybackSpider, start_urls=[starting_url], link_storage=link_storage, allowed_domains=['wayback.archive-it.org'])

# process.start()

# print("link storage has {} items now".format(len(link_storage.storage)))

# with open("output.txt", 'w') as f:

#     for entry in link_storage.storage:
#         f.write("{}\n".format(entry))

# print("done crawling")
