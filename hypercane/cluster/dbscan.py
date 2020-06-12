import logging
import traceback
from distance import hamming

from ..utils import get_raw_simhash
from ..errors import errorstore

module_logger = logging.getLogger('hypercane.cluster.dbscan')

def shdist(a, b, **oo):
    return hamming(a, b) / 64

def cluster_by_simhash_distance(urimdata, cache_storage, simhash_function=get_raw_simhash, min_samples=2, eps=0.3):

    import concurrent.futures
    import numpy as np
    from datetime import datetime
    from sklearn.cluster import DBSCAN
    from ..utils import get_memento_http_metadata

    # learn existing cluster assignments
    urim_to_cluster = {}
    clusters_to_urims = {}
    for urim in urimdata:

        try:
            clusters_to_urims.setdefault( urimdata[urim]['Cluster'], [] ).append(urim)
            urim_to_cluster[urim] = urimdata[urim]['Cluster']
        except KeyError:
            clusters_to_urims.setdefault( None, [] ).append(urim)
            urim_to_cluster[urim] = None

    # compute simhashes
    urim_to_simhash = {}

    # module_logger.info("before clustering by Simhash, cluster assignments are: {}".format(clusters_to_urims))

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # module_logger.info("executing threads to acquire simhashes for {} urims".format(len(urim_to_cluster.keys())))

        # TODO: allow user to choose tf-simhash rather than raw simhash
        future_to_urim = { executor.submit(get_raw_simhash, urim, cache_storage): urim for urim in urim_to_cluster.keys() }

        for future in concurrent.futures.as_completed(future_to_urim):
            urim = future_to_urim[future]

            try:
                simhash = future.result()
                module_logger.info("result is {}".format(simhash))
                # simhash is stored as a string in the database, convert to float for clustering
                urim_to_simhash[urim] = float(simhash)

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}]'.format(urim, repr(exc)))
                errorstore.add(urim, traceback.format_exc())

    # module_logger.info("urim_to_simhash: {}".format(urim_to_simhash))

    for cluster in clusters_to_urims:

        simhash_list = []

        for urim in clusters_to_urims[cluster]:
            module_logger.info("examining URI-M {}".format(urim))
            simhash_list.append(urim_to_simhash[urim])

        X = np.matrix(simhash_list)

        db = DBSCAN(eps=eps, min_samples=min_samples, metric=shdist).fit(X.T)

        for index, label in enumerate(db.labels_):

            urim = clusters_to_urims[cluster][index]

            if cluster is None:
                urimdata[urim]['Cluster'] = "{}".format(label)
            else:
                 # preserve original cluster assignment
                urimdata[urim]['Cluster'] = "{}~~~{}".format(cluster, label)

    return urimdata

def cluster_by_memento_datetime(urimdata, cache_storage, min_samples=5, eps=0.5):

    import concurrent.futures
    import traceback
    import numpy as np
    from datetime import datetime
    from sklearn.cluster import DBSCAN
    from ..utils import get_memento_http_metadata

    # Memento-Datetime values are not all Unique, but does it matter?
    # Two URI-Ms with the same Memento-Datetime will be in the same cluster.

    output_clusters = {}

    # learn existing cluster assignments
    urim_to_cluster = {}
    clusters_to_urims = {}
    for urim in urimdata:

        try:
            clusters_to_urims.setdefault( urimdata[urim]['Cluster'], [] ).append(urim)
        except KeyError:
            clusters_to_urims.setdefault( None, [] ).append(urim)

    urim_to_mementodatetime = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_http_metadata, urim, cache_storage, metadata_fields=["memento-datetime"]): urim for urim in urim_to_cluster.keys() }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                mdt = future.result()[0]
                mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")
                urim_to_mementodatetime[urim] = datetime.timestamp(mdt)
            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, exc))
                errorstore.add(urim, traceback.format_exc())


    for cluster in clusters_to_urims:

        mdt_list = []

        for urim in clusters_to_urims[cluster]:

            mdt_list.append(urim_to_mementodatetime[urim])

        X = np.matrix(mdt_list)

        db = DBSCAN(min_samples=min_samples).fit(X.T)

        for index, label in enumerate(db.labels_):
            urim = clusters_to_urims[cluster][index]

            if cluster is None:
                output_clusters[urim] = "{}".format(label)
            else:
                # preserve original cluster assignment
                output_clusters[urim] = "{}~~~{}".format(cluster, label)

    return output_clusters
