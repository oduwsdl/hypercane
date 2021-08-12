import argparse
from argparse import RawTextHelpFormatter

import hypercane.actions.sample

sample_parser = argparse.ArgumentParser(prog="hc sample",
    description='hc sample executes different sampling algorithms to selecting exemplars from a web archive collection',
    formatter_class=RawTextHelpFormatter
    )

subparsers = sample_parser.add_subparsers(help='sampling methods', dest='sampling method (e.g., true-random, dsa1)')
subparsers.required = True

truerandom_parser = subparsers.add_parser('true-random', help="sample probabilistically by randomly sampling k mementos from the input")
truerandom_parser.set_defaults(
    which='true-random',
    exec=hypercane.actions.sample.sample_with_true_random
)

truerandom_parser.add_argument(
    '-k', dest='sample_count', required=True,
    help="the number of items to sample"
)

# dsa1_parser = subparsers.add_parser(name='dsa1', help="sample intelligently with the DSA1 algorithm")
# dsa1_parser.set_defaults(which='dsa1')

# dsa1_parser.add_argument(
#     '--working-directory', dest='working_directory', required=True,
#     help="The directory to which this application should write output."
# )

# dsa2_parser = subparsers.add_parser(name='dsa2', help="sample intelligently with the DSA2 algorithm")
# dsa2_parser.set_defaults(which='dsa2')

# dsa3_parser = subparsers.add_parser(name='dsa3', help="sample intelligently with the DSA3 algorithm")
# dsa3_parser.set_defaults(which='dsa3')

# dsa4_parser = subparsers.add_parser(name='dsa4', help="sample intelligently with the DSA3 algorithm")
# dsa4_parser.set_defaults(which='dsa4')

# filteredrandom_parser = subparsers.add_parser(name='filtered-random', help="sample semi-intelligently by filtering off-topic mementos, near-duplicates, and randomly sampling k from the remainder")
# filteredrandom_parser.set_defaults(which='filtered-random')

# filteredrandom_parser.add_argument(
#     '-k', dest='sample_count', required=True,
#     help="the number of items to sample"
# )

systematic_parser = subparsers.add_parser(name='systematic', help="returns every jth memento from the input")
systematic_parser.set_defaults(
    which='systematic',
    exec=hypercane.actions.sample.sample_with_systematic
)

systematic_parser.add_argument(
    '-j', dest='iteration', required=True,
    help="the iteration of the item to sample, e.g., --j 5 for every 5th item"
)

# stratifiedrandom_parser = subparsers.add_parser(name='stratified-random', help="returns j items randomly chosen from each cluster, requries that the input be clustered with the cluster action")
# stratifiedrandom_parser.set_defaults(which='stratified-random')
# stratifiedrandom_parser.add_argument(
#     '-j', dest='j', required=True,
#     help="the number of items to randomly sample from each cluster"
# )

# randomcluster_parser = subparsers.add_parser(name='random-cluster', help="return j randomly selected clusters from the sample, requires that the input be clustered with the cluster action")
# randomcluster_parser.set_defaults(which='random-cluster')
# randomcluster_parser.add_argument(
#     '-j', dest='cluster_count', required=True,
#     help="the number of clusters to randomly sample, e.g., --cluster-count 5 for every 5th item from each cluster"
# )

# randomoversample_parser = subparsers.add_parser(name='random-oversample', help="randomly duplicates URI-Ms in the smaller clusters until they match the size of the largest cluster, requires input be clustered with the cluster action")
# randomoversample_parser.set_defaults(which='random-oversample')

# randomundersample_parser = subparsers.add_parser(name='random-undersample', help="randomly chooses URI-Ms from the larger clusters until they match the size of the smallest cluster, requires input be clustered with the cluster action")
# randomundersample_parser.set_defaults(which='random-undersample')

