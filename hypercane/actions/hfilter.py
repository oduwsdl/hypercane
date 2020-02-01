import sys


def process_remove_offtopic_args(args, parser):

    import otmt
    from hypercane.actions import add_input_args, add_default_args

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

def remove_offtopic(parser, args):

    from hypercane.actions import get_logger, calculate_loglevel
    from hypercane.utils import get_web_session
    from pymongo import MongoClient
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_timemaps_by_input_type, download_urits_and_extract_urims
    from hypercane.hfilter.remove_offtopic import detect_off_topic

    args = process_remove_offtopic_args(args, parser)
    output_type = 'timemaps'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of off-topic documents...")

    session = get_web_session(cache_storage=args.cache_storage)
    dbconn = MongoClient(args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_timemaps_by_input_type
    )

    urits = list(urimdata.keys())
    urims = download_urits_and_extract_urims(urits, session)

    ontopic_mementos = detect_off_topic(
        dbconn, session, urits, urims, args.timemap_measures, 
        num_topics=args.num_topics)

    logger.info("discovered {} on-topic mementos".format(len(ontopic_mementos)))

    with open(args.output_filename, 'w') as f:
        for urim in ontopic_mementos:
            f.write("{}\n".format(urim))

    logger.info("done with off-topic run, on-topic mementos are in {}".format(args.output_filename))

def exclude_offtopic(args):
    
    import argparse

    parser = argparse.ArgumentParser(
        description="Filter the off-topic mementos from a collection.",
        prog="hc filter exclude off-topic"
    )

    remove_offtopic(parser, args)

def include_ontopic(args):

    import argparse

    parser = argparse.ArgumentParser(
        description="Include only the on-topic mementos from a collection.",
        prog="hc filter include-only on-topic"
    )

    remove_offtopic(parser, args)

def remove_near_duplicates(parser, args):

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.near_duplicates import filter_near_duplicates
    from hypercane.utils import save_resource_data

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of near-duplicate documents...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urims = list(urimdata.keys())

    filtered_urims = filter_near_duplicates(urims, args.cache_storage)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("Completed detection of near-duplicates, output is saved to {}".format(args.output_filename))

def include_nonduplicates(args):

    import argparse

    parser = argparse.ArgumentParser(
        description="Remove the near-duplicate documents from a collection.",
        prog="hc filter include-only non-duplicates"
    )
    
    remove_near_duplicates(parser, args)

def exclude_nearduplicates(args):

    import argparse

    parser = argparse.ArgumentParser(
        description="Remove the near-duplicate documents from a collection.",
        prog="hc filter exclude near-duplicates"
    )
    
    remove_near_duplicates(parser, args)

def extract_rank_key_from_input(urimdata):

    for urim in urimdata:
        foundkeys = []
        for key in urimdata[urim]:
            if 'rank' in key.lower():
                foundkeys.append(key)

        if len(foundkeys) > 0:
            if len(foundkeys) == 1:
                rankkey = foundkeys[0]
            else:
                raise ValueError(
                    "Too many rank fields in the inputs."
                )
        else:
            raise ValueError(
                "The input file does not contain rank information."
            )

    return rankkey

def include_rank(args):

    import argparse
    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.utils import get_web_session
    from hypercane.utils import save_resource_data

    parser = argparse.ArgumentParser(
        description="Include only mementos containing a rank meeting the given criteria.",
        prog="hc filter include-only rank"
    )

    parser.add_argument('--criteria', default=1, dest='criteria',
        help="The numeric criteria to use when selecting which values to keep."
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of documents meeting the criteria for rank ...")

    session = get_web_session(cache_storage=args.cache_storage)

    # TODO: add a note about no crawling for this filter
    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    rankkey = extract_rank_key_from_input(urimdata)

    filtered_urims = []

    for urim in urimdata:
        if eval("{}{}".format(
            urimdata[urim][rankkey], args.criteria
            )):
            filtered_urims.append(urim)

    logger.info("Saving {} filtered URI-Ms to {}".format(
        len(filtered_urims), args.output_filename))

    save_resource_data(
        args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("Done filtering mementos by rank, output is saved to {}".format(
        args.output_filename
    ))


def exclude_rank(args):

    import argparse
    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.utils import get_web_session
    from hypercane.utils import save_resource_data

    parser = argparse.ArgumentParser(
        description="Include only mementos containing a rank meeting the given criteria.",
        prog="hc filter include-only rank"
    )

    parser.add_argument('--criteria', default=1, dest='criteria',
        help="The numeric criteria to use when selecting which values to keep."
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of documents meeting the criteria for rank ...")

    session = get_web_session(cache_storage=args.cache_storage)

    # TODO: add a note about no crawling for this filter
    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    rankkey = extract_rank_key_from_input(urimdata)

    filtered_urims = []

    for urim in urimdata:
        if not eval("{}{}".format(
            urimdata[urim][rankkey], args.criteria
            )):
            filtered_urims.append(urim)

    logger.info("Saving {} filtered URI-Ms to {}".format(
        len(filtered_urims), args.output_filename))

    save_resource_data(
        args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("Done filtering mementos by rank, output is saved to {}".format(
        args.output_filename
    ))

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

    Supported commands:
    * on-topic - execute the Off-Topic Memento Toolkit to only include on-topic mementos
    * non-duplicates - employ Simhash to only include mementos that are not duplicates
    * language - include mementos with the given languages (specified with --lang)
    * rank - include mementos with the given rank value (requires output from hc rank)

    Examples:
    
    hc filter include-only language en,es -i archiveit=8788 -o ontopic-mementos.txt

    hc filter include-only rank "=1" -i mementos=file-with-scored-mementos.txt -o filtered-mementos.txt
    
""")

def print_exclude_usage():

    print("""'hc filter exclude' is used to employ techniques to filter a web archive collection by excluding mementos that satisfy the given criteria

    Supported commands:
    * off-topic - execute the Off-Topic Memento Toolkit to exclude off-topic mementos
    * near-duplicates - employ Simhash to exclude mementos that are near-duplicates
    * language - exclude mementos with the given languages (specified with --lang)
    * rank - include mementos with the given rank value (requires output from hc rank)

    Examples:
    
    hc filter exclude language en,de -i archiveit=8788 -o ontopic-mementos.txt

    hc filter exclude rank ">1" -i mementos=file-with-scored-mementos.txt -o filtered-mementos.txt
    
""")

include_criteria = {
    "languages": include_languages,
    "non-duplicates": include_nonduplicates,
    "on-topic": include_ontopic,
    "rank": include_rank
}

exclude_criteria = {
    "languages": exclude_languages,
    "near-duplicates": exclude_nearduplicates,
    "off-topic": exclude_offtopic,
    "rank": exclude_rank
}


