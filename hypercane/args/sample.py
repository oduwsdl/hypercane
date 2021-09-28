import sys
import os
import errno
import argparse
import tempfile
import json
from argparse import RawTextHelpFormatter

import hypercane.actions.sample
from pathlib import Path

sample_parser = argparse.ArgumentParser(prog="hc sample",
    description="'sample' produces a list of exemplars from a collection by applying an existing algorithm",
    formatter_class=RawTextHelpFormatter
    )

subparsers = sample_parser.add_subparsers(help='sampling methods', dest='sampling method (e.g., true-random, dsa1)')
subparsers.required = True

sample_cli_required_args = [
    {
        'flags': [ '--working-directory' ],
        'argument_params': {
            'required': False,
            'dest': 'working_directory',
            'help': 'The directory in which intermediate error, log, and output files will be stored. Defaults to generated temporary directory. May not be used by all sample commands.',
            'default': tempfile.mkdtemp()
        }
    }
]

# custom algorithms are listed first
if sys.platform != "win32":
    # assumes all other platforms support shell scripts
    # recall that we cannot use a function to handle duplicate arguments because Wooey does not appear to support it

    custom_script_data = {}

    script_paths = []

    hypercane_algorithm_extension = '.halg'

    user_algorithm_dir = '{}/.hypercane/algorithms'.format( str(Path.home()) )

    custom_algorithm_dirs = [
        "{}/../packaged_algorithms".format(
            os.path.dirname(os.path.realpath(__file__))
        )
    ]

    if os.path.exists(user_algorithm_dir):
        custom_algorithm_dirs.append(user_algorithm_dir)

    for algorithm_dir in custom_algorithm_dirs:

        for filename in os.listdir(algorithm_dir):

            base, ext = os.path.splitext(filename)

            if ext == hypercane_algorithm_extension:
                script_path = "{}/{}".format(
                    algorithm_dir,
                    filename
                )
                script_paths.append(script_path)

    for script_path in script_paths:
            
        algorithm_name = os.path.basename(script_path).replace(hypercane_algorithm_extension, '')
        helptext = "custom algorithm {}".format(algorithm_name)
        argjson = ""

        with open(script_path) as f:

            argstate = 0
            
            for line in f:
                # print("examining line {}".format(line))
                if line [0] != '#':
                    continue
                else:

                    if 'END ARGUMENT JSON' in line:
                        argstate = 0

                    if argstate == 1:
                        argjson += line[1:] # get rid of initial #

                    if 'algorithm name:' in line:
                        algorithm_name = line.split(':')[1].strip()
                    
                    if 'algorithm description:' in line:
                        algorithm_description = line.split(':', 1)[1].strip()
                        helptext = algorithm_description

                    if 'START ARGUMENT JSON' in line:
                        argstate = 1

        if algorithm_name in custom_script_data:
            error_message = "Duplicate algorithm name {} found in script {}, please rename algorithm to avoid this clash!".format(algorithm_name, script_path)
            print("ERROR: {} Refusing to Continue.".format(error_message))
            sys.exit(errno.EINVAL)

        if user_algorithm_dir in script_path:
            helptext += " (algorithm from {})".format(script_path)

        custom_script_data[algorithm_name] = {
            'script_path': script_path,
            'helptext': helptext,
            'argjson': argjson
        }

    # for alg in sorted(custom_script_data):
    #     print(alg, custom_script_data[alg])

    for algorithm_name in sorted(custom_script_data):
        custom_algorithm_parser = subparsers.add_parser(
            name=algorithm_name,
            help=custom_script_data[algorithm_name]['helptext']
        )
        custom_algorithm_parser.set_defaults(
            which=algorithm_name,
            exec=hypercane.actions.sample.sample_with_custom_script,
            script_path=custom_script_data[algorithm_name]['script_path']
        )
        # custom_algorithm_parser.add_argument(
        #     '--working-directory', dest='working_directory',
        #     help='The directory in which intermediate error, log, and output files will be stored. Defaults to generated temporary directory.', default=tempfile.mkdtemp()
        # )

        # print(algorithm_name)

        if len(custom_script_data[algorithm_name]['argjson'].strip()) > 0:
            argstruct = json.loads(custom_script_data[algorithm_name]['argjson'])

            for arg in argstruct:
                flags = arg['flags']
                argument_params = arg['argument_params']
                custom_algorithm_parser.add_argument(*flags, **argument_params)

# probabilistic algorithms are listed after
truerandom_parser = subparsers.add_parser('true-random', help="sample probabilistically by randomly sampling k mementos from the input")
truerandom_parser.set_defaults(
    which='true-random',
    exec=hypercane.actions.sample.sample_with_true_random
)

truerandom_parser.add_argument(
    '-k', dest='sample_count', required=True,
    help="the number of items to sample"
)

systematic_parser = subparsers.add_parser(name='systematic', help="returns every jth memento from the input")
systematic_parser.set_defaults(
    which='systematic',
    exec=hypercane.actions.sample.sample_with_systematic
)

systematic_parser.add_argument(
    '-j', dest='iteration', required=True,
    help="the iteration of the item to sample, e.g., --j 5 for every 5th item"
)

stratifiedrandom_parser = subparsers.add_parser(name='stratified-random', help="returns j items randomly chosen from each cluster, requries that the input be clustered with the cluster action")
stratifiedrandom_parser.set_defaults(
    which='stratified-random',
    exec=hypercane.actions.sample.sample_with_stratified_random
)
stratifiedrandom_parser.add_argument(
    '-j', dest='j', required=True,
    help="the number of items to randomly sample from each cluster"
)

stratifiedsystematic_parser = subparsers.add_parser(name='stratified-systematic', help="returns every jth URI-M from each cluster, requries that the input be clustered with the cluster action")
stratifiedsystematic_parser.set_defaults(
    which='stratified-random',
    exec=hypercane.actions.sample.sample_with_stratified_systematic
)
stratifiedsystematic_parser.add_argument(
    '-j', 
    required=True,
    help="the iteration of the item to sample from each cluster, e.g., --j 5 for every 5th item from each cluster",
    dest='iteration'
)

randomcluster_parser = subparsers.add_parser(name='random-cluster', help="return j randomly selected clusters from the sample, requires that the input be clustered with the cluster action")
randomcluster_parser.set_defaults(
    which='random-cluster',
    exec=hypercane.actions.sample.sample_with_random_cluster
    )
randomcluster_parser.add_argument(
    '--cluster-count',
    required=True,
    help="the number of clusters to randomly sample, e.g., --cluster-count 5 to randomly sample 5 clusters from input",
    dest='cluster_count'
)

randomoversample_parser = subparsers.add_parser(name='random-oversample', help="randomly duplicates URI-Ms in the smaller clusters until they match the size of the largest cluster, requires input be clustered with the cluster action")
randomoversample_parser.set_defaults(
    which='random-oversample',
    exec=hypercane.actions.sample.sample_with_random_oversample
)

randomundersample_parser = subparsers.add_parser(name='random-undersample', help="randomly chooses URI-Ms from the larger clusters until they match the size of the smallest cluster, requires input be clustered with the cluster action")
randomundersample_parser.set_defaults(
    which='random-undersample',
    exec=hypercane.actions.sample.sample_with_random_undersample
)

