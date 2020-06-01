import logging
import otmt
import lxml.etree
import random
import copy

from justext import justext, get_stoplist
from aiu import convert_LinkTimeMap_to_dict
from requests.exceptions import ConnectionError, TooManyRedirects
from requests.exceptions import RequestException
from requests_futures.sessions import FuturesSession
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils import get_web_session, get_boilerplate_free_content

module_logger = logging.getLogger('hypercane.hfilter.remove_offtopic')

class HypercaneMementoCollectionModel(otmt.CollectionModel):

    def __init__(self, dbconn, session):
        """This class assumes session is an instance of CachedSession"""

        self.dbconn = dbconn
        self.session = session

        db = self.dbconn.get_default_database()
        self.error_collection = db.mementoerrors
        self.derived_collection = db.derivedvalues

        self.urimlist = []
        self.uritlist = []

    def __del__(self):
        """Override parent destructor."""
        pass

    def addTimeMap(self, urit):
        """Adds a TimeMap to the object, parsing it if it is in link-format
        and then stores the TimeMap as a dict in memory and JSON on disk.
        If JSON is given as `content`, then it is just converted to a dict.
        """
        self.session.get(urit)
        self.uritlist.append(urit)

    def getTimeMap(self, urit):
        """
            Returns the dict form of TimeMap at `urit` provided that it
            was previously stored via `addTimeMap`.
        """
        return convert_LinkTimeMap_to_dict(self.session.get(urit).text)

    def addMemento(self, urim):
        try:
            self.session.get(urim)
            raw_urim = otmt.generate_raw_urim(urim)
            self.session.get(raw_urim)
            self.urimlist.append(urim)
        except (ConnectionError, TooManyRedirects, RequestException) as e:
            self.addMementoError(urim, repr(e))

    def addManyMementos(self, urims):

        module_logger.info("started with {} URI-Ms for processing...".format(len(urims)))

        # protect the function from duplicates in the urims list
        urims = list(set(urims))

        module_logger.info("found duplicates, now using {} URI-Ms for processing...".format(len(urims)))

        futuressession = FuturesSession(session=self.session)

        retry = Retry(
            total=10,
            read=10,
            connect=10,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        futuressession.mount('http://', adapter)
        futuressession.mount('https://', adapter)

        futures = {}

        working_urim_list = []

        for uri in urims:

            raw_urim = otmt.generate_raw_urim(uri)
            working_urim_list.append(uri)
            futures[uri] = futuressession.get(uri)
            futures[raw_urim] = futuressession.get(raw_urim)

        working_starting_size = len(working_urim_list)

        def uri_generator(urilist):

            while len(urilist) > 0:

                uchoice = random.choice(urilist)

                yield uchoice

        for uri in uri_generator(working_urim_list):

            if futures[uri].done():

                module_logger.debug("uri {} is done, processing...".format(uri))

                if len(working_urim_list) % 100 == 0:
                    module_logger.info("{}/{} mementos left to process".format(len(working_urim_list), working_starting_size))

                try:
                    r = futures[uri].result()
                    if 'memento-datetime' not in r.headers:
                        self.addMementoError(uri, "URI-M {} does not produce a memento".format(uri))
                    else:
                        # the content should be cached by the session
                        # we just need to keep track of the URI-Ms for this run
                        self.urimlist.append(uri)

                except Exception as e:
                    self.addMementoError(uri, repr(e))

                working_urim_list.remove(uri)
                del futures[uri]


    def addMementoError(self, urim, errorinformation):
        """Associates `errorinformation` with memento specified by `urim` to
        the object, `content` and `headers` can also be stored from the given
        input transaction. If there are no headers or content, use content=""
        and headers={}.
        """
        self.error_collection.insert_one(
            {
                "urim": urim,
                "error_information": errorinformation
            }
        )

    def getMementoContent(self, urim):
        """Returns the HTTP entity of memento at `urim` provided that it
        was previously stored via `addMemento`.

        If no data was stored via `addMemento` for `urim`, then
        `CollectionModelNoSuchMementoException` is thrown.

        If data was stored via `addMementoError` for `urim`, then
        `CollectionModelMementoErrorException` is thrown.
        """
        raw_urim = otmt.generate_raw_urim(urim)
        return self.session.get(raw_urim).text

    def getMementoErrorInformation(self, urim):
        """Returns the error information associated with `urim`, provided that
        it was previously stored via `addMementoError`.
        If no data was stored via `addMemento` for `urim`, then
        `CollectionModelNoSuchMementoException` is thrown.
        """

        result = self.error_collection.find_one(
            { "urim": urim }
        )

        if result is None:
            if urim in self.urimlist:
                return None
        else:
            return result["error_information"]

    def getMementoContentWithoutBoilerplate(self, urim):
        """Returns the HTTP entity of memento at `urim` with all boilerplate
        removed, provided that it was previously stored via `addMemento`.

        If no data was stored via `addMemento` for `urim`, then
        `CollectionModelNoSuchMementoException` is thrown.

        If data was stored via `addMementoError` for `urim`, then
        `CollectionModelMementoErrorException` is thrown.

        If the boilerplate removal process produces an error for `urim`,
        then CollectionModelBoilerPlateRemovalFailureException is thrown.
        """

        if self.getMementoErrorInformation(urim) is not None:
            raise otmt.CollectionModelMementoErrorException(
                "Errors were recorded for URI-M {}".format(urim))

        try:
            bpfree = get_boilerplate_free_content(urim, dbconn=self.dbconn, session=self.session)
            return bpfree
        except (lxml.etree.ParserError, lxml.etree.XMLSyntaxError) as e:
            raise otmt.collectionmodel.CollectionModelBoilerPlateRemovalFailureException(repr(e))

    def getMementoHeaders(self, urim):
        """Returns the headers associated with memento at `urim`.
        """
        return self.session.get(urim).headers

    def getMementoURIList(self):
        """Returns a list of all URI-Ms stored in this object."""
        return copy.deepcopy(self.urimlist)

    def getTimeMapURIList(self):
        """Returns a list of all URI-Ts stored in this object."""
        return copy.deepcopy(self.uritlist)

def get_list_of_ontopic(measuremodel):

    ontopic_mementos = []

    for urit in measuremodel.get_TimeMap_URIs():
        for urim in measuremodel.get_Memento_URIs_in_TimeMap(urit):

            try:
                if measuremodel.get_overall_off_topic_status(urim) == "on-topic":
                    ontopic_mementos.append(urim)
            except KeyError:
                module_logger.warning("failed to get on-topic status for URI-M {}".format(urim))

    return ontopic_mementos

def detect_off_topic(dbconn, session, urits, urims, timemap_measures, num_topics=None):

    cm = HypercaneMementoCollectionModel(dbconn, session)

    module_logger.info("adding {} URI-Ts to collection model".format(
        len( urits )
    ))

    for urit in urits:
        module_logger.debug("adding URI-T {}".format(urit))
        cm.addTimeMap(urit)

    module_logger.info("adding URI-Ms from {} URI-Ts in collection model".format(
        len( cm.getTimeMapURIList() )
    ))

    # for urim in urims:
    #     module_logger.debug("adding URI-M {}".format(urim))
    #     cm.addMemento(urim)
    cm.addManyMementos(urims)

    # TOOD: what about document collections outside of web archives?
    # Note: these algorithms only work for collections with TimeMaps,
    # so how would that work exactly?

    module_logger.info(
        "stored {} mementos for processing...".format(
            len(cm.getMementoURIList())
        )
    )

    mm = otmt.MeasureModel()

    for measure in timemap_measures:

        module_logger.info("Processing mementos using TimeMap measure {}".format(measure))

        if measure == "gensim_lda" or measure == "gensim_lsi":

            if num_topics is None:
                num_topics = otmt.supported_timemap_measures[measure]["default number of topics"]

            mm = otmt.supported_timemap_measures[measure]["function"](
                cm, mm, num_topics=num_topics)

        else:

            mm = otmt.supported_timemap_measures[measure]["function"](
                cm, mm)

        module_logger.info("mm: {}".format(mm))

        threshold = timemap_measures[measure]

        mm.calculate_offtopic_by_measure(
            "timemap measures", measure, threshold,
            otmt.supported_timemap_measures[measure]["comparison direction"]
            )

        mm.calculate_overall_offtopic_status()

        ontopic_mementos = get_list_of_ontopic(mm)

        return ontopic_mementos
