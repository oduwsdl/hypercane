import os

import hypercane.actions.cluster
import hypercane.errors

from hypercane.args import universal_gui_required_args, universal_gui_optional_args
from hypercane.args.cluster import cluster_parser
from hypercane.version import __useragent__
from hypercane.actions import get_logger, calculate_loglevel


cluster_functions = {
    "time-slice": hypercane.actions.cluster.time_slice,
    "dbscan": hypercane.actions.cluster.cluster_by_dbscan,
    "lda": hypercane.actions.cluster.cluster_by_lda,
    "kmeans": hypercane.actions.cluster.cluster_by_kmeans,
    "domainname": hypercane.actions.cluster.cluster_by_domain_name,
    "original-resource": hypercane.actions.cluster.cluster_by_urir,

}

if __name__ == '__main__':

    for item in cluster_parser._subparsers._group_actions:
        for key in item.choices:

            subparser = item.choices[key]

            # Wooey's install script does not know how to handle functions, so we have to repeat this
            required = subparser.add_argument_group('required arguments')

            for entry in universal_gui_required_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                required.add_argument(*flags, **argument_params)

            optional = subparser.add_argument_group('optional arguments')
            for entry in universal_gui_optional_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                optional.add_argument(*flags, **argument_params)

    args = cluster_parser.parse_args()

    # setting expected arguments for GUI
    vars(args)['output_filename'] = "sampled-mementos.tsv"
    vars(args)['logfile'] = "sample.log"
    vars(args)['errorfilename'] = "hypercane-errors.dat"
    vars(args)['cache_storage'] = os.environ.get('HC_CACHE_STORAGE')
    vars(args)['input_arguments'] = args.input_file.name

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    if args.errorfilename is not None:
        hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

    print("starting to identify {} in input".format(args.which))
    cluster_functions[args.which](args)
    print("done identifying {}".format(args.which))
