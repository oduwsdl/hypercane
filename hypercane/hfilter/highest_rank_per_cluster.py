
def return_highest_ranking_memento_per_cluster(urimdata, rankkey):

    cluster_assignments = {}
    highest_rank_per_cluster = []

    for urim in urimdata:
        cluster = urimdata[urim]['Cluster']
        cluster_assignments.setdefault(cluster, []).append(urim)

    for cluster in cluster_assignments:

        cluster_ranks = []

        for urim in cluster:
            cluster_ranks.append( (urimdata[urim][rankkey], urim) )

        highest_rank_per_cluster.append( max(cluster_ranks)[1] )

    return highest_rank_per_cluster