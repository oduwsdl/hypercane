import logging

module_logger = logging.getLogger("hypercane.actions.cluster")

class HypercaneClusterInputException(Exception):
    pass

def cluster_by_kmeans(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.kmeans import cluster_by_memento_datetime, \
        cluster_by_tfidf

    output_type = 'mementos'

    module_logger.info("Beginning the clustering of the collection by K-means with feature {}...".format(args.feature))

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    k = args.k

    if len(urimdata) < args.k:
        k = len(urimdata)

    if args.feature == 'memento-datetime':
        urimdata = cluster_by_memento_datetime(urimdata, args.cache_storage, k)
    elif args.feature == 'tfidf' or args.feature == 'tf-idf':
        urimdata = cluster_by_tfidf(urimdata, args.cache_storage, k)
    else:
        raise NotImplementedError("Clustering feature of {} not yet supported.".format(args.feature))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Clustering of collection into {} clusters via K-means on feature {} is complete,"
        "output is available in {}".format(args.k, args.feature, args.output_filename))

def cluster_by_dbscan(args):

    from hypercane.utils import get_web_session, save_resource_data, \
        get_raw_simhash, get_tf_simhash

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.dbscan import cluster_by_simhash_distance, \
        cluster_by_memento_datetime, cluster_by_tfidf, cluster_by_lda_vector

    output_type = 'mementos'

    module_logger.info("Beginning the clustering of the collection by dbscan...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    if args.feature == "raw-simhash":
        module_logger.info("Clustering URI-Ms by Raw Simhash")

        if args.eps is None:
            # from https://github.com/yasmina85/DSA-stories/blob/master/src/story_extractor.py
            eps = 0.3
        else:
            eps = float(args.eps)

        if args.min_samples is None:
            # from https://github.com/yasmina85/DSA-stories/blob/master/src/story_extractor.py
            min_samples = 2
        else:
            min_samples = float(args.min_samples)

        module_logger.info("applying eps = {}".format(eps))

        urimdata = cluster_by_simhash_distance(
            urimdata, args.cache_storage,
            simhash_function=get_raw_simhash,
            min_samples=min_samples,
            eps=eps)

    elif args.feature == "tf-simhash":
        module_logger.info("Clustering URI-Ms by Term Frequency Simhash")

        if args.eps is None:
            # from https://doi.org/10.25777/zm0w-gp91
            eps = 0.4
        else:
            eps = float(args.eps)

        if args.min_samples is None:
            # from https://github.com/yasmina85/DSA-stories/blob/master/src/story_extractor.py
            min_samples = 2
        else:
            min_samples = float(args.min_samples)

        module_logger.info("applying eps = {}".format(eps))

        urimdata = cluster_by_simhash_distance(
            urimdata, args.cache_storage,
            simhash_function=get_tf_simhash,
            min_samples=int(args.min_samples),
            eps=eps)

    elif args.feature == "memento-datetime":
        module_logger.info("Clustering URI-Ms by Memento-Datetime")

        urimdata = cluster_by_memento_datetime(
            urimdata, args.cache_storage,
            min_samples=int(args.min_samples),
            eps=args.eps)

    elif args.feature == "tfidf" or args.feature == "tf-idf":
        module_logger.info("Clustering URI-Ms by TF-IDF")

        urimdata = cluster_by_tfidf(
            urimdata, args.cache_storage,
            min_samples=int(args.min_samples),
            eps=args.eps)

    elif args.feature == "topic-vector":
        module_logger.info("Clustering URI-Ms by Topic Vector")

        urimdata = cluster_by_lda_vector(
            urimdata, args.cache_storage,
            min_samples=int(args.min_samples),
            eps=args.eps)

    else:
        raise NotImplementedError("Clustering feature of {} not yet supported.".format(args.feature))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Clustering of collection via DBSCAN on feature {} is complete, output is in {}".format(args.feature, args.output_filename))


def time_slice(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.time_slice import execute_time_slice

    output_type = 'mementos'

    module_logger.info("Beginning time slicing of collection...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    urimdata_with_slices = execute_time_slice(
        urimdata, args.cache_storage, number_of_slices=args.k)

    # we use urimdata and urimdata_with_slices because they should match, if they don't we will detect an error
    save_resource_data(args.output_filename, urimdata_with_slices, 'mementos', list(urimdata.keys()))

    module_logger.info("finished time slicing, output is available at {}".format(args.output_filename))

def cluster_by_lda(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.lda import cluster_with_lda

    output_type = 'mementos'

    module_logger.info("Beginning LDA clustering of collection...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    urimdata_with_slices = cluster_with_lda(urimdata, args.cache_storage, args.num_topics, args.num_iterations, args.num_passes)

    # we use urimdata and urimdata_with_slices because they should match, if they don't we will detect an error
    save_resource_data(args.output_filename, urimdata_with_slices, 'mementos', list(urimdata.keys()))

    module_logger.info("finished clustering with LDA, output is available at {}".format(args.output_filename))

def cluster_by_domain_name(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.domain import cluster_by_domain_name

    output_type = 'mementos'

    module_logger.info("Beginning domain name clustering of collection...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    urimdata_with_clusters = cluster_by_domain_name(urimdata, args.cache_storage)

    # we use urimdata and urimdata_with_clusters because they should match, if they don't we will detect an error
    save_resource_data(args.output_filename, urimdata_with_clusters, 'mementos', list(urimdata.keys()))

    module_logger.info("finished clustering by domain name, output is available at {}".format(args.output_filename))

def cluster_by_urir(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.original_resource import cluster_by_urir

    output_type = 'mementos'

    module_logger.info("Beginning original resource URI clustering of collection...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    urimdata_with_clusters = cluster_by_urir(urimdata, args.cache_storage)

    # we use urimdata and urimdata_with_clusters because they should match, if they don't we will detect an error
    save_resource_data(args.output_filename, urimdata_with_clusters, 'mementos', list(urimdata.keys()))

    module_logger.info("finished clustering by original resource URI, output is available at {}".format(args.output_filename))


