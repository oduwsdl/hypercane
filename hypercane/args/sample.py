import sys
import argparse
from argparse import RawTextHelpFormatter

from hypercane.version import __appname__,__appversion__

sample_parser = argparse.ArgumentParser(prog="{}".format(sys.argv[0]),
    description='hc sample is used execute different sampling algorithms to selecting exemplars from a web archive collection',
    formatter_class=RawTextHelpFormatter
    )

sample_parser.add_argument(
    '-i', '--it', '--input-type', required=True, dest='input_type',
    help="the input type, one of mementos, timemaps, original-resources, archiveit, trove, or pandora-collection",
)

sample_parser.add_argument(
    '-a', '--ia', '--input-arguments', required=True, dest='input_arguments',
    help="either a file containing a list of URIs, or an Archive-It collection identifier",
)

sample_parser.add_argument(
    '-o', required=True, dest='output_filename',
    help="the file to which we write output",
)

sample_parser.add_argument(
    '-l', '--logfile', required=True, dest='logfile',
    help="The path to a logging file. The log is printed to screen by default.",
)

sample_parser.add_argument(
    '-v', '--verbose', required=False, dest='verbose', action='store_true',
    help="This will raise the logging level to debug for more verbose output.",
)

sample_parser.add_argument(
    '-q', '--quiet', required=False, dest='quiet', action='store_true',
    help="This will lower the logging level to only show warnings or errors.",
)

sample_parser.add_argument(
    '-cs', required=False, dest='cache_storage',
    help="The path to the MongoDB database to use as a cache.",
)

sample_parser.add_argument(
    '-e', required=False, dest='errorfilename',
    help="The path to filename that records URL processing failures.",
)

# Wooey can't handle action='version' even though this is what argparse recommends
# sample_parser.add_argument(
#     '--version', action='version', version="{}/{}".format(__appname__, __appversion__),
#     help="Show program's version number and exit.",
# )

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

