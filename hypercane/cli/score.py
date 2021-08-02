import hypercane.actions.score
import hypercane.errors

from hypercane.args import universal_cli_required_args, universal_cli_optional_args
from hypercane.args.score import score_parser
from hypercane.version import __useragent__
from hypercane.actions import get_logger, calculate_loglevel

score_functions = {
    "dsa1-scoring": hypercane.actions.score.dsa1_scoring,
    "bm25": hypercane.actions.score.bm25_ranking,
    "image-count": hypercane.actions.score.image_count_scoring,
    "simple-card-score": hypercane.actions.score.simple_card_scoring,
    "path-depth": hypercane.actions.score.path_depth_scoring,
    "url-category-score": hypercane.actions.score.category_scoring,
    "top-entities-and-bm25": hypercane.actions.score.score_by_top_entities_and_bm25,
    "distance-from-centroid": hypercane.actions.score.score_by_distance_from_centroid,
    "size" : hypercane.actions.score.score_by_size,
    "dsa2-scoring": hypercane.actions.score.dsa2_scoring
}

if __name__ == '__main__':

    for item in score_parser._subparsers._group_actions:
        for key in item.choices:

            subparser = item.choices[key]

            # Wooey's install script does not know how to handle functions, so we have to repeat this
            required = subparser.add_argument_group('required arguments')

            for entry in universal_cli_required_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                required.add_argument(*flags, **argument_params)

            optional = subparser.add_argument_group('optional arguments')
            for entry in universal_cli_optional_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                optional.add_argument(*flags, **argument_params)

    args = score_parser.parse_args()

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    if args.errorfilename is not None:
        hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

    score_functions[args.which](args)
