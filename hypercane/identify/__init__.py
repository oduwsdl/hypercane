import multiprocessing
import random
import logging
import time
import argparse
import math
import os
import csv
import traceback
import requests

from random import randint
from datetime import datetime
from archivenow import archivenow
from copy import deepcopy
from aiu import ArchiveItCollection, convert_LinkTimeMap_to_dict, NLACollection
from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException
from urllib.parse import urlparse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from .archivecrawl import crawl_mementos, StorageObject, crawl_live_web_resources
from ..utils import process_input_for_cluster_and_rank, get_memento_http_metadata
import hypercane.errors
from hypercane.version import __useragent__

module_logger = logging.getLogger('hypercane.identify')

def extract_uris_from_input(input_string):

    uri_list = input_string.split(',')
    uri_output_list = []

    for uri in uri_list:
        o = urlparse(uri)
        if o.scheme == 'http' or o.scheme == 'https':
            uri_output_list.append(uri)
        elif o.scheme == 'file':
            with open(o.path) as f:
                for line in f:
                    line = line.strip()
                    uri_output_list.append(line)
        else:
            # assume it is a filename
            with open(uri) as f:
                for line in f:
                    line = line.strip()
                    uri_output_list.append(line)

    return uri_output_list

def extract_urims_from_TimeMap(timemap_json_text):

    urimlist = []

    for memento in timemap_json_text["mementos"]["list"]:
        urimlist.append( memento['uri'] )

    return urimlist

def download_urits_and_extract_urims(uritlist, session):

    urimlist = []
    cpucount = multiprocessing.cpu_count()
    futuresesion = FuturesSession(session=session, max_workers=cpucount)
    futures = {}
    working_list = deepcopy(uritlist)

    for urit in uritlist:
        futures[urit] = futuresesion.get(urit)

    def urit_generator(workinglist):

        while len(workinglist) > 0:
            yield random.choice(workinglist)

    for workinguri in urit_generator(working_list):

        if futures[workinguri].done():

            try:
                r = futures[workinguri].result()
            except RequestException:
                pass

            if r.status_code == 200:
                timemap_content = convert_LinkTimeMap_to_dict(r.text)

                try:
                    urims = extract_urims_from_TimeMap(timemap_content)
                except KeyError as e:
                    module_logger.exception(
                        "Skipping TimeMap {}, encountered problem extracting URI-Ms from TimeMap: {}".format(workinguri, repr(e)))
                    hypercane.errors.errorstore.add(workinguri, traceback.format_exc())

                urimlist.extend(urims)

            working_list.remove(workinguri)
            del futures[workinguri]

    return urimlist

def extract_urts_from_urims(urimlist, session):

    urits = []

    cpucount = multiprocessing.cpu_count()
    futuresesion = FuturesSession(session=session, max_workers=cpucount)
    futures = {}
    working_list = deepcopy(urimlist)

    for urim in urimlist:
        futures[urim] = futuresesion.get(urim)

    def urim_generator(workinglist):

        while len(workinglist) > 0:
            yield random.choice(workinglist)

    for workinguri in urim_generator(working_list):

        if futures[workinguri].done():

            try:
                r = futures[workinguri].result()
                r.raise_for_status()

                urit = r.links['timemap']['url']

                if urit not in urits:
                    urits.append(urit)

            except Exception as e:
                module_logger.exception("Error: {}, failed to process {} - skipping...".format(repr(e), workinguri))
                hypercane.errors.errorstore.add(workinguri, traceback.format_exc())

            working_list.remove(workinguri)
            del futures[workinguri]

    return urits

def generate_archiveit_urits(cid, seed_uris):
    """This function generates TimeMap URIs (URI-Ts) for a list of `seed_uris`
    from an Archive-It colleciton specified by `cid`.
    """

    urit_list = []

    for urir in seed_uris:
        urit = "http://wayback.archive-it.org/{}/timemap/link/{}".format(
            cid, urir
        )

        urit_list.append(urit)

    return urit_list

def list_seed_uris(collection_id, session):

    aic = ArchiveItCollection(collection_id, session=session)

    return aic.list_seed_uris()

def find_or_create_mementos(urirs, session, accept_datetime=None,
    timegates=[
        "https://timetravel.mementoweb.org/timegate/",
        "https://web.archive.org/web/"
    ]):

    urims = []

    req_headers = {}

    if accept_datetime is not None:
        req_headers['accept-datetime'] = \
            accept_datetime.strftime( "%a, %d %b %Y %H:%M:%S GMT" )

    retry = Retry(
        total=10,
        read=10,
        connect=10,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)

    for urir in urirs:
        # check for URI-M first and just take it if it exists

        for urig in timegates:

            module_logger.info("checking if {} exists via {}".format(urir, urig))
            available = False

            urig = urig[:-1] if urig[-1] == '/' else urig

            try:

                urig = "{}/{}".format(urig, urir)

                # no caching for datetime negotiation
                dt_neg_session = requests.Session()
                dt_neg_session.mount('http://', adapter)
                dt_neg_session.mount('https://', adapter)
                dt_neg_session.headers.update({'user-agent': __useragent__})

                r = dt_neg_session.get(urig, headers=req_headers)

                if r.status_code != 200:
                    module_logger.info(
                        "got a status of {} for {} -- could not find a memento for {} via {}".format(
                            r.status_code, r.url, urir, urig))
                    available = False
                else:
                    if 'memento-datetime' in r.headers:
                        available = True
                    else:
                        available = False

            except RequestException:
                module_logger.exception(
                    "Failed to find memento for {}".format(urir))
                available = False

        if r.url[0:29] == "https://web.archive.org/save/":
            available = False

        # module_logger.info("a candidate memento for {} was found: {}".format(urir, available))

        if available is True:
            candidate_urim = r.url
            module_logger.info("adding available URI-M {}".format(candidate_urim))
            urims.append(candidate_urim)
        else:
            numsecs = randint(3, 10)
            module_logger.info("sleeping {} seconds before pushing into web archive...".format(numsecs))
            time.sleep(numsecs)

            module_logger.info("pushing {} into Internet Archive".format(urir))
            create_memento_session = requests.Session()
            create_memento_session.mount('http://', adapter)
            create_memento_session.mount('https://', adapter)
            create_memento_session.headers.update({'user-agent': __useragent__})

            candidate_urim = archivenow.push(urir, "ia", session=create_memento_session)[0]

            module_logger.info("received candidate URI-M {} from the Internet Archive".format(candidate_urim))

            if candidate_urim[0:5] == "Error" or candidate_urim[0:29] == "https://web.archive.org/save/":
                # for now, skip if error
                # TODO: try with other archives, we don't use archive.is because new mementos don't immediately have Memento headers
                # candidate_urim = archivenow.push(urir, "is")[0]
                module_logger.warning("Failed to push {} into the Internet Archive, skipping...".format(urir))
                hypercane.errors.errorstore.add(urir, "Failed to create URI-M for {}".format(urir))
            else:
                module_logger.info("adding newly minted URI-M {}".format(candidate_urim))
                urims.append(candidate_urim)

    return urims

def discover_timemaps_by_input_type(input_type, input_args, crawl_depth, session, **kwargs):

    module_logger.info("discovering timemaps for input type: {}".format(input_type))
    urits = []

    if input_type == "archiveit":
        collection_id = input_args
        module_logger.info("Archive-It collection identifier: {}".format(collection_id))
        seeds = list_seed_uris(collection_id, session)
        urits = generate_archiveit_urits(collection_id, seeds)
        module_logger.info("discovered {} URI-Ts prior to deeper crawling".format(
            len(urits))
        )

        if crawl_depth > 1:
            urims = download_urits_and_extract_urims(urits, session)
            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:
                urits.append(item[0])

    elif input_type == "nla":

        collection_id = input_args
        module_logger.info("NLA collection identifier: {}".format(collection_id))

        raise NotImplementedError("TimeMap discovery not yet supported for NLA collections")

    elif input_type == "timemaps":

        urits = input_args

        if crawl_depth > 1:
            urims = download_urits_and_extract_urims(urits, session)
            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:
                urits.append(item[0])

            urits = list(set(urits)) # in case of overlap

    elif input_type == "mementos":
        urims = input_args

        for urim in urims:

            module_logger.debug("seeking for URI-R for URI-M {}".format(urim))
            urit = get_memento_http_metadata(urim, session.cache_storage, 
                metadata_fields=['timemap'])[0]

            urits.append(urit)

        if crawl_depth > 1:

            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:
                urits.append(item[0])

    elif input_type == "original-resources":

        urirs = input_args

        link_storage = StorageObject()
        crawl_live_web_resources(link_storage, urirs, crawl_depth)

        for urir in link_storage.storage:

            if urir not in urirs:
                urirs.append(urir)

        urims = find_or_create_mementos(urirs, session)
        urits = extract_urts_from_urims(urims, session)

    else:
        raise argparse.ArgumentTypeError(
            "Error: Unsupported input type {}.".format(input_args)
        )

    module_logger.info("returning {} URI-Ts".format(len(urits)))

    return urits

def discover_mementos_by_input_type(input_type, input_args, crawl_depth, session, accept_datetime=None, timegates=None):

    output_urims = []

    module_logger.info("discovering mementos for input type {}".format(input_type))

    if input_type == "archiveit":

        if accept_datetime is not None:
            module_logger.warning("ignoring accept-datetime for archiveit input type")

        collection_id = input_args
        seeds = list_seed_uris(collection_id, session)
        urits = generate_archiveit_urits(collection_id, seeds)

        if crawl_depth > 1:
            urims = download_urits_and_extract_urims(urits, session)
            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:
                urits.append(item[0])

            urits = list(set(urits)) # in case of overlap

        output_urims = download_urits_and_extract_urims(urits, session)

    elif input_type == "nla":

        collection_id = input_args
        module_logger.info("NLA collection identifier: {}".format(collection_id))

        nlac = NLACollection(collection_id, session=session)

        candidate_urims = nlac.list_memento_urims()
        output_urims = []

        # sometimes the NLA JSON returns extra \n characters around the URI-M

        for urim in candidate_urims:

            urim = urim.strip()
            output_urims.append(urim)

        if crawl_depth > 1:
            module_logger.warning(
                "Crawling not yet implemented for NLA collections, ignoring crawl depth {}".format(crawl_depth))

    elif input_type == "timemaps":

        if accept_datetime is not None:
            module_logger.warning("ignoring accept-datetime for timemaps input type")

        urits = input_args

        if crawl_depth > 1:
            urims = download_urits_and_extract_urims(urits, session)
            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:
                urits.append(item[0])

            urits = list(set(urits)) # in case of overlap

        output_urims = download_urits_and_extract_urims(urits, session)

    elif input_type == "mementos":

        if accept_datetime is not None:
            module_logger.warning("ignoring accept-datetime for mementos input type")

        output_urims = input_args

        if crawl_depth > 1:
            urits = []
            link_storage = StorageObject()
            crawl_mementos(link_storage, output_urims, crawl_depth)

            module_logger.info("discovered {} items from crawl".format(len(link_storage.storage)))

            for item in link_storage.storage:
                urits.append(item[0])

            urits = list(set(urits)) # in case of overlap
            output_urims = download_urits_and_extract_urims(urits, session)

            module_logger.info("returning {} URI-Ms from crawl".format(len(output_urims)))

    elif input_type == "original-resources":

        if accept_datetime is not None:
            module_logger.info("applying accept-datetime {} to discovery of mementos".format(accept_datetime))

        urirs = input_args
        output_urims = find_or_create_mementos(
            urirs, session, accept_datetime=accept_datetime,
            timegates=timegates)

    else:
        raise argparse.ArgumentTypeError(
            "Error: Unsupported input type {}.".format(input_args)
        )

    return output_urims

def discover_original_resources_by_input_type(input_type, input_args, crawl_depth, session, **kwargs):

    output_urirs = []

    module_logger.info("discovering mementos for input type {}".format(input_type))

    if input_type == "archiveit":
        collection_id = input_args
        module_logger.info("Collection type: {}".format(input_type))
        module_logger.info("Collection identifier: {}".format(collection_id))
        output_urirs = list_seed_uris(collection_id, session)

        if crawl_depth > 1:

            urits = generate_archiveit_urits(collection_id, output_urirs)
            urims = download_urits_and_extract_urims(urits, session)
            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:
                output_urirs.append(item[1])

    elif input_type == "nla":

        collection_id = input_args
        module_logger.info("NLA collection identifier: {}".format(collection_id))

        nlac = NLACollection(collection_id, session=session)

        output_urirs = nlac.list_seed_uris()

        # sometimes seeds do not contain proper URIs

        if crawl_depth > 1:
            module_logger.warning(
                "Crawling not yet implemented for NLA collections, ignoring crawl depth {}".format(crawl_depth))

    elif input_type == "timemaps":
        urits = input_args
        urims = download_urits_and_extract_urims(urits, session)
        link_storage = StorageObject()
        crawl_mementos(link_storage, urims, crawl_depth)

        for item in link_storage.storage:
            output_urirs.append(item[1])

    elif input_type == "mementos":
        urims = input_args

        for urim in urims:
            module_logger.debug("seeking for URI-R for URI-M {}".format(urim))
            urir = get_memento_http_metadata(urim, session.cache_storage, 
                metadata_fields=['original'])[0]
            output_urirs.append(urir)

        if crawl_depth > 1:
            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:

                urir = item[1]

                if urir not in output_urirs:
                    output_urirs.append(urir)

    elif input_type == "original-resources":

        output_urirs = input_args

        if crawl_depth > 1:
            link_storage = StorageObject()
            crawl_live_web_resources(link_storage, output_urirs, crawl_depth)

            for item in link_storage.storage:

                if item not in output_urirs:
                    output_urirs.append(item)

    else:
        raise argparse.ArgumentTypeError(
            "Error: Unsupported input type {}.".format(input_args)
        )

    return output_urirs

def discover_resource_data_by_input_type(input_type, output_type, input_arguments, crawl_depth, session, discovery_function, accept_datetime=None, timegates=None):

    uridata = {}

    input_type_keys = {
        'mementos': 'URI-M',
        'timemaps': 'URI-T',
        'original-resources': 'URI-R'
    }

    module_logger.info("processing input for type {}".format(input_type))

    if input_type == 'archiveit' or input_type == 'nla':
        input_data = input_arguments
        uridata = None
    else:
        uridata = process_input_for_cluster_and_rank(input_arguments, input_type_keys[input_type])
        input_data = list(uridata.keys())

        if input_type != output_type:
            uridata = None

    output_uris = discovery_function(
        input_type, input_data, crawl_depth, session,accept_datetime=accept_datetime,
        timegates=timegates)

    module_logger.info("discovered {} URIs".format(len(output_uris)))

    if uridata is None:
        uridata = {}
        for uri in output_uris:
            uridata[uri] = {}
    else:
        fieldnames = []

        for uri in uridata:
            if len(list(uridata[uri].keys())) > 0:
                fieldnames.extend(list(uridata[uri].keys()))
            # just do it once
            break

        for uri in output_uris:
            if uri not in uridata:
                uridata[uri] = {}
                for fieldname in fieldnames:
                    uridata[uri][fieldname] = ''

    return uridata

