import logging

module_logger = logging.getLogger("hypercane.actions.sample")

def sample_with_custom_algorithm(args):

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
            'sampling method (e.g., true-random, dsa1)'
        ]:
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

# def run_sample_with(parser, args, algorithm_name, algorithm_script):

#     from sys import platform
#     import errno

#     if platform == "win32":
#         print("Error: AlNoamany's Algorithm can only be executed via `hc sample` on Linux or macOS. Please see documentation for how to execute it on Windows and submit an issue to our Issue Tracker if you need Windows support.")
#         sys.exit(errno.ENOTSUP)

#     import argparse
#     import subprocess
#     import os
#     import shlex
#     from datetime import datetime
#     from hypercane.actions import add_input_args, add_default_args
#     from hypercane.actions import get_logger, calculate_loglevel
#     from hypercane.utils import get_web_session, save_resource_data
#     from hypercane.identify import discover_resource_data_by_input_type, \
#         discover_timemaps_by_input_type

#     parser = add_input_args(parser)

#     parser = add_default_args(parser)

#     runtime_string = "{}".format(datetime.now()).replace(' ', 'T')

#     parser.add_argument('--working-directory', required=False,
#         help="the directory to which this application should write output",
#         default="/tmp/hypercane/working/{}".format(runtime_string),
#         dest='working_directory')

#     args = parser.parse_args(args)

#     logger = get_logger(
#         __name__,
#         calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
#         args.logfile
#     )

#     logger.info("Executing the {} algorithm with working directory {}".format(
#         algorithm_name, args.working_directory))

#     logger.info("Using cache storage of '{}'".format(args.cache_storage))

#     os.makedirs(args.working_directory, exist_ok=True)

#     logger.info("executing algorithm script from {}".format(algorithm_script))

#     logger.info("args: {}".format(args))

#     if type(args.logfile) != str:
#         args.logfile = ""

#     if args.errorfilename is None:
#         args.errorfilename = ""

#     other_arglist = []

#     for argname, argvalue in vars(args).items():
#         if argname not in [
#             'input_type',
#             'input_arguments',
#             'cache_storage',
#             'working_directory',
#             'output_filename',
#             'logfile',
#             'errorfilename'
#         ]:
#             if argvalue is not False:
#                 other_arglist.append( "--{} {}".format(
#                     argname.replace('_', '-'), argvalue
#                 ) )

#     other_args = '"' + " ".join(other_arglist) + '"'

#     logger.info("using other arguments: {}".format(other_args))

#     cp = subprocess.run(
#         [
#             "/bin/bash",
#             algorithm_script,
#             args.input_type,
#             args.input_arguments,
#             args.cache_storage,
#             args.working_directory,
#             args.output_filename,
#             args.logfile,
#             args.errorfilename,
#             other_args
#         ]
#     )

#     if cp.returncode != 0:
#         logger.critical("An error was encountered while executing the {} algorithm".format(algorithm_name))
#     else:
#         logger.info("Done executing the {} algorithm".format(algorithm_name))

#     return args

# def run_sample_with_dsa1(parser, args):

#     from sys import platform
#     import errno

#     if platform == "win32":
#         print("Error: AlNoamany's Algorithm can only be executed via `hc sample` on Linux or macOS. Please see documentation for how to execute it on Windows and submit an issue to our Issue Tracker if you need Windows support.")
#         sys.exit(errno.ENOTSUP)

#     import argparse
#     import subprocess
#     import os
#     import shlex
#     from datetime import datetime
#     from hypercane.actions import add_input_args, add_default_args
#     from hypercane.actions import get_logger, calculate_loglevel
#     from hypercane.utils import get_web_session, save_resource_data
#     from hypercane.identify import discover_resource_data_by_input_type, \
#         discover_timemaps_by_input_type

#     parser = add_input_args(parser)

#     parser = add_default_args(parser)

#     runtime_string = "{}".format(datetime.now()).replace(' ', 'T')

#     parser.add_argument('--working-directory', required=False,
#         help="the directory to which this application should write output",
#         default="/tmp/hypercane/working/{}".format(runtime_string),
#         dest='working_directory')

#     args = parser.parse_args(args)

#     logger = get_logger(
#         __name__,
#         calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
#         args.logfile
#     )

#     logger.info("Executing DSA1 (AlNoamany's) algorithm with working directory {}".format(args.working_directory))

#     os.makedirs(args.working_directory, exist_ok=True)

#     scriptdir = os.path.dirname(os.path.realpath(__file__))

#     algorithm_script = "{}/../packaged_algorithms/dsa1.sh".format(scriptdir)

#     logger.info("executing algorithm script from {}".format(algorithm_script))

#     if type(args.logfile) != str:
#         args.logfile = ""

#     cp = subprocess.run(
#         [
#             "/bin/bash",
#             algorithm_script,
#             args.input_type,
#             args.input_arguments,
#             args.cache_storage,
#             args.working_directory,
#             args.output_filename,
#             args.logfile
#         ]
#     )

#     if cp.returncode != 0:
#         logger.critical("An error was encountered while executing DSA1 (AlNoamany's) algorithm")
#     else:
#         logger.info("Done executing DSA1 (AlNoamany's) algorithm")

#     return args

# def sample_with_dsa1(args):

#     import argparse
#     import os

#     parser = argparse.ArgumentParser(
#         description="Sample URI-Ms from a web archive collection with DSA1 (AlNoamany's) algorithm.",
#         prog="hc sample dsa1"
#     )

#     parser.add_argument('--memento-damage-url', dest='memento_damage_url',
#         default=None,
#         help="The URL of the Memento-Damage service to use for scoring."
#     )

#     algorithm_script = "{}/../packaged_algorithms/dsa1.sh".format(
#         os.path.dirname(os.path.realpath(__file__))
#     )

#     # run_sample_with_dsa1(parser, args)
#     run_sample_with(parser, args, "DSA1", algorithm_script)

# def sample_with_alnoamany(args):

#     import argparse
#     import os

#     parser = argparse.ArgumentParser(
#         description="Sample URI-Ms from a web archive collection with DSA1 (AlNoamany's) algorithm.",
#         prog="hc sample alnoamany"
#         )

#     parser.add_argument('--memento-damage-url', dest='memento_damage_url',
#         default=None,
#         help="The URL of the Memento-Damage service to use for ranking."
#     )

#     algorithm_script = "{}/../packaged_algorithms/dsa1.sh".format(
#         os.path.dirname(os.path.realpath(__file__))
#     )

#     # run_sample_with_dsa1(parser, args)
#     run_sample_with(parser, args, "AlNoamany", algorithm_script)

# def sample_with_filtered_random(args):

#     import argparse
#     import os

#     parser = argparse.ArgumentParser(
#         description="Sample URI-Ms from a web archive collection by filtering off-topic mementos, filtering near-duplicates, and then sampling k of the remainder, randomly.",
#         prog="hc sample filtered-random"
#         )

#     algorithm_script = "{}/../packaged_algorithms/filtered_random.sh".format(
#          os.path.dirname(os.path.realpath(__file__))
#     )

#     parser.add_argument('-k', required=False, help="the number of items to sample", default=28, dest='k')

#     run_sample_with(parser, args, "Filtered Random", algorithm_script)

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

    module_logger.info("Starting random sampling of URI-Ms.")

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
