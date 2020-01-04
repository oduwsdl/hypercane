import sys
import os
import argparse
import json

from ..identify import list_seed_uris, generate_archiveit_urits, download_urits_and_extract_urims, list_seed_mementos, generate_collection_metadata
from ..version import __useragent__
from . import get_logger, calculate_loglevel, get_web_session, add_default_args, process_collection_input_types

def process_discover_seeds_args(args):
    
    parser = argparse.ArgumentParser(
        description="Discover the seeds in a web archive collection. Only Archive-It is supported at this time.",
        prog="hc discover seeds"
        )

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

    session = get_web_session(cachefile=args.cachefile)

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

def process_discover_timemaps_args(args):
    
    parser = argparse.ArgumentParser(
        description="Discover the timemaps in a web archive collection. Only Archive-It is supported at this time.",
        prog="hc discover timemaps"
        )

    parser.add_argument('-i', help="the input type and identifier, only archiveit and a collection ID is supported at this time, example: -i archiveit=8788", dest='input_type', required=True, type=process_collection_input_types)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def discover_timemaps(args):

    args = process_discover_timemaps_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cachefile=args.cachefile)

    logger.info("Starting timemap discovery run.")

    collection_type = args.input_type[0]
    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))

    seeds = list_seed_uris(collection_id, session)
    urits = generate_archiveit_urits(collection_id, seeds)

    with open(args.output_filename, 'w') as output:
        for urit in urits:
            output.write("{}\n".format(urit))

    logger.info("Done with timemap discovery run.")

def process_discover_seed_mementos_args(args):
    
    parser = argparse.ArgumentParser(
        description="Discover the seed mementos in a web archive collection. Only Archive-It is supported at this time.",
        prog="hc discover timemaps"
        )

    parser.add_argument('-i', help="the input type and identifier, only archiveit and a collection ID is supported at this time, example: -i archiveit=8788", dest='input_type', required=True, type=process_collection_input_types)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args    

def discover_seed_mementos(args):
    
    args = process_discover_seed_mementos_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cachefile=args.cachefile)

    logger.info("Starting seed memento discovery run.")

    collection_type = args.input_type[0]
    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))

    urims = list_seed_mementos(collection_id, session)

    with open(args.output_filename, 'w') as output:
        for urim in urims:
            output.write("{}\n".format(urim))

    logger.info("Done with seed memento discovery run.")

def process_discover_original_resources_args(args):
    
    parser = argparse.ArgumentParser(
        description="Discover the original resources in a web archive collection. Only Archive-It is supported at this time.",
        prog="hc discover seeds"
        )

    parser.add_argument('-i', help="the input type and identifier, only archiveit and a collection ID is supported at this time, example: -i archiveit=8788", dest='input_type', required=True, type=process_collection_input_types)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def discover_original_resources(args):

    args = process_discover_original_resources_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cachefile=args.cachefile)

    logger.info("Starting original resources discovery run.")

    collection_type = args.input_type[0]
    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))

    seeds = list_seed_uris(collection_id, session)

    with open(args.output_filename, 'w') as output:
        for seed in seeds:
            output.write("{}\n".format(seed))

    logger.info("Done with seed discovery run.")   


def process_discover_collection_metadata_args(args):

    parser = argparse.ArgumentParser(
        description="Discover the collection metadata in a web archive collection. Only Archive-It is supported at this time.",
        prog="hc discover timemaps"
        )

    parser.add_argument('-i', help="the input type and identifier, only archiveit and a collection ID is supported at this time, example: -i archiveit=8788", dest='input_type', required=True, type=process_collection_input_types)

    parser.add_argument('-o', required=True, help="the file to which we write output", dest='output_filename')

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args  

def discover_collection_metadata(args):
    
    args = process_discover_collection_metadata_args(args)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cachefile=args.cachefile)

    logger.info("Starting collection metadata discovery run.")

    collection_type = args.input_type[0]
    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))

    metadata = generate_collection_metadata(collection_id, session)

    with open(args.output_filename, 'w') as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    logger.info("Done with collection metadata discovery run.")

def print_usage():

    print("""'hc discover' is used discover resource identifiers in a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

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
    "timemaps": discover_timemaps,
    "seed-mementos": discover_seed_mementos,
    "original-resources": discover_original_resources,
    "metadata": discover_collection_metadata
}

