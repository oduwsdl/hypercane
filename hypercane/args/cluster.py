import argparse
from argparse import RawTextHelpFormatter

cluster_parser = argparse.ArgumentParser(prog="hc cluster",
    description="'hc cluster' employs techniques to cluster a list of URI-Ms",
    formatter_class=RawTextHelpFormatter
)

subparsers = cluster_parser.add_subparsers(help='clustering methods', dest="clustering method ('e.g., kmeans")
subparsers.required = True

timeslice_parser = subparsers.add_parser('time-slice', help="slice the collection into buckets by Memento-Datetime, as in AlNoamany's Algorithm")
timeslice_parser.set_defaults(which='time-slice')

timeslice_parser.add_argument('-k', dest='k',
    default=None, type=int,
    help='The number of clusters to create.'
)

dbscan_parser = subparsers.add_parser('dbscan', help="cluster the user-supplied feature using the DBSCAN algorithm")
dbscan_parser.set_defaults(which='dbscan')

dbscan_parser.add_argument('--feature', dest='feature',
    default='tf-simhash',
    help='The feature in which to cluster the documents.'
)

dbscan_parser.add_argument('--eps', dest='eps',
    default=None,
    help='The maximum distance between two samples for one to be considered as in the neighbordhood of the other. We will compute defaults if no value specified. See: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html'
)

dbscan_parser.add_argument('--min-samples', dest='min_samples',
    default=2,
    help="The number of samples in a neighbordhood for a point to be considered as a core point. See: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html"
)

lda_parser = subparsers.add_parser('lda', help="cluster the collection via LDA topic modeling")
lda_parser.set_defaults(which='lda')

lda_parser.add_argument('--num_topics', dest='num_topics',
    default=20, required=False, type=int,
    help='The number of topics to cluster.'
)

lda_parser.add_argument('--passes', dest='num_passes',
    default=2, required=False, type=int,
    help='The number of passes through the corpus during training. This corresponds to the Gensim LDA setting of the same name. See: https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html'
)

lda_parser.add_argument('--iterations', dest='num_iterations',
    default=50, required=False, type=int,
    help='The number of iterations through each document during training. This corresponds to the Gensim LDA setting of the same name. See: https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html'
)

kmeans_parser = subparsers.add_parser('kmeans', help="cluster the user-supplied feature using K-means clustering")
kmeans_parser.set_defaults(which='kmeans')

kmeans_parser.add_argument('--feature', dest='feature',
    default='memento-datetime',
    help='The feature in which to cluster the documents.'
)

kmeans_parser.add_argument('-k', dest='k',
    default=28, type=int,
    help='The number of clusters to create.'
)

domainname_parser = subparsers.add_parser('domainname', help="cluster the URI-Ms by domainname")
domainname_parser.set_defaults(which='domainname')

originalresource_parser = subparsers.add_parser('original-resource', help="cluster the URI-Ms by URI-R")
originalresource_parser.set_defaults(which='original-resource')