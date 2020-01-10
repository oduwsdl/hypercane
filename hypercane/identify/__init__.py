import multiprocessing
import random
import logging

from copy import deepcopy
from aiu import ArchiveItCollection, convert_LinkTimeMap_to_dict
from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException
from urllib.parse import urlparse

from .archivecrawl import crawl_mementos, StorageObject

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
                urims = extract_urims_from_TimeMap(timemap_content)

            urimlist.extend(urims)

            working_list.remove(workinguri)
            del futures[workinguri]

    return urimlist

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

def list_seed_mementos(collection_id, session):

    seeds = list_seed_uris(collection_id, session)
    urits = generate_archiveit_urits(collection_id, seeds)

    urims = download_urits_and_extract_urims(urits, session)

    return urims

def generate_collection_metadata(collection_id, session):

    aic = ArchiveItCollection(collection_id, session=session)

    return aic.return_all_metadata_dict()

def discover_timemaps_by_input_type(input_type, input_args, crawl_depth, session):

    module_logger.info("discovering timemaps for input type: {}".format(input_type))
    urits = []

    if input_type == "archiveit":
        collection_id = input_args
        module_logger.info("Collection identifier: {}".format(collection_id))
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

    elif input_type == "timemaps":
        urits = extract_uris_from_input(input_args)
    elif input_type == "mementos":
        urims = extract_uris_from_input(input_args)
        link_storage = StorageObject()
        crawl_mementos(link_storage, urims, crawl_depth)

        for item in link_storage.storage:
            urits.append(item[0])
        
    elif input_type == "original-resources":
        # TODO: implement this with a user-specified aggregator so they can create their own collections
        raise NotImplementedError("Extracting TimeMaps from Original Resources is not implemented at this time")
    elif input_type == "warcs":
        raise NotImplementedError("Extracting TimeMaps from WARCs is not implemented at this time")

    module_logger.info("returning {} URI-Ts".format(len(urits)))

    return urits

def discover_mementos_by_input_type(input_type, input_args, crawl_depth, session):
    
    output_urims = []

    module_logger.info("discovering mementos for input type {}".format(input_type))

    if input_type == "archiveit":

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

    elif input_type == "timemaps":
        urits = extract_uris_from_input(input_args)
        
        if crawl_depth > 1:
            urims = download_urits_and_extract_urims(urits, session)
            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:
                urits.append(item[0])

            urits = list(set(urits)) # in case of overlap

        output_urims = download_urits_and_extract_urims(urits, session)

    elif input_type == "mementos":
        # identity
        output_urims = extract_uris_from_input(input_args)

    elif input_type == "original-resources":
        # TODO: implement this with a user-specified aggregator so they can create their own collections
        raise NotImplementedError("Extracting Mementos from Original Resources is not implemented at this time")

    elif input_type == "warcs":
        # TODO: implement this with an option to provide a URI prefix with which to construct URI-Ms
        raise NotImplementedError("Extracting Mementos from WARCs is not implemented at this time")

    return output_urims


