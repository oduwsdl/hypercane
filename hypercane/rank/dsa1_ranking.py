import re
import requests.exceptions
import json
import logging

from urllib.parse import urlparse

module_logger = logging.getLogger('hypercane.rank.dsa1_ranking')

# Borrowed from: https://github.com/yasmina85/DSA-stories/blob/181d2453a7931bbbe8b56d46575a4d8491d736c2/src/memento_picker.py#L13
# Credit goes to Yasmin AlNoamany
def get_memento_uri_category(memento_uri):
    base_ait_idx_end = memento_uri.find('http',10)
    original_uri = memento_uri[ base_ait_idx_end:]
    
    o = urlparse(original_uri)
    hostname = o.hostname
    if hostname == None:
        return -1  
    if  bool(re.search('.*twitter.*', hostname)) or bool(re.search('.*t.co.*', hostname)) or \
        bool(re.search('.*redd.it.*', hostname)) or bool(re.search('.*twitter.*', hostname)) or \
        bool(re.search('.*facebook.*', hostname)) or bool(re.search('.*fb.me.*', hostname)) or \
        bool(re.search('.*plus.google.*', hostname))  or   bool(re.search('.*wiki.*', hostname)) or \
        bool(re.search('.*globalvoicesonline.*', hostname))  or  bool(re.search('.*fbcdn.*', hostname)):
        return 0.5
    elif  bool(re.search('.*cnn.*', hostname)) or  bool(re.search('.*bbc.*', hostname)) or \
        bool(re.search('news', hostname)) or  bool(re.search('.*news.*', hostname)) or  \
        bool(re.search('.*rosaonline.*', hostname))or  bool(re.search('.*aljazeera.*', hostname)) or  \
        bool(re.search('.*guardian.*', hostname)) or  bool(re.search('.*USATODAY.*', hostname)) or  \
        bool(re.search('.*nytimes.*', hostname))or  bool(re.search('.*abc.*', hostname))or  \
        bool(re.search('.*foxnews.*', hostname)) or  bool(re.search('.*allvoices.*', hostname)) or \
        bool(re.search('.*huffingtonpost.*', hostname)) :
        return 0.7 
    elif  bool(re.search('.*dailymotion.*', hostname)) or  \
        bool(re.search('.*youtube.*', hostname)) or \
        bool(re.search('.*youtu.be.*', hostname)): 
        return 0.7
    elif bool(re.search('.*wordpress.*', hostname)) or  bool(re.search('.*blog.*', hostname)):
        return 0.4
    elif  bool(re.search('.*flickr.*', hostname)) or bool(re.search('.*flic.kr.*', hostname)) or  \
        bool(re.search('.*instagram.*', hostname)) or  bool(re.search('.*twitpic.*', hostname)):
        return 0.6
    else:
        return 0

# Borrowed from https://github.com/yasmina85/DSA-stories/blob/181d2453a7931bbbe8b56d46575a4d8491d736c2/src/memento_picker.py#L5
# Credit goes to Yasmin AlNoamany
def get_memento_depth(mem_uri):
    if mem_uri.endswith('/'):
        mem_uri = mem_uri[0:-1]
    original_uri_idx = mem_uri.find('http',10)
    original_uri = mem_uri[original_uri_idx+7:-1]
    level = original_uri.count('/')
    return level/10.0

def get_memento_damage(memento_uri, memento_damage_url, session):
    if memento_damage_url == None:
        return 0

    if memento_damage_url.endswith('/'):
        api_endpoint = "{}api/damage/{}".format(
            memento_damage_url, memento_uri)
    else:
        api_endpoint = "{}/api/damage/{}".format(
            memento_damage_url, memento_uri)

    try:
        r = session.get(api_endpoint)
    except requests.exceptions.RequestException:
        module_logger.warning("Failed to download Memento Damage data for URI-M {} "
            "using endpoint {}".format(memento_uri, api_endpoint))
        return 0

    try:
        damagedata = r.json()
    except json.decoder.JSONDecodeError:
        module_logger.warning("Failed to extract Memento Damage data for URI-M {} "
            "using endpoint {}".format(memento_uri, api_endpoint))
        return 0

    if 'total_damage' in damagedata:
        return damagedata['total_damage']
    else:
        return 0

def rank_by_dsa1_score(urim_clusters, session, memento_damage_url=None, damage_weight=-0.40, category_weight=0.15, path_depth_weight=0.45):

    urim_to_cluster = {}
    clusters_to_urims = {}

    for entry in urim_clusters:
        urim = entry[1]
        cluster = entry[0]

        urim_to_cluster[urim] = cluster
        clusters_to_urims.setdefault(cluster, []).append(urim)

    urim_to_score = {}

    for cluster in clusters_to_urims:

        for urim in clusters_to_urims[cluster]:

            category_score = get_memento_uri_category(urim)
            path_depth_score = get_memento_depth(urim)
            damage_score = get_memento_damage(urim, memento_damage_url, session)

            score = ( 1 -  damage_weight * damage_score ) + \
                ( path_depth_weight * path_depth_score ) + \
                ( category_weight * category_score )

            urim_to_score[urim] = score

    outptut_data = []

    for urim in urim_to_score:
        outptut_data.append(
            (
                urim,
                urim_to_cluster[urim],
                urim_to_score[urim]
            )
        )

    return outptut_data