import os

import hypercane.actions.identify
import hypercane.errors

from copy import deepcopy

from hypercane.args import universal_gui_required_args, universal_gui_optional_args
from hypercane.args.synthesize import synthesize_parser
from hypercane.version import __useragent__
from hypercane.actions import get_logger, calculate_loglevel

synthesize_functions = {
    "warcs": hypercane.actions.synthesize.synthesize_warcs,
    "files": hypercane.actions.synthesize.synthesize_files,
    "bpfree-files": hypercane.actions.synthesize.synthesize_bpfree_files,
    "raintale-story": hypercane.actions.synthesize.raintale_story,
    "combine": hypercane.actions.synthesize.combine_files
}

if __name__ == '__main__':

    for item in synthesize_parser._subparsers._group_actions:
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

    args = synthesize_parser.parse_args()

    # setting expected arguments for GUI
    if args.which == 'raintale-story':
        vars(args)['output_filename'] = "hypercane-synthesize-output.json"
    
    elif args.which == 'combine':
        vars(args)['output_filename'] = "hypercane-synthesize-output.tsv"

    else:
        vars(args)['output_directory'] = "hypercane-synthesize-output"

    vars(args)['logfile'] = "hypercane-status.log"
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
    synthesize_parser[args.which](args)
    print("done identifying {}".format(args.which))
