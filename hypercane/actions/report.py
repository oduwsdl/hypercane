import argparse
import json

from . import get_logger, calculate_loglevel, add_default_args, process_collection_input_types
from ..identify import generate_collection_metadata
from ..utils import get_web_session

def process_discover_collection_metadata_args(args):

    parser = argparse.ArgumentParser(
        description="Discover the collection metadata in a web archive collection. Only Archive-It is supported at this time.",
        prog="hc report metadata"
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

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection metadata discovery run.")

    collection_type = args.input_type[0]

    if collection_type != 'archiveit':
        raise NotImplementedError("Metadata reports are only supported for Archive-It collections")

    collection_id = args.input_type[1]

    logger.info("Collection type: {}".format(collection_type))
    logger.info("Collection identifier: {}".format(collection_id))

    metadata = generate_collection_metadata(collection_id, session)

    with open(args.output_filename, 'w') as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    logger.info("Done with collection metadata discovery run.")

def print_usage():

    print("""'hc report' is used print reports about web archive collections

    Supported commands:
    * metadata - for discovering the metadata associated with seeds, only Archive-It is supported at this time

    Examples:
    
    hc report metadata -i archiveit=8788 -o 8788-metadata.json
    
""")

supported_commands = {
    "metadata": discover_collection_metadata
}

