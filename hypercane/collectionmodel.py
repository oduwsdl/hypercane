import logging

from requests_futures.sessions import FuturesSession

from memstock.memstock import MemStock, MemStockFailureOnFind
from memstock.memwetstock import MemWETStock
from memstock.timemapstock import TimeMapStock

from otmt.collectionmodel import CollectionModelMementoErrorException
from otmt.collectionmodel import CollectionModelBoilerPlateRemovalFailureException

module_logger = logging.getLogger('hypercane.collectionmodel')

class DSACollectionModel:

    def __init__(self, collection_id, working_directory, warcdir=None, wetdir=None, tmdir=None, session=None):
        
        module_logger.debug("setting up DSACollectionModel with working directory {}".format(working_directory))

        if warcdir is None:
            self.warcdir = "{}/warcs".format(working_directory)
        else:
            self.warcdir = warcdir

        if wetdir is None:
            self.wetdir = "{}/wets".format(working_directory)
        else:
            self.wetdir = wetdir

        if tmdir is None:
            self.tmdir = "{}/timemaps".format(working_directory)
        else:
            self.tmdir = tmdir

        if session is None:
            self.session = FuturesSession()
        else:
            self.session = session

        self.collection_id = collection_id

        self.memstock = MemStock(self.warcdir, cid=self.collection_id, session=self.session)
        self.wetstock = MemWETStock(self.wetdir, memstock=self.memstock, cid=self.collection_id, session=self.session)
        self.tmstock = TimeMapStock(self.tmdir, cid=self.collection_id, session=self.session)
        self.metadata = {}

        self.seedlist = []
        self.seed_urits = {}

    def add(self, urim):
        self.memstock.addByURIM(urim)

    def get(self, urim):
        return self.memstock.getByURIM(urim)

    def add_TimeMap(self, urit):
        self.tmstock.add(urit)

    def add_TimeMapMementos(self, urit):
        
        self.tmstock.add(urit)
        
        urims = self.tmstock.getURIMs(urit)

        module_logger.debug("adding {} URI-Ms from TimeMaps".format(len(urims)))
        
        for urim in urims:
            module_logger.debug("adding URI-M {} to collection".format(urim))
            self.add(urim)

    def getMementoURIList(self):
        return self.memstock.getAllURIMs()

    def collect_all_results(self):
        module_logger.info("collecting all results for collection...")
        self.tmstock.collect_all_results()
        self.memstock.collect_all_results()
        self.wetstock.collect_all_results()

    def getMementoURIListFromTimeMaps(self):

        module_logger.debug("acquiring URI-M list from TimeMaps...")
        
        allurims = []

        urits = self.tmstock.getURITs()

        for urit in urits:
            urims = self.tmstock.getURIMs(urit)
            allurims += urims

        return allurims

    ### the following functions are needed by OTMT ### 

    def getMementoContent(self, urim):
        """

        raises:
        * CollectionModelBoilerPlateRemovalFailureException
        * CollectionModelMementoErrorException
        """

        return self.memstock.getByURIM(urim).raw_stream.read()

    def getMementoContentWithoutBoilerplate(self, urim):
        """

        raises:
        * CollectionModelBoilerPlateRemovalFailureException
        * CollectionModelMementoErrorException
        """

        return self.wetstock.getByURIM(urim).raw_stream.read()

    def getTimeMapURIList(self):
        return self.tmstock.getURITs()

    def get_TimeMap(self, urit):
        return self.tmstock.getByURIT(urit)

    def get_MementoErrorInformation(self, urim):

        error = self.memstock.errorstock.get_error(urim)

        if error is not None :
            return error

        else:
            return None
