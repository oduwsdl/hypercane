import sys

def generate_collection_metadata(collection_id, session):

    from aiu import ArchiveItCollection

    aic = ArchiveItCollection(collection_id, session=session)

    return aic.return_all_metadata_dict()

def generate_blank_metadata(urirs):

    from datetime import datetime

    blank_metadata = {'id': None,
        'exists': None,
        'metadata_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'name': None,
        'uri': None,
        'collected_by': None,
        'collected_by_uri': None,
        'description': None,
        'subject': [],
        'archived_since': None,
        'private': None,
        'optional': {},
        'seed_metadata': {
            'seeds': {}
        },
        'timestamps': {
            'seed_metadata_timestamp': '2020-01-25 16:45:59',
            'seed_report_timestamp': '2020-01-25 16:45:59'
        }
    }

    for urir in urirs:
        blank_metadata['seed_metadata']['seeds'][urir] = {
            'collection_web_pages': [{}],
            'seed_report': {}
        }

    return blank_metadata

def discover_collection_metadata(args):
    
    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_original_resources_by_input_type

    import json

    parser = argparse.ArgumentParser(
        description="Discover the collection metadata in a web archive collection. Only Archive-It is supported at this time.",
        prog="hc report metadata"
        )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection metadata discovery run.")

    if args.input_type == 'archiveit':
        metadata = generate_collection_metadata(args.input_arguments, session)
    else:
        logger.warning("Metadata reports are only supported for Archive-It collections, proceeding to create JSON output for URI-Rs.")

        urirdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_original_resources_by_input_type
        )
        metadata = generate_blank_metadata(list(urirdata.keys()))

    with open(args.output_filename, 'w') as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    logger.info("Done with collection metadata discovery run.")

def report_image_data(args):
    
    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.report.imagedata import generate_image_data, \
        rank_images

    import json

    parser = argparse.ArgumentParser(
        description="Provide a report on the images from in the mementos discovered in the input.",
        prog="hc report image-data"
        )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection image data run")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )
    
    metadata = {}
    metadata['image data'] = generate_image_data(urimdata, args.cache_storage)
    metadata['ranked data'] = rank_images(metadata['image data'])

    with open(args.output_filename, 'w') as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    logger.info("Done with collection image data run")

def report_ranked_terms(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.report.ranked_terms import generate_ranked_terms

    import json

    parser = argparse.ArgumentParser(
        description="Provide a report containing the terms from the collection and their associated frequencies.",
        prog="hc report ranked-terms"
        )

    parser.add_argument('-n', '--ngram-length', description="The size of the n-grams", dest='ngram_length', default=1, type=int)

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection image data run")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    ranked_terms = generate_ranked_terms(list(urimdata.keys()), args.count, args.ngram_length)

    for term in ranked_terms:
        pass

    logger.info("Done with collection image data run")

def print_usage():

    print("""'hc report' is used print reports about web archive collections

    Supported commands:
    * metadata - for discovering the metadata associated with seeds
    * image-data - for generating a report of the images associated with the mementos found in the input
    * ranked-terms - generates term frequency for the terms in the collection and returns the top k

    Examples:
    
    hc report metadata -i archiveit -ia 8788 -o 8788-metadata.json -cs mongodb://localhost/cache
    
""")

supported_commands = {
    "metadata": discover_collection_metadata,
    "image-data": report_image_data,
    "ranked-terms": report_ranked_terms
}

