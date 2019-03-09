import random
import logging
import io

import requests
from PIL import ImageFile, Image

module_logger = logging.getLogger('hypercane.algorithms.random')

class RandomNAlgorithm:
    
    def __init__(self, collection_model, memento_count=None):

        self.collection_model = collection_model
        self.urilist = []
        self.executed = False

        if memento_count is None:
            self.memento_count = 20
        else:
            self.memento_count = int(memento_count)

    def pick_randomn(self):

        urimlist = self.collection_model.getMementoURIListFromTimeMaps()

        module_logger.debug("there are {} URI-Ms to choose from".format(
            len(urimlist)
        ))

        maxcount = self.memento_count if len(urimlist) > self.memento_count else len(urimlist)

        random_choices = []

        while(len(random_choices) < maxcount):

            pick = random.choice(urimlist)

            module_logger.debug("chose URI-M {}".format(pick))

            if pick not in random_choices:
                random_choices.append(pick)

        return random_choices

    def execute(self):
        module_logger.info("executing Random 20 Algorithm...")

        self.urilist = self.pick_randomn()

        self.executed = True

    def get_output_data(self, execute_again=False):

        if self.executed is False:
            execute_again = True

        if execute_again:
            self.execute()

        output_data = {
            "id": self.collection_model.collection_id,
            "elements": []
        }

        module_logger.info("returning data for {} URI-Ms".format(len(self.urilist)))

        for uri in self.urilist:
            output_item = {}
            output_item["type"] = "link"
            output_item["value"] = uri
            output_data["elements"].append(output_item)

        return output_data

            
# class Random20AlgorithmWithThumbnailCheck(Random20Algorithm):

#     def __init__(self, collection_model, mementoembed_api_endpoint, session=None):
#         super().__init__(collection_model)

#         self.mementoembed_api_endpoint = mementoembed_api_endpoint

#         if session is None:
#             self.session = requests.Session()

#     def pick_random_20(self):

#         urimlist = self.collection_model.getMementoURIListFromTimeMaps()

#         module_logger.debug("there are {} URI-Ms to choose from".format(
#             len(urimlist)
#         ))

#         maxcount = 20 if len(urimlist) > 20 else len(urimlist)

#         random_choices = []

#         while(len(random_choices) < maxcount):

#             pick = random.choice(urimlist)

#             module_logger.debug("chose URI-M {}".format(pick))

#             if pick not in random_choices:

#                 # acquire MementoEmbed Algorithm

#                 r = requests.get("{}/services/produce/thumbnail/{}".format(
#                     self.mementoembed_api_endpoint,
#                     pick
#                 ))

#                 imgcontent = r.content

#                 p = ImageFile.Parser()
#                 p.feed(imgcontent)
#                 p.close()

#                 h = p.image.histogram().count(0)

#                 random_choices.append(pick)

#         return random_choices
