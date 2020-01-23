import argparse
import random

from datetime import datetime

from ..sample.true_random import select_true_random
from ..sample.fmfns import execute_fmfns
from ..sample.storygraph import sample_component_from_storygraph, sample_unconnected_nodes_from_storygraph
from . import get_logger, calculate_loglevel, add_default_args, process_collection_input_types
from ..utils import get_web_session

def sample_with_storygraph_args(args):

    parser = argparse.ArgumentParser(
        description="Sample URLs from Storygraph.",
        prog="hc sample storygraph"
        )
    
    parser.add_argument('--storygraph-url', help="The URL to Storygraph Polar Media Consensus Graph (e.g., http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph)",
        dest='storygraph_url', required=False, default="http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph")

    parser.add_argument('--strongly-connected-rank', help='The rank of the strongly connected component.',
        dest='strongly_connected_rank', required=False, default=1
    )

    parser.add_argument('--disconnected-nodes', help='Choose all unconnected nodes. Will override --strongly-connected-rank if both are specified.',
        dest='disconnected_nodes', required=False, action='store_true'
    )

    parser.add_argument('--date', 
        help='The date to sample from, in YYYY/mm/dd format.',
        dest='date', required=False, default=datetime.now().strftime('%Y/%m/%d')
    )

    parser.add_argument('--hour', 
        help='The hour to sample, from 1 to 24.',
        dest='hour', required=False, default=1
    )

    parser = add_default_args(parser)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    args = parser.parse_args(args)

    return args

def sample_with_storygraph(args):

    args = sample_with_storygraph_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting sampling of Storygraph URI-Rs and converting them to URI-Ms.")

    logger.info("using session {}".format(session))

    if args.disconnected_nodes is True:
        urims = sample_unconnected_nodes_from_storygraph(
            session, args.storygraph_url, args.date, args.hour
            )
    else:
        urims = sample_component_from_storygraph(
            session, args.strongly_connected_rank, args.storygraph_url,
            args.date, args.hour
            )

    with open(args.output_filename, 'w') as f:
        for urim in urims:
            f.write("{}\n".format(urim))

    logger.info("Done with sampling Storygraph URI-Rs and convering them to URI-Ms.")

def sample_with_true_random_args(args):

    parser = argparse.ArgumentParser(
        description="Sample random URLs from a web archive collection. Only Archive-It is supported at this time.",
        prog="hc sample true-random"
        )

    # TODO: add support for an input file of URI-Ms, and an input file of URI-Ts
    parser.add_argument('-i', help="the input type and identifier, only archiveit and a collection ID is supported at this time, example: -i archiveit=8788", dest='input_type', required=True, type=process_collection_input_types)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser.add_argument('-n', required=False, help="the number of items to sample", default=28, dest='sample_count')

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def sample_with_true_random(args):
    
    args = sample_with_true_random_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting random sampling of URI-Ms.")

    collection_type = args.input_type[0]
    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))
    logger.info("Number of mementos to return: {}".format(args.sample_count))

    logger.info("Executing select true random algorithm")
    sampled_urims = select_true_random(collection_id, session, int(args.sample_count))

    logger.info("Writing sampled URI-Ms out to {}".format(args.output_filename))
    with open(args.output_filename, 'w') as output:
        for urim in sampled_urims:
            output.write("{}\n".format(urim))

    logger.info("Done sampling.")

def sample_fmfns_args(args):

    parser = argparse.ArgumentParser(
        description="Sample the first memento of the first n seeds. Only Archive-It is supported at this time.",
        prog="hc sample fmfns"
        )

    # TODO: add support for an input file of URI-Ms, and an input file of URI-Ts
    parser.add_argument('-i', help="the input type and identifier, only archiveit and a collection ID is supported at this time, example: -i archiveit=8788", dest='input_type', required=True, type=process_collection_input_types)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser.add_argument('-n', required=False, help="the number of items to sample", default=28, dest='sample_count')

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def sample_fmfns(args):
    
    args = sample_with_true_random_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting sampling of URI-Ms with FMFNS algorithm.")

    collection_type = args.input_type[0]
    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))
    logger.info("Number of mementos to return: {}".format(args.sample_count))

    logger.info("Executing first memento of first n seeds algorithm")
    sampled_urims = execute_fmfns(collection_id, session, int(args.sample_count))

    logger.info("Writing sampled URI-Ms out to {}".format(args.output_filename))
    with open(args.output_filename, 'w') as output:
        for urim in sampled_urims:
            output.write("{}\n".format(urim))

    logger.info("Done sampling.")

def print_usage():

    print("""hc sample is used execute different algorithms for selecting mementos from a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * true-random - randomly chooses n URI-Ms from the input
    * fmfns - choose the first memento of the first n seeds in the collection, arranged in alphabetical order

    Examples:
    
    hc sample true-random -i archiveit=8788 -o seed-output-file.txt -n 10

    hc sample fmfns -i archiveit=8788 -o timemap-output-file.txt -n 10
    
""")

supported_commands = {
    "true-random": sample_with_true_random,
    "fmfns": sample_fmfns,
    "storygraph": sample_with_storygraph
}

