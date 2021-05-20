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
