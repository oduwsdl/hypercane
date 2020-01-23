import logging
import math
import time

from random import randint
from archivenow import archivenow

module_logger = logging.getLogger('hypercane.sample.storygraph')

def preserve_uris(urirs, session):

    urims = []
    for urir in urirs:
        # TODO: try the Memento aggregator once UKWA fixes itself
        # check for URI-M first and just take it

        module_logger.info("checking if {} exists at Internet Archive".format(urir))
        r = session.get("https://web.archive.org/web/{}".format(urir))
        
        if r.status_code == 200:
            urims.append(r.url)
            continue

        candidate_urim = archivenow.push(urir, "ia")[0]

        if candidate_urim[0:5] == "Error":
            # for now, skip if error
            # TODO: try with other archives, we don't use archive.is because new mementos don't immediately have Memento headers
            # candidate_urim = archivenow.push(urir, "is")[0]
            # if candidate_urim[0:5] == "Error":
            continue

        module_logger.info("adding URI-M {}".format(candidate_urim))
        urims.append(candidate_urim)
        numsecs = randint(3, 20)
        module_logger.info("sleeping {} seconds...".format(numsecs))
        time.sleep(numsecs)

    return urims

def sample_component_from_storygraph(session, rank, storygraph_url, date, hour):
    
    if storygraph_url[-1] == '/':
        storygraph_url = storygraph_url[:-1]

    json_url = "{}/{}/graph{}.json".format(storygraph_url, date, hour)

    module_logger.info("downloading JSON from {}".format(json_url))

    r = session.get(json_url)
    jdata = r.json()

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

    urirs = []

    for i in range(0, len(jdata["nodes"])):
        if i in comp["nodes"]:
            module_logger.info("adding link from node {}".format(i))
            link = jdata["nodes"][i]["link"]
            module_logger.info("adding link {}".format(link))
            urirs.append(link)
    
    module_logger.info("creating mementos of {} URI-Rs".format(len(urirs)))

    urims = preserve_uris(urirs, session)

    return urims

def sample_unconnected_nodes_from_storygraph(session, storygraph_url, date, hour):
    
    if storygraph_url[-1] == '/':
        storygraph_url = storygraph_url[:-1]

    json_url = "{}/{}/graph{}.json".format(storygraph_url, date, hour)

    module_logger.info("downloading JSON from {}".format(json_url))

    r = session.get(json_url)
    jdata = r.json()

    connected_nodes = []

    for comp in jdata["connected-comps"]:
        connected_nodes.extend( comp["nodes"] )

    urirs = []

    for i in range(0, len(jdata["nodes"])):
        if i not in connected_nodes:
            module_logger.info("adding link from node {}".format(i))
            link = jdata["nodes"][i]["link"]
            module_logger.info("adding link {}".format(link))
            urirs.append(link)

    module_logger.info("creating mementos of {} URI-Rs".format(len(urirs)))

    urims = preserve_uris(urirs, session)

    return urims
