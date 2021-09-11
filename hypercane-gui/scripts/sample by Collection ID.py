import os

import hypercane.actions.sample
import hypercane.errors

from hypercane.args import universal_by_cid_gui_required_args, universal_gui_optional_args
from hypercane.args.sample import sample_parser
from hypercane.version import __useragent__
from hypercane.actions import get_logger, calculate_loglevel

if __name__ == '__main__':

    for item in sample_parser._subparsers._group_actions:
        for key in item.choices:

            subparser = item.choices[key]

            # Wooey's install script does not know how to handle functions, so we have to repeat this
            required = subparser.add_argument_group('required arguments')

            for entry in universal_by_cid_gui_required_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                required.add_argument(*flags, **argument_params)

            optional = subparser.add_argument_group('optional arguments')
            for entry in universal_gui_optional_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                optional.add_argument(*flags, **argument_params)

    args = sample_parser.parse_args()

    # setting expected arguments for GUI
    vars(args)['output_filename'] = "hypercane-sample-output.tsv"
    vars(args)['logfile'] = "hypercane-status.log"
    vars(args)['errorfilename'] = "hypercane-errors.dat"
    vars(args)['cache_storage'] = os.environ.get('HC_CACHE_STORAGE')
    vars(args)['input_arguments'] = args.collection_id
    vars(args)['working_directory'] = '.'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    if args.errorfilename is not None:
        hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

    print("starting to create sample with method {} using function {}".format(args.which, args.exec.__name__), flush=True)
    print("in case of an issue, your administrator may need to know that the output of this job is stored in {}".format(os.getcwd()), flush=True)
    args.exec(args)
    print("done creating sample", flush=True)
