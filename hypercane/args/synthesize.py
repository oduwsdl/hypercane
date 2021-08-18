import argparse
from argparse import RawTextHelpFormatter

import hypercane.actions.synthesize

synthesize_parser = argparse.ArgumentParser(prog="hc synthesize",
    description="'synthesize' synthesize a web archive collection into other formats, like WARC, JSON, or a set of files in a directory.",
    formatter_class=RawTextHelpFormatter
)

subparsers = synthesize_parser.add_subparsers(help='synthesizing outputs', dest="synthesizing output (e.g., warcs, raintale-story)")
subparsers.required = True

warcs_parser = subparsers.add_parser('warcs', help="Create WARCs from the mementos in the input.")
warcs_parser.set_defaults(
    which='warcs',
    exec=hypercane.actions.synthesize.synthesize_warcs
)

warcs_parser.add_argument('--no-download-embedded', dest='no_download_embedded',
    help="issue this argument to avoid synthesizing a WARC with embedded images, JavaScript, and stylesheets",
    required=False, default=False, action='store_true'
)

files_parser = subparsers.add_parser('files', help="Save copies of mementos as files from the mementos in the input.")
files_parser.set_defaults(
    which='files',
    exec=hypercane.actions.synthesize.synthesize_files
)

bpfreefiles_parser = subparsers.add_parser('bpfree-files', help="Save boilerplate-free files of the mementos in the input.")
bpfreefiles_parser.set_defaults(
    which='bpfree-files',
    exec=hypercane.actions.synthesize.synthesize_bpfree_files
)

raintalestory_parser = subparsers.add_parser('raintale-story', help="Generate a story suitable for input to Raintale.")
raintalestory_parser.set_defaults(
    which='raintale-story',
    exec=hypercane.actions.synthesize.raintale_story
)

raintalestory_parser.add_argument('--title', dest='title',
    help='The title of the story', required=False, default=None
)

raintalestory_parser.add_argument('--imagedata', dest='imagedata_filename',
    help='A file containing image data, as produced by hc report image-data',
    required=False, default=None
)

raintalestory_parser.add_argument('--termdata', dest='termdata_filename',
    help='A file containing term data, as produced by hc report terms',
    required=False, default=None
)

raintalestory_parser.add_argument('--term-count', dest='term_count',
    help='The number of top terms to select from the term data.',
    required=False, default=5
)

raintalestory_parser.add_argument('--entitydata', dest='entitydata_filename',
    help='A file containing term data, as produced by hc report entities',
    required=False, default=None
)

raintalestory_parser.add_argument('--collection_metadata', dest='collection_metadata_filename',
    help='A file containing Archive-It colleciton metadata, as produced by hc report metadata',
    required=False, default=None
)

raintalestory_parser.add_argument('--entity-count', dest='entity_count',
    help='The number of top terms to select from the term data.',
    required=False, default=5
)

raintalestory_parser.add_argument('--extradata', dest='extra_data',
    help='a JSON file containing extra data that will be included in the Raintale JSON, '
    'multiple filenames may follow this argument, '
    'the name of the file without the extension will be the JSON key', nargs='*',
    default=[]
)

combine_parser = subparsers.add_parser('combine', help="Combine the output from several Hypercane commands into one TSV file.")
combine_parser.set_defaults(
    which='combine',
    exec=hypercane.actions.synthesize.combine_files
)

combine_parser.add_argument('--append-files', dest='append_files',
    help='the Hypercane files to append to the file specified by the -a command',
    nargs='*'
)
