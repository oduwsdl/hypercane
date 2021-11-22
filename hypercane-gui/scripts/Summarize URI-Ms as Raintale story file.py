import argparse

from argparse import RawTextHelpFormatter
from copy import deepcopy

import hypercane.args.sample
import hypercane.actions.sample
import hypercane.actions.report
import hypercane.actions.synthesize
import hypercane.errors

from hypercane.utils import get_hc_cache_storage
from hypercane.args.report import default_entity_types_str

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    description="Submit a file containing a set of archived page URLs (i.e., mementos, captures, URI-Ms) and Hypercane will sample documents from the collection, generate metadata, and synthesize a rich story file for use with Raintale.",
    formatter_class=RawTextHelpFormatter
)

required = parser.add_argument_group('required arguments')
required.add_argument('--title', dest='title', help="Title for your Raintale story", required=True)
required.add_argument('-a', dest='input_file', help="A file containing a list of archvied page URLs (i.e., mementos, captures, URI-Ms).", type=argparse.FileType('r'), required=True)

sample_algorithm_function_mapping = {
    "DSA1": "DSA1",
    "DSA2": "DSA2",
    "DSA3": "DSA3",
    "DSA4": "DSA4",
    "True Random": None,
    "Filtered Random": "filtered-random",
    "Order By Memento Datetime Then Systematically Sample": "ordered-systematic"
}

required.add_argument('-s', dest='sampling_algorithm', help="The sampling algorithm to execute to generate the sample documents from the collection.", required=True, choices=list(sample_algorithm_function_mapping.keys()))

optional = parser.add_argument_group('optional arguments')
optional.add_argument('--sample-size', dest='sample_size', help="The target size of the sample. Only used by 'True Random' and 'Filtered Random' sampling algorithms, ignore otherwise.", default=28, type=int)
optional.add_argument('--systematic-skip', dest='systematic_skip', help="The number of items to skip when applying Systematic Sampling, ignored otherwise.", default=100, type=int)
optional.add_argument('--term-count', dest='term_count', help='The number of phrases to include, ranked by frequency, in the Raintale story file.', default=5, type=int)
optional.add_argument('--entity-count', dest='entity_count', help='The number of entities (e.g., places, people, organizations, event names) to include, ranked by frequency, in the Raintale story file.', default=5, type=int)
optional.add_argument('-v', dest='verbose', action='store_true', help="This will raise the logging level to debug for more verbose output in the log files.")
optional.add_argument('-q', dest='quiet', action='store_true', help="This will lower the logging level to only show warnings or errors in the log files.")

args = parser.parse_args()

vars(args)['crawl_depth'] = 1
vars(args)['sample_count'] = args.sample_size
vars(args)['input_arguments'] = args.collection_id
vars(args)['cache_storage'] = get_hc_cache_storage()

print("starting the process of producing a collection sample and a rich story file for use with Raintale", flush=True)

# 1 sample using given algorithm
vars(args)['output_filename'] = "sample-story-mementos.tsv"
vars(args)['logfile'] = "sample-mementos.log"
vars(args)['errorfilename'] = "sample-mementos.dat"
print("creating a sample of mementos from collection {} and saving it to {}".format(args.collection_id, args.output_filename), flush=True)
if args.sampling_algorithm == "True Random":
    hypercane.actions.sample.sample_with_true_random(args)
else:
    # make a *deep* copy of args before proceeding
    sample_args = deepcopy(args)
    delattr(sample_args, 'entity_count')
    delattr(sample_args, 'term_count')
    vars(sample_args)['which'] = args.sampling_algorithm
    vars(sample_args)['script_path'] = hypercane.args.sample.custom_script_data[
        sample_algorithm_function_mapping[args.sampling_algorithm]
    ]['script_path']
    # because these integer values must become strings for passing internal to Hypercane
    vars(sample_args)['sample_size'] = str(args.sample_size)
    vars(sample_args)['sample_count'] = str(args.sample_count)
    vars(sample_args)['systematic_skip'] = str(args.systematic_skip)
    vars(sample_args)['working_directory'] = '.'
    hypercane.actions.sample.sample_with_custom_script(sample_args)

# 2 metadata report
vars(args)['output_filename'] = "report-metadata.json"
vars(args)['logfile'] = "report-metadata.log"
vars(args)['errorfilename'] = "report-entites-errors.dat"
print("creating a report of collection metadata and saving it to {}".format(args.output_filename), flush=True)
hypercane.actions.report.discover_collection_metadata(args)

# 3 report entities
vars(args)['input_type'] = 'mementos'
vars(args)['input_arguments'] = "sample-story-mementos.tsv"
vars(args)['entity_types'] = default_entity_types_str
vars(args)['output_filename'] = "report-entities.tsv"
vars(args)['logfile'] = "report-entities.log"
vars(args)['errorfilename'] = "report-entites-errors.dat"
print("creating a report of entities (e.g., places, people, organizations, event names) and saving it to {}".format(args.output_filename), flush=True)
hypercane.actions.report.report_entities(args)

# 4 report sumgrams
vars(args)['input_type'] = 'mementos'
vars(args)['input_arguments'] = "sample-story-mementos.tsv"
vars(args)['output_filename'] = "report-sumgrams.tsv"
vars(args)['logfile'] = "report-sumgrams.log"
vars(args)['errorfilename'] = "report-sumgrams-errors.dat"
vars(args)['use_sumgrams'] = True
vars(args)['added_stopword_filename'] = None
print("creating a report of common phrases (i.e., sumgrams) from the text and saving it to {}".format(args.output_filename), flush=True)
hypercane.actions.report.report_ranked_terms(args)

# 5 report image
vars(args)['input_type'] = 'mementos'
vars(args)['input_arguments'] = "sample-story-mementos.tsv"
vars(args)['output_filename'] = "report-images.json"
vars(args)['logfile'] = "report-images.log"
vars(args)['errorfilename'] = "report-images-errors.dat"
vars(args)['use_urirs'] = False
vars(args)['output_format'] = 'json'
print("analyzing all images from the input documents and saving to {}".format(args.output_filename), flush=True)
hypercane.actions.report.report_image_data(args)

# 6 Raintale story data file
vars(args)['input_type'] = 'mementos'
vars(args)['input_arguments'] = "sample-story-mementos.tsv"
vars(args)['output_filename'] = "raintale-story.json"
vars(args)['logfile'] = "synthesize-raintale-story-status.log"
vars(args)['errorfilename'] = "synthesize-raintale-story-errors.dat"
vars(args)['entitydata_filename'] = "report-entities.tsv"
vars(args)['termdata_filename'] = "report-sumgrams.tsv"
vars(args)['imagedata_filename'] = "report-images.json"
vars(args)['collection_metadata_filename'] = "report-metadata.json"
vars(args)['extra_data'] = []
print("generating Raintale story data file at {}".format(args.output_filename), flush=True)
hypercane.actions.synthesize.raintale_story(args)

print("done generating a rich Raintale story file, download {} and submit it to Raintale to visualize your story".format(args.output_filename), flush=True)
