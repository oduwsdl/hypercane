import logging

module_logger = logging.getLogger("hypercane.actions.order")

def memento_datetime(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.order.memento_datetime import order_by_memento_datetime

    output_type = 'mementos'

    module_logger.info("Starting ordering of the documents by memento-datetime")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.input_type == "mementos":
        # urims = extract_uris_from_input(args.input_arguments)
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for ordering".format(args.input_type))

    module_logger.info("extracted {} mementos from input".format(len(urimdata.keys())))

    ordered_urims = order_by_memento_datetime(list(urimdata.keys()), args.cache_storage)

    module_logger.info("placed {} mementos in order".format(len(ordered_urims)))

    save_resource_data(args.output_filename, urimdata, 'mementos', ordered_urims)

    module_logger.info("Finished ordering documents, output is at {}".format(args.output_filename))

def pubdate_else_memento_datetime(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.order.dsa1_publication_alg import order_by_dsa1_publication_alg

    output_type = 'mementos'

    module_logger.info("Starting ordering of the documents by the DSA1 publication algorithm")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.input_type == "mementos":
        # urims = extract_uris_from_input(args.input_arguments)
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for ordering".format(args.input_type))

    module_logger.info("extracted {} mementos from input".format(len(urimdata.keys())))

    ordered_urims = order_by_dsa1_publication_alg(list(urimdata.keys()), args.cache_storage)

    module_logger.info("placed {} mementos in order".format(len(ordered_urims)))

    save_resource_data(args.output_filename, urimdata, 'mementos', ordered_urims)

    module_logger.info("Finished ordering documents, output is at {}".format(args.output_filename))

def score_sort(args):

    from hypercane.utils import save_resource_data, get_web_session

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    from hypercane.order.score import order_by_score

    output_type = 'mementos'

    module_logger.info("Starting ordering of the documents by their scores")

    session = get_web_session(cache_storage=args.cache_storage)

    if args.input_type == "mementos":
        # urims = extract_uris_from_input(args.input_arguments)
        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        # TODO: derive URI-Ms from input type
        raise NotImplementedError("Input type of {} not yet supported for ordering".format(args.input_type))

    if args.scoring_field is None:
        scoring_fields = list(urimdata[list(urimdata.keys())[0]].keys())
        scoring_field = scoring_fields[0]
    else:
        scoring_field = args.scoring_field

    module_logger.info("ordering by field {}".format(scoring_field))
    module_logger.info("extracted {} mementos from input".format(len(urimdata.keys())))

    ordered_urims = order_by_score(urimdata, args.descending, scoring_field)

    module_logger.info("placed {} mementos in order".format(len(ordered_urims)))

    save_resource_data(args.output_filename, urimdata, 'mementos', ordered_urims)

    module_logger.info("Finished ordering documents by score, output is at {}".format(args.output_filename))
