import os

default_required_args = [
    [ '-i', 'input_type',  "The input type, one of mementos, timemaps, original-resources, archiveit, trove, or pandora-collection.", 'store', None ],
    [ '-a', 'input_arguments',  "Either a file containing a list of URIs, or a collection identifier from Archive-It, Pandora, or Trove.", 'store', ['mementos', 'timemaps', 'original-resources', 'archive-it', 'pandora-subject', 'pandora-collection', 'trove'] ],
    [ '-o', 'output_filename',  "The file to which we write output.", 'store', None ],
]

default_optional_args = [
    # TODO: if logfile is None, set to STDOUT
    [ '-l', 'logfile',  "The path to a logging file. The log is printed to screen by default.", 'store', None ],
    [ '-v', 'verbose',  "This will raise the logging level to debug for more verbose output.", 'store_true', None ],
    [ '-q', 'quiet',  "This will lower the logging level to only show warnings or errors.", 'store_true', None ],
    [ '-cs', 'cache_storage', "The path to the MongoDB database to use as a cache.", 'store', os.environ.get('HC_CACHE_STORAGE') ],
    [ '-e', 'errorfilename', "The path to filename that records URL processing failures.", 'store', 'hypercane-errors.dat'],
]

