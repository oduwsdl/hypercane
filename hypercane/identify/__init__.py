import multiprocessing
import random
import logging
import time
import argparse
import math

from random import randint
from datetime import datetime
from archivenow import archivenow
from copy import deepcopy
from aiu import ArchiveItCollection, convert_LinkTimeMap_to_dict
from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException
from urllib.parse import urlparse

from .archivecrawl import crawl_mementos, StorageObject, crawl_live_web_resources

module_logger = logging.getLogger('hypercane.identify')

storygraph_url = "http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph"

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

def extract_storygraph_arguments_from_input(input_string):

    rank = 1
    year = datetime.now().year
    month = datetime.now().month
    date = datetime.now().day
    hour = datetime.now().hour - 1 # in case there is nothing generated yet

    if ';' in input_string:
        rank, other = input_string.split(';')

        if other.count('/') == 2:

            year, month, rest = other.split('/')

            if 'T' in rest:

                date, rest = rest.split('T')

                hour, minute, second = rest.split(':')

            else:
                date = rest

        elif other.count('/') == 1:

            year, rest = other.split('/')
            
        else:
            raise argparse.ArgumentTypeError(
                "Error: Storygraph input arguments are not formatted correctly."
            )

        if '/' in other:

            items = other.split('/')

            year = items[0]

            if len(items) == 3:
                month = items[1]

        else:
            year = other

    else:
        rank = input_string

    storygraph_args = {}
    storygraph_args['rank'] = int(rank)
    storygraph_args['year'] = int(year)
    storygraph_args['month'] = int(month)
    storygraph_args['date'] = int(date)
    storygraph_args['hour'] = int(hour)

    return storygraph_args
    

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
            except RequestException:
                pass

            if r.status_code == 200:
                urit = r.links['timemap']['url']

                if urit not in urits:
                    urits.append(urit)

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

def find_or_create_mementos(urirs, session):

    # TODO: make TimeGate endpoint configurable

    urims = []

    for urir in urirs:
        # check for URI-M first and just take it if it exists

        module_logger.info("checking if {} exists via LANL Memento Aggregator".format(urir))
        available = True

        try:
            r = session.get("http://timetravel.mementoweb.org/timegate/{}".format(urir))

            if r.status_code != 200:
                available = False

        except RequestException:
            available = False

        if available is False:
            # some web archives (e.g., UKWA) issue a 451 or otherwise do not expose holdings
            module_logger.info("checking if {} exists at Internet Archive".format(urir))

            available = True

            try:
                r = session.get("https://web.archive.org/web/{}".format(urir))
                candidate_urim = r.url


                if r.status_code != 200:
                    available = False

                if 'memento-datetime' not in r.headers:
                    available = False

            except RequestException:
                available = False

        if available is True:
            candidate_urim = r.url
        else:
            numsecs = randint(3, 10)
            module_logger.info("sleeping {} seconds before pushing into web archive...".format(numsecs))
            time.sleep(numsecs)

            module_logger.info("pushing {} into Internet Archive".format(urir))
            candidate_urim = archivenow.push(urir, "ia")[0]
        
            if candidate_urim[0:5] == "Error":
                # for now, skip if error
                # TODO: try with other archives, we don't use archive.is because new mementos don't immediately have Memento headers
                # candidate_urim = archivenow.push(urir, "is")[0]
                module_logger.warning("Failed to push {} into the Internet Archive, skipping...".format(urir))
                continue

        module_logger.info("adding URI-M {}".format(candidate_urim))
        urims.append(candidate_urim)

    return urims

def get_uris_from_storygraph(session, storygraph_url, rank, year, month, date, hour):

    if storygraph_url[-1] == '/':
        storygraph_url = storygraph_url[:-1]

    if int(month / 10) == 0:
        month = "0{}".format(month)
    
    if int(date / 10) == 0:
        date = "0{}".format(date)

    json_url = "{}/{}/{}/{}/graph{}.json".format(
        storygraph_url, year, month, date, hour)

    module_logger.info("downloading JSON from {}".format(json_url))

    r = session.get(json_url)
    jdata = r.json()
    urirs = []

    if rank > 0:

        max_avg_degree = 0

        for comp in jdata["connected-comps"]:
            if comp["avg-degree"] > max_avg_degree:
                max_avg_degree = comp["avg-degree"]

        module_logger.info("maximum average degree: {}".format(max_avg_degree))

        comp_nodes = []

        for comp in jdata["connected-comps"]:
            module_logger.info("comp['avg-degree']: {}".format(comp["avg-degree"]))
            if math.isclose(comp["avg-degree"], max_avg_degree):
                comp_nodes = comp["nodes"]
                break

        module_logger.info("number of component nodes: {}".format(len(comp_nodes)))

        for i in range(0, len(jdata["nodes"])):
            if i in comp["nodes"]:
                module_logger.info("adding link from node {}".format(i))
                link = jdata["nodes"][i]["link"]
                module_logger.info("adding link {}".format(link))
                urirs.append(link)


    else:

        connected_nodes = []

        for comp in jdata["connected-comps"]:
            connected_nodes.extend( comp["nodes"] )

        for i in range(0, len(jdata["nodes"])):
            if i not in connected_nodes:
                module_logger.info("adding link from node {}".format(i))
                link = jdata["nodes"][i]["link"]
                module_logger.info("adding link {}".format(link))
                urirs.append(link)

    return urirs

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

    elif input_type == "storygraph":

        storygraph_arguments = extract_storygraph_arguments_from_input(input_args)

        urirs = get_uris_from_storygraph(session, storygraph_url, storygraph_arguments['rank'],
            storygraph_arguments['year'], storygraph_arguments['month'], storygraph_arguments['date'],
            storygraph_arguments['hour']
        )

        if crawl_depth > 1:
            link_storage = StorageObject()
            crawl_live_web_resources(link_storage, urirs, crawl_depth)

            for item in link_storage.storage:
                
                if item not in urirs:
                    urirs.append(item)

        urims = find_or_create_mementos(urirs, session)
        urits = extract_urts_from_urims(urims, session)

    elif input_type == "timemaps":

        urits = extract_uris_from_input(input_args)
        
        if crawl_depth > 1:
            urims = download_urits_and_extract_urims(urits, session)
            link_storage = StorageObject()
            crawl_mementos(link_storage, urims, crawl_depth)

            for item in link_storage.storage:
                urits.append(item[0])

            urits = list(set(urits)) # in case of overlap

    elif input_type == "mementos":
        urims = extract_uris_from_input(input_args)
        link_storage = StorageObject()
        crawl_mementos(link_storage, urims, crawl_depth)

        for item in link_storage.storage:
            urits.append(item[0])
        
    elif input_type == "original-resources":

        urirs = extract_uris_from_input(input_args)

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

    elif input_type == "storygraph":

        storygraph_arguments = extract_storygraph_arguments_from_input(input_args)

        urirs = get_uris_from_storygraph(session, storygraph_url, storygraph_arguments['rank'],
            storygraph_arguments['year'], storygraph_arguments['month'], storygraph_arguments['date'],
            storygraph_arguments['hour']
        )

        if crawl_depth > 1:
            link_storage = StorageObject()
            crawl_live_web_resources(link_storage, urirs, crawl_depth)

            for item in link_storage.storage:
                
                if item not in urirs:
                    urirs.append(item)

        output_urims = find_or_create_mementos(urirs, session)

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

        output_urims = input_args

        print(output_urims)

        if crawl_depth > 1:
            urits = []
            link_storage = StorageObject()
            crawl_mementos(link_storage, output_urims, crawl_depth)

            for item in link_storage.storage:
                urits.append(item[0])

            urits = list(set(urits)) # in case of overlap
            output_urims = download_urits_and_extract_urims(urits, session)                

    elif input_type == "original-resources":

        urirs = extract_uris_from_input(input_args)
        output_urims = find_or_create_mementos(urirs, session)

    else:
        raise argparse.ArgumentTypeError(
            "Error: Unsupported input type {}.".format(input_args)
        )

    return output_urims

def discover_original_resources_by_input_type(input_type, input_args, crawl_depth, session):
    
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

    elif input_type == "storygraph":

        storygraph_arguments = extract_storygraph_arguments_from_input(input_args)

        output_urirs = get_uris_from_storygraph(session, storygraph_url, storygraph_arguments['rank'],
            storygraph_arguments['year'], storygraph_arguments['month'], storygraph_arguments['date'],
            storygraph_arguments['hour']
        )

        if crawl_depth > 1:
            link_storage = StorageObject()
            crawl_live_web_resources(link_storage, output_urirs, crawl_depth)

            for item in link_storage.storage:
                
                if item not in output_urirs:
                    output_urirs.append(item)

    elif input_type == "timemaps":
        urits = extract_uris_from_input(input_type)
        urims = download_urits_and_extract_urims(urits, session)
        link_storage = StorageObject()
        crawl_mementos(link_storage, urims, crawl_depth)

        for item in link_storage.storage:
            output_urirs.append(item[1])

    elif input_type == "mementos":
        urims = extract_uris_from_input(input_type)
        link_storage = StorageObject()
        crawl_mementos(link_storage, urims, crawl_depth)

        for item in link_storage.storage:

            urir = item[1]

            if urir not in output_urirs:
                output_urirs.append(urir)
        
    elif input_type == "original-resources":

        output_urirs = extract_uris_from_input(input_args)

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

