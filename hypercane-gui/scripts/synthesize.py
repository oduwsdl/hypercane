import os
import zipfile
import shutil
import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.identify
from hypercane.actions.synthesize import raintale_story
import hypercane.errors

from hypercane.args import universal_gui_required_args, universal_gui_optional_args
from hypercane.args.synthesize import subparsers_and_arguments
from hypercane.version import __useragent__
from hypercane.actions import get_logger, calculate_loglevel
from hypercane.utils import get_hc_cache_storage

def zipdir(path, ziph):
    # code from https://www.tutorialspoint.com/How-to-zip-a-folder-recursively-using-Python
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

synthesize_parser = argparse.ArgumentParser(prog="hc synthesize",
    description="'synthesize' synthesizes a web archive collection into other formats, like WARC, JSON, or a set of files in a directory.",
    formatter_class=RawTextHelpFormatter
)

if __name__ == '__main__':

    subparsers = synthesize_parser.add_subparsers(help='synthesizing outputs', dest="synthesizing output (e.g., warcs, raintale-story)")
    subparsers.required = True

    for subparser_name in subparsers_and_arguments:

        # if this doesn't exist, we don't include the subparser for the WUI
        if 'wui-arguments' in subparsers_and_arguments[subparser_name]:

            subparser = subparsers.add_parser(
                subparser_name,
                help=subparsers_and_arguments[subparser_name]['help']
            )
            defaults_definition = subparsers_and_arguments[subparser_name]['set_defaults']
            subparser.set_defaults(
                which=defaults_definition['which'],
                output_extension=defaults_definition['output_extension'],
                exec=defaults_definition['exec']
            )

            for argument in subparsers_and_arguments[subparser_name]['wui-arguments']:
                flags = argument['flags']
                argument_params = argument['argument_params']
                subparser.add_argument(*flags, **argument_params)

            for entry in universal_gui_required_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                subparser.add_argument(*flags, **argument_params)

            for entry in universal_gui_optional_args:
                flags = entry['flags']
                argument_params = entry['argument_params']
                subparser.add_argument(*flags, **argument_params)

    args = synthesize_parser.parse_args() 

    # setting expected arguments for GUI
    if args.output_extension == 'directory':
        vars(args)['output_directory'] = "hypercane-synthesize-output"
    else:
        vars(args)['output_filename'] = "hypercane-synthesize-output{}".format(args.output_extension)      

    vars(args)['logfile'] = "hypercane-status.log"
    vars(args)['errorfilename'] = "hypercane-errors.dat"
    vars(args)['cache_storage'] = get_hc_cache_storage()
    vars(args)['input_arguments'] = args.input_file.name

    from datetime import datetime
    with open("newfile-{}.dat".format(datetime.now()), 'w') as f:
        f.write(str(datetime.now()))

    # TODO: the other files for synthesize and combine need to be updated to use their filenames instead of their file handles
    for raintale_story_filearg in [ 'collection_metadata_filename', 'entitydata_filename', 'termdata_filename', 'imagedata_filename' ]:
        print("searching for {} in the input".format(raintale_story_filearg))
        if raintale_story_filearg in vars(args):
            if vars(args)[raintale_story_filearg] is not None:
                print("adding {} data file {} to the list of files to include in the Raintale story file".format(
                    raintale_story_filearg,
                    vars(args)[raintale_story_filearg].name
                ), flush=True)
                fh = vars(args)[raintale_story_filearg]
                vars(args)[raintale_story_filearg] = fh.name
                fh.close()

    if 'extra_data' in vars(args):
        print("found extra data files")
        if vars(args)['extra_data'] is not None:
            filename_list = []
            for fh in vars(args)['extra_data']:
                print("adding extra data file {} to the list of files to include in the Raintale story file".format(fh.name), flush=True)
                filename_list.append(fh.name)
                fh.close()
            vars(args)['extra_data'] = filename_list
        else:
            print("setting extra data file list to a default empty list")
            vars(args)['extra_data'] = []

    else:
        print("setting extra data file list to a default empty list")
        vars(args)['extra_data'] = []

    if 'append_files' in vars(args):
        if vars(args)['append_files'] is not None:
            filename_list = []
            for fh in vars(args)['append_files']:
                print("appending file {} to the list of files to combine".format(fh.name), flush=True)
                filename_list.append(fh.name)
                fh.close()
            vars(args)['append_files'] = filename_list

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    if args.errorfilename is not None:
        hypercane.errors.errorstore.type = hypercane.errors.FileErrorStore(args.errorfilename)

    print("starting to synthesize {} in input".format(args.which))
    args.exec(args)

    if args.output_extension == 'directory':
        print("compressing output into a single zip file")
        outputZip = zipfile.ZipFile('hypercane-synthesize-output.zip', 'w')
        zipdir(args.output_directory, outputZip)
        outputZip.close()
        shutil.rmtree(args.output_directory)

    print("done synthesizing {}".format(args.which))
