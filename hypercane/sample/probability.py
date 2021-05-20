import random

def select_true_random(urims, sample_count):

    if len(urims) <= sample_count:
        return urims
    else:
        # sampled_urims = random.choices(urims, k=int(sample_count))
        sampled_urims = random.sample(urims, k=int(sample_count))

    return sampled_urims

def select_systematically(urims, iteration):

    icounter = 1

    sampled_urims = []

    for urim in urims:

        if icounter == iteration:
            sampled_urims.append(urim)
            icounter = 0

        icounter += 1

    return sampled_urims

def select_random_per_cluster(memento_clusters, sample_count):

    sampled_urims = []

    for cluster in memento_clusters:

        sampled_urims.extend( select_true_random( memento_clusters[cluster], sample_count ) )

    return sampled_urims

def select_systematic_per_cluster(memento_clusters, iteration):

    sampled_urims = []

    for cluster in memento_clusters:

        sampled_urims.extend( select_systematically( memento_clusters[cluster], iteration) )

    return sampled_urims

def select_random_clusters(memento_clusters, cluster_count):

    sampled_urims = []

    sampled_clusters = random.sample( list(memento_clusters.keys()), cluster_count )

    for cluster in sampled_clusters:

        sampled_urims.extend( memento_clusters[cluster] )

    return sampled_urims

def select_by_random_oversampling(memento_clusters):

    sampled_urims = []

    largest_cluster_size = 0
    largest_cluster = None

    for cluster in memento_clusters:

        if len(memento_clusters[cluster]) > largest_cluster_size:
            largest_cluster = cluster
            largest_cluster_size = len(memento_clusters[cluster])

    sampled_urims.extend( memento_clusters[largest_cluster] )

    for cluster in memento_clusters:

        if cluster == largest_cluster:
            continue

        cluster_sample = []
        cluster_sample.extend( memento_clusters[cluster] )

        while len(cluster_sample) < largest_cluster_size:

            cluster_size_diff = largest_cluster_size - len(cluster_sample)
            sample_extension = select_true_random(memento_clusters[cluster], cluster_size_diff)
            cluster_sample.extend( sample_extension )

        sampled_urims.extend(cluster_sample)

    return sampled_urims
        
def select_by_random_undersamping(memento_clusters):

    import math

    sampled_urims = []

    smallest_cluster_size = math.inf
    smallest_cluster = None

    for cluster in memento_clusters:

        if len(memento_clusters[cluster]) < smallest_cluster_size:
            smallest_cluster = cluster
            smallest_cluster_size = len(memento_clusters[cluster])

    sampled_urims.extend( memento_clusters[smallest_cluster] )

    for cluster in memento_clusters:

        if cluster == smallest_cluster:
            continue

        cluster_sample = []

        while len(cluster_sample) < smallest_cluster_size:

            cluster_size_diff = smallest_cluster_size - len(cluster_sample)
            sample_extension = select_true_random(memento_clusters[cluster], cluster_size_diff)
            cluster_sample.extend( sample_extension )

        sampled_urims.extend(cluster_sample)

    return sampled_urims

