import sys
import os
import argparse
import json
import otmt
import concurrent.futures
import langdetect
import errno

from pymongo import MongoClient
from guess_language import guess_language
from justext import justext, get_stoplist

from ..actions import add_input_args, add_default_args, \
    get_logger, calculate_loglevel, get_web_session
from ..identify import discover_timemaps_by_input_type, \
    discover_mementos_by_input_type, download_urits_and_extract_urims
from ..reduce.remove_offtopic import detect_off_topic, \
    HypercaneMementoCollectionModel, get_boilerplate_free_content

def process_input_args(args, parser):

    parser = add_input_args(parser)

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

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
        "(e.g., jaccard=0.10,cosine=0.15,wcount);\n"
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
        prog="hc reduce remove-offtopic"
    )

    args = process_remove_offtopic_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of off-topic documents...")

    input_type = args.input_type[0]
    input_args = args.input_type[1]

    session = get_web_session(cache_storage=args.cache_storage)

    dbconn = MongoClient(args.cache_storage)
    urits = discover_timemaps_by_input_type(
        input_type, input_args, args.crawl_depth, session)
    urims = download_urits_and_extract_urims(urits, session)
    cm = HypercaneMementoCollectionModel(dbconn, session)

    # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    #     future_to_url = {executor.submit(load_urim, urim, 60): urim for urim in urims}

    #     for future in concurrent.futures.as_completed(future_to_url):
    #         urim = future_to_url[future]

    logger.info("adding {} URI-Ts to collection model".format(
        len( urits )
    ))

    for urit in urits:
        cm.addTimeMap(urit)

    logger.info("adding URI-Ms from {} URI-Ts in collection model".format(
        len( cm.getTimeMapURIList() )
    ))

    for urim in urims:
        cm.addMemento(urim)

    # TOOD: what about document collections outside of web archives?
    # Note: these algorithms only work for collections with TimeMaps, 
    # so how would that work exactly?

    logger.info(
        "stored {} mementos for processing...".format(
            len(cm.getMementoURIList())
        )
    )

    ontopic_mementos = detect_off_topic(
        cm, args.timemap_measures, num_topics=args.num_topics)

    logger.info("discovered {} on-topic mementos".format(len(ontopic_mementos)))

    with open(args.output_filename, 'w') as f:
        for urim in ontopic_mementos:
            f.write("{}\n".format(urim))

    logger.info("done with off-topic run, on-topic mementos are in {}".format(args.output_filename))



def get_language(urim, cache_storage):

    dbconn = MongoClient(cache_storage)
    # session = get_web_session(cache_storage)
    db = dbconn.get_default_database()

    # 1 if lang of urim in cache, return it
    try:
        return db.derivedvalues.find_one(
            { "urim": urim }
        )["language"]
    except (KeyError, TypeError):
        
        content = get_boilerplate_free_content(
            urim, cache_storage=cache_storage, dbconn=dbconn
        )

        language = guess_language(content)

        db.derivedvalues.update(
            { "urim": urim },
            { "$set": { "language": language }},
            upsert=True
        )
    
        return language

def by_language(args):

    parser = argparse.ArgumentParser(
        description="Only keep documents from a collection with a specific language.",
        prog="hc reduce by-language"
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

    input_type = args.input_type[0]
    input_args = args.input_type[1]

    session = get_web_session(cache_storage=args.cache_storage)

    urims = discover_mementos_by_input_type(
        input_type, input_args, args.crawl_depth, session
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
        prog="hc reduce remove-near-duplicates"
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of near-duplicate documents...")

    input_type = args.input_type[0]
    input_args = args.input_type[1]

    session = get_web_session(cache_storage=args.cache_storage)

    dbconn = MongoClient(args.cache_storage)

    urims = discover_mementos_by_input_type(
        input_type, input_args, args.crawl_depth, session
    )

    logger.info("discovered {} mementos in input, downloading or extracting from cache...".format(len(urims)))

    cm = HypercaneMementoCollectionModel(dbconn, session)
    cm.addManyMementos(urims)

    logger.info("computing Simhashes on documents...")
    simhashes = []
    for urim in urims:
        simhash = cm.getRawSimhash(urim)
        simhashes.append(simhash)

    logger.info("using {} Simahshes to remove duplicates from output...".format(len(simhashes)))
    output_urims = []
    for simhash in simhashes:
        firsturim = cm.getFirstURIMByRawSimhash(simhash)
        output_urims.append( firsturim )

    with open(args.output_filename, 'w') as f:

        for urim in output_urims:
            f.write('{}\n'.format(urim))

    logger.info("Completed detection of near-duplicates, output is saved to {}".format(args.output_filename))

def print_usage():

    print("""'hc reduce' is used to employ techniques to reduce a web archive collection, document collection, a list of TimeMaps, or a directory containing WARCs

    Supported commands:
    * remove-offtopic - for removing mementos that are off-topic
    * by-language - for keeping documents with a specific language
    * remove-near-duplicates - for removing near duplicate documents

    Examples:
    
    hc reduce remove-offtopic -i archiveit=8788 -o ontopic-mementos.txt

    hc reduce by-language -i archiveit=8788 --keep en,es -o english-and-spanish-docs.txt

    hc reduce remove-near-duplicates -i mementos=ontopic-mementos.txt -o novel-content.txt
    
""")

supported_commands = {
    "remove-offtopic": remove_offtopic,
    "by-language": by_language,
    "remove-near-duplicates": remove_near_duplicates
}
