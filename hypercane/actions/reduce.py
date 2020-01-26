import sys
import os
import argparse
import json
import concurrent.futures
import langdetect
import errno

from datetime import datetime
from pymongo import MongoClient
from justext import justext, get_stoplist
from simhash import Simhash

# TODO: come back to this
# the OTMT imports a version of sklearn that generates the following warning:
# DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
# I cannot fix sklearn, but I can quiet the warning
# import warnings

# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=DeprecationWarning)
#     import otmt
import otmt

from ..actions import add_input_args, add_default_args, \
    get_logger, calculate_loglevel, process_input_args
from ..identify import discover_timemaps_by_input_type, \
    discover_mementos_by_input_type, download_urits_and_extract_urims, \
    extract_uris_from_input
from ..reduce.remove_offtopic import detect_off_topic
from ..reduce.near_duplicates import filter_near_duplicates
from ..utils import get_memento_datetime_and_timemap, \
    get_web_session, get_language, get_raw_simhash
from .cluster import HypercaneClusterInputException

def process_remove_offtopic_args(args, parser):

    parser = add_input_args(parser)

    tmmeasurehelp = ""
    for measure in otmt.supported_timemap_measures:
        tmmeasurehelp += "* {} - {}, default threshold {}\n".format(
            measure, otmt.supported_timemap_measures[measure]['name'],
            otmt.supported_timemap_measures[measure]['default threshold'])

    parser.add_argument('-tm', '--timemap-measures', dest='timemap_measures',
        type=otmt.process_timemap_similarity_measure_inputs,
        default='cosine',
        help="The TimeMap-based similarity measures specified will be used. \n"
        "For each of these measures, the first memento in a TimeMap\n"
        "is compared with each subsequent memento to measure topic drift.\n"
        "Specify measure with optional threshold separated by equals.\n"
        "Multiple measures can be specified.\n"
        "(e.g., jaccard=0.10,cosine=0.15,wordcount);\n"
        "Leave thresholds off to use default thresholds.\n"
        "Accepted values:\n{}".format(tmmeasurehelp)
    )

    parser.add_argument('--number-of-topics', dest="num_topics", type=int,
        help="The number of topics to use for gensim_lda and gensim_lsi, "
        "ignored if these measures are not requested.")

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def load_urim(collection_model, urim):
    collection_model.addMemento(urim)
    return urim

def remove_offtopic(args):

    parser = argparse.ArgumentParser(
        description="Remove the off-topic documents from a collection.",
        prog="hc filter remove-offtopic"
    )

    args = process_remove_offtopic_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of off-topic documents...")

    session = get_web_session(cache_storage=args.cache_storage)
    dbconn = MongoClient(args.cache_storage)
    urits = discover_timemaps_by_input_type(
        args.input_type, args.input_arguments, 
        args.crawl_depth, session)
    urims = download_urits_and_extract_urims(urits, session)

    ontopic_mementos = detect_off_topic(
        dbconn, session, urits, urims, args.timemap_measures, 
        num_topics=args.num_topics)

    logger.info("discovered {} on-topic mementos".format(len(ontopic_mementos)))

    with open(args.output_filename, 'w') as f:
        for urim in ontopic_mementos:
            f.write("{}\n".format(urim))

    logger.info("done with off-topic run, on-topic mementos are in {}".format(args.output_filename))

def by_language(args):

    parser = argparse.ArgumentParser(
        description="Only keep documents from a collection with a specific language.",
        prog="hc filter by-language"
    )

    parser.add_argument('--lang', '--languages', dest='languages',
        help="The list of languages to keep in the output, separated by commas.",
        required=True
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of languages...")

    session = get_web_session(cache_storage=args.cache_storage)

    urims = discover_mementos_by_input_type(
        args.input_type, args.input_arguments, args.crawl_depth, session
    )

    logger.info("discovered {} mementos in input, downloading or extracting from cache...".format(len(urims)))

    desired_languages = [ i.strip() for i in args.languages.split(',')]
    logger.info("comparing languages of documents with requested languages of {}...".format(desired_languages))

    with open(args.output_filename, 'w') as f:

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_urim = { executor.submit(get_language, urim, args.cache_storage): urim for urim in urims }

            for future in concurrent.futures.as_completed(future_to_urim):
                urim = future_to_urim[future]

                try:
                    language = future.result()
                    if language in desired_languages:
                        f.write("{}\n".format(urim))
                except Exception as exc:
                    logger.exception('URI-M [{}] generated an exception: [{}]'.format(urim, exc))
                    logger.critical("failed to detect language for [{}] quitting...".format(urim))
                    sys.exit(errno.EWOULDBLOCK)

    logger.info("done with language detection run, mementos in the languages of {} are in {}".format(desired_languages, args.output_filename))

def remove_near_duplicates(args):

    parser = argparse.ArgumentParser(
        description="Remove the near-duplicate documents from a collection.",
        prog="hc filter remove-near-duplicates"
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of near-duplicate documents...")

    session = get_web_session(cache_storage=args.cache_storage)

    urims = discover_mementos_by_input_type(
        args.input_type, args.input_arguments,
        args.crawl_depth, session
    )

    output_urims = filter_near_duplicates(urims, args.cache_storage)

    with open(args.output_filename, 'w') as f:

        for urim in output_urims:
            f.write('{}\n'.format(urim))

    logger.info("Completed detection of near-duplicates, output is saved to {}".format(args.output_filename))

def process_input_for_clusters_and_ranks(input_list):

    list_of_cluster_assignments = []

    for item in input_list:
        if '\t' in item:
            uri, clusterid, rank = item.split('\t')
            list_of_cluster_assignments.append( (clusterid, uri, rank) )

    if len(list_of_cluster_assignments) != len(input_list):

        raise HypercaneClusterInputException("The assignment of clusters to URIs in inconsistent")

    return list_of_cluster_assignments

def highest_ranking_per_cluster(args):

    parser = argparse.ArgumentParser(
        description="Remove the near-duplicate documents from a collection.",
        prog="hc filter remove-near-duplicates"
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting selection of the highest ranked documents in input...")

    urim_to_rank = {}
    cluster_to_urims = {}

    if args.input_type == "mementos":
        items = extract_uris_from_input(args.input_arguments)
        ranked_and_clustered_urims = process_input_for_clusters_and_ranks(items)

        for entry in ranked_and_clustered_urims:
            cluster = entry[0]
            urim = entry[1]
            rank = entry[2]

            urim_to_rank[urim] = rank
            cluster_to_urims.setdefault(cluster, []).append(urim)

    else:
        raise NotImplementedError(
            "Input type of {} not yet supported for ranking".format(
                args.input_type))

    output_urims = []

    for cluster in cluster_to_urims:

        cluster_ranks_to_urims = []

        for urim in cluster_to_urims[cluster]:
            cluster_ranks_to_urims.append( ( urim_to_rank[urim], urim ) )

        highest_scoring_urim_in_cluster = max(cluster_ranks_to_urims)[1]

        output_urims.append(highest_scoring_urim_in_cluster)

    with open(args.output_filename, 'w') as f:

        for urim in output_urims:
            f.write("{}\n".format(urim))

    logger.info("Finished selection of highest ranked documents in input; output is at {}".format(args.output_filename))

def print_usage():

    print("""'hc filter' is used to employ techniques to filter a web archive collection

    Supported commands:
    * remove-offtopic - for removing mementos that are off-topic
    * by-language - for keeping documents with a specific language
    * remove-near-duplicates - for removing near duplicate documents
    * highest-ranking-per-cluster - takes input from "hc rank" and produces a list of the identifiers of the highest ranking documents per cluster

    Examples:
    
    hc filter remove-offtopic -i archiveit=8788 -o ontopic-mementos.txt

    hc filter by-language -i archiveit=8788 --keep en,es -o english-and-spanish-docs.txt

    hc filter remove-near-duplicates -i mementos=ontopic-mementos.txt -o novel-content.txt

    hc filter highest-ranking-per-cluster -i mementos=file-with-scored-mementos.txt -o filtered-mementos.txt
    
""")

supported_commands = {
    "remove-offtopic": remove_offtopic,
    "by-language": by_language,
    "remove-near-duplicates": remove_near_duplicates,
    "highest-ranking-per-cluster": highest_ranking_per_cluster
}
