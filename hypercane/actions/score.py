import logging

module_logger = logging.getLogger("hypercane.actions.score")

def score_by_top_entities_and_bm25(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.bm25 import bm25_by_entites

    # TODO: make this configurable
    default_entity_types = ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW']

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by BM25")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = bm25_by_entites(
        urimdata, session, args.cache_storage, args.k, default_entity_types
    )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished scoring by BM25, output is at {}".format(args.output_filename))

def bm25_ranking(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.bm25 import rank_by_bm25

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by BM25")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = rank_by_bm25(
        urimdata, session, args.query, args.cache_storage
    )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished scoring by BM25, output is at {}".format(args.output_filename))

def dsa1_scoring(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.dsa1_score import rank_by_dsa1_score

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by DSA1 scoring equation")

    if args.input_type == "mementos":
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for scoring".format(
            args.input_type))

    urimdata = rank_by_dsa1_score(
        urimdata, session,
        memento_damage_url=args.memento_damage_url,
        damage_weight=float(args.damage_weight),
        category_weight=float(args.category_weight),
        path_depth_weight=float(args.path_depth_weight)
        )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished ranking by DSA1 scoring equation, output is at {}".format(args.output_filename))

def dsa2_scoring(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.dsa2_score import score_by_dsa2_score

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by DSA2 scoring equation")

    if args.input_type == "mementos":
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for scoring".format(
            args.input_type))

    urimdata = score_by_dsa2_score(
        urimdata, args.cache_storage,
        card_weight=float(args.card_weight),
        size_weight=float(args.size_weight),
        image_count_weight=float(args.image_count_weight)
        )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished ranking by DSA2 scoring equation, output is at {}".format(args.output_filename))

def image_count_scoring(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.image_count import score_by_image_count

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by image count")

    if args.input_type == "mementos":
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for scoring".format(
            args.input_type))

    module_logger.info("using session {}".format(session))
    module_logger.info("using cache storage: {}".format(args.cache_storage))

    urimdata = score_by_image_count(
        urimdata, session
    )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished scoring by image count, output is at {}".format(args.output_filename))

def simple_card_scoring(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.card_score import compute_simple_card_scores

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by image count")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("using session {}".format(session))
    module_logger.info("using cache storage: {}".format(args.cache_storage))

    urimdata = compute_simple_card_scores(urimdata, session)

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished scoring by card-score, output is at {}".format(args.output_filename))

def path_depth_scoring(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.dsa1_score import score_by_path_depth

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by DSA1 scoring equation")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = score_by_path_depth(
        urimdata, session
    )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished ranking by path depth, output is at {}".format(args.output_filename))

def category_scoring(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.dsa1_score import score_by_category

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by URL category equation")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = score_by_category(
        urimdata, session
        )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished scoring by URL category, output is at {}".format(args.output_filename))

def score_by_distance_from_centroid(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.distance_from_centroid import compute_distance_from_centroid

    # TODO: an ignore outliers option to run DBSCAN instead of kmeans

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by distance from centroid category equation")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = compute_distance_from_centroid(urimdata, args.cache_storage, more_similar=args.more_similar)

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished scoring by cluster distance, output is at {}".format(args.output_filename))

def score_by_size(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.document_size import compute_boilerplate_free_character_size, \
        compute_character_size

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Beginning the scoring by mementy by size with feature {}".format(args.feature))

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    if args.feature == 'bytes':
        urimdata = compute_character_size(urimdata, args.cache_storage, bytes=True)

    elif args.feature == 'characters':
        urimdata = compute_character_size(urimdata, args.cache_storage, bytes=False)

    elif args.feature == 'boilerplate-free-characters':
        urimdata = compute_boilerplate_free_character_size(urimdata, args.cache_storage, unit='characters')

    elif args.feature == 'words':
        urimdata = compute_boilerplate_free_character_size(urimdata, args.cache_storage, unit='words')

    elif args.feature == 'sentences':
        urimdata = compute_boilerplate_free_character_size(urimdata, args.cache_storage, unit='sentences')

    else:
        raise NotImplementedError("Feature '{}' not yet implemented with this score".format(args.feature))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Finished scoring by size with feature {}, output is at {}".format(args.feature, args.output_filename))
