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
        discover_mementos_by_input_type, discover_original_resources_by_input_type

    from hypercane.report.imagedata import generate_image_data, \
        rank_images, output_image_data_as_jsonl

    import json

    parser = argparse.ArgumentParser(
        description="Provide a report on the images from in the mementos discovered in the input.",
        prog="hc report image-data"
        )

    parser.add_argument('--use-urirs', required=False, 
        dest='use_urirs', action='store_true',
        help="Regardless of headers, assume the input are URI-Rs and do not try to archive them."
    )

    parser.add_argument('--output-format', required=False,
        dest="output_format", default="json",
        help="Choose the output format, valid formats are JSON and JSONL"
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

    if args.use_urirs == True:
        uridata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_original_resources_by_input_type
        )
    else:
        uridata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    
    if args.output_format == 'json':

        metadata = {}
        metadata['image data'] = generate_image_data(uridata, args.cache_storage)
        metadata['ranked data'] = rank_images(metadata['image data'])

        with open(args.output_filename, 'w') as metadata_file:
            json.dump(metadata, metadata_file, indent=4)

    elif args.output_format == 'jsonl':
        output_image_data_as_jsonl(uridata, args.output_filename, args.cache_storage)        

    logger.info("Done with collection image data run, output is at {}".format(args.output_filename))

def report_ranked_terms(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    import json

    parser = argparse.ArgumentParser(
        description="Provide a report containing the terms from the collection and their associated frequencies.",
        prog="hc report terms"
        )

    parser.add_argument('--ngram-length', help="The size of the n-grams", dest='ngram_length', default=1, type=int)

    parser.add_argument('--sumgrams', '--use-sumgrams', help="If specified, generate sumgrams rather than n-grams.",
        action='store_true', default=False, dest='use_sumgrams'
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

    if args.use_sumgrams is True:

        from hypercane.report.sumgrams import generate_sumgrams

        ranked_terms = generate_sumgrams(list(urimdata.keys()), args.cache_storage)

        with open(args.output_filename, 'w') as f:

            f.write("Term\tFrequency in Corpus\tTerm Rate\n")

            for term, frequency, term_rate in ranked_terms:
                f.write("{}\t{}\t{}\n".format(
                    term, frequency, term_rate
                ))

    else:
        from hypercane.report.terms import generate_ranked_terms

        ranked_terms = generate_ranked_terms(list(urimdata.keys()), args.cache_storage, ngram_length=args.ngram_length)

        with open(args.output_filename, 'w') as f:

            f.write("Term\tFrequency in Corpus\tProbability in Corpus\tDocument Frequency\tInverse Document Frequency\tCorpus TF-IDF\n")

            for term, frequency, probability, df, idf, tfidf in ranked_terms:
                f.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(term, frequency, probability, df, idf, tfidf))
        

    logger.info("Done with collection term frequency report, output is in {}".format(args.output_filename))

def report_entities(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.report.entities import generate_entities

    import json

    parser = argparse.ArgumentParser(
        description="Provide a report containing the terms from the collection and their associated frequencies.",
        prog="hc report entities"
        )

    default_entity_types = ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW']

    parser.add_argument('--entity-types', help="The types of entities to report, from https://spacy.io/api/annotation#named-entities", dest='entity_types', default=default_entity_types, type=int)

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

    ranked_terms = generate_entities(list(urimdata.keys()), args.cache_storage, args.entity_types)

    with open(args.output_filename, 'w') as f:

        f.write("Entity\tFrequency in Corpus\tProbability in Corpus\tDocument Frequency\tInverse Document Frequency\tCorpus TF-IDF\n")

        for term, frequency, probability, df, idf, tfidf in ranked_terms:
            f.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(term, frequency, probability, df, idf, tfidf))
        

    logger.info("Done with collection term frequency report, output is in {}".format(args.output_filename))

def print_usage():

    print("""'hc report' is used print reports about web archive collections

    Supported commands:
    * metadata - for discovering the metadata associated with seeds
    * image-data - for generating a report of the images associated with the mementos found in the input
    * terms - generates corpus term frequency, probability, document frequency, inverse document frequency, and corpus TF-IDF for the terms in the collection
    * entities - generates corpus term frequency, probability, document frequency, inverse document frequency, and corpus TF-IDF for the named entities in the collection

    Examples:
    
    hc report metadata -i archiveit -ia 8788 -o 8788-metadata.json -cs mongodb://localhost/cache
    
""")

supported_commands = {
    "metadata": discover_collection_metadata,
    "image-data": report_image_data,
    "terms": report_ranked_terms,
    "entities": report_entities
}

