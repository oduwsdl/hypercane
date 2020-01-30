import sys

def sample_with_true_random_args(args):

    import argparse

    from hypercane.actions import add_input_args, add_default_args

    parser = argparse.ArgumentParser(
        description="Sample random URLs from a web archive collection. Only Archive-It is supported at this time.",
        prog="hc sample true-random"
        )

    parser = add_input_args(parser)

    parser.add_argument('-k', required=False, help="the number of items to sample", default=28, dest='sample_count')

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def sample_with_true_random(args):
    
    from hypercane.sample.true_random import select_true_random
    from hypercane.actions import get_logger, calculate_loglevel
    from hypercane.utils import get_web_session, save_resource_data
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    args = sample_with_true_random_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting random sampling of URI-Ms.")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("Executing select true random algorithm")
    sampled_urims = select_true_random(list(urimdata.keys()), int(args.sample_count))

    logger.info("Writing sampled URI-Ms out to {}".format(args.output_filename))
    save_resource_data(args.output_filename, urimdata, 'original-resources', sampled_urims)

    logger.info("Done sampling.")

def print_usage():

    print("""hc sample is used execute different algorithms for selecting mementos from a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * true-random - randomly chooses n URI-Ms from the input

    Examples:
    
    hc sample true-random -i archiveit=8788 -o seed-output-file.txt -n 10
    
""")

supported_commands = {
    "true-random": sample_with_true_random
}

