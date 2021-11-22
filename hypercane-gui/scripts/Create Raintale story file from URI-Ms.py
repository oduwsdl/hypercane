import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.report
import hypercane.actions.synthesize
import hypercane.errors

from hypercane.utils import get_hc_cache_storage
from hypercane.args.report import default_entity_types_str

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    prog="create Raintale story file from URI-Ms.py",
    description="Submit a file containing a set of archived page URLs (i.e., mementos, captures, URI-Ms) and Hypercane will  generate metadata and synthesize a rich story file for use with Raintale.",
    formatter_class=RawTextHelpFormatter
)

# Wooey's install script does not know how to handle functions, so we have to repeat this
required = parser.add_argument_group('required arguments')
required.add_argument('--title', dest='title', help="Title for your Raintale story")
required.add_argument('-a', dest='input_file', help="A file containing a list of archvied page URLs (i.e., mementos, captures, URI-Ms).", type=argparse.FileType('r'))

optional = parser.add_argument_group('optional arguments')
optional.add_argument('--term-count', dest='term_count', help='The number of phrases to include, ranked by frequency, in the story output.', default=5, type=int)
optional.add_argument('--entity-count', dest='entity_count', help='The number of entities (e.g., places, people, organizations, event names) to include, ranked by frequency, in the story output.', default=5, type=int)
optional.add_argument('-v', dest='verbose', action='store_true', help="This will raise the logging level to debug for more verbose output in the log files.")
optional.add_argument('-q', dest='quiet', action='store_true', help="This will lower the logging level to only show warnings or errors in the log files.")

args = parser.parse_args()
vars(args)['input_type'] = 'mementos'
vars(args)['input_arguments'] = args.input_file.name
vars(args)['cache_storage'] = get_hc_cache_storage()
vars(args)['crawl_depth'] = 1
vars(args)['added_stopword_filename'] = None

print("starting to generate all data necessary to produce a rich story file for use with Raintale")

# 1 report entities
vars(args)['entity_types'] = default_entity_types_str
vars(args)['output_filename'] = "report-entities.tsv"
vars(args)['logfile'] = "report-entities.log"
vars(args)['errorfilename'] = "report-entites-errors.dat"
print("creating a report of entities (e.g., places, people, organizations, event names) and saving it to {}".format(args.output_filename))
hypercane.actions.report.report_entities(args)

# 2 report sumgrams
vars(args)['output_filename'] = "report-sumgrams.tsv"
vars(args)['logfile'] = "report-sumgrams.log"
vars(args)['errorfilename'] = "report-sumgrams-errors.dat"
vars(args)['use_sumgrams'] = True
print("creating a report of common phrases (i.e., sumgrams) from the text and saving it to {}".format(args.output_filename))
hypercane.actions.report.report_ranked_terms(args)

# 3 report image
vars(args)['output_filename'] = "report-images.json"
vars(args)['logfile'] = "report-images.log"
vars(args)['errorfilename'] = "report-images-errors.dat"
vars(args)['use_urirs'] = False
vars(args)['output_format'] = 'json'
print("analyzing all images from the input documents and saving to {}".format(args.output_filename))
hypercane.actions.report.report_image_data(args)

# 4 Raintale story data file
vars(args)['output_filename'] = "raintale-story.json"
vars(args)['logfile'] = "synthesize-raintale-story-status.log"
vars(args)['errorfilename'] = "synthesize-raintale-story-errors.dat"
vars(args)['entitydata_filename'] = "report-entities.tsv"
vars(args)['termdata_filename'] = "report-sumgrams.tsv"
vars(args)['imagedata_filename'] = "report-images.json"
vars(args)['collection_metadata_filename'] = None
vars(args)['extra_data'] = []
print("generating Raintale story data file at {}".format(args.output_filename))
hypercane.actions.synthesize.raintale_story(args)

print("done generating a rich Raintale story file, download {} and submit it to Raintale to visualize your story".format(args.output_filename))
