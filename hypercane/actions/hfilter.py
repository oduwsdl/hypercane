import sys
import hypercane.errors

def process_remove_offtopic_args(args, parser):

    import otmt
    import argparse
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

    # print("storing errors in errorfile named {}".format(args.errorfilename))

    if args.errorfilename is not None:
        hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

    return args

def remove_offtopic(parser, args):

    import argparse
    from hypercane.actions import get_logger, calculate_loglevel
    from hypercane.utils import get_web_session
    from pymongo import MongoClient
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_timemaps_by_input_type, download_urits_and_extract_urims, \
        discover_mementos_by_input_type, generate_faux_urits
    from hypercane.hfilter.remove_offtopic import detect_off_topic
    from hypercane.utils import save_resource_data

    args = process_remove_offtopic_args(args, parser)
    processing_type = 'timemaps'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of off-topic documents...")

    session = get_web_session(cache_storage=args.cache_storage)
    dbconn = MongoClient(args.cache_storage)

    useFauxTimeMaps = False

    if args.input_type == 'mementos':
        # logger.warning(
        #     "Beware that an input type of 'mementos' may cause unexpected behavior. Specific mementos will be converted to TimeMaps and thus provide more mementos for consideration of off-topic analysis than were submitted."
        # )
        logger.warning("Beware that an input type of 'mementos' may cause unexpected behavior. If you want a full accounting of all mementos in each TimeMap, please run hc identify timemaps first and feed that list into this command. Otherwise, we will create 'faux TimeMaps' based on the mementos you submtted.")
        useFauxTimeMaps = True

    if useFauxTimeMaps == True:

        urimdata = discover_resource_data_by_input_type(
            args.input_type, processing_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )

        urims = list(urimdata.keys())
        urits = generate_faux_urits(urims, args.cache_storage)

    else:
        uritdata = discover_resource_data_by_input_type(
            args.input_type, processing_type, args.input_arguments, args.crawl_depth,
            session, discover_timemaps_by_input_type
        )

        urits = list(uritdata.keys())
        urims = download_urits_and_extract_urims(urits, session)

    logger.info("applying TimeMap measures {} to determine if mementos are off-topic".format(args.timemap_measures))

    ontopic_mementos = detect_off_topic(
        dbconn, session, urits, urims, args.timemap_measures,
        num_topics=args.num_topics, allow_noncompliant_archives=args.allow_noncompliant_archives)

    logger.info("discovered {} on-topic mementos".format(len(ontopic_mementos)))

    # when reading in TimeMap URIs and writing out mementos, the urimdata will not match
    urimdata = {}
    for urim in ontopic_mementos:
        urimdata[urim] = {}

    save_resource_data(args.output_filename, urimdata, 'mementos', ontopic_mementos)

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

    logger.info("Starting detection of near-duplicate mementos...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.debug("urimdata: {}".format(urimdata))

    urims = list(urimdata.keys())

    filtered_urims = filter_near_duplicates(urims, args.cache_storage)

    logger.info("writing {} to {}".format(filtered_urims, args.output_filename))

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
            if 'score' in key.lower():
                foundkeys.append(key)

        if len(foundkeys) > 0:
            if len(foundkeys) == 1:
                rankkey = foundkeys[0]
            else:
                raise ValueError(
                    "Too many score fields in the inputs."
                )
        else:
            raise ValueError(
                "The input file does not contain score information."
            )

    return rankkey

def include_score_range(args):

    import argparse
    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.utils import get_web_session
    from hypercane.utils import save_resource_data

    parser = argparse.ArgumentParser(
        description="Include only mementos containing a score meeting the given criteria.",
        prog="hc filter include-only score"
    )

    parser.add_argument('--criteria', default=1, dest='criteria',
        help="The numeric criteria to use when selecting which values to keep.",
        required=True
    )

    parser.add_argument('--scoring-field', help="Specify the scoring field to sort by, default is first encountered",
        default=None, dest='scoring_field'
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of documents meeting the criteria for score ...")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.crawl_depth > 1:
        logger.warning("Refusing to crawl when only analyzing prior score data")

    if args.input_type == 'mementos':
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, 1,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for filtering by score, score information must come from a prior execution of the score command".format(args.input_type))

    if args.scoring_field is None:
        scoring_fields = list(urimdata[list(urimdata.keys())[0]].keys())
        scoring_field = scoring_fields[0]
    else:
        scoring_field = args.scoring_field

    filtered_urims = []

    for urim in urimdata:
        if eval("{}{}".format(
            urimdata[urim][scoring_field], args.criteria
            )):
            filtered_urims.append(urim)

    logger.info("Saving {} filtered URI-Ms to {}".format(
        len(filtered_urims), args.output_filename))

    save_resource_data(
        args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("Done filtering mementos by score, output is saved to {}".format(
        args.output_filename
    ))

def include_largest_clusters(args):

    import argparse
    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.largest_cluster import return_largest_clusters
    from hypercane.utils import save_resource_data

    parser = argparse.ArgumentParser(
        description="Include only mementos from the largest clusters. Input must contain cluster information. If two clusters have the same size, the first listed in the input is returned.",
        prog="hc filter include-only largest-cluster"
    )

    parser.add_argument('--cluster-count', default=1, dest='cluster_count',
        help="The number of clusters' worth of mementos to returned, sorted descending by cluster size."
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of mementos in the largest cluster...")

    session = get_web_session(cache_storage=args.cache_storage)

    # TODO: add a note about no crawling for this filter
    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    filtered_urims = return_largest_clusters(urimdata, int(args.cluster_count))

    logger.info("returning largest cluster with {} mementos".format(len(filtered_urims)))

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("Completed detection of mementos in the largest cluster, output is in {}".format(
        args.output_filename
    ))

def include_highest_score_per_cluster(args):

    import argparse
    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.highest_rank_per_cluster import return_highest_ranking_memento_per_cluster
    from hypercane.utils import save_resource_data

    parser = argparse.ArgumentParser(
        description="Include only mementos with the highest score from each cluster.",
        prog="hc filter include-only highest-score-per-cluster"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of mementos with the highest score in each cluster...")

    session = get_web_session(cache_storage=args.cache_storage)

    # TODO: add a note about no crawling for this filter
    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    rankkey = extract_rank_key_from_input(urimdata)

    logger.info("using score key {}".format(rankkey))

    filtered_urims = return_highest_ranking_memento_per_cluster(urimdata, rankkey)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("Completed detection of mementos with the highest score in each cluster, output is in {}".format(
        args.output_filename
    ))

def start_containing_pattern(parser, args, include):

    import argparse
    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.utils import save_resource_data, get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.containing_pattern import filter_pattern

    parser.add_argument('--pattern', dest='pattern_string',
        help="The regular expression pattern to match (as Python regex)",
        required=True
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting filter of mementos containing pattern...")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urims = list(urimdata.keys())

    filtered_urims = filter_pattern(
        urims, args.cache_storage, args.pattern, include
    )

    save_resource_data(
        args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("done filtering mementos by pattern, output is in {}".format(args.output_filename))

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

def include_containing_pattern(args):

    import argparse

    parser = argparse.ArgumentParser(
        description="Include mementos containing the specified pattern after boilerplate removal.",
        prog="hc filter include containing-pattern"
    )

    start_containing_pattern(parser, args, True)

def include_urir(args):

    import argparse
    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.containing_urir import filter_by_urir
    from hypercane.utils import save_resource_data

    parser = argparse.ArgumentParser(
        description="Include only mementos with an original resource matching the given pattern.",
        prog="hc filter include-only containing-url-pattern"
    )

    parser.add_argument('--url-pattern', '--urir-pattern', dest='urir_pattern',
        help="The regular expression pattern of the URL to match (as Python regex)",
        required=True
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting detection of mementos whose original resource URL matches pattern {}...".format(args.urir_pattern))

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    urims = list(urimdata.keys())

    filtered_urims = filter_by_urir(urims, args.cache_storage, args.urir_pattern)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("Completed detection of mementos whose original resource URL matches pattern {}, output is in {}".format(
        args.urir_pattern, args.output_filename
    ))

def include_near_datetime(args):

    import argparse
    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.near_datetime import filter_by_memento_datetime
    from hypercane.utils import save_resource_data
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description="Include mementos whose memento-datetimes fall within the range of start-datetime and end-datetime.",
        prog="hc filter include-only near-datetime"
    )

    parser.add_argument('--start-datetime', '--lower-datetime',
        dest='lower_datetime',
        help="The lower bound datetime in YYYY-mm-ddTHH:MM:SS format.",
        required=True
    )

    parser.add_argument('--end-datetime', '--upper-datetime',
        dest='upper_datetime',
        help="The upper bound datetime in YYYY-mm-ddTHH:MM:SS format.",
        required=True
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting filtering of mementos by memento-datetime...")

    lower_datetime = datetime.strptime(
        args.lower_datetime,
        "%Y-%m-%dT%H:%M:%S"
    )

    upper_datetime = datetime.strptime(
        args.upper_datetime,
        "%Y-%m-%dT%H:%M:%S"
    )

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urims = list(urimdata.keys())

    filtered_urims = filter_by_memento_datetime(
        urims, args.cache_storage, lower_datetime, upper_datetime)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    logger.info("done filtering mementos by memento-datetime, output is in {}".format(args.output_filename))

def exclude_containing_pattern(args):

    import argparse
    from hypercane.utils import save_resource_data

    parser = argparse.ArgumentParser(
        description="Exclude mementos containing the specified pattern after boilerplate removal.",
        prog="hc filter include containing-pattern"
    )

    start_containing_pattern(parser, args, False)


def print_usage():

    print("""'hc filter' filters a web archive collection by different criteria

    Supported commands:
    * include-only - include mementos from the input that satisfy the given criteria
    * exclude - exclude mementos from the input by the given criteria

    Examples:

    hc filter include-only language --lang en,es -i archiveit -a 8788 -o english-and-spanish-docs.tsv -cs mongodb://localhost/cache

    hc filter exclude off-topic -i timemaps -a 8788-timemaps.tsv -o ontopic-mementos.tsv -cs mongodb://localhost/cache

    hc filter exclude near-duplicates -i mementos -a ontopic-mementos.tsv -o novel-content.tsv -cs mongodb://localhost/cache

    hc filter include-only score "=1" -i mementos -a file-with-scored-mementos.tsv -o filtered-mementos.tsv -cs mongodb://localhost/cache

""")

def print_include_usage():

    print("""'hc filter include-only' filters a web archive collection by only including mementos that satisfy the given criteria

    Supported commands:
    * languages - include mementos with the given languages (specified with --lang)
    * non-duplicates - employ Simhash to only include mementos that are not duplicates
    * on-topic - execute the Off-Topic Memento Toolkit to only include on-topic mementos
    * score - include only those mementos containing a score meeting the given criteria, supplied by the --criteria argument, requires that the input contains scoring information
    * highest-score-per-cluster - include only the highest ranking memento in each cluster, requires that the input contain clustered mementos
    * containing-pattern - include only mementos that contain the given regular experession pattern
    * near-datetime - include only mementos whose memento-datetime falls into the given range
    * containing-url-pattern - include only mementos whose original resource URL matches the given regular expression pattern
    * largest-clusters - include only the mementos from the largest cluster, requires that input contain clustered mementos

    Examples:

    hc filter include-only languages --lang en,es -i archiveit -a 8788 -o english-spanish-mementos.txt

    hc filter include-only on-topic -i timemaps -a uritfile.txt -o ontopic-mementos.txt

""")

def print_exclude_usage():

    print("""'hc filter exclude' filters a web archive collection by excluding mementos that satisfy the given criteria

    Supported commands:
    * languages - exclude mementos with the given languages (specified with --lang)
    * off-topic - execute the Off-Topic Memento Toolkit to exclude off-topic mementos
    * near-duplicates - employ Simhash to exclude mementos that are near-duplicates
    * containing-pattern - exclue mementos that contain the given regular experession pattern

    Examples:

    hc filter exclude languages --lang en,de -i archiveit -a 8788 -o nonenglish-nongerman-mementos.txt

    hc filter exclude containing_pattern --pattern 'cheese' -i mementos -a mementofile.tsv -o mementos-without-cheese.tsv

""")

include_criteria = {
    "language": include_languages,
    "languages": include_languages,
    "non-duplicates": include_nonduplicates,
    "on-topic": include_ontopic,
    "score": include_score_range,
    "highest-score-per-cluster": include_highest_score_per_cluster,
    "containing-pattern": include_containing_pattern,
    "near-datetime": include_near_datetime,
    "containing-url-pattern": include_urir,
    "largest-clusters": include_largest_clusters
}

exclude_criteria = {
    "language": exclude_languages,
    "languages": exclude_languages,
    "near-duplicates": exclude_nearduplicates,
    "off-topic": exclude_offtopic,
    "containing-pattern": exclude_containing_pattern
}


