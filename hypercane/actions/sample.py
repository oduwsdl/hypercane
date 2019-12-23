import argparse
import random

from ..discover import list_seed_mementos
from . import get_logger, calculate_loglevel, get_web_session, add_default_args, process_collection_input_types

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

    session = get_web_session(cachefile=args.cachefile)

    logger.info("Starting random sampling of URI-Ms.")

    collection_type = args.input_type[0]
    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))

    urims = list_seed_mementos(collection_id, session)
    sampled_urims = random.choices(urims, k=args.sample_count)

    with open(args.output_filename, 'w') as output:
        for urim in sampled_urims:
            output.write("{}\n".format(urim))

supported_commands = {
    "true-random": sample_with_true_random
}

