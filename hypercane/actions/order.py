import sys

def memento_datetime(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.order.memento_datetime import order_by_memento_datetime

    parser = argparse.ArgumentParser(
        description="Order by memento-datetime.",
        prog="hc order memento_datetime"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting ordering of the documents by the DSA1 publication algorithm...")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.input_type == "mementos":
        # urims = extract_uris_from_input(args.input_arguments)
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for ordering".format(args.input_type))

    logger.info("extracted {} mementos from input".format(len(urimdata.keys())))

    ordered_urims = order_by_memento_datetime(list(urimdata.keys()), args.cache_storage)

    logger.info("placed {} mementos in order".format(len(ordered_urims)))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished ordering documents, output is at {}".format(args.output_filename))



def pubdate_else_memento_datetime(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.order.dsa1_publication_alg import order_by_dsa1_publication_alg

    parser = argparse.ArgumentParser(
        description="Order by publication date first, fall back to memento-datetime.",
        prog="hc order pubdate_else_memento_datetime"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting ordering of the documents by the DSA1 publication algorithm...")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.input_type == "mementos":
        # urims = extract_uris_from_input(args.input_arguments)
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for ordering".format(args.input_type))

    logger.info("extracted {} mementos from input".format(len(urimdata.keys())))

    ordered_urims = order_by_dsa1_publication_alg(list(urimdata.keys()), args.cache_storage)

    logger.info("placed {} mementos in order".format(len(ordered_urims)))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished ordering documents, output is at {}".format(args.output_filename))

def score_sort(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import save_resource_data, get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.order.score import order_by_score

    parser = argparse.ArgumentParser(
        description="Order by publication date first, fall back to memento-datetime.",
        prog="hc order pubdate_else_memento_datetime"
    )

    parser.add_argument('--descending', help="If specified, sort such that highest scoring URI-Ms are first.",
        action='store_true', default=False, dest='descending'
    )

    parser.add_argument('--scoring-field', help="Specify the scoring field to sort by, default is first encountered",
        default=None, dest='scoring_field'
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting ordering of the documents by their scores...")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.input_type == "mementos":
        # urims = extract_uris_from_input(args.input_arguments)
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for ordering".format(args.input_type))

    if args.scoring_field is None:
        scoring_fields = list(urimdata[list(urimdata.keys())[0]].keys())
        scoring_field = scoring_fields[0]
    else:
        scoring_field = args.scoring_field

    logger.info("ordering by field {}".format(scoring_field))

    logger.info("extracted {} mementos from input".format(len(urimdata.keys())))

    ordered_urims = order_by_score(urimdata, args.descending, scoring_field)

    logger.info("placed {} mementos in order".format(len(ordered_urims)))

    save_resource_data(args.output_filename, urimdata, 'mementos', ordered_urims)

    logger.info("Finished ordering documents by score, output is at {}".format(args.output_filename))

def print_usage():

    print("""'hc order' is used to employ techniques that order the mementos from the input

    Supported commands:
    * pubdate-else-memento-datetime - order the documents according to AlNoamany's Algorithm
    * memento-datetime - order the documents by memento-datetime
    * score - order the documents by score, use --descending to sort by highest first

    Examples:

    hc order pubdate-else-memento-datetime -i mementos -a scored_mementos.tsv -o ordered_mementos.tsv -cs mongodb://localhost/cache

""")

supported_commands = {
    "pubdate-else-memento-datetime": pubdate_else_memento_datetime,
    "memento-datetime": memento_datetime,
    "score": score_sort
}

