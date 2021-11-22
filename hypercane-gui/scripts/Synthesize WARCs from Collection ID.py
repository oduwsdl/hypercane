import argparse
import zipfile
import shutil
import os

from argparse import RawTextHelpFormatter

import hypercane.actions.synthesize
import hypercane.errors

from hypercane.args import universal_by_cid_gui_required_args, universal_gui_optional_args
from hypercane.version import __useragent__
from hypercane.utils import get_hc_cache_storage
from hypercane.actions import get_logger, calculate_loglevel

def zipdir(path, ziph):
    # code from https://www.tutorialspoint.com/How-to-zip-a-folder-recursively-using-Python
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

parser = argparse.ArgumentParser(
    description="Submit a public Collection ID and Hypercane will generate a ZIP file containing WARCs synthesized from these URLs suitable for analysis with tools like SolrWayback and Archives Unleashed Toolkit.",
    formatter_class=RawTextHelpFormatter
)

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

optional.add_argument('--no-download-embedded', dest='no_download_embedded',
    help="issue this argument to avoid synthesizing a WARC with embedded images, JavaScript, and stylesheets",
    required=False, default=False, action='store_true'
)

args = parser.parse_args()

vars(args)['logfile'] = "hypercane-status.log"
vars(args)['errorfilename'] = "hypercane-errors.dat"
vars(args)['cache_storage'] = get_hc_cache_storage()
vars(args)['input_arguments'] = args.collection_id
vars(args)['output_directory'] = "warcs-output"

print("starting to synthesize WARCs from the {} web archive collection collection ID {}".format(args.input_type, args.collection_id), flush=True) 
print("in case of an issue, your administrator may need to know that the output of this job is stored in {}".format(os.getcwd()), flush=True)

# do this or you get no logging
logger = get_logger(
    __name__,
    calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
    args.logfile
)

# do this or you get no errorfile
hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

hypercane.actions.synthesize.synthesize_warcs(args)

print("compressing output into a single zip file", flush=True)
outputZip = zipfile.ZipFile('warcs-output.zip', 'w')
zipdir(args.output_directory, outputZip)
outputZip.close()
shutil.rmtree(args.output_directory)

print("done synthesizing WARCs from collection ID {}, output is stored in warcs-output.zip".format(args.collection_id), flush=True)
