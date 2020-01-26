import sys
import os
import argparse
import json

from ..actions import add_input_args, add_default_args, \
    get_logger, calculate_loglevel, process_input_args
from ..identify import extract_uris_from_input
from ..utils import get_web_session
from ..order.dsa1_publication_alg import order_by_dsa1_publication_alg

def pubdate_else_memento_datetime(args):

    parser = argparse.ArgumentParser(
        description="Remove the near-duplicate documents from a collection.",
        prog="hc order pubdate_else_memento_datetime"
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting ordering of the documents by the DSA1 publication algorithm...")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.input_type == "mementos":
        urims = extract_uris_from_input(args.input_arguments)
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for clustering".format(args.input_type))

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
    "pubdate_else_memento_datetime": pubdate_else_memento_datetime
    # "memento-datetime": memento_datetime,
}

