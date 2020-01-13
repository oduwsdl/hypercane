import sys
import os
import argparse
import json

from ..actions import add_input_args, add_default_args, \
    get_logger, calculate_loglevel
from ..identify import extract_uris_from_input
from ..utils import get_web_session
from ..order.dsa1_publication_alg import order_by_dsa1_publication_alg

def process_input_args(args, parser):

    parser = add_input_args(parser)

    # TODO: add clustered-mementos= as an input argument

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def dsa1_publication_alg(args):

    parser = argparse.ArgumentParser(
        description="Remove the near-duplicate documents from a collection.",
        prog="hc reduce remove-near-duplicates"
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting ordering of the documents by the DSA1 publication algorithm...")

    input_type = args.input_type[0]
    input_args = args.input_type[1]

    session = get_web_session(cache_storage=args.cache_storage)

    if input_type == "mementos":
        urims = extract_uris_from_input(input_args)
    else:
        raise NotImplementedError("Input type of {} not yet supported for clustering".format(input_type))

    logger.info("extracted {} mementos from input".format(len(urims)))

    ordered_urims = order_by_dsa1_publication_alg(urims, args.cache_storage)

    logger.info("placed {} mementos in order".format(len(ordered_urims)))

    with open(args.output_filename, 'w') as f:
        for item in ordered_urims:
            urim = item[1]

            f.write("{}\n".format(urim))

    logger.info("Finished ordering documents, output is at {}".format(args.output_filename))

def print_usage():

    print("""'hc order' is used to employ techniques that order the mementos from the input

    Supported commands:
    * dsa1-publication-alg - order the documents according to AlNoamany's Algorithm

    Examples:

    hc order dsa1-publication-alg -i mementos=ranked_mementos.txt -o ordered_mementos.txt
    
""")

supported_commands = {
    "dsa1-publication-alg": dsa1_publication_alg
    # "memento-datetime": memento_datetime,
}

