import hypercane.actions.synthesize
import hypercane.errors

from copy import deepcopy

from hypercane.args import universal_cli_required_args, universal_cli_optional_args
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
            for entry in universal_cli_required_args:

                flags = entry['flags']

                argument_params = deepcopy(entry['argument_params'])

                if key in ['warcs', 'files', 'bpfree-files']:

                    if argument_params['dest'] == 'output_filename':

                        argument_params['dest'] = 'output_directory'
                        argument_params['help'] = "the directory to which we write the output"

                required.add_argument(*flags, **argument_params)

            optional = subparser.add_argument_group('optional arguments')
            for entry in universal_cli_optional_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                optional.add_argument(*flags, **argument_params)

    args = synthesize_parser.parse_args()

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    if args.errorfilename is not None:
        hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

    synthesize_functions[args.which](args)
