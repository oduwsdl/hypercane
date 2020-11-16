import logging
import traceback
import concurrent.futures
from datetime import datetime
import hypercane.errors

module_logger = logging.getLogger('hypercane.cluster.kmeans')

def cluster_by_memento_datetime(urimdata, cache_storage, k):

    # Memento-Datetime values are not all Unique, but does it matter?
    # Two URI-Ms with the same Memento-Datetime will be in the same cluster.

    from sklearn.cluster import KMeans
    import numpy as np
    from hypercane.utils import get_memento_http_metadata

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
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    km = KMeans(n_clusters=k)

    for cluster in clusters_to_urims:

        mdt_list = []

        for urim in clusters_to_urims[cluster]:
            module_logger.info("examining URI-M {}".format(urim))
            mdt_list.append(urim_to_mementodatetime[urim])

        X = np.matrix(mdt_list)

        try:
            db = km.fit(X.T)
        except ValueError as e:
            module_logger.exception("Issue with fitting cluster, assigning all to same cluster")
            label = 99999 # something obscenely high that we hopefully will never hit

            for urim in clusters_to_urims[cluster]:
                if cluster is None:
                    urimdata[urim]['Cluster'] = "{}".format(label)
                else:
                    # preserve original cluster assignment
                    urimdata[urim]['Cluster'] = "{}~~~{}".format(cluster, label)

            continue

        for index, label in enumerate(db.labels_):

            urim = clusters_to_urims[cluster][index]

            if cluster is None:
                urimdata[urim]['Cluster'] = "{}".format(label)
            else:
                 # preserve original cluster assignment
                urimdata[urim]['Cluster'] = "{}~~~{}".format(cluster, label)


    return urimdata
