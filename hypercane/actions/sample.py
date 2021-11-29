import logging

module_logger = logging.getLogger("hypercane.actions.sample")

def sample_with_custom_script(args):

    import sys
    import os
    import errno
    import subprocess

    module_logger.info("Starting sampling with algorithm {}".format(args.which))
   
    # we will not honor crawl depth -- log this if specified
    if args.crawl_depth > 1:
        module_logger.warning("ignoring crawl depth setting of {}".format(args.crawl_depth))

    if args.errorfilename == 'hypercane-errors.dat':
        module_logger.warning(
            "ignoring error filename of {}, individual error files for each step will be in {}".format(
                args.errorfilename, args.working_directory))

    other_args = ""
    for argname, argvalue in vars(args).items():
        if argname not in [
            'input_file',
            'input_type',
            'input_arguments',
            'cache_storage',
            'working_directory',
            'output_filename',
            'logfile',
            'verbose',
            'quiet',
            'crawl_depth',
            'which',
            'exec',
            'script_path',
            'errorfilename',
            'sampling method (e.g., true-random, dsa1)',
            'allow_noncompliant_archives',
            'collection_id'
        ]:
            # print(argname)
            if argvalue is not None:
                other_args += argname + " " + argvalue

    module_logger.info("running custom script {}".format(args.script_path))
    module_logger.info("log messages for each step may be stored in separate log files available in {}".format(args.working_directory))
    module_logger.info("additional supplied to script: {}".format(other_args))

    command = [
        "/bin/bash",
        args.script_path,
        args.input_type,
        args.input_arguments,
        args.output_filename,
        args.working_directory,
        other_args
    ]

    module_logger.info("running command line: {}".format(command))

    cp = subprocess.run(command)

    if cp.returncode != 0:
        module_logger.critical("An error was encountered while executing the {} algorithm".format(args.which))
    else:
        module_logger.info("Done executing the {} algorithm".format(args.which))

    if os.path.exists(args.output_filename):
        module_logger.info("Output is available in {}".format(args.output_filename))
    else:
        module_logger.critical("FAILURE: Output filename {} is missing! Review output in {} to determine what may have gone wrong.".format(args.output_filename, args.working_directory))
        sys.exit(errno.ENXIO)

    module_logger.info("Done sampling.")

def sample_with_true_random(args):

    from hypercane.utils import get_web_session, save_resource_data
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hypercane.sample.probability import select_true_random

    module_logger.info("Starting true random sampling of {} URI-Ms.".format(args.sample_count))

    session = get_web_session(cache_storage=args.cache_storage)
    output_type = 'mementos'
    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("Executing select true random algorithm to select {} from {} URI-Ms".format(
        int(args.sample_count), len(urimdata.keys())))
    sampled_urims = select_true_random(list(urimdata.keys()), int(args.sample_count))

    module_logger.info("Writing sampled URI-Ms out to {}".format(args.output_filename))
    save_resource_data(args.output_filename, urimdata, 'mementos', sampled_urims)

    module_logger.info("Done with random sampling of {} URI-Ms. Output is in {}.".format(args.sample_count, args.output_filename))

def sample_with_systematic(args):

    from hypercane.sample.probability import select_systematically
    from hypercane.utils import get_web_session, save_resource_data
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    session = get_web_session(cache_storage=args.cache_storage)
    output_type = 'mementos'

    module_logger.info("Starting systematic sampling of URI-Ms.")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("Executing systemic sample to select every {}th item from from {} URI-Ms".format(
        int(args.iteration), len(urimdata.keys())))
    sampled_urims = select_systematically(list(urimdata.keys()), int(args.iteration))

    module_logger.info("Writing systematically sampled URI-Ms out to {}".format(args.output_filename))
    save_resource_data(args.output_filename, urimdata, 'mementos', sampled_urims)

    module_logger.info("Done sampling.")

def sample_with_stratified_random(args):

    from hypercane.sample.probability import select_random_per_cluster
    from hypercane.utils import get_web_session, save_resource_data, organize_mementos_by_cluster
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    session = get_web_session(cache_storage=args.cache_storage)
    output_type = 'mementos'

    module_logger.info("Starting random sampling of URI-Ms.")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    memento_clusters = organize_mementos_by_cluster(urimdata)

    module_logger.info("Executing stratified random sample to select {} items each from {} clusters of {} URI-Ms".format(
        int(args.j), len(memento_clusters), len(urimdata.keys())))
    
    sampled_urims = select_random_per_cluster(memento_clusters, int(args.j))

    module_logger.info("Writing {} sampled URI-Ms out to {}".format(len(sampled_urims), args.output_filename))
    save_resource_data(args.output_filename, urimdata, 'mementos', sampled_urims)

    module_logger.info("Done sampling.")

def sample_with_stratified_systematic(args):

    from hypercane.sample.probability import select_systematic_per_cluster
    from hypercane.utils import get_web_session, save_resource_data, organize_mementos_by_cluster
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    session = get_web_session(cache_storage=args.cache_storage)
    output_type = 'mementos'

    module_logger.info("Starting stratified systematic sampling of URI-Ms.")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    memento_clusters = organize_mementos_by_cluster(urimdata)

    module_logger.info("Executing stratified systematic sample to select each {} item each from {} clusters of {} URI-Ms".format(
        int(args.iteration), len(memento_clusters), len(urimdata.keys())))
    
    sampled_urims = select_systematic_per_cluster(memento_clusters, int(args.iteration))

    module_logger.info("Writing {} sampled URI-Ms out to {}".format(len(sampled_urims), args.output_filename))
    save_resource_data(args.output_filename, urimdata, 'mementos', sampled_urims)

    module_logger.info("Done sampling.")

def sample_with_random_cluster(args):

    from hypercane.sample.probability import select_random_clusters
    from hypercane.utils import get_web_session, save_resource_data, organize_mementos_by_cluster
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    session = get_web_session(cache_storage=args.cache_storage)
    output_type = 'mementos'

    module_logger.info("Starting sampling of random clusters of URI-Ms.")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    memento_clusters = organize_mementos_by_cluster(urimdata)

    module_logger.info("Executing random cluster selection to sample {} clusters from {} clusters of {} URI-Ms".format(
        int(args.cluster_count), len(memento_clusters), len(urimdata.keys())))
    
    sampled_urims = select_random_clusters(memento_clusters, int(args.cluster_count))

    module_logger.info("Writing {} sampled URI-Ms out to {}".format(len(sampled_urims), args.output_filename))
    save_resource_data(args.output_filename, urimdata, 'mementos', sampled_urims)

    module_logger.info("Done sampling.")

def sample_with_random_oversample(args):

    from hypercane.sample.probability import select_by_random_oversampling
    from hypercane.utils import get_web_session, save_resource_data, organize_mementos_by_cluster
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    session = get_web_session(cache_storage=args.cache_storage)
    output_type = 'mementos'

    module_logger.info("Starting random oversampling of clusters of URI-Ms.")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    memento_clusters = organize_mementos_by_cluster(urimdata)

    module_logger.info("Executing random oversample from {} clusters of {} URI-Ms".format(
        len(memento_clusters), len(urimdata.keys())))
    
    sampled_urims = select_by_random_oversampling(memento_clusters)

    module_logger.info("Writing {} sampled URI-Ms out to {}".format(len(sampled_urims), args.output_filename))
    save_resource_data(args.output_filename, urimdata, 'mementos', sampled_urims)

    module_logger.info("Done sampling.")

def sample_with_random_undersample(args):

    from hypercane.sample.probability import select_by_random_undersamping
    from hypercane.utils import get_web_session, save_resource_data, organize_mementos_by_cluster
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    session = get_web_session(cache_storage=args.cache_storage)
    output_type = 'mementos'

    module_logger.info("Starting random undersampling of clusters of URI-Ms.")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    memento_clusters = organize_mementos_by_cluster(urimdata)

    module_logger.info("Executing random undersample from {} clusters of {} URI-Ms".format(
        len(memento_clusters), len(urimdata.keys())))
    
    sampled_urims = select_by_random_undersamping(memento_clusters)

    module_logger.info("Writing {} sampled URI-Ms out to {}".format(len(sampled_urims), args.output_filename))
    save_resource_data(args.output_filename, urimdata, 'mementos', sampled_urims)

    module_logger.info("Done sampling.")
