import logging

module_logger = logging.getLogger("hypercane.actions.hfilter")

def remove_offtopic(args):

    from hypercane.utils import get_web_session
    from pymongo import MongoClient
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_timemaps_by_input_type, download_urits_and_extract_urims, \
        discover_mementos_by_input_type, generate_faux_urits
    from hypercane.hfilter.remove_offtopic import detect_off_topic
    from hypercane.utils import save_resource_data

    processing_type = 'timemaps'

    module_logger.info("Starting detection of off-topic documents...")

    module_logger.info("using cache storage at {}".format(args.cache_storage))

    session = get_web_session(cache_storage=args.cache_storage)
    dbconn = MongoClient(args.cache_storage)

    useFauxTimeMaps = False

    if args.input_type == 'mementos':
        # logger.warning(
        #     "Beware that an input type of 'mementos' may cause unexpected behavior. Specific mementos will be converted to TimeMaps and thus provide more mementos for consideration of off-topic analysis than were submitted."
        # )
        module_logger.warning("Beware that an input type of 'mementos' may cause unexpected behavior. If you want a full accounting of all mementos in each TimeMap, please run hc identify timemaps first and feed that list into this command. Otherwise, we will create 'faux TimeMaps' based on the mementos you submtted.")
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

    module_logger.info("applying TimeMap measures {} to determine if mementos are off-topic".format(args.timemap_measures))

    ontopic_mementos = detect_off_topic(
        dbconn, session, urits, urims, args.timemap_measures,
        num_topics=args.num_topics, allow_noncompliant_archives=args.allow_noncompliant_archives)

    module_logger.info("discovered {} on-topic mementos".format(len(ontopic_mementos)))

    # when reading in TimeMap URIs and writing out mementos, the urimdata will not match
    urimdata = {}
    for urim in ontopic_mementos:
        urimdata[urim] = {}

    save_resource_data(args.output_filename, urimdata, 'mementos', ontopic_mementos)

    module_logger.info("done with off-topic run, on-topic mementos are in {}".format(args.output_filename))

def remove_near_duplicates(args):

    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.near_duplicates import filter_near_duplicates
    from hypercane.utils import save_resource_data

    output_type = 'mementos'

    module_logger.info("Starting filter of near-duplicate mementos...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.debug("urimdata: {}".format(urimdata))

    urims = list(urimdata.keys())

    filtered_urims = filter_near_duplicates(urims, args.cache_storage, use_faux_TimeMaps=args.allow_noncompliant_archives)

    module_logger.info("writing {} to {}".format(filtered_urims, args.output_filename))

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    module_logger.info("Completed detection of near-duplicates, output is saved to {}".format(args.output_filename))

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
                rankkey = foundkeys[-1]

        else:
            raise ValueError(
                "The input file does not contain score information."
            )

    return rankkey

def include_score_range(args):

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.utils import get_web_session
    from hypercane.utils import save_resource_data

    output_type = 'mementos'

    module_logger.info("Starting detection of documents meeting the criteria for score ...")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.crawl_depth > 1:
        module_logger.warning("Refusing to crawl when only analyzing prior score data")

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

    module_logger.info("Saving {} filtered URI-Ms to {}".format(
        len(filtered_urims), args.output_filename))

    save_resource_data(
        args.output_filename, urimdata, 'mementos', filtered_urims)

    module_logger.info("Done filtering mementos by score, output is saved to {}".format(
        args.output_filename
    ))

def exclude_containing_cluster_id(args):

    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.utils import save_resource_data
    from hypercane.hfilter.by_clusterid import exclude_by_cluster_id

    output_type = 'mementos'

    module_logger.info("Starting filtering of mementos with cluster ID {}...".format(args.cluster_id))

    session = get_web_session(cache_storage=args.cache_storage)

    # TODO: add a note about no crawling for this filter
    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    filtered_urims = exclude_by_cluster_id(urimdata, args.cluster_id, args.match_subclusters)

    module_logger.info("returning {} mementos that do not belong to cluster {}".format(len(filtered_urims), args.cluster_id))

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    module_logger.info("Completed filtering of mementos with cluster ID {}, output is in {}".format(
        args.cluster_id, args.output_filename
    ))

def include_largest_clusters(args):

    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.largest_cluster import return_largest_clusters
    from hypercane.utils import save_resource_data

    output_type = 'mementos'

    module_logger.info("Starting detection of mementos in the largest cluster...")

    session = get_web_session(cache_storage=args.cache_storage)

    # TODO: add a note about no crawling for this filter
    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    filtered_urims = return_largest_clusters(urimdata, int(args.cluster_count))

    module_logger.info("returning largest cluster with {} mementos".format(len(filtered_urims)))

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    module_logger.info("Completed detection of mementos in the largest cluster, output is in {}".format(
        args.output_filename
    ))

def include_highest_score_per_cluster(args):

    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.highest_rank_per_cluster import return_highest_ranking_memento_per_cluster
    from hypercane.utils import save_resource_data

    output_type = 'mementos'

    module_logger.info("Starting detection of mementos with the highest score in each cluster...")

    session = get_web_session(cache_storage=args.cache_storage)

    # TODO: add a note about no crawling for this filter
    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    if args.score_key is None:
        rankkey = extract_rank_key_from_input(urimdata)
    else:
        rankkey = args.score_key

    module_logger.info("using score key {}".format(rankkey))

    filtered_urims = return_highest_ranking_memento_per_cluster(urimdata, rankkey)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    module_logger.info("Completed detection of mementos with the highest score in each cluster, output is in {}".format(
        args.output_filename
    ))

def start_containing_pattern(args, include):

    from hypercane.utils import save_resource_data, get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.containing_pattern import filter_pattern

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Starting filter of mementos containing pattern...")

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

    module_logger.info("done filtering mementos by pattern, output is in {}".format(args.output_filename))

def include_languages(args):

    from hypercane.hfilter.languages import filter_languages,language_included
    from hypercane.utils import save_resource_data
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    output_type = 'mementos'

    module_logger.info("Starting filtering of mementos by languages...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urims = list(urimdata.keys())

    module_logger.info("discovered {} mementos in input, downloading or extracting from cache...".format(len(urims)))

    desired_languages = [ i.strip() for i in args.languages.split(',')]
    module_logger.info("comparing languages of documents with requested languages of {}...".format(desired_languages))

    filtered_urims = filter_languages(
        urims, args.cache_storage, desired_languages, language_included)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    module_logger.info("done, mementos including the languages of {} are in {}".format(desired_languages, args.output_filename))

def exclude_languages(args):

    from hypercane.hfilter.languages import filter_languages, language_not_included
    from hypercane.utils import save_resource_data
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    output_type = 'mementos'

    module_logger.info("Starting filtering of mementos by languages...")

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urims = list(urimdata.keys())

    module_logger.info("discovered {} mementos in input, downloading or extracting from cache...".format(len(urims)))

    desired_languages = [ i.strip() for i in args.languages.split(',')]
    module_logger.info("comparing languages of documents with requested languages of {}...".format(desired_languages))

    filtered_urims = filter_languages(
        urims, args.cache_storage, desired_languages, language_not_included)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    module_logger.info("done, mementos not including the languages of {} are in {}".format(desired_languages, args.output_filename))

def include_containing_pattern(args):

    start_containing_pattern(args, True)

def include_urir(args):

    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.containing_urir import filter_by_urir
    from hypercane.utils import save_resource_data

    output_type = 'mementos'

    module_logger.info("Starting detection of mementos whose original resource URL matches pattern {}...".format(args.urir_pattern))

    session = get_web_session(cache_storage=args.cache_storage)

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, 1,
        session, discover_mementos_by_input_type
    )

    urims = list(urimdata.keys())

    filtered_urims = filter_by_urir(urims, args.cache_storage, args.urir_pattern)

    save_resource_data(args.output_filename, urimdata, 'mementos', filtered_urims)

    module_logger.info("Completed detection of mementos whose original resource URL matches pattern {}, output is in {}".format(
        args.urir_pattern, args.output_filename
    ))

def include_near_datetime(args):

    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.hfilter.near_datetime import filter_by_memento_datetime
    from hypercane.utils import save_resource_data
    from datetime import datetime

    output_type = 'mementos'

    module_logger.info("Starting filtering of mementos by memento-datetime...")

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

    module_logger.info("done filtering mementos by memento-datetime, output is in {}".format(args.output_filename))

def exclude_containing_pattern(args):

    start_containing_pattern(args, False)


