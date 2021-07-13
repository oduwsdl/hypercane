import logging

module_logger = logging.getLogger('hypercane.hfilter.by_clusterid')

def exclude_by_cluster_id(urimdata, cluster_id):

    urims_with_cluster_excluded = []

    for urim in urimdata:
        cluster = urimdata[urim]['Cluster']

        if cluster != cluster_id:
            urims_with_cluster_excluded.append(urim)

    return urims_with_cluster_excluded

def include_only_cluster_id(urimdata, cluster_id):

    urims_with_cluster_included = []

    for urim in urimdata:
        cluster = urimdata[urim]['Cluster']

        if cluster == cluster_id:
            urims_with_cluster_included.append(urim)

    return urims_with_cluster_included

