import sys
import argparse

from datetime import datetime

def discover_timemaps(args):

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_timemaps_by_input_type

    parser = argparse.ArgumentParser(
        description="Discover the timemaps in a web archive collection.",
        prog="hc identify timemaps"
        )

    args = process_input_args(args, parser)
    output_type = 'timemaps'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting timemap discovery run.")
    logger.info("Using {} for cache storage".format(args.cache_storage))

    uritdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_timemaps_by_input_type
    )

    save_resource_data(args.output_filename, uritdata, 'timemaps', list(uritdata.keys()))

    logger.info("Done with timemap discovery run. Output is in {}".format(
        args.output_filename))

def discover_original_resources(args):

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_original_resources_by_input_type

    parser = argparse.ArgumentParser(
        description="Discover the original resources in a web archive collection.",
        prog="hc identify original-resources"
        )

    args = process_input_args(args, parser)
    output_type = 'original-resources'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting original resource discovery run.")
    logger.info("Using {} for cache storage".format(args.cache_storage))

    urirdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_original_resources_by_input_type
    )

    save_resource_data(args.output_filename, urirdata, 'original-resources', list(urirdata.keys()))

    logger.info("Done with original resource discovery run. Output is in {}".format(args.output_filename))

def discover_mementos(args):

    from hypercane.actions import process_input_args, get_logger, \
            calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    parser = argparse.ArgumentParser(
        description="Discover the mementos in a web archive collection.",
        prog="hc identify mementos"
        )

    parser.add_argument('--accept-datetime', '--desired-datetime',
        default=None, required=False, dest='accept_datetime',
        help='(only for original resource input type)\n'
        'discover mementos closest to this datetime in YYYY-mm-ddTHH:MM:SS format',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
    )

    parser.add_argument('--timegates',
        default=[
            "https://timetravel.mementoweb.org/timegate/",
            "https://web.archive.org/web/"
        ], required=False, dest='timegates',
        help='(only for original resource input type)\n'
        'use the given TimeGate endpoints to discover mementos',
        type=lambda s: [i.strip() for i in s.split(',')]
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting memento discovery run.")

    logger.info("Using {} for cache storage".format(args.cache_storage))

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type,
        accept_datetime=args.accept_datetime,
        timegates=args.timegates
    )

    logger.info("discovered {} mementos, preparing to write the list to {}".format(
        len(urimdata), args.output_filename))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Done with memento discovery run. Output is in {}".format(args.output_filename))

def print_usage():

    print("""'hc identify' is used discover resource identifiers in a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * timemaps - for discovering the TimeMap URI-Ts
    * mementos - for discovering the memento URI-Ms
    * original-resources - for discovering the original resource URI-Rs

    Examples:

    hc identify original-resources -i archiveit -a 8788 -o seed-output-file.tsv -cs mongodb://localhost/cache

    hc identify timemaps -i archiveit -a 8788 -o timemap-output-file.tsv -cs mongodb://localhost/cache

    hc identify mementos -i timemaps -a timemap-input-file.tsv -o mementos.tsv -cs mongodb://localhost/cache

""")

supported_commands = {
    "timemaps": discover_timemaps,
    "mementos": discover_mementos,
    "original-resources": discover_original_resources
}

