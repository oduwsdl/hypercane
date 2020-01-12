import sys
import os
import argparse
import json
import concurrent.futures
import math

from datetime import datetime

from ..actions import add_input_args, add_default_args, get_logger, calculate_loglevel
from ..identify import discover_timemaps_by_input_type, \
    discover_mementos_by_input_type, download_urits_and_extract_urims
from ..utils import get_web_session, get_memento_http_metadata
from ..cluster.time_slice import execute_time_slice

def process_input_args(args, parser):

    parser = add_input_args(parser)

    # TODO: add clustered-mementos= as an input argument

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def time_slice(args):
    
    parser = argparse.ArgumentParser(
        description="Only keep documents from a collection with a specific language.",
        prog="hc cluster time-slice"
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("beginning time slicing of collection")

    input_type = args.input_type[0]
    input_args = args.input_type[1]

    session = get_web_session(cache_storage=args.cache_storage)

    urims = discover_mementos_by_input_type(
        input_type, input_args, args.crawl_depth, session
    )

    cache_storage = args.cache_storage

    logger.info("There were {} mementos discovered in the input".format(len(urims)))

    slices = execute_time_slice(urims, cache_storage)

    with open(args.output_filename, 'w') as f:

        for i in range(0, len(slices)):

            for urim in slices[i]:
                f.write("{}\t{}\n".format(urim, i))

    logger.info("finished time slicing, output is available at {}".format(args.output_filename))

def dbscan(args):
    raise NotImplementedError("DBSCAN Clustering Not Implementing Yet")

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
    "dbscan": dbscan
}

