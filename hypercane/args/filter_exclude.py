import argparse
from argparse import RawTextHelpFormatter
import otmt
import hypercane.actions.hfilter

filter_exclude_parser = argparse.ArgumentParser(prog="hc filter exclude",
    description="'filter exclude' filters a web archive collection by excluding mementos that satisfy the given criteria",
    formatter_class=RawTextHelpFormatter
)

subparsers = filter_exclude_parser.add_subparsers(
    help = "filtering criteria",
    dest = "filtering criteria (e.g., languages, off-topic)"
)

language_parser = subparsers.add_parser(
    'languages',
    help = "exclude mementos with the given languages (specified with --lang)"
)
language_parser.set_defaults(
    which='languages',
    exec=hypercane.actions.hfilter.exclude_languages
)

language_parser.add_argument('--lang', '--languages', dest='languages',
    help="The list of languages to match, separated by commas.",
    required=True
)

nearduplicate_parser = subparsers.add_parser(
    'near-duplicates',
    help = "employ Simhash to exclude mementos that are near-duplicates"
)
nearduplicate_parser.set_defaults(
    which='near-duplicates',
    exec=hypercane.actions.hfilter.remove_near_duplicates
)

offtopic_parser = subparsers.add_parser(
    'off-topic',
    help = "execute the Off-Topic Memento Toolkit to exclude off-topic mementos from the output",
    formatter_class=RawTextHelpFormatter
)
offtopic_parser.set_defaults(
    which='off-topic',
    exec=hypercane.actions.hfilter.remove_offtopic
)

tmmeasurehelp = ""
for measure in otmt.supported_timemap_measures:
    tmmeasurehelp += "* {} - {}, default threshold {}\n".format(
        measure, otmt.supported_timemap_measures[measure]['name'],
        otmt.supported_timemap_measures[measure]['default threshold'])

offtopic_parser.add_argument('-tm', '--timemap-measures', dest='timemap_measures',
    type=otmt.process_timemap_similarity_measure_inputs,
    default='cosine',
    help="The TimeMap-based similarity measures specified will be used. \n"
    "For each of these measures, the first memento in a TimeMap\n"
    "is compared with each subsequent memento to measure topic drift.\n"
    "Specify measure with optional threshold separated by equals.\n"
    "Multiple measures can be specified.\n"
    "(e.g., jaccard=0.10,cosine=0.15,wordcount);\n"
    "Leave thresholds off to use default thresholds.\n"
    "Accepted values:\n{}".format(tmmeasurehelp)
)

offtopic_parser.add_argument('--number-of-topics', dest="num_topics", type=int,
    help="The number of topics to use for gensim_lda and gensim_lsi, "
    "ignored if these measures are not requested.")

containing_pattern_parser = subparsers.add_parser(
    'containing-pattern',
    help = "include only mementos that contain the given regular experession pattern"
)
containing_pattern_parser.set_defaults(
    which="containing-pattern",
    exec=hypercane.actions.hfilter.exclude_containing_pattern
)
containing_pattern_parser.add_argument('--pattern', dest='pattern_string',
    help="The regular expression pattern to match (as Python regex)",
    required=True
)

with_cluster_id_parser = subparsers.add_parser(
    'with-cluster-id',
    help = "exclude mementos with the given cluster id; requires that the input be clustered"
)
with_cluster_id_parser.set_defaults(
    which="with-cluster-id",
    exec=hypercane.actions.hfilter.exclude_containing_cluster_id
)
with_cluster_id_parser.add_argument('--cluster-id', required=True,
    dest='cluster_id',
    help="The ID of the cluster to exclude from the output."
)
with_cluster_id_parser.add_argument('--match-subclusters',
    required=False, default=False,
    dest='match_subclusters',
    help="Match subclusters with this cluster-id"
)
