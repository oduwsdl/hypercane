import sys
import argparse
from argparse import RawTextHelpFormatter

from hypercane.version import __appname__,__appversion__

from . import default_required_args, default_optional_args

sample_parser = argparse.ArgumentParser(prog="{}".format(sys.argv[0]),
    description='hc sample is used execute different sampling algorithms to selecting exemplars from a web archive collection',
    formatter_class=RawTextHelpFormatter
    )

for arg in default_required_args:

    if arg[4] is None:

        sample_parser.add_argument(
            arg[0],
            required=True,
            dest=arg[1],
            help=arg[2],
            action=arg[3]
        )

    else:

        sample_parser.add_argument(
            arg[0],
            required=True,
            dest=arg[1],
            help=arg[2],
            action=arg[3],
            choices=arg[4]
        )


for arg in default_optional_args:

    if arg[4] is None:
        sample_parser.add_argument(
            arg[0],
            required=False,
            dest=arg[1],
            help=arg[2],
            action=arg[3]
        )
    else:
        sample_parser.add_argument(
            arg[0],
            required=False,
            dest=arg[1],
            help=arg[2],
            action=arg[3],
            default=arg[4]
        )

sample_parser.add_argument('color', choices=['red', 'yellow', 'purple'])

subparsers = sample_parser.add_subparsers(help='sampling methods')

truerandom_parser = subparsers.add_parser('true-random', help="sample probabilistically by randomly sampling k mementos from the input")
truerandom_parser.set_defaults(which='true-random')

truerandom_parser.add_argument(
    '-k', dest='sample_count', required=True,
    help="the number of items to sample"
)

dsa1_parser = subparsers.add_parser('dsa1', help="sample intelligently with the DSA1 algorithm")
dsa1_parser.set_defaults(which='dsa1')

dsa1_parser.add_argument(
    '--working-directory', dest='working_directory', required=True,
    help="The directory to which this application should write output."
)

dsa2_parser = subparsers.add_parser('dsa2', help="sample intelligently with the DSA2 algorithm")
dsa2_parser.set_defaults(which='dsa2')

dsa3_parser = subparsers.add_parser('dsa3', help="sample intelligently with the DSA3 algorithm")
dsa3_parser.set_defaults(which='dsa3')

dsa4_parser = subparsers.add_parser('dsa4', help="sample intelligently with the DSA3 algorithm")
dsa4_parser.set_defaults(which='dsa4')

filteredrandom_parser = subparsers.add_parser('filtered-random', help="sample semi-intelligently by filtering off-topic mementos, near-duplicates, and randomly sampling k from the remainder")
filteredrandom_parser.set_defaults(which='filtered-random')

systematic_parser = subparsers.add_parser('systematic', help="returns every jth memento from the input")
systematic_parser.set_defaults(which='filtered-random')

stratifiedrandom_parser = subparsers.add_parser('stratified-random', help="returns j items randomly chosen from each cluster, requries that the input be clustered with the cluster action")
stratifiedrandom_parser.set_defaults(which='stratified-random')

randomcluster_parser = subparsers.add_parser('random-cluster', help="return j randomly selected clusters from the sample, requires that the input be clustered with the cluster action")
randomcluster_parser.set_defaults(which='random-cluster')

randomoversample_parser = subparsers.add_parser('random-oversample', help="randomly duplicates URI-Ms in the smaller clusters until they match the size of the largest cluster, requires input be clustered with the cluster action")
randomoversample_parser.set_defaults(which='random-oversample')

randomundersample_parser = subparsers.add_parser('random-undersample', help="randomly chooses URI-Ms from the larger clusters until they match the size of the smallest cluster, requires input be clustered with the cluster action")
randomundersample_parser.set_defaults(which='random-undersample')

