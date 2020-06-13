import sys

import hypercane.errors

def get_logger(appname, loglevel, logfile):

    import logging

    logger = logging.getLogger(appname)

    if logfile == sys.stdout:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            level=loglevel)
    else:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            level=loglevel,
            filename=logfile)

    return logger

def calculate_loglevel(verbose=False, quiet=False):

    import logging

    # verbose trumps quiet
    if verbose:
        return logging.DEBUG

    if quiet:
        return logging.WARNING

    return logging.INFO

def generate_default_cache_storage():

    import os
    import json

    config_locations = []

    homedir = os.getenv('HOME')

    config_locations.append( "{}/.hc-config.json".format(homedir))
    config_locations.append( "./.hc-config.json" )
    config_locations.append( "./hc-config.json" )
    config_locations.append( "/etc/hc-config.json" )

    cache_storage = os.getenv('HC_CACHE_STORAGE')

    if cache_storage is not None:

        for config in config_locations:

            if os.path.exists(config):
                with open(config) as f:
                    jdata = json.load(f)
                    cache_storage = jdata['cache_storage']
                    break

    else:

        cache_storage = None

    return cache_storage


def add_default_args(parser):

    from hypercane.version import __useragent__

    parser.add_argument('-l', '--logfile', dest='logfile',
        default=sys.stdout,
        help="The path to a logging file. The log is printed to screen by default.")

    parser.add_argument('-v', '--verbose', dest='verbose',
        action='store_true',
        help="This will raise the logging level to debug for more verbose output")

    parser.add_argument('-q', '--quiet', dest='quiet',
        action='store_true',
        help="This will lower the logging level to only show warnings or errors")

    parser.add_argument('-cs', '--cache-storage', dest='cache_storage',
        default=generate_default_cache_storage(),
        help="The path to the MongoDB database to use as a cache."
    )

    parser.add_argument('-e', '--errorfilename', dest='errorfilename',
        default=None,
        help="The path to filename that records URL processing failures"
    )

    parser.add_argument('--version', action='version',
        version="{}".format(__useragent__))

    return parser

def add_input_args(parser):

    parser.add_argument('-i', '--it', '--input-type',
        help="the input type, one of mementos, timemaps, archiveit, or original-resources",
        dest="input_type", required=True
    )

    parser.add_argument('-a', '-ia', '--input-arguments',
        help="either a file containing a list of URIs, or an Archive-It collection identifier",
        dest='input_arguments', required=False, default=None
    )

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser.add_argument('--crawl-depth', '--depth', required=False, help="the number of levels to use in the crawl", dest='crawl_depth', default=1, type=int)

    return parser

def test_input_args(args):

    import argparse

    input_types_requiring_files = [
        "timemaps",
        "mementos",
        "original-resources"
    ]

    if args.input_type in input_types_requiring_files:
        if args.input_arguments is None:
            raise argparse.ArgumentTypeError(
                "ERROR: input type {} requires a filename containing URIs".format(
                    args.input_arguments))
    elif args.input_type == 'archiveit':
        if args.input_arguments is None:
            raise argparse.ArgumentTypeError(
                "Error: input type archiveit requires an Archive-It collection identifier")

    return args

def process_input_args(args, parser):

    parser = add_input_args(parser)

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    args = test_input_args(args)

    print("args.errorfilename is {}".format(args.errorfilename))
    sys.exit(255)

    if args.errorfilename is not None:
        hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

    return args
