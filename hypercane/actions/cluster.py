import sys

class HypercaneClusterInputException(Exception):
    pass

def cluster_by_kmeans(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data, \
        get_raw_simhash, get_tf_simhash

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.kmeans import cluster_by_memento_datetime

    parser = argparse.ArgumentParser(
        description="Cluster the input using the dbscan algorithm.",
        prog="hc cluster kmeans"
    )

    parser.add_argument('--feature', dest='feature',
        default='memento-datetime',
        help='The feature in which to cluster the documents.'
    )

    parser.add_argument('-k', dest='k',
        default=28, type=int,
        help='The number of clusters to create.'
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Beginning the clustering of the collection by dbscan...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    k = args.k

    if len(urimdata) < args.k:
        k = len(urimdata)

    if args.feature == 'memento-datetime':
        urimdata = cluster_by_memento_datetime(urimdata, args.cache_storage, k)
    else:
        raise NotImplementedError("Clustering feature of {} not yet supported.".format(args.feature))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Clustering of collection into {} clusters via K-means on feature {} is complete,"
        "output is available in {}".format(args.k, args.feature, args.output_filename))

def cluster_by_dbscan(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data, \
        get_raw_simhash, get_tf_simhash

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.dbscan import cluster_by_simhash_distance, \
        cluster_by_memento_datetime

    parser = argparse.ArgumentParser(
        description="Cluster the input using the dbscan algorithm.",
        prog="hc cluster dbscan"
    )

    parser.add_argument('--feature', dest='feature',
        default='simhash',
        help='The feature in which to cluster the documents.'
    )

    parser.add_argument('--eps', dest='eps',
        default=0.5,
        help='The maximum distance between two samples for one to be considered as in the neighbordhood of the other. See: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html'
    )

    parser.add_argument('--min-samples', dest='min_samples',
        default=5,
        help="The number of samples in a neighbordhood for a point to be considered as a core point. See: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Beginning the clustering of the collection by dbscan...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    if args.feature == "raw-simhash":
        logger.info("Clustering URI-Ms by Raw Simhash")
        urimdata = cluster_by_simhash_distance(
            urimdata, args.cache_storage,
            simhash_function=get_raw_simhash,
            min_samples=int(args.min_samples),
            eps=float(args.eps))

    elif args.feature == "tf-simhash":
        logger.info("Clustering URI-Ms by Term Frequency Simhash")
        urimdata = cluster_by_simhash_distance(
            urimdata, args.cache_storage,
            simhash_function=get_tf_simhash,
            min_samples=int(args.min_samples),
            eps=float(args.eps))

    elif args.feature == "memento-datetime":
        logger.info("Clustering URI-Ms by Memento-Datetime")
        urimdata = cluster_by_memento_datetime(
            urimdata, args.cache_storage,
            min_samples=int(args.min_samples),
            eps=float(args.eps))

    else:
        raise NotImplementedError("Clustering feature of {} not yet supported.".format(args.feature))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Clustering of collection via DBSCAN on feature {} is complete".format(args.feature))


def time_slice(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.time_slice import execute_time_slice

    parser = argparse.ArgumentParser(
        description="Cluster the input into slices based on memento-datetime.",
        prog="hc cluster time-slice"
    )

    parser.add_argument('-k', dest='k',
        default=None, type=int,
        help='The number of clusters to create.'
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Beginning time slicing of collection...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    urimdata_with_slices = execute_time_slice(
        urimdata, args.cache_storage, number_of_slices=args.k)

    # we use urimdata and urimdata_with_slices because they should match, if they don't we will detect an error
    save_resource_data(args.output_filename, urimdata_with_slices, 'mementos', list(urimdata.keys()))

    logger.info("finished time slicing, output is available at {}".format(args.output_filename))

def cluster_by_lda(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.cluster.lda import cluster_with_lda

    parser = argparse.ArgumentParser(
        description="Cluster the input based on LDA topic modeling with gensim.",
        prog="hc cluster lda"
    )

    # TODO: add argument for top scoring cluster (default) or all of them

    parser.add_argument('--num_topics', dest='num_topics',
        default=20, required=False, type=int,
        help='The number of topics to cluster.'
    )

    parser.add_argument('--num_passes', dest='num_passes',
        default=2, required=False, type=int,
        help='The number of passes through the corpus during training. This corresponds to the Gensim LDA setting of the same name. See: https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html'
    )

    parser.add_argument('--num_iterations', dest='num_iterations',
        default=50, required=False, type=int,
        help='The number of iterations through each document during training. This corresponds to the Gensim LDA setting of the same name. See: https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html'
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Beginning LDA clustering of collection...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    urimdata_with_slices = cluster_with_lda(urimdata, args.cache_storage, args.num_topics, args.num_iterations, args.num_passes)

    logger.info(urimdata_with_slices)

    # we use urimdata and urimdata_with_slices because they should match, if they don't we will detect an error
    save_resource_data(args.output_filename, urimdata_with_slices, 'mementos', list(urimdata.keys()))

    logger.info("finished clustering with LDA, output is available at {}".format(args.output_filename))


def print_usage():

    print("""'hc cluster' is used to employ techniques to cluster a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * time-slice - slice the collection into buckets by Memento-Datetime, as in AlNoamany's Algorithm
    * dbscan - cluster the user-supplied feature using the DBSCAN algorithm
    * lda - cluster the collection via LDA topic modeling
    * kmeans - cluster the user-supplied feature using K-means clustering

    Examples:

    hc cluster time-slice -i mementos -a novel-content.tsv -o mdt-slices.tsv -cs mongodb://localhost/cache

    hc cluster dbscan -i mementos -a mdt-slices.tsv -o sliced-and-clustered.tsv --feature tf-simhash -cs mongodb://localhost/cache

    hc cluster lda -i archiveit -a 8778 -o clustered.tsv -cs mongodb://localhost/cache

""")

supported_commands = {
    "time-slice": time_slice,
    "dbscan": cluster_by_dbscan,
    "lda": cluster_by_lda,
    "kmeans": cluster_by_kmeans,
    "k-means": cluster_by_kmeans
}

