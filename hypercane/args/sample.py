import argparse
from argparse import RawTextHelpFormatter

import hypercane.actions.sample


sample_parser = argparse.ArgumentParser(prog="hc sample",
    description="'sample' produces a list of exemplars from a collection by applying an existing algorithm",
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

