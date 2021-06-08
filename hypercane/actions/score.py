def score_by_top_entities_and_bm25(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.bm25 import bm25_by_entites

    parser = argparse.ArgumentParser(
        description="Score the input using the top k entities as a query to BM25.",
        prog="hc score top-entities-and-bm25"
    )

    parser.add_argument('-k', dest='k',
        required=False, help="The number of top entities to use", 
        default=10
    )

    # TODO: make this configurable
    default_entity_types = ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW']

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by BM25")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = bm25_by_entites(
        urimdata, session, args.cache_storage, args.k, default_entity_types
    )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished scoring by BM25, output is at {}".format(args.output_filename))

def bm25_ranking(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.bm25 import rank_by_bm25

    parser = argparse.ArgumentParser(
        description="Score the input using a query and the BM25 algorithm.",
        prog="hc score bm25"
    )

    parser.add_argument('--query', dest='query',
        required=True, help="The query to use with BM25"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by BM25")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = rank_by_bm25(
        urimdata, session, args.query, args.cache_storage
    )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished scoring by BM25, output is at {}".format(args.output_filename))



def dsa1_scoring(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.dsa1_score import rank_by_dsa1_score

    parser = argparse.ArgumentParser(
        description="Score the input using the DSA1 scoring equation.",
        prog="hc score dsa1-scoring"
    )

    parser.add_argument('--memento-damage-url', dest='memento_damage_url',
        default=None,
        help="The URL of the Memento-Damage service to use for scoring."
    )

    parser.add_argument('--damage-weight', dest='damage_weight',
        default=-0.40, type=float,
        help="The weight for the Memento-Damage score in the scoring."
    )

    parser.add_argument('--category-weight', dest='category_weight',
        default=0.15, type=float,
        help="The weight for the URI-R category score in the scoring."
    )

    parser.add_argument('--path-depth-weight', dest='path_depth_weight',
        default=0.45, type=float,
        help="The weight for the URI-R path depth score in the scoring."
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by DSA1 scoring equation")

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

    logger.info("Finished ranking by DSA1 scoring equation, output is at {}".format(args.output_filename))

def dsa2_scoring(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.dsa2_score import score_by_dsa2_score

    parser = argparse.ArgumentParser(
        description="Score the input using the DSA2 scoring equation.",
        prog="hc score dsa2-scoring"
    )

    parser.add_argument('--card-weight', dest='card_weight',
        default=-0.50, type=float,
        help="The weight for how well a page can produce a card."
    )

    parser.add_argument('--size-weight', dest='size_weight',
        default=0.25, type=float,
        help="The weight for the size of the content, in case a card is not possible."
    )

    parser.add_argument('--image-count-weight', dest='image_count_weight',
        default=0.25, type=float,
        help="The weight for number of images, in case a card is not possible."
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by DSA2 scoring equation")

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

    logger.info("Finished ranking by DSA2 scoring equation, output is at {}".format(args.output_filename))

def image_count_scoring(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.image_count import score_by_image_count

    parser = argparse.ArgumentParser(
        description="Score the input using the number of images detected in each memento.",
        prog="hc score image-count"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by image count")

    if args.input_type == "mementos":
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for scoring".format(
            args.input_type))

    logger.info("using session {}".format(session))
    logger.info("using cache storage: {}".format(args.cache_storage))

    urimdata = score_by_image_count(
        urimdata, session
    )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished scoring by image count, output is at {}".format(args.output_filename))

def simple_card_scoring(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.card_score import compute_simple_card_scores

    parser = argparse.ArgumentParser(
        description="Score the input by how well it would create a card on Facebook and Twitter.",
        prog="hc score card-score"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by image count")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("using session {}".format(session))
    logger.info("using cache storage: {}".format(args.cache_storage))

    urimdata = compute_simple_card_scores(urimdata, session)

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished scoring by card-score, output is at {}".format(args.output_filename))

def path_depth_scoring(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.dsa1_score import score_by_path_depth

    parser = argparse.ArgumentParser(
        description="Score the input using the path depth of the URI-R of each memento.",
        prog="hc score path-depth"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by DSA1 scoring equation")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = score_by_path_depth(
        urimdata, session
        )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished ranking by path depth, output is at {}".format(args.output_filename))

def category_scoring(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.dsa1_score import score_by_category

    parser = argparse.ArgumentParser(
        description="Score the input using the path depth of the URI-R of each memento.",
        prog="hc score url-category-score"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by URL category equation")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = score_by_category(
        urimdata, session
        )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished scoring by URL category, output is at {}".format(args.output_filename))

def score_by_distance_from_centroid(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.distance_from_centroid import compute_distance_from_centroid

    parser = argparse.ArgumentParser(
        description="Score the input by computing each cluster's TF-IDF cluster center and the computing the distance from that center. A higher score is farther from the other documents and hence more unique. Use --more-similar to reverse this.",
        prog="hc score distance-from-centroid"
    )

    parser.add_argument('--more-similar', dest='more_similar',
        action='store_true',
        help='This will subtract all scores by 0 so that highest means more similar and not more unique.'
    )

    # TODO: an ignore outliers option to run DBSCAN instead of kmeans

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by distance from centroid category equation")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    urimdata = compute_distance_from_centroid(urimdata, args.cache_storage, more_similar=args.more_similar)

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished scoring by cluster distance, output is at {}".format(args.output_filename))

def score_by_size(args):

    import argparse

    from hypercane.actions import process_input_args, get_logger, \
        calculate_loglevel

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.score.document_size import compute_boilerplate_free_character_size, \
        compute_character_size

    parser = argparse.ArgumentParser(
        description="Score the input by size.",
        prog="hc score size"
    )

    parser.add_argument('--feature', dest='feature',
        required=False, help="The feature to score with, options are: 'bytes', 'characters', 'boilerplate-free-characters', 'words', 'sentences'", 
        default="bytes"
    )

    # TODO: an ignore outliers option to run DBSCAN instead of kmeans

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Beginning the scoring by mementy by size with feature {}".format(args.feature))

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

    logger.info("Finished scoring by size with feature {}, output is at {}".format(args.feature, args.output_filename))


# def textrank_scoring(args):

#     import argparse

#     from hypercane.actions import process_input_args, get_logger, \
#         calculate_loglevel

#     from hypercane.utils import get_web_session, save_resource_data

#     from hypercane.identify import discover_resource_data_by_input_type, \
#         discover_mementos_by_input_type

#     from hypercane.score.textrank import score_by_textrank

#     parser = argparse.ArgumentParser(
#         description="Score the input using the Gensim TextRank algorithm.",
#         prog="hc score image-count"
#     )

#     args = process_input_args(args, parser)
#     output_type = 'mementos'

#     logger = get_logger(
#         __name__,
#         calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
#         args.logfile
#     )

#     session = get_web_session(cache_storage=args.cache_storage)

#     logger.info("Beginning the scoring by image count")

#     if args.input_type == "mementos":
#         urimdata = discover_resource_data_by_input_type(
#             args.input_type, output_type, args.input_arguments, args.crawl_depth,
#             session, discover_mementos_by_input_type
#         )
#     else:
#         # TODO: derive URI-Ms from input type
#         raise NotImplementedError("Input type of {} not yet supported for scoring".format(
#             args.input_type))

#     logger.info("using session {}".format(session))
#     logger.info("using cache storage: {}".format(args.cache_storage))

#     urimdata = score_by_textrank(urimdata, args.cache_storage)

#     save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

#     logger.info("done scoring by Textrank, output is at: {}".format(args.output_filename))

def print_usage():

    print("""'hc score' is used to employ techniques that score the mementos in a web archive collection

    Supported commands:
    * dsa1-scoring - score the documents according to the scoring function of AlNoamany's Algorithm (https://doi.org/10.1145/3091478.3091508)
    * bm25 - score documents according to the input query with BM25
    * image-count - score by the number of images in each document
    * simple-card-score - score by how well the memento creates a social card on Facebook and Twitter
    * path-depth - score by path depth, as defined by McCown et al. (https://arxiv.org/abs/cs/0511077)
    * url-category-score - score by the categories from Padia et al. (https://doi.org/10.1145/2232817.2232821)
    * top-entites-and-bm25 - score by the top k entities and BM25
    * distance-from-centroid - score by the distance of each memento from the center of its cluster
    * size - score by the size of each memento

    Examples:

    hc score dsa1-scoring -i mementos -a input_mementos.tsv -o scored_mementos.tsv -cs mongodb://localhost/cache

    hc score bm25 -i mementos -a input_mementos.tsv -o scored_mementos.tsv -cs mongodb://localhost/cache --query cheese

    hc score simple-card-score -i pandora-subject -a 82 -o scored_mementos.tsv -cs mongodb://localhost/cache

    hc score path-depth -i timemap -a input_timemaps.tsv -o scored_mementos.tsv -cs mongodb://localhost/cache

""")

supported_commands = {
    "dsa1-scoring": dsa1_scoring,
    "bm25": bm25_ranking,
    "image-count": image_count_scoring,
    "simple-card-score": simple_card_scoring,
    "path-depth": path_depth_scoring,
    "url-category-score": category_scoring,
    "top-entities-and-bm25": score_by_top_entities_and_bm25,
    "distance-from-centroid": score_by_distance_from_centroid,
    "size": score_by_size,
    "dsa2-scoring": dsa2_scoring
    # "textrank": textrank_scoring
}

