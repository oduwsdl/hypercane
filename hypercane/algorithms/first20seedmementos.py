import random
import logging
import io

import requests

module_logger = logging.getLogger('hypercane.algorithms.first20seedmementos')

class First20SeedMementos:

    def __init__(self, collection_model):

        self.collection_model = collection_model
        self.urilist = []
        self.executed = False

    def pick_first20(self):

        urims = []

        sortedseeds = sorted(self.collection_model.seedlist)

        module_logger.debug("sorted seeds: {}".format(sortedseeds))

        i = 0

        while len(urims) < 20:

            try:
                urir = sortedseeds[i]
            except IndexError:
                module_logger.warning("Not enough mementos to fill quota of 20, using what we have...")

            urit = self.collection_model.seed_urits[urir]

            timemap = self.collection_model.get_TimeMap(urit)

            try:
                urim = timemap["mementos"]["first"]["uri"]
                urims.append(urim)
            except KeyError:
                module_logger.warning("Cannot acquire first mement for seed {}, skipping...".format(urir))

            i += 1

        return urims

    def execute(self):
        module_logger.info("executing Algorithm: First 20 Seed Mementos")

        self.urilist = self.pick_first20()

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
