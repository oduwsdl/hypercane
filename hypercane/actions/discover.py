import sys
import os
import argparse
import logging

from requests import Session

from ..discover import list_seed_uris
from ..version import __appversion__, __useragent__

def get_logger(appname, loglevel, logfile):

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
  
    # verbose trumps quiet
    if verbose:
        return logging.DEBUG

    if quiet:
        return logging.WARNING

    return logging.INFO

def get_web_session():
    
    proxies = None

    http_proxy = os.getenv('HTTP_PROXY')
    https_proxy = os.getenv('HTTPS_PROXY')

    if http_proxy is not None and https_proxy is not None:
        proxies = {
            'http': http_proxy,
            'https': https_proxy
        }

    session = Session()
    session.proxies = proxies

    return session

def process_collection_input_types(input_argument):

    supported_input_types = [
        "archiveit"
    ]

    if '=' not in input_argument:
        raise argparse.ArgumentTypeError(
            "no required argument supplied for input type {}\n\n"
            "Examples:\n"
            "for an Archive-It collection use something like\n"
            "-i archiveit=3639"
            .format(input_argument)
            )

    input_type, argument = input_argument.split('=') 

    if input_type not in supported_input_types:
        raise argparse.ArgumentTypeError(
            "{} is not a supported input type, supported types are {}".format(
                input_type, list(supported_input_types)
                )
            )

    return input_type, argument

def add_default_args(parser):

    parser.add_argument('-l', '--logfile', dest='logfile',
        default=sys.stdout,
        help="The path to a logging file. The log is printed to screen by default.")

    parser.add_argument('-v', '--verbose', dest='verbose',
        action='store_true',
        help="This will raise the logging level to debug for more verbose output")

    parser.add_argument('-q', '--quiet', dest='quiet',
        action='store_true',
        help="This will lower the logging level to only show warnings or errors")

    parser.add_argument('--version', action='version', 
        version=__appversion__)

    return parser

def process_discover_seeds_args(args):
    
    parser = argparse.ArgumentParser(description="Discover the seeds in a web archive collection. Only Archive-It is supported at this time.")

    parser.add_argument('-i', help="the input type and identifier, only archiveit and a collection ID is supported at this time, example: -i archiveit=8788", dest='input_type', required=True, type=process_collection_input_types)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def discover_seeds(args):
    
    args = process_discover_seeds_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session()

    logger.info("Starting seed discovery run.")

    collection_type = args.input_type[0]
    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))

    seeds = list_seed_uris(collection_id, session)

    with open(args.output_filename, 'w') as output:
        for seed in seeds:
            output.write("{}\n".format(seed))

    logger.info("Done with seed discovery run.")

def discover_timemaps(args):

    # parser = argparse.ArgumentParser(description="Discover the TimeMap URI-Ts in a web archive collection. Only Archive-It is supported at this time.")

    # parser.add_argument('-i', help="the input type and identifier, only archiveit and a collection ID is supported at this time, example: -i archiveit=8788", dest='input_type')

    # parser.add_argument('-o', help="the file to which we write output", dest='output_filename')

    # parser = add_default_args(parser)
    pass
    

def discover_seed_mementos(args):
    pass

def discover_original_resources(args):
    pass

def discover_collection_metadata(args):
    pass

def print_usage():

    print("""hc discover is used discover resource identifiers in a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * seeds - for discovering seeds in a web archive collection
    * timemaps - for discovering the TimeMap URI-Ts from a web archive collection
    * seed-mementos - for discovering the seed memento URI-Ms in a web archive collection
    * original-resources - for discovering the original resource URI-Rs in a web archive collection, list of TimeMap URI-Ts, or a directory containing WARCs
    * metadata - for discovering the metadata associated with a web archive collection

    Examples:
    
    hc discover seeds -i archiveit=8788 -o seed-output-file.txt

    hc discover timemaps -i archiveit=8788 -o timemap-output-file.txt

    hc discover metadata -i archiveit=8788 -o collection-8788-metadata.json
    
""")

supported_commands = {
    "seeds": discover_seeds,
    "timemap": discover_timemaps,
    "seed-mementos": discover_seed_mementos,
    "original-resources": discover_original_resources,
    "metadata": discover_collection_metadata
}

