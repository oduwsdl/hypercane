import logging

from datetime import datetime

module_logger = logging.getLogger("hypercane.actions.sample")

def discover_timemaps(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_timemaps_by_input_type, generate_faux_urits, \
        discover_mementos_by_input_type

    output_type = 'timemaps'

    session = get_web_session(cache_storage=args.cache_storage)
    session.cache_storage = args.cache_storage

    module_logger.info("Starting timemap discovery run.")
    module_logger.info("Using {} for cache storage".format(args.cache_storage))

    if args.faux_tms_acceptable == True:

        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )

        urits = generate_faux_urits(list(urimdata.keys()), args.cache_storage)

        uritdata = {}
        for urit in urits:
            uritdata[urit] = {}

    else:
        uritdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_timemaps_by_input_type
        )

    save_resource_data(args.output_filename, uritdata, 'timemaps', list(uritdata.keys()))

    module_logger.info("Done with timemap discovery run. Output is in {}".format(
        args.output_filename))

def discover_original_resources(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_original_resources_by_input_type

    output_type = 'original-resources'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Starting original resource discovery run.")
    module_logger.info("Using {} for cache storage".format(args.cache_storage))

    urirdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_original_resources_by_input_type
    )

    save_resource_data(args.output_filename, urirdata, 'original-resources', list(urirdata.keys()))

    module_logger.info("Done with original resource discovery run. Output is in {}".format(args.output_filename))

def discover_mementos(args):

    from hypercane.utils import get_web_session, save_resource_data

    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Starting memento discovery run.")

    module_logger.info("Using {} for cache storage".format(args.cache_storage))

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type,
        accept_datetime=args.accept_datetime,
        timegates=args.timegates
    )

    module_logger.info("discovered {} mementos, preparing to write the list to {}".format(
        len(urimdata), args.output_filename))

    save_resource_data(args.output_filename, urimdata, 'mementos', list(urimdata.keys()))

    module_logger.info("Done with memento discovery run. Output is in {}".format(args.output_filename))
