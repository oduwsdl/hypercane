import logging
import sys
import os
import argparse
from requests_cache import CachedSession
from requests import Session

from ..version import __useragent__

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

def get_web_session(cachefile=None):
    
    proxies = None

    http_proxy = os.getenv('HTTP_PROXY')
    https_proxy = os.getenv('HTTPS_PROXY')

    if http_proxy is not None and https_proxy is not None:
        proxies = {
            'http': http_proxy,
            'https': https_proxy
        }

    if cachefile is not None:
        # TODO: a cachefile with Redis credentials
        session = CachedSession(cache_name=cachefile, extension='')
    else:
        session = Session()

    session.proxies = proxies
    session.headers.update({'User-Agent': __useragent__})

    return session

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

    parser.add_argument('-cf', '--cachefile', dest='cachefile',
        default='/tmp/hypercane-cache.sqlite',
        help="A SQLite file for use as a cache."
    )

    parser.add_argument('--version', action='version', 
        version="{}".format(__useragent__))

    return parser

def process_collection_input_types(input_argument):

    supported_input_types = [
        "archiveit",
        "timemaps"
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