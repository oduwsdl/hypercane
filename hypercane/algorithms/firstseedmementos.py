import random
import logging
import io

import requests
from PIL import ImageFile, Image
from memstock.timemapstock import TimeMapStockFailureOnFind

module_logger = logging.getLogger('hypercane.algorithms.first20seedmementos')

class FirstNSeedMementos:

    def __init__(self, collection_model, memento_count=None):

        self.collection_model = collection_model
        self.urilist = []
        self.executed = False

        if memento_count is None:
            self.memento_count = 20
        # else:
        #     self.memento_count = int(memento_count)

    def pick_firstn(self):

        urims = []

        sortedseeds = sorted(self.collection_model.seedlist)

        module_logger.debug("sorted seeds: {}".format(sortedseeds))

        i = 0

        while len(urims) < self.memento_count:

            try:
                urir = sortedseeds[i]
            except IndexError:
                module_logger.warning("Not enough mementos to fill quota of 20, using what we have...")

            urit = self.collection_model.seed_urits[urir]

            try:

                timemap = self.collection_model.get_TimeMap(urit)

            except TimeMapStockFailureOnFind:
                module_logger.warn("failed to acquire TimeMap for seed {}, skipping...".format(urir))
                i += 1
                continue # on to the next one

            try:
                urim = timemap["mementos"]["first"]["uri"]
                urims.append(urim)
            except KeyError:
                module_logger.warning("Cannot acquire first mement for seed {}, skipping...".format(urir))

            i += 1

        return urims

    def execute(self):
        module_logger.info("executing Algorithm: First 20 Seed Mementos")

        self.urilist = self.pick_firstn()

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

class FirstNSeedMementosWithThumbnailCheck(FirstNSeedMementos):

    def __init__(self, collection_model, mementoembed_api_endpoint,
        session=None, memento_count=None):
        super().__init__(collection_model, memento_count=memento_count)

        self.mementoembed_api_endpoint = mementoembed_api_endpoint

        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

    def pick_firstn(self):

        urims = []

        sortedseeds = sorted(self.collection_model.seedlist)

        module_logger.debug("sorted seeds: {}".format(sortedseeds))

        i = 0

        while len(urims) < self.memento_count:

            try:
                urir = sortedseeds[i]
            except IndexError:
                module_logger.warning("Not enough mementos to fill quota of 20, using what we have...")

            urit = self.collection_model.seed_urits[urir]

            module_logger.debug("acquiring TimeMap at {}".format(urit))

            try:

                timemap = self.collection_model.get_TimeMap(urit)

            except TimeMapStockFailureOnFind:
                module_logger.warn("failed to acquire TimeMap for seed {}, skipping...".format(urir))
                i += 1
                continue # on to the next one

            try:
                urim = timemap["mementos"]["first"]["uri"]

                module_logger.info("examining thumbnail of URI-M {}...".format(urim))

                thumbnail_uri = "{}/services/product/thumbnail/{}".format(
                    self.mementoembed_api_endpoint,
                    urim
                )

                module_logger.info("issuing thumbnail request to {}".format(thumbnail_uri))

                r = self.session.get(thumbnail_uri)

                if r.status_code != 200:
                    module_logger.warn(
                        "MementoEmbed thumbnail service failed to produce a thumbnail for {}, skipping...".format(
                        urim
                    ))
                else:

                    imgcontent = r.content

                    try:
                        p = ImageFile.Parser()
                        p.feed(imgcontent)
                        p.close()

                        h = p.image.histogram().count(0)
                        module_logger.info("h value of {} in histogram for thumbnail of {}".format(h, urim))

                        if h > 525:
                            module_logger.warn("image histogram indicates too much white, likely a bad Memento, h={} for URI-M {}, skipping...".format(h, urim))
                            i += 1
                            continue # on to the next one

                        urims.append(urim)
                    except IOError:
                        module_logger.warn("cannot parse the image for thumbnail of {}, skipping...".format(urim))

            except KeyError:
                module_logger.warning("Cannot acquire first memento for seed {}, skipping...".format(urir))

            i += 1

        return urims
