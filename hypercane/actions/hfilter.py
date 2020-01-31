import sys
# import os
# import argparse
# import json
# import concurrent.futures
# import errno

# from datetime import datetime
# from pymongo import MongoClient
# from justext import justext, get_stoplist
# from simhash import Simhash

# TODO: come back to this
# the OTMT imports a version of sklearn that generates the following warning:
# DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
# I cannot fix sklearn, but I can quiet the warning
# import warnings

# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=DeprecationWarning)
#     import otmt
# import otmt

# from ..actions import add_input_args, add_default_args, \
#     get_logger, calculate_loglevel, process_input_args
# from ..identify import discover_timemaps_by_input_type, \
#     discover_mementos_by_input_type, download_urits_and_extract_urims, \
#     extract_uris_from_input, discover_resource_data_by_input_type
# from ..hfilter.remove_offtopic import detect_off_topic
# from ..hfilter.near_duplicates import filter_near_duplicates
# from ..hfilter.languages import language_included, language_not_included, \
#     filter_languages
# from ..utils import get_memento_datetime_and_timemap, \
#     get_web_session, get_language, get_raw_simhash, \
#     save_resource_data
# from .cluster import HypercaneClusterInputException

# def process_remove_offtopic_args(args, parser):

#     parser = add_input_args(parser)

#     tmmeasurehelp = ""
#     for measure in otmt.supported_timemap_measures:
#         tmmeasurehelp += "* {} - {}, default threshold {}\n".format(
#             measure, otmt.supported_timemap_measures[measure]['name'],
#             otmt.supported_timemap_measures[measure]['default threshold'])

#     parser.add_argument('-tm', '--timemap-measures', dest='timemap_measures',
#         type=otmt.process_timemap_similarity_measure_inputs,
#         default='cosine',
#         help="The TimeMap-based similarity measures specified will be used. \n"
#         "For each of these measures, the first memento in a TimeMap\n"
#         "is compared with each subsequent memento to measure topic drift.\n"
#         "Specify measure with optional threshold separated by equals.\n"
#         "Multiple measures can be specified.\n"
#         "(e.g., jaccard=0.10,cosine=0.15,wordcount);\n"
#         "Leave thresholds off to use default thresholds.\n"
#         "Accepted values:\n{}".format(tmmeasurehelp)
#     )

#     parser.add_argument('--number-of-topics', dest="num_topics", type=int,
#         help="The number of topics to use for gensim_lda and gensim_lsi, "
#         "ignored if these measures are not requested.")

#     parser = add_default_args(parser)

#     args = parser.parse_args(args)

#     return args

# def load_urim(collection_model, urim):
#     collection_model.addMemento(urim)
#     return urim

# def remove_offtopic(args):

#     parser = argparse.ArgumentParser(
#         description="Remove the off-topic documents from a collection.",
#         prog="hc filter remove-offtopic"
#     )

#     args = process_remove_offtopic_args(args, parser)

#     logger = get_logger(
#         __name__,
#         calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
#         args.logfile
#     )

#     logger.info("Starting detection of off-topic documents...")

#     session = get_web_session(cache_storage=args.cache_storage)
#     dbconn = MongoClient(args.cache_storage)
#     urits = discover_timemaps_by_input_type(
#         args.input_type, args.input_arguments, 
#         args.crawl_depth, session)
#     urims = download_urits_and_extract_urims(urits, session)

#     ontopic_mementos = detect_off_topic(
#         dbconn, session, urits, urims, args.timemap_measures, 
#         num_topics=args.num_topics)

#     logger.info("discovered {} on-topic mementos".format(len(ontopic_mementos)))

#     with open(args.output_filename, 'w') as f:
#         for urim in ontopic_mementos:
#             f.write("{}\n".format(urim))

#     logger.info("done with off-topic run, on-topic mementos are in {}".format(args.output_filename))

# def remove_near_duplicates(args):

#     parser = argparse.ArgumentParser(
#         description="Remove the near-duplicate documents from a collection.",
#         prog="hc filter remove-near-duplicates"
#     )

#     args = process_input_args(args, parser)

#     logger = get_logger(
#         __name__,
#         calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
#         args.logfile
#     )

#     logger.info("Starting detection of near-duplicate documents...")

#     session = get_web_session(cache_storage=args.cache_storage)

#     urims = discover_mementos_by_input_type(
#         args.input_type, args.input_arguments,
#         args.crawl_depth, session
#     )

#     output_urims = filter_near_duplicates(urims, args.cache_storage)

#     with open(args.output_filename, 'w') as f:

#         for urim in output_urims:
#             f.write('{}\n'.format(urim))

#     logger.info("Completed detection of near-duplicates, output is saved to {}".format(args.output_filename))

# def process_input_for_clusters_and_ranks(input_list):

#     list_of_cluster_assignments = []

#     for item in input_list:
#         if '\t' in item:
#             uri, clusterid, rank = item.split('\t')
#             list_of_cluster_assignments.append( (clusterid, uri, rank) )

#     if len(list_of_cluster_assignments) != len(input_list):

#         raise HypercaneClusterInputException("The assignment of clusters to URIs in inconsistent")

#     return list_of_cluster_assignments

# def highest_ranking_per_cluster(args):

#     parser = argparse.ArgumentParser(
#         description="Remove the near-duplicate documents from a collection.",
#         prog="hc filter remove-near-duplicates"
#     )

#     args = process_input_args(args, parser)

#     logger = get_logger(
#         __name__,
#         calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
#         args.logfile
#     )

#     logger.info("Starting selection of the highest ranked documents in input...")

#     urim_to_rank = {}
#     cluster_to_urims = {}

#     if args.input_type == "mementos":
#         items = extract_uris_from_input(args.input_arguments)
#         ranked_and_clustered_urims = process_input_for_clusters_and_ranks(items)

#         for entry in ranked_and_clustered_urims:
#             cluster = entry[0]
#             urim = entry[1]
#             rank = entry[2]

#             urim_to_rank[urim] = rank
#             cluster_to_urims.setdefault(cluster, []).append(urim)

#     else:
#         raise NotImplementedError(
#             "Input type of {} not yet supported for ranking".format(
#                 args.input_type))

#     output_urims = []

#     for cluster in cluster_to_urims:

#         cluster_ranks_to_urims = []

#         for urim in cluster_to_urims[cluster]:
#             cluster_ranks_to_urims.append( ( urim_to_rank[urim], urim ) )

#         highest_scoring_urim_in_cluster = max(cluster_ranks_to_urims)[1]

#         output_urims.append(highest_scoring_urim_in_cluster)

#     with open(args.output_filename, 'w') as f:

#         for urim in output_urims:
#             f.write("{}\n".format(urim))

#     logger.info("Finished selection of highest ranked documents in input; output is at {}".format(args.output_filename))

def start_language_processing(parser, args):

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    
    parser.add_argument('--lang', '--languages', dest='languages',
        help="The list of languages to match, separated by commas.",
        required=True
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting filtering of mementos by languages...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    return args, logger, urimdata

def include_languages(args):

    import argparse
    from hypercane.hfilter.languages import filter_languages,language_included
    from hypercane.utils import save_resource_data
    
    parser = argparse.ArgumentParser(
        description="Include only mementos containing the specified languages.",
        prog="hc filter include-only languages"
    )

    args, logger, urimdata = start_language_processing(parser, args)
    urims = list(urimdata.keys())

    logger.info("discovered {} mementos in input, downloading or extracting from cache...".format(len(urims)))

    desired_languages = [ i.strip() for i in args.languages.split(',')]
    logger.info("comparing languages of documents with requested languages of {}...".format(desired_languages))

    filtered_urims = filter_languages(
        urims, args.cache_storage, desired_languages, language_included)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("done, mementos including the languages of {} are in {}".format(desired_languages, args.output_filename))

def exclude_languages(args):

    import argparse
    from hypercane.hfilter.languages import filter_languages, language_not_included
    from hypercane.utils import save_resource_data

    parser = argparse.ArgumentParser(
        description="Exclude mementos with the specified languages.",
        prog="hc filter exclude languages"
    )

    args, logger, urimdata = start_language_processing(parser, args)
    urims = list(urimdata.keys())

    logger.info("discovered {} mementos in input, downloading or extracting from cache...".format(len(urims)))

    desired_languages = [ i.strip() for i in args.languages.split(',')]
    logger.info("comparing languages of documents with requested languages of {}...".format(desired_languages))

    filtered_urims = filter_languages(
        urims, args.cache_storage, desired_languages, language_not_included)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("done, mementos not including the languages of {} are in {}".format(desired_languages, args.output_filename))

def print_usage():

    print("""'hc filter' is used to employ techniques to filter a web archive collection

    Supported commands:
    * include-only - include mementos from the input that satisfy the given criteria
    * exclude - exclude mementos from the input by the given criteria

    Examples:
    
    hc filter include-only language en,es -i archiveit=8788 -o ontopic-mementos.txt

    hc filter exclude off-topic -i archiveit=8788 --keep en,es -o english-and-spanish-docs.txt

    hc filter exclude near-duplicates -i mementos=ontopic-mementos.txt -o novel-content.txt

    hc filter include-only rank "=1" -i mementos=file-with-scored-mementos.txt -o filtered-mementos.txt
    
""")

def print_include_usage():

    print("""'hc filter include-only' is used to employ techniques to filter a web archive collection by including mementos that satisfy the given criteria

    Examples:
    
    hc filter include-only language en,es -i archiveit=8788 -o ontopic-mementos.txt

    hc filter include-only rank "=1" -i mementos=file-with-scored-mementos.txt -o filtered-mementos.txt
    
""")

def print_exclude_usage():

    print("""'hc filter exclude' is used to employ techniques to filter a web archive collection by excluding mementos that satisfy the given criteria

    Examples:
    
    hc filter exclude language en,de -i archiveit=8788 -o ontopic-mementos.txt

    hc filter exclude rank ">1" -i mementos=file-with-scored-mementos.txt -o filtered-mementos.txt
    
""")

include_criteria = {
    "languages": include_languages
}

exclude_criteria = {
    "languages": exclude_languages
}


