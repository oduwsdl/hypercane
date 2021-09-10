import argparse
from argparse import RawTextHelpFormatter

import hypercane.actions.score

score_parser = argparse.ArgumentParser(prog="hc score",
    description="'score' scores the mementos in the input",
    formatter_class=RawTextHelpFormatter
)

subparsers = score_parser.add_subparsers(help='scoring methods', dest='scoring method (e.g., dsa1-scoring, image-count, bm25)')
subparsers.required = True

dsa1_scoring_parser = subparsers.add_parser('dsa1-scoring', help="score the documents according to the scoring function of AlNoamany's Algorithm (https://doi.org/10.1145/3091478.3091508)")
dsa1_scoring_parser.set_defaults(
    which='dsa1-scoring',
    exec=hypercane.actions.score.dsa1_scoring
)

dsa1_scoring_parser.add_argument('--memento-damage-url', dest='memento_damage_url',
    default=None,
    help="The URL of the Memento-Damage service to use for scoring."
)

dsa1_scoring_parser.add_argument('--damage-weight', dest='damage_weight',
    default=-0.40, type=float,
    help="The weight for the Memento-Damage score in the scoring."
)

dsa1_scoring_parser.add_argument('--category-weight', dest='category_weight',
    default=0.15, type=float,
    help="The weight for the URI-R category score in the scoring."
)

dsa1_scoring_parser.add_argument('--path-depth-weight', dest='path_depth_weight',
    default=0.45, type=float,
    help="The weight for the URI-R path depth score in the scoring."
)

dsa2_scoring_parser = subparsers.add_parser('dsa2-scoring', help="score the documents according to the scoring function of DSA2, optimizing for documents that likely produce good surrogates")
dsa2_scoring_parser.set_defaults(
    which='dsa2-scoring',
    exec=hypercane.actions.score.dsa2_scoring
)

dsa2_scoring_parser.add_argument('--card-weight', dest='card_weight',
    default=0.50, type=float,
    help="The weight for how well a page can produce a card."
)

dsa2_scoring_parser.add_argument('--size-weight', dest='size_weight',
    default=0.25, type=float,
    help="The weight for the size of the content, in case a card is not possible."
)

dsa2_scoring_parser.add_argument('--image-count-weight', dest='image_count_weight',
    default=0.25, type=float,
    help="The weight for number of images, in case a card is not possible."
)

bm25_parser = subparsers.add_parser('bm25', help="score documents according to the input query with BM25")
bm25_parser.set_defaults(
    which='bm25',
    exec=hypercane.actions.score.bm25_ranking
)

bm25_parser.add_argument('--query', dest='query',
    required=True, help="The query to use with BM25"
)

imagecount_parser = subparsers.add_parser('image-count', help="score by the number of images in each document")
imagecount_parser.set_defaults(
    which='image-count',
    exec=hypercane.actions.score.image_count_scoring
)

simplecardscore_parser = subparsers.add_parser('simple-card-score', help="score by how well the memento creates a social card on Facebook and Twitter")
simplecardscore_parser.set_defaults(
    which='simple-card-score',
    exec=hypercane.actions.score.simple_card_scoring
)

pathdepth_parser = subparsers.add_parser('path-depth', help="score by path depth, as defined by McCown et al. (https://arxiv.org/abs/cs/0511077)")
pathdepth_parser.set_defaults(
    which='path-depth',
    exec=hypercane.actions.score.path_depth_scoring
)

urlcategoryscore_parser = subparsers.add_parser('url-category-score', help="score by how well the memento creates a social card on Facebook and Twitter")
urlcategoryscore_parser.set_defaults(
    which='url-category-score',
    exec=hypercane.actions.score.category_scoring
)

topentitesandbm25_parser = subparsers.add_parser('top-entities-and-bm25', help="score by the top k entities and BM25")
topentitesandbm25_parser.set_defaults(
    which='top-entities-and-bm25',
    exec=hypercane.actions.score.score_by_top_entities_and_bm25
)

topentitesandbm25_parser.add_argument('-k', dest='k',
    required=False, help="The number of top entities to use", 
    default=10
)

distancefromcentroid_parser = subparsers.add_parser('distance-from-centroid', help="score by the distance of each memento from the center of its cluster")
distancefromcentroid_parser.set_defaults(
    which='distance-from-centroid',
    exec=hypercane.actions.score.score_by_distance_from_centroid
)

distancefromcentroid_parser.add_argument('--more-similar', dest='more_similar',
    action='store_true',
    help='This will subtract all scores by 0 so that highest means more similar and not more unique.'
)

size_parser = subparsers.add_parser('size', help="score by the size of each memento")
size_parser.set_defaults(
    which='size',
    exec=hypercane.actions.score.score_by_size
)

size_parser.add_argument('--feature', dest='feature',
    required=False, help="The feature to score with, options are: 'bytes', 'characters', 'boilerplate-free-characters', 'words', 'sentences'", 
    default="bytes"
)
