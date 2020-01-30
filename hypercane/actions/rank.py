import sys
import os
import argparse
import json

from ..actions import add_input_args, add_default_args, get_logger, \
    calculate_loglevel, process_input_args
from ..identify import extract_uris_from_input, \
    discover_resource_data_by_input_type, discover_mementos_by_input_type
from ..rank.dsa1_ranking import rank_by_dsa1_score
from ..utils import get_web_session, save_resource_data

def dsa1_ranking(args):

    parser = argparse.ArgumentParser(
        description="Rank the input using the DSA1 scoring equation.",
        prog="hc rank dsa1-ranking"
    )

    parser.add_argument('--memento-damage-url', dest='memento_damage_url',
        default=None,
        help="The URL of the Memento-Damage service to use for ranking."
    )

    parser.add_argument('--damage-weight', dest='damage_weight',
        default=-0.40,
        help="The weight for the Memento-Damage score in the ranking."
    )

    parser.add_argument('--category-weight', dest='category_weight',
        default=0.15,
        help="The weight for the URI-R category score in the ranking."
    )

    parser.add_argument('--path-depth-weight', dest='path_depth_weight',
        default=0.45,
        help="The weight for the URI-R path depth score in the ranking."
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the ranking by DSA1 scoring equation")

    if args.input_type == "mementos":
        urimdata = discover_resource_data_by_input_type(
            args.input_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for ranking".format(
            args.input_type))

    urimdata = rank_by_dsa1_score(
        urimdata, session,
        memento_damage_url=args.memento_damage_url,
        damage_weight=args.damage_weight,
        category_weight=args.category_weight,
        path_depth_weight=args.path_depth_weight
        )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished ranking by DSA1 scoring equation, output is at {}".format(args.output_filename))


def print_usage():

    print("""'hc rank' is used to employ techniques that rank the mementos in a web archive collection

    Supported commands:
    * dsa1-ranking - rank the documents according to the scoring function of AlNoamany's Algorithm

    Examples:

    hc rank dsa1-ranking -i mementos=input_mementos.txt -o ranked_mementos.txt 
    
""")

supported_commands = {
    "dsa1-ranking": dsa1_ranking
}

