import sys
import os
import argparse
import json
import csv

from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess

from ..identify import list_seed_uris, generate_archiveit_urits, \
    download_urits_and_extract_urims, discover_timemaps_by_input_type, \
    extract_uris_from_input, discover_mementos_by_input_type, \
    discover_original_resources_by_input_type
from ..identify.archivecrawl import crawl_mementos, StorageObject
from ..version import __useragent__
from . import get_logger, calculate_loglevel, \
    add_default_args, process_input_args
from ..utils import get_web_session, process_input_for_cluster_and_rank

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

    urits = discover_timemaps_by_input_type(
        args.input_type, args.input_arguments, 
        args.crawl_depth, session)

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

    urirs = discover_original_resources_by_input_type(
        args.input_type, args.input_arguments,
        args.crawl_depth, session
    )

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

    urimdata = {}

    if args.input_type == 'mementos':
        if os.path.exists(args.input_arguments):
            urimdata = process_input_for_cluster_and_rank(args.input_arguments)
            input_data = list(urimdata.keys())
        else:
            input_data = extract_uris_from_input(args.input_arguments)
            for urim in input_data:
                urimdata[urim] = {}

    else:
        input_data = args.input_arguments
        urimdata = None

    output_urims = discover_mementos_by_input_type(
        args.input_type, input_data,
        args.crawl_depth, session)

    if urimdata is None:
        urimdata = {}
        for urim in output_urims:
            urimdata[urim] = {}

    with open(args.output_filename, 'w') as output:

        fieldnames = ['URI-M']

        for urim in urimdata:
            if len(list(urimdata[urim].keys())) > 0:
                fieldnames.append(list(urimdata[urim].keys()))
            # just do it once
            break

        print("fieldnames: {}".format(fieldnames))

        writer = csv.DictWriter(output, fieldnames=fieldnames)

        writer.writeheader()

        for urim in output_urims:

            row = {}
            row['URI-M'] = urim

            for key in row.keys():
                if key != 'URI-M':
                    if key in urimdata[urim]:
                        row[key] = urimdata[urim][key]
                    else:
                        row[key] = None

            writer.writerow(row)

    logger.info("Done with memento discovery run. Output is in {}".format(args.output_filename))

def print_usage():

    print("""'hc identify' is used discover resource identifiers in a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * timemaps - for discovering the TimeMap URI-Ts
    * mementos - for discovering the memento URI-Ms
    * original-resources - for discovering the original resource URI-Rs

    Examples:
    
    hc identify original-resources -i archiveit=8788 -o seed-output-file.txt

    hc identify timemaps -i archiveit=8788 -o timemap-output-file.txt

    hc identify mementos -i timemaps=http://archive.example.net/timemap/link/http://example.com,http://archive2.example.net/timemap/json/http://example3.com -o timemap-output-file.txt
    
""")

supported_commands = {
    "timemaps": discover_timemaps,
    "mementos": discover_mementos,
    "original-resources": discover_original_resources
}

