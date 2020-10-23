import logging

module_logger = logging.getLogger('hypercane.hfilter.largest_cluster')

def return_largest_clusters(urimdata, number_of_clusters):
    
    cluster_assignments = {}

    for urim in urimdata:
        cluster = urimdata[urim]['Cluster']
        cluster_assignments.setdefault(cluster, []).append(urim)

    module_logger.debug("cluster_assignments: {}".format(cluster_assignments))
    module_logger.debug("urimdata: {}".format(urimdata))

    cluster_sizes = []

    for cluster in cluster_assignments:
        cluster_sizes.append( ( len(cluster_assignments[cluster]), cluster ) )

    largest_clusters = sorted(cluster_sizes, reverse=True)[0:number_of_clusters]

    urims_from_largest_clusters = []

    for count, cluster in largest_clusters:
        urims_from_largest_clusters.extend(cluster_assignments[cluster])

    return urims_from_largest_clusters
