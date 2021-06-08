import logging
import otmt
import lxml.etree
import random
import copy
import traceback
import pprint
import time

from justext import justext, get_stoplist
from aiu import convert_LinkTimeMap_to_dict
from requests.exceptions import ConnectionError, TooManyRedirects
from requests.exceptions import RequestException
from requests_futures.sessions import FuturesSession
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse

from ..utils import get_web_session, get_boilerplate_free_content, get_faux_TimeMap_json, generate_raw_urim
import hypercane.errors

module_logger = logging.getLogger('hypercane.hfilter.remove_offtopic')
pp = pprint.PrettyPrinter(indent=4)

class HypercaneMementoCollectionModel(otmt.CollectionModel):

    def __init__(self, dbconn, session, allow_noncompliant_archives=False):
        """This class assumes session is an instance of CachedSession"""

        self.dbconn = dbconn
        self.session = session

        db = self.dbconn.get_default_database()
        self.error_collection = db.mementoerrors
        self.derived_collection = db.derivedvalues
        self.allow_noncompliant_archives = allow_noncompliant_archives

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

        o = urlparse(urit)

        if o.scheme != 'fauxtm':

            # cache for future calls
            self.session.get(urit)
        
        self.uritlist.append(urit)

    def getTimeMap(self, urit):
        """
            Returns the dict form of TimeMap at `urit` provided that it
            was previously stored via `addTimeMap`.
        """

        o = urlparse(urit)

        if o.scheme == 'fauxtm':

            cache_storage = "mongodb://{}:{}/{}".format(
                self.dbconn.HOST,
                self.dbconn.PORT,
                self.dbconn.get_default_database().name
            )
            timemap_json = get_faux_TimeMap_json(urit, self.urimlist, cache_storage)

            module_logger.debug("for {} returning TimeMap JSON: {}".format(urit, timemap_json))

            return timemap_json

        else:
            return convert_LinkTimeMap_to_dict(self.session.get(urit).text)

    def addMemento(self, urim):
        try:
            r = self.session.get(urim)

            if len(r.history) == 0:
                raw_urim = generate_raw_urim(urim)
            else:
                raw_urim = generate_raw_urim(r.url)

            self.session.get(raw_urim)
            self.urimlist.append(urim)
        except (ConnectionError, TooManyRedirects, RequestException) as e:
            self.addMementoError(urim, repr(e))

    def addManyMementos(self, urims):

        module_logger.info("started with {} URI-Ms for processing...".format(len(urims)))

        # protect the function from duplicates in the urims list
        urims = list(set(urims))

        module_logger.info("removed duplicate URI-Ms, now using {} URI-Ms for processing...".format(len(urims)))

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
        raw_futures = {}

        working_urim_list = []
        
        raw_urims = []

        for uri in urims:

            # raw_urim = otmt.generate_raw_urim(uri)
            working_urim_list.append(uri)
            futures[uri] = futuressession.get(uri)
            # futures[raw_urim] = futuressession.get(raw_urim)

        working_starting_size = len(working_urim_list)

        def uri_generator(urilist):

            while len(urilist) > 0:

                uchoice = random.choice(urilist)

                yield uchoice

        for uri in uri_generator(working_urim_list):

            # module_logger.debug("checking on URI-M {}".format(uri))

            if futures[uri].done():

                module_logger.debug("URI-M {} is done, processing...".format(uri))

                if len(working_urim_list) % 100 == 0:
                    module_logger.info("{}/{} mementos left to process".format(len(working_urim_list), working_starting_size))

                try:
                    module_logger.debug("examining result for URI-M {}".format(uri))

                    r = futures[uri].result()

                    if len(r.history) == 0:
                        raw_urim = generate_raw_urim(uri)
                    else:
                        raw_urim = generate_raw_urim(r.url)

                    module_logger.debug("adding {} to raw URI-M list".format(raw_urim))
                    raw_urims.append( raw_urim )

                    module_logger.debug("headers for {} are: {}".format(uri, r.headers))

                    if 'memento-datetime' not in r.headers:
                        module_logger.debug("allow noncompliant archives is {}, found a noncompliant memento at {}".format(
                            self. allow_noncompliant_archives, uri))
                        if self.allow_noncompliant_archives == True:
                            module_logger.debug("adding noncompilant memento {} to URI-M list".format(uri))
                            self.urimlist.append(uri)
                        else:
                            self.addMementoError(uri, "URI-M {} does not produce a memento".format(uri))
                    else:
                        # the content should be cached by the session
                        # we just need to keep track of the URI-Ms for this run
                        module_logger.debug("adding compliant memento {} to URI-M list".format(uri))
                        self.urimlist.append(uri)

                except Exception as e:
                    self.addMementoError(uri, repr(e))

                working_urim_list.remove(uri)
                del futures[uri]

        module_logger.info("done adding {} mementos, now adding corresponding {} raw mementos...".format( len(urims), len(raw_urims) ))

        working_raw_urim_list = []

        for raw_urim in list(set(raw_urims)):

            working_raw_urim_list.append(raw_urim)
            raw_futures[raw_urim] = futuressession.get(raw_urim)

        working_rawurims_starting_size = len(working_raw_urim_list)

        # for raw_urim in uri_generator(working_raw_urim_list):

        while len(working_raw_urim_list) > 0:

            raw_urim = random.choice(working_raw_urim_list)

            module_logger.debug("fetching results for raw URI-M {}".format(raw_urim))
            # module_logger.debug("are the keys the same as the working list: {}".format( set(working_raw_urim_list) == set(list(raw_futures.keys())) ) )
            module_logger.debug("raw mementos working list size: {}".format(len(working_raw_urim_list)))
            module_logger.debug("raw mementos futures keys size: {}".format(len(raw_futures)))

            # try:
            #     raw_futures[raw_urim]
            # except KeyError:
            #     module_logger.error("{} is not in futures".format(raw_urim))
            #     module_logger.error("is it: {}".format( raw_urim in raw_futures ))
            #     module_logger.error("")
            #     module_logger.error("working list follows:")
            #     module_logger.error(pp.pformat(working_raw_urim_list))
            #     module_logger.error("")
            #     module_logger.error("raw_futures keys follows:")
            #     module_logger.error(pp.pformat(list(raw_futures.keys())))
                

            if raw_futures[raw_urim].done():
                module_logger.debug("raw URI-M {} is done, processing...".format(raw_urim))

                if len(working_raw_urim_list) % 100 == 0:
                    module_logger.info("{}/{} raw mementos left to process".format(len(working_raw_urim_list), working_rawurims_starting_size))

                try:
                    module_logger.debug("extracting result from raw URI-M download for {}".format(raw_urim))
                    r = raw_futures[raw_urim].result()

                    if 'memento-datetime' not in r.headers:
                        if self.allow_noncompliant_archives == True:
                            # module_logger.debug("adding noncompilant raw memento {} to URI-M list".format(uri))
                            # self.urimlist.append(raw_urim)
                            module_logger.warning("not adding noncompliant raw memento {} to URI-M list".format(uri))
                        else:
                            self.addMementoError(uri, "URI-M {} does not produce a memento".format(uri))
                    else:
                        # the content should be cached by the session
                        # we just need to keep track of the URI-Ms for this run
                        module_logger.debug("adding compliant raw memento {} to URI-M list".format(uri))
                        self.urimlist.append(raw_urim)

                except Exception as e:
                    self.addMementoError(raw_urim, repr(e))

                # module_logger.debug("removing {} from working raw URI-M list and raw futures keys".format(raw_urim))
                working_raw_urim_list.remove(raw_urim)
                del raw_futures[raw_urim]

                # time.sleep(1)

        module_logger.debug("urimlist of length {} is now {}".format(len(self.urimlist), self.urimlist))


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
        raw_urim = generate_raw_urim(urim)
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

        module_logger.debug("requesting boilerplate-free content for off-topic analysis from {}".format(urim))

        if self.getMementoErrorInformation(urim) is not None:
            raise otmt.CollectionModelMementoErrorException(
                "Errors were recorded for URI-M {} : {}".format(
                    urim, self.getMementoErrorInformation(urim)
                ))

        try:
            bpfree = get_boilerplate_free_content(urim, dbconn=self.dbconn, session=self.session)
            return bpfree
        except (lxml.etree.ParserError, lxml.etree.XMLSyntaxError) as e:
            hypercane.errors.errorstore.add( urim, traceback.format_exc() )
            raise otmt.collectionmodel.CollectionModelBoilerPlateRemovalFailureException(repr(e))
        except Exception:
            module_logger.exception("failed to process URI-M, returning empty content for {}".format(urim))
            module_logger.info("errorstore is of type {}".format(type(hypercane.errors.errorstore)))
            hypercane.errors.errorstore.add( urim, traceback.format_exc() )
            return bytes()

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

    # module_logger.debug("measuremodel: {}".format(measuremodel))
    module_logger.debug("scoremodel: {}".format(measuremodel.scoremodel))

    for urit in measuremodel.get_TimeMap_URIs():
        module_logger.debug("examining TimeMap at {} for topic status".format(urit))
        for urim in measuremodel.get_Memento_URIs_in_TimeMap(urit):

            module_logger.debug("examining URI-M {} in TimeMap".format(urim))

            try:
                topic_status = measuremodel.get_overall_off_topic_status(urim)
                module_logger.debug("topic status for {} is {}".format(urim, topic_status))
                if topic_status == "on-topic":
                    ontopic_mementos.append(urim)
            except KeyError as e:
                # this largely happens because the boilerplate removal returns nothing 
                # and the OTMT does not report the problem
                module_logger.exception("failed to get on-topic status for URI-M {}, skipping...".format(urim))

    return ontopic_mementos

def detect_off_topic(dbconn, session, urits, urims, timemap_measures, num_topics=None, allow_noncompliant_archives=False):

    cm = HypercaneMementoCollectionModel(dbconn, session, allow_noncompliant_archives=allow_noncompliant_archives)

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
        "stored {} mementos and raw mementos for processing...".format(
            len(cm.getMementoURIList())
        )
    )

    mm = otmt.MeasureModel()

    module_logger.info("mementos are stored, now using timemap measures {}".format(timemap_measures))

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
