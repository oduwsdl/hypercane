import argparse
from argparse import RawTextHelpFormatter
import otmt
import hypercane.actions.hfilter

filter_includeonly_parser = argparse.ArgumentParser(prog="hc filter include-only",
    description="'filter include-only' filters a web archive collection by only including mementos that satisfy the given criteria",
    formatter_class=RawTextHelpFormatter
)

subparsers = filter_includeonly_parser.add_subparsers(help='filtering criteria', dest="filtering criteria (e.g., languages, on-topic)")
subparsers.required = True

language_parser = subparsers.add_parser(
    'languages',
    help = "include mementos with the given languages (specified with --lang)"
)
language_parser.set_defaults(
    which='languages',
    exec=hypercane.actions.hfilter.include_languages
)

language_parser.add_argument('--lang', '--languages', dest='languages',
    help="The list of languages to match, separated by commas.",
    required=True
)

nonduplicate_parser = subparsers.add_parser(
    'non-duplicates',
    help = "employ Simhash to only include mementos that are not duplicates"
)
nonduplicate_parser.set_defaults(
    which='non-duplicates',
    exec=hypercane.actions.hfilter.remove_near_duplicates
)

ontopic_parser = subparsers.add_parser(
    'on-topic',
    help = "execute the Off-Topic Memento Toolkit to only include on-topic mementos in the output",
    formatter_class=RawTextHelpFormatter
)
ontopic_parser.set_defaults(
    which='on-topic',
    exec=hypercane.actions.hfilter.remove_offtopic
)

tmmeasurehelp = ""
for measure in otmt.supported_timemap_measures:
    tmmeasurehelp += "* {} - {}, default threshold {}\n".format(
        measure, otmt.supported_timemap_measures[measure]['name'],
        otmt.supported_timemap_measures[measure]['default threshold'])

ontopic_parser.add_argument('-tm', '--timemap-measures', dest='timemap_measures',
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

ontopic_parser.add_argument('--number-of-topics', dest="num_topics", type=int,
    help="The number of topics to use for gensim_lda and gensim_lsi, "
    "ignored if these measures are not requested.")

score_parser = subparsers.add_parser(
    'score',
    help = "include only those mementos containing a score meeting the given criteria, supplied by the --criteria argument, requires that the input contains scoring information"
)
score_parser.set_defaults(
    which="score",
    exec=hypercane.actions.hfilter.include_score_range
)
score_parser.add_argument('--criteria', default=1, dest='criteria',
    help="The numeric criteria to use when selecting which values to keep.",
    required=True
)

score_parser.add_argument('--scoring-field', help="Specify the scoring field to sort by, default is first encountered",
    default=None, dest='scoring_field'
)

highest_scoring_per_cluster_parser = subparsers.add_parser(
    'highest-score-per-cluster',
    help = "include only the highest ranking memento in each cluster, requires that the input contain clustered mementos"
)
highest_scoring_per_cluster_parser.set_defaults(
    which="highest-score-per-cluster",
    exec=hypercane.actions.hfilter.include_highest_score_per_cluster
)
highest_scoring_per_cluster_parser.add_argument('--score-key', dest='score_key',
    help="The field name of the score in the input file. It is possible for the input to contain multiple score keys. This argument allows you to choose one.", required=False, default=None
)

containing_pattern_parser = subparsers.add_parser(
    'containing-pattern',
    help = "include only mementos that contain the given regular experession pattern"
)
containing_pattern_parser.set_defaults(
    which="containing-pattern",
    exec=hypercane.actions.hfilter.include_containing_pattern
)
containing_pattern_parser.add_argument('--pattern', dest='pattern_string',
    help="The regular expression pattern to match (as Python regex)",
    required=True
)

near_datetime_parser = subparsers.add_parser(
    'near-datetime',
    help = "include only mementos whose memento-datetime falls into the given range"
)
near_datetime_parser.set_defaults(
    which="near-datetime",
    exec=hypercane.actions.hfilter.include_near_datetime
)
near_datetime_parser.add_argument('--start-datetime', '--lower-datetime',
    dest='lower_datetime',
    help="The lower bound datetime in YYYY-mm-ddTHH:MM:SS format.",
    required=True
)
near_datetime_parser.add_argument('--end-datetime', '--upper-datetime',
    dest='upper_datetime',
    help="The upper bound datetime in YYYY-mm-ddTHH:MM:SS format.",
    required=True
)

containing_url_pattern_parser = subparsers.add_parser(
    'containing-url-pattern',
    help = "include only mementos whose original resource URL matches the given regular expression pattern"
)
containing_url_pattern_parser.set_defaults(
    which="containing-url-pattern",
    exec=hypercane.actions.hfilter.include_urir
)
containing_url_pattern_parser.add_argument('--url-pattern', '--urir-pattern', dest='urir_pattern',
    help="The regular expression pattern of the URL to match (as Python regex)",
    required=True
)

largest_clusters_parser = subparsers.add_parser(
    'largest-clusters',
    help = "include only the mementos from the largest cluster, requires that input contain clustered mementos"
)
largest_clusters_parser.set_defaults(
    which="largest-clusters",
    exec=hypercane.actions.hfilter.include_largest_clusters
)
largest_clusters_parser.add_argument('--cluster-count', default=1, dest='cluster_count',
    help="The number of clusters' worth of mementos to returned, sorted descending by cluster size."
)
