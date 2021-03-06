import sys

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

    from hypercane.score.dsa1_ranking import rank_by_dsa1_score

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
        damage_weight=args.damage_weight,
        category_weight=args.category_weight,
        path_depth_weight=args.path_depth_weight
        )

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    logger.info("Finished ranking by DSA1 scoring equation, output is at {}".format(args.output_filename))

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
    * dsa1-scoring - score the documents according to the scoring function of AlNoamany's Algorithm
    * bm25 - score documents according to the input query
    * image-count - score by the number of images in each document

    Examples:

    hc score dsa1-scoring -i mementos -a input_mementos.tsv -o scored_mementos.tsv -cs mongodb://localhost/cache

""")

supported_commands = {
    "dsa1-scoring": dsa1_scoring,
    "bm25": bm25_ranking,
    "image-count": image_count_scoring,
    # "textrank": textrank_scoring
}

