import concurrent.futures
import logging

import numpy as np

from datetime import datetime
from sklearn.cluster import DBSCAN
from distance import hamming

from ..utils import get_raw_simhash, get_memento_http_metadata
from ..reduce.near_duplicates import NearDuplicateException

module_logger = logging.getLogger('hypercane.cluster.dbscan')

def shdist(a, b, **oo):
    return hamming(a, b)

def cluster_by_rawsimhash_distance(urim_clusters, cache_storage):

    output_clusters = {}

    # learn existing cluster assignments
    urim_to_cluster = {}
    clusters_to_urims = {}
    for entry in urim_clusters:
        urim = entry[1]
        cluster = entry[0]
        urim_to_cluster[urim] = cluster
        clusters_to_urims.setdefault(cluster, []).append(urim)

    # compute simhashes
    urim_to_simhash = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        # TODO: allow user to choose tf-simhash rather than raw simhash
        future_to_urim = { executor.submit(get_raw_simhash, urim, cache_storage): urim for urim in urim_to_cluster.keys() }

        for future in concurrent.futures.as_completed(future_to_urim):
            urim = future_to_urim[future]

            try:
                simhash = future.result()
                # simhash is stored as a string in the database, convert to float for clustering
                urim_to_simhash[urim] = float(simhash)

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}]'.format(urim, repr(exc)))
                # module_logger.critical("failed to acquire Simhash for [{}] quitting...".format(urim))
                raise NearDuplicateException("Failed to acquire Simhash for [{}]".format(urim))

    for cluster in clusters_to_urims:

        simhash_list = []

        for urim in clusters_to_urims[cluster]:

            simhash_list.append(urim_to_simhash[urim])

        X = np.matrix(simhash_list)

        db = DBSCAN(eps=0.3, min_samples=2, metric=shdist).fit(X.T)

        for index, label in enumerate(db.labels_):
            urim = clusters_to_urims[cluster][index]
           
            if cluster is None:
                output_clusters[urim] = "{}".format(label)
            else:
                 # preserve original cluster assignment
                output_clusters[urim] = "{}~~~{}".format(cluster, label)
    
    return output_clusters

def cluster_by_memento_datetime(urim_clusters, cache_storage):

    output_clusters = {}

    # learn existing cluster assignments
    urim_to_cluster = {}
    clusters_to_urims = {}
    for entry in urim_clusters:
        urim = entry[1]
        cluster = entry[0]
        urim_to_cluster[urim] = cluster
        clusters_to_urims.setdefault(cluster, []).append(urim)

    # compute simhashes
    urim_to_mementodatetime = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        # TODO: allow user to choose tf-simhash rather than raw simhash
        future_to_urim = { executor.submit(get_memento_http_metadata, urim, cache_storage, metadata_fields=["memento-datetime"]): urim for urim in urim_to_cluster.keys() }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]
            mdt = future.result()[0]
            mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")
            urim_to_mementodatetime[urim] = datetime.timestamp(mdt)

    for cluster in clusters_to_urims:

        mdt_list = []

        for urim in clusters_to_urims[cluster]:

            mdt_list.append(urim_to_mementodatetime[urim])

        X = np.matrix(mdt_list)

        db = DBSCAN(min_samples=2).fit(X.T)

        for index, label in enumerate(db.labels_):
            urim = clusters_to_urims[cluster][index]
            
            if cluster is None:
                output_clusters[urim] = "{}".format(label)
            else:
                # preserve original cluster assignment
                output_clusters[urim] = "{}~~~{}".format(cluster, label)
    
    return output_clusters