import sys
import os
import argparse
import json

from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess

from ..identify import list_seed_uris, generate_archiveit_urits, \
    download_urits_and_extract_urims, list_seed_mementos, \
    generate_collection_metadata, discover_timemaps_by_input_type, \
    extract_uris_from_input, discover_mementos_by_input_type
from ..identify.archivecrawl import crawl_mementos, StorageObject
from ..version import __useragent__
from . import get_logger, calculate_loglevel, \
    add_default_args, process_collection_input_types, add_input_args
from ..utils import get_web_session

def process_input_args(args, parser):

    parser = add_input_args(parser)

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def discover_timemaps(args):

    parser = argparse.ArgumentParser(
        description="Discover the timemaps in a web archive collection.",
        prog="hc identify timemaps"
        )
    
    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting timemap discovery run.")

    input_type = args.input_type[0]
    input_args = args.input_type[1]

    urits = discover_timemaps_by_input_type(
        input_type, input_args, args.crawl_depth, session)

    with open(args.output_filename, 'w') as output:
        for urit in urits:
            output.write("{}\n".format(urit))

    logger.info("Done with timemap discovery run. Output is in {}".format(
        args.output_filename))

def discover_original_resources(args):

    parser = argparse.ArgumentParser(
        description="Discover the original resources in a web archive collection.",
        prog="hc identify original-resources"
        )
    
    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting original resource discovery run.")

    collection_type = args.input_type[0]
    urirs = []

    if collection_type == "archiveit":
        collection_id = args.input_type[1]
        logger.info("Collection type: {}".format(collection_type))
        logger.info("Collection identifier: {}".format(collection_id))
        seeds = list_seed_uris(collection_id, session)
        urits = generate_archiveit_urits(collection_id, seeds)
        urims = download_urits_and_extract_urims(urits, session)
        link_storage = StorageObject()
        crawl_mementos(link_storage, urims, args.crawl_depth)

        for item in link_storage.storage:
            urirs.append(item[1])

    elif collection_type == "timemaps":
        urits = extract_uris_from_input(args.input_type[1])
        urims = download_urits_and_extract_urims(urits, session)
        link_storage = StorageObject()
        crawl_mementos(link_storage, urims, args.crawl_depth)

        for item in link_storage.storage:
            urirs.append(item[1])

    elif collection_type == "mementos":
        urims = extract_uris_from_input(args.input_type[1])
        link_storage = StorageObject()
        crawl_mementos(link_storage, urims, args.crawl_depth)

        for item in link_storage.storage:
            urirs.append(item[1])
        
    elif collection_type == "original-resources":
        # identity
        urirs = extract_uris_from_input(args.input_type[1])

    elif collection_type == "warcs":
        # TODO: extract from WARC-Target-URI
        raise NotImplementedError("Extracting Original Resources from WARCs is not implemented at this time")

    with open(args.output_filename, 'w') as output:
        for urir in urirs:
            output.write("{}\n".format(urir))

    logger.info("Done with original resource discovery run. Output is in {}".format(args.output_filename))

def discover_mementos(args):

    parser = argparse.ArgumentParser(
        description="Discover the mementos in a web archive collection.",
        prog="hc identify mementos"
        )
    
    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting memento discovery run.")

    input_type = args.input_type[0]
    input_args = args.input_type[1]

    output_urims = discover_mementos_by_input_type(input_type, input_args, args.crawl_depth, session)

    with open(args.output_filename, 'w') as output:
        for urim in output_urims:
            output.write("{}\n".format(urim))

    logger.info("Done with memento discovery run. Output is in {}".format(args.output_filename))

def discover_files(args):

    parser = argparse.ArgumentParser(
        description="Discover the files in a local directory and generate file:// URIs for further processing with other Hypercane actions.",
        prog="hc identify files"
        )

    parser.add_argument('-i', help="a directory structure containing files to be processed", dest='input_dir', required=True)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser.add_argument('--match', help="only find files containing the given string", dest="match", default=None)

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting directory search")

    output_filenames = []

    for directory, subdirectories, filenames in os.walk(args.input_dir):

        for fname in filenames:
            file_url = "file://{}/{}".format(directory, fname)
            if args.match is None:
                output_filenames.append(file_url)
            else:
                if args.match in file_url:
                    output_filenames.append(file_url)

    with open(args.output_filename, 'w') as output:
        for filename in output_filenames:
            output.write("{}\n".format(filename))

    logger.info("Done with directory search")


def print_usage():

    print("""'hc identify' is used discover resource identifiers in a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * timemaps - for discovering the TimeMap URI-Ts
    * mementos - for discovering the memento URI-Ms
    * original-resources - for discovering the original resource URI-Rs
    * files - for discovering files recursively in a directory and constructing file:// URIs for use with other Hypercane actions

    Examples:
    
    hc identify original-resources -i archiveit=8788 -o seed-output-file.txt

    hc identify timemaps -i archiveit=8788 -o timemap-output-file.txt

    hc identify mementos -i timemaps=http://archive.example.net/timemap/link/http://example.com,http://archive2.example.net/timemap/json/http://example3.com -o timemap-output-file.txt
    
""")

supported_commands = {
    "timemaps": discover_timemaps,
    "mementos": discover_mementos,
    "original-resources": discover_original_resources,
    "files": discover_files
}

