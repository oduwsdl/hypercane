import logging

module_logger = logging.getLogger('hypercane.report.seedstats')

def calculate_domain_diversity(uri_list):
    
    import tldextract

    domains = []

    for uri in uri_list:

        ext = tldextract.extract(uri)
        domains.append( ext.registered_domain )

    u = len(set(domains))
    n = len(domains)

    module_logger.info("discovered {} unique domains".format(u))

    module_logger.info("size of collection: {}".format(n))

    if n == 1:
        return 1

    return (u - 1) / (n - 1)

def path_depth(uri):

    from urllib.parse import urlparse

    o = urlparse(uri)

    score = len( [ i for i in o.path.split('/') if i != '' ] )

    if o.query != '':
        score += 1

    return score

def calculate_path_depth_diversity(uri_list):

    depths = []

    for uri in uri_list:

        depth = path_depth(uri)
        depths.append( depth )

    u = len(set(depths))
    n = len(depths)

    module_logger.info("discovered {} unique depths".format(u))

    module_logger.info("size of collection: {}".format(n))

    if n == 1:
        return 1

    return (u - 1) / (n - 1)

def most_frequent_seed_uri_path_depth(uri_list):

    from statistics import mode, StatisticsError

    depths = []

    for uri in uri_list:

        depth = path_depth(uri)
        depths.append( depth )

    try:
        mf = mode(depths)
    except StatisticsError:

        depthcount = []

        for i in depths:
            depthcount.append( (depths.count(i), i) )

        depthcount.sort(reverse=True)

        mf = depthcount[0][1]

    return mf

def calculate_top_level_path_percentage(uri_list):
    
    depths = []

    for uri in uri_list:

        depth = path_depth(uri)
        depths.append( depth )

    return depths.count(0) / len(depths)

def calculate_percentage_querystring(uri_list):

    from urllib.parse import urlparse

    qscore = 0

    for uri in uri_list:
        o = urlparse(uri)

        if o.query != '':
            qscore += 1

    return qscore / len(uri_list)
