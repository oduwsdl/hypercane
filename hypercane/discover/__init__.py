import multiprocessing
import random

from copy import deepcopy
from aiu import ArchiveItCollection, convert_LinkTimeMap_to_dict
from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException

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