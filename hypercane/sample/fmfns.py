import multiprocessing
import random
import logging

from copy import deepcopy
from aiu import convert_LinkTimeMap_to_dict
from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException

from ..identify import list_seed_uris, generate_archiveit_urits

module_logger = logging.getLogger('hypercane.sample.fmfns')

def fetch_first_urim_of_urits(uritlist, session):

    module_logger.info("discovered {} URI-Ts".format(len(uritlist)))

    cpucount = multiprocessing.cpu_count()    
    futuresesion = FuturesSession(session=session, max_workers=cpucount)
    futures = {}
    working_list = deepcopy(uritlist)
    first_urims = []

    module_logger.debug("starting download of {} URI-Ts".format(len(uritlist)))
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

            module_logger.debug("HTTP status for {} is {}".format(workinguri, r.status_code))

            if r.status_code == 200:
                if len(r.text) > 0:
                    timemap_content = convert_LinkTimeMap_to_dict(r.text)
                    try:
                        first_urims.append(
                            timemap_content["mementos"]["first"]["uri"]
                        )
                    except KeyError as e:
                        module_logger.warning("encountered KeyError while working on URI {}, details: {} [SKIPPING URI]".format(workinguri, e))
                else:
                    module_logger.warning("received empty TimeMap for URI-T {} [SKIPPING URI]".format(workinguri))

            module_logger.debug("removing {} from download list".format(workinguri))
            working_list.remove(workinguri)
            del futures[workinguri]

    module_logger.info("returning {} candidate URI-Ms".format(len(first_urims)))

    return first_urims

def extract_redirect_endpoints(urimlist, session):

    cpucount = multiprocessing.cpu_count()    
    futuresesion = FuturesSession(session=session, max_workers=cpucount)
    futures = {}
    working_list = deepcopy(urimlist)
    endpoint_urims = []

    for urit in urimlist:
        futures[urit] = futuresesion.get(urit)

    def urim_generator(workinglist):

        while len(workinglist) > 0:
            yield random.choice(workinglist)

    for workinguri in urim_generator(working_list):

        try:
            r = futures[workinguri].result()
        except RequestException:
            pass

        module_logger.debug("HTTP status for {} is {}".format(workinguri, r.status_code))

        if r.status_code == 200:
            endpoint_urims.append(r.url)

        module_logger.debug("removing {} from download list".format(workinguri))
        working_list.remove(workinguri)
        del futures[workinguri]

    return endpoint_urims


def execute_fmfns(cid, session, seed_count):

    first_n_seeds = list_seed_uris(cid, session)[0:seed_count]

    uritlist = generate_archiveit_urits(cid, first_n_seeds)

    candidate_first_urims = fetch_first_urim_of_urits(uritlist, session)
    first_urims = extract_redirect_endpoints(candidate_first_urims, session)
    
    return first_urims
