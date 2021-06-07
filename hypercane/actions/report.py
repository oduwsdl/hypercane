import sys

from datetime import datetime

def dtconverter(o):

    if isinstance(o, datetime):
        return o.__str__()

def generate_collection_metadata(archive_name, collection_id, session):

    if archive_name == 'archiveit':

        from aiu import ArchiveItCollection

        aic = ArchiveItCollection(collection_id, session=session)

        return aic.return_all_metadata_dict()

    elif archive_name == 'trove':

        from aiu import TroveCollection
        from urllib.parse import unquote

        tc = TroveCollection(collection_id, session=session)

        metadata_dict = generate_blank_metadata([])
        
        metadata_dict['id'] = collection_id
        metadata_dict['name'] = tc.get_collection_name()
        metadata_dict['exists'] = tc.does_exist()
        metadata_dict['uri'] = unquote(tc.get_collection_uri())
        metadata_dict['collected_by'] = tc.get_collectedby()
        del metadata_dict['collected_by_uri']
        metadata_dict['archived_since'] = tc.get_archived_since()
        metadata_dict['archived_until'] = tc.get_archived_until()
        del metadata_dict['private']
        del metadata_dict['optional']
        metadata_dict['subcollections'] = tc.get_subcollections()
        metadata_dict['supercollections'] = tc.get_breadcrumbs()
        metadata_dict['subject'] = tc.get_subject()
        metadata_dict['memento_list'] = [ i.strip() for i in tc.list_memento_urims() ]

        del metadata_dict['seed_metadata'] # Archive-It like seeds
        metadata_dict['seed_list'] = [] # NLA seeds
        
        for urir in tc.list_seed_uris():

            if urir[0:4] != 'http':
                urir = urir[urir.find('/http') + 1:]

                if urir[0:4] != 'http':
                    urir = 'http://' + urir[urir.find('/', urir.find('/') + 1) + 1:]

            metadata_dict['seed_list'].append(urir)

        return metadata_dict

    elif archive_name == 'pandora-subject':

        from aiu import PandoraSubject

        ps = PandoraSubject(collection_id, session=session)

        metadata_dict = generate_blank_metadata([])
        
        metadata_dict['id'] = collection_id
        metadata_dict['name'] = ps.get_subject_name()
        metadata_dict['exists'] = ps.does_exist()
        metadata_dict['uri'] = ps.subject_uri
        metadata_dict['collected_by'] = ps.get_collectedby()
        del metadata_dict['collected_by_uri']
        del metadata_dict['archived_since']
        del metadata_dict['private']
        del metadata_dict['optional']
        metadata_dict['subcategories'] = ps.list_subcategories()
        metadata_dict['collections'] = ps.list_collections()
        del metadata_dict['subject']
        metadata_dict['memento_list'] = [ i.strip() for i in ps.list_memento_urims() ]

        del metadata_dict['seed_metadata'] # Archive-It like seeds
        metadata_dict['seed_list'] = [] # NLA seeds

        for urir in ps.list_seed_uris():

            if urir[0:4] != 'http':
                urir = urir[urir.find('/http') + 1:]

                if urir[0:4] != 'http':
                    urir = 'http://' + urir[urir.find('/', urir.find('/') + 1) + 1:]

            metadata_dict['seed_list'].append(urir)

        return metadata_dict

    elif archive_name == 'pandora-collection':

        from aiu import PandoraCollection

        pc = PandoraCollection(collection_id, session=session)

        metadata_dict = generate_blank_metadata([])
        
        metadata_dict['id'] = collection_id
        metadata_dict['name'] = pc.get_collection_name()
        metadata_dict['exists'] = pc.does_exist()
        metadata_dict['uri'] = pc.collection_uri
        metadata_dict['collected_by'] = pc.get_collectedby()
        del metadata_dict['collected_by_uri']
        del metadata_dict['archived_since']
        del metadata_dict['private']
        del metadata_dict['optional']
        del metadata_dict['subject']
        metadata_dict['memento_list'] = [ i.strip() for i in pc.list_memento_urims() ]

        del metadata_dict['seed_metadata'] # Archive-It like seeds
        metadata_dict['seed_list'] = [] # NLA seeds

        for urir in pc.list_seed_uris():

            if urir[0:4] != 'http':
                urir = urir[urir.find('/http') + 1:]

                if urir[0:4] != 'http':
                    urir = 'http://' + urir[urir.find('/', urir.find('/') + 1) + 1:]

            metadata_dict['seed_list'].append(urir)

        return metadata_dict

    else:
        raise NotImplementedError("Collection Metadata Only Available for collections of type 'archiveit', 'pandora-collection', 'pandora-subject', and 'trove'")
        

def generate_blank_metadata(urirs):

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
    output_type = 'original-resources'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection metadata discovery run.")

    if args.input_type in [ 'archiveit', 'pandora-subject', 'pandora-collection', 'trove' ]:
        metadata = generate_collection_metadata(args.input_type, args.input_arguments, session)
    else:
        logger.warning("Metadata reports are only supported for Pandora Subjects, Pandora Collections, Archive-It Collections, and Trove Collections, proceeding to create JSON output for URI-Rs.")

        urirdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_original_resources_by_input_type
        )
        metadata = generate_blank_metadata(list(urirdata.keys()))

    with open(args.output_filename, 'w') as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    logger.info("Done with collection metadata discovery run, output is in {}.".format(args.output_filename))

def report_metadatastats(args):

    import sys

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type, discover_original_resources_by_input_type

    from hypercane.report.metadatastats import get_pct_seeds_with_metadata, \
        get_pct_seeds_with_specific_field, get_pct_seeds_with_title, \
        get_pct_seeds_with_description, get_mean_default_field_score, \
        get_metadata_compression_ratio, get_mean_raw_field_count

    import json

    parser = argparse.ArgumentParser(
        description="Discover the collection metadata in a web archive collection. Only Archive-It is supported at this time.",
        prog="hc report metadata"
        )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection metadata statistics run.")

    output = {}

    if args.input_type == 'archiveit':
        metadata = generate_collection_metadata(args.input_type, args.input_arguments, session)
        output['id'] = metadata['id']
        output['archived since'] = metadata['archived_since']
        output['# of seeds'] = len(metadata['seed_metadata']['seeds'])
        output['% of seeds with any metadata'] = get_pct_seeds_with_metadata(metadata)
        output['% title field use'] = get_pct_seeds_with_title(metadata)
        output['% description field use'] = get_pct_seeds_with_description(metadata)
        output['mean default fields metadata score'] = get_mean_default_field_score(metadata)
        output['mean non-normalized metadata count'] = get_mean_raw_field_count(metadata)
        output['metadata compression ratio'] = get_metadata_compression_ratio(metadata)
    else:
        logger.critical("Metadata statistics are only supported for Archive-It collections")
        sys.exit(255)

    with open(args.output_filename, 'w') as report_file:
        json.dump(output, report_file, indent=4)

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
        help="Regardless of headers, assume the input are URI-Rs and do not try to archive or convert them to URI-Ms."
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
    
    parser.add_argument('--added-stopwords', help="If specified, add stopwords from this file.",
        dest='added_stopword_filename', default=None
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

    added_stopwords = []

    if args.added_stopword_filename is not None:
        with open(args.added_stopword_filename) as f:
            for line in f:
                added_stopwords.append(line.strip())

    if args.use_sumgrams is True:

        from hypercane.report.sumgrams import generate_sumgrams
        from hypercane import package_directory

        ranked_terms = generate_sumgrams(
            list(urimdata.keys()), args.cache_storage,
            added_stopwords=added_stopwords
            )

        with open(args.output_filename, 'w') as f:

            f.write("Term\tFrequency in Corpus\tTerm Rate\n")

            for term, frequency, term_rate in ranked_terms:
                f.write("{}\t{}\t{}\n".format(
                    term, frequency, term_rate
                ))

    else:
        from hypercane.report.terms import generate_ranked_terms

        ranked_terms = generate_ranked_terms(
            list(urimdata.keys()), args.cache_storage, 
            ngram_length=args.ngram_length,
            added_stopwords=added_stopwords)

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

    # TODO: make this work, how is this type=int ?
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

def report_seedstats(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_original_resources_by_input_type

    from hypercane.report.seedstats import calculate_domain_diversity, \
        calculate_path_depth_diversity, most_frequent_seed_uri_path_depth, \
        calculate_top_level_path_percentage, calculate_percentage_querystring

    import json

    parser = argparse.ArgumentParser(
        description="Provide a report containing statistics on the original-resources derived from the input.",
        prog="hc report seed-statistics"
        )

    args = process_input_args(args, parser)
    output_type = 'original-resources'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection original resource statistics run")

    urirs = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_original_resources_by_input_type
    )

    output = {}
    output['number of original-resources'] = len(urirs)
    output['domain diversity'] = calculate_domain_diversity(urirs)
    output['path depth diversity'] = calculate_path_depth_diversity(urirs)
    output['most frequent path depth'] = most_frequent_seed_uri_path_depth(urirs)
    output['percentage of top-level URIs'] = calculate_top_level_path_percentage(urirs)
    output['query string percentage'] = calculate_percentage_querystring(urirs)

    with open(args.output_filename, 'w') as report_file:
        json.dump(output, report_file, indent=4)

    logger.info("Done with collection original resource statistics report, output is in {}".format(args.output_filename))

def report_growth_curve_stats(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_timemaps_by_input_type

    from hypercane.report.growth import get_last_memento_datetime, \
        get_first_memento_datetime, process_timemaps_for_mementos, \
        calculate_mementos_per_seed, calculate_memento_seed_ratio, \
        calculate_number_of_mementos, parse_data_for_mementos_list, \
        convert_mementos_list_into_mdts_pct_urim_pct_and_urir_pct, \
        draw_both_axes_pct_growth

    import json

    from sklearn.metrics import auc

    parser = argparse.ArgumentParser(
        description="Provide a report containing statistics growth of mementos derived from the input.",
        prog="hc report growth"
        )

    parser.add_argument('--growth-curve-file', dest='growthcurve_filename',
        help="If present, draw a growth curve and write it to the filename specified.",
        default=None, required=False)

    args = process_input_args(args, parser)
    output_type = 'original-resources'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection original resource statistics run")

    urits = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_timemaps_by_input_type
    )

    timemap_data, errors_data = process_timemaps_for_mementos(urits, session)
    mementos_list = parse_data_for_mementos_list(timemap_data)
    mdts_pct, urims_pct, urirs_pct = \
        convert_mementos_list_into_mdts_pct_urim_pct_and_urir_pct(
        mementos_list)

    output = {}
    output['auc_memento_curve'] = auc(mdts_pct, urims_pct)
    output['auc_seed_curve'] = auc(mdts_pct, urirs_pct)
    output['auc_memento_minus_diag'] = output['auc_memento_curve'] - 0.5
    output['auc_seed_minus_diag'] = output['auc_seed_curve'] - 0.5
    output['auc_seed_minus_auc_memento'] = output['auc_seed_curve'] - output['auc_memento_curve']
    output['memento_seed_ratio'] = calculate_memento_seed_ratio(timemap_data)
    output['mementos_per_seed'] = calculate_mementos_per_seed(timemap_data)
    output['first_memento_datetime'] = get_first_memento_datetime(timemap_data)
    output['last_memento_datetime'] = get_last_memento_datetime(timemap_data)
    output["number_of_original_resources"] = len(urits)
    output["number_of_mementos"] = calculate_number_of_mementos(timemap_data)
    output['lifespan_secs'] = (get_last_memento_datetime(timemap_data) - get_first_memento_datetime(timemap_data)).total_seconds()
    output['lifespan_mins'] = output['lifespan_secs'] / 60
    output['lifespan_hours'] = output['lifespan_secs'] / 60 / 60
    output['lifespan_days'] = output['lifespan_secs'] / 60 / 60 / 24
    output['lifespan_weeks'] = output['lifespan_secs'] / 60 / 60 / 24 / 7
    output['lifespan_years'] = output['lifespan_secs'] / 60 / 60 / 24 / 365

    with open(args.output_filename, 'w') as report_file:
        json.dump(output, report_file, indent=4, default=dtconverter)

    logger.info("Done with collection growth statistics, report saved to {}".format(args.output_filename))

    if args.growthcurve_filename is not None:

        logger.info("Beginning to render collection growth curve...")

        draw_both_axes_pct_growth(
            mdts_pct, urims_pct, urirs_pct,
            args.growthcurve_filename
        )

        logger.info("Growth curve saved to {}".format(args.growthcurve_filename))


def report_html_metadata(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type, discover_original_resources_by_input_type

    from hypercane.report.per_page_metadata import output_page_metadata_as_ors

    import json

    parser = argparse.ArgumentParser(
        description="Provide a report on the HTML metadata of the mementos discovered in the input.",
        prog="hc report html-metadata"
        )

    parser.add_argument('--use-urirs', required=False,
        dest='use_urirs', action='store_true',
        help="Regardless of headers, assume the input are URI-Rs and do not try to archive or convert them to URI-Ms."
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection html metadata run")

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

    output_page_metadata_as_ors(uridata, args.cache_storage, args.output_filename)

    logger.info("Done with html metadata data run, output is at {}".format(args.output_filename))

def report_http_status(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type, discover_original_resources_by_input_type

    from hypercane.report.http_status import output_http_status_as_tsv

    parser = argparse.ArgumentParser(
        description="Provide a report on all URI-Ms, their HTTP response status (before redirects), whether they are a redirect, datetime of check, and memento header information.",
        prog="hc report http-status"
        )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting collection HTTP status data run")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    output_http_status_as_tsv(urimdata, args.cache_storage, args.output_filename)

    logger.info("Done with http status report, output is at {}".format(args.output_filename))

def report_generated_queries(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    import json

    from hypercane.report.generate_queries import generate_queries_from_documents_with_doct5query, \
            generate_queries_from_metadata_with_doct5query

    parser = argparse.ArgumentParser(
        description="Apply techniques to generate queries from the text of the input documents.",
        prog="hc report generated-queries"
        )

    parser.add_argument('--query-count', dest='query_count',
        help="create this many queries per document, ", default=5, required=False
    )

    parser.add_argument('--use-metadata', dest='use_metadata', action='store_true',
        help="use collection metadata to generate queries instead of documents from input, requires that input be a collection type"
    )

    # parser.add_argument('--generation-method', dest='generation_method',
    #     help="apply the given generation method for queries, valid values are 'top10entities', 'doc2query-T5'",
    #     default='doc2query-T5', required=False
    # )

    # TODO: generate query per cluster

    # TODO: use a different query generation technique than docTTTTTquery, like top n entities, top n terms

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting query generation based on input mementos")

    if args.use_metadata == True:

        if args.input_type not in ['archiveit', 'pandora-subject', 'pandora-collection', 'trove']:

            raise NotImplementedError("Can only apply to query generation for inputs of type 'archiveit', 'pandora-collection', 'pandora-subject', and 'trove'")

        else:

            metadata = generate_collection_metadata(args.input_type, args.input_arguments, session)
            querydata = generate_queries_from_metadata_with_doct5query(metadata, args.cache_storage, args.query_count)

    else:

        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        ) 

        querydata = generate_queries_from_documents_with_doct5query(urimdata, args.cache_storage, args.query_count)

    with open(args.output_filename, 'w') as f:
        json.dump(querydata, f, indent=4)

    logger.info("Done with http status report, output is at {}".format(args.output_filename))

def print_usage():

    print("""'hc report' is used to print reports about web archive collections

    Supported commands:
    * metadata - for discovering the metadata associated with seeds
    * image-data - for generating a report of the images associated with the mementos found in the input
    * terms - generates corpus term frequency, probability, document frequency, inverse document frequency, and corpus TF-IDF for the terms in the collection
    * entities - generates corpus term frequency, probability, document frequency, inverse document frequency, and corpus TF-IDF for the named entities in the collection
    * seed-statistics - calculates metrics on the original resources discovered from the input
    * growth - calculates metrics based on the growth of the TimeMaps discovered from the input
    * metadata-statistics - statistics about the metadata for this collection (Archive-It only)
    * html-metadata - a listing of all URI-Ms and associated HTML metadata containing a NAME or PROPERTY attribute
    * http-status - a TSV listing of all URI-Ms, their HTTP response status (before redirects), whether they are a redirect, datetime of check, and memento header information
    * generate-queries - generate a series of queries from the text in the input documents


    Examples:

    hc report metadata -i archiveit -a 8788 -o 8788-metadata.json -cs mongodb://localhost/cache

    hc report metadata -i trove -a 13742 -o 13742-metadata.json -cs mongodb://localhost/cache

    hc report entities -i mementos -a memento-file.tsv -o entity-report.json

    hc report seed-statistics -i original-resources -a urirs.tsv -o seedstats.json

""")

supported_commands = {
    "metadata": discover_collection_metadata,
    "image-data": report_image_data,
    "terms": report_ranked_terms,
    "entities": report_entities,
    "seed-statistics": report_seedstats,
    "growth": report_growth_curve_stats,
    "metadata-statistics": report_metadatastats,
    "html-metadata": report_html_metadata,
    "http-status": report_http_status,
    "generate-queries": report_generated_queries
}

