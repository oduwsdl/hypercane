import argparse
import os

from argparse import RawTextHelpFormatter

import hypercane.actions.identify
import hypercane.errors

from hypercane.args import universal_by_cid_gui_required_args, universal_gui_optional_args
from hypercane.actions import get_logger, calculate_loglevel
from hypercane.utils import get_hc_cache_storage

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    description="Submit a public web archive collection's ID and Hypercane will generate a file listing all archived page URLs (i.e., mementos, captures, URI-Ms).",
    formatter_class=RawTextHelpFormatter
)

# Wooey's install script does not know how to handle functions, so we have to repeat this
required = parser.add_argument_group('required arguments')
for entry in universal_by_cid_gui_required_args:
    flags = entry['flags']
    argument_params = entry['argument_params']
    required.add_argument(*flags, **argument_params)

optional = parser.add_argument_group('optional arguments')
for entry in universal_gui_optional_args:
    flags = entry['flags']
    argument_params = entry['argument_params']
    optional.add_argument(*flags, **argument_params)

args = parser.parse_args()

vars(args)['output_filename'] = "archived-page-urls.txt"
vars(args)['logfile'] = "hypercane-status.log"
vars(args)['errorfilename'] = "hypercane-errors.dat"
vars(args)['cache_storage'] = get_hc_cache_storage()
vars(args)['input_arguments'] = args.collection_id

# needed by discover_mementos, but not used
vars(args)['accept_datetime'] = None
vars(args)['timegates'] = None

logger = get_logger(
    __name__,
    calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
    args.logfile
)

if args.errorfilename is not None:
    hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

print("starting to identify archived page URLs (i.e., mementos, captures, URI-Ms) for {} collection ID {}".format(args.input_type, args.collection_id))
print("in case of an issue, your administrator may need to know that the output of this job is stored in {}".format(os.getcwd()), flush=True)
print("using cache at location {}".format(args.cache_storage))
hypercane.actions.identify.discover_mementos(args)
print("done identifying archived page URLs (i.e., mementos, captures, URI-Ms) from {} collection {}, saved list to file {}".format(args.input_type, args.collection_id, args.output_filename))
