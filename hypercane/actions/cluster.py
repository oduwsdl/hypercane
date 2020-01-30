import sys
import os
import argparse
import json
import concurrent.futures
import math

from datetime import datetime

from ..actions import add_input_args, add_default_args, get_logger, \
    calculate_loglevel, process_input_args
from ..identify import discover_timemaps_by_input_type, \
    discover_mementos_by_input_type, download_urits_and_extract_urims, \
    extract_uris_from_input, discover_resource_data_by_input_type
from ..utils import get_web_session, get_memento_http_metadata, \
    get_raw_simhash, get_tf_simhash, save_resource_data
from ..cluster.time_slice import execute_time_slice
from ..cluster.dbscan import cluster_by_simhash_distance, cluster_by_memento_datetime

class HypercaneClusterInputException(Exception):
    pass

def cluster_by_dbscan(args):

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

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Beginning the clustering of the collection")

    session = get_web_session(cache_storage=args.cache_storage)

    # TODO: Note that we do not support crawling for clustering, why not?
    # look at https://stackoverflow.com/questions/32807319/disable-remove-argument-in-argparse for how to remove arguments
    if args.input_type == "mementos":
        urimdata = discover_resource_data_by_input_type(
            args.input_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )

    else:
        raise NotImplementedError("Input type of {} not yet supported for clustering".format(args.input_type))

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
            simhash_function=get_raw_simhash, 
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
    
    parser = argparse.ArgumentParser(
        description="Cluster the input into slices based on memento-datetime.",
        prog="hc cluster time-slice"
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("beginning time slicing of collection")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.input_type == "mementos":
        urimdata = discover_resource_data_by_input_type(
            args.input_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )

    else:
        raise NotImplementedError("Input type of {} not yet supported for clustering".format(args.input_type))

    cache_storage = args.cache_storage

    logger.info("There were {} mementos discovered in the input".format(len(urimdata)))

    slices = execute_time_slice(urimdata, cache_storage)

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("finished time slicing, output is available at {}".format(args.output_filename))

def print_usage():

    print("""'hc cluster' is used to employ techniques to cluster a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * time-slice - slice the collection into buckets by Memento-Datetime, as in AlNoamany's Algorithm
    * dbscan - cluster the user-supplied feature using the DBSCAN algorithm

    Examples:
    
    hc cluster time-slice -i mementos=novel-content.txt -o mdt-slices.json 

    hc cluster dbscan features=tf-simhash -i clustered-mementos=mdt-slices.json -o sliced-and-clustered.json
    
""")

supported_commands = {
    "time-slice": time_slice,
    "dbscan": cluster_by_dbscan
}

