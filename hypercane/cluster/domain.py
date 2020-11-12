import logging
import hypercane.errors

module_logger = logging.getLogger("hypercane.cluster.domain")

def cluster_by_domain_name(urimdata, cache_storage):

    from ..utils import get_memento_http_metadata
    import concurrent.futures
    import traceback
    from urllib.parse import urlparse

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
    
    module_logger.info("stored existing clusters for {} URI-Ms".format(len(urim_to_cluster)))

    urims = list(urimdata.keys())

    urir_to_urims = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_http_metadata, urim, cache_storage, metadata_fields=['original']): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            try:
                urim = future_to_urim[future]
                module_logger.info("extracting result from future for {}".format(urim))
                urir = future.result()[0]

                o = urlparse(urir)

                urir_to_urims.setdefault(o.netloc, []).append(urim)


            except Exception as exc:
                module_logger.exception("Error: {}, Failed to determine memento-datetime for {}, skipping...".format(repr(exc), urim))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    module_logger.info("learned {} URI-Rs from these URI-Ms".format(len(urir_to_urims)))

    clusterid = 0
    urim_to_newcluster = {}

    for urir in urir_to_urims:

        for urim in urir_to_urims[urir]:
            urim_to_newcluster[urim] = clusterid

        clusterid += 1

    module_logger.info("applied cluster assignments to {} URI-Ms based on URI-R".format(len(urim_to_newcluster)))

    for urim in urim_to_newcluster:

        existing_cluster = urim_to_cluster[urim]
        new_cluster = urim_to_newcluster[urim]

        if existing_cluster is None:
            urimdata[urim]['Cluster'] = "{}".format(new_cluster)
        else:
            urimdata[urim]['Cluster'] = "{}~~~{}".format(existing_cluster, new_cluster)

    module_logger.info("new clusters should be assigned to {} URI-Ms".format(len(urimdata)))

    return urimdata
