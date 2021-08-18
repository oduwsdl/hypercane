import argparse
from argparse import RawTextHelpFormatter

from hypercane.actions.report import discover_collection_metadata, \
    report_image_data, report_ranked_terms, report_entities, \
    report_seedstats, report_growth_curve_stats, report_metadatastats, \
    report_html_metadata, report_http_status, report_generated_queries

default_entity_types = ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW']
default_entity_types_str = ','.join( default_entity_types)

report_parser = argparse.ArgumentParser(prog="hc report",
    description="'report' prints reports about web archive collections, including story metadata",
    formatter_class=RawTextHelpFormatter
)

subparsers = report_parser.add_subparsers(help='reports', dest="report (e.g., metadata, growth)")
subparsers.required = True

metadata_parser = subparsers.add_parser('metadata', help="Discover the collection metadata in a web archive collection.")
metadata_parser.set_defaults(which='metadata', exec=discover_collection_metadata)

imagedata_parser = subparsers.add_parser('image-data', help="Provide a report on the images from in the mementos discovered in the input.")
imagedata_parser.set_defaults(which='image-data', exec=report_image_data)

imagedata_parser.add_argument('--use-urirs', required=False,
    dest='use_urirs', action='store_true',
    help="Regardless of headers, assume the input are URI-Rs and do not try to archive or convert them to URI-Ms."
)

imagedata_parser.add_argument('--output-format', required=False,
    dest="output_format", default="json",
    help="Choose the output format, valid formats are JSON and JSONL"
)

terms_parser = subparsers.add_parser('terms', help="Provide a report containing the terms from the collection and their associated frequencies.")
terms_parser.set_defaults(which='terms', exec=report_ranked_terms)

terms_parser.add_argument('--ngram-length', help="The size of the n-grams", dest='ngram_length', default=1, type=int)

terms_parser.add_argument('--sumgrams', '--use-sumgrams', help="If specified, generate sumgrams rather than n-grams.",
    action='store_true', default=False, dest='use_sumgrams'
)

terms_parser.add_argument('--added-stopwords', help="If specified, add stopwords from this file.",
    dest='added_stopword_filename', default=None
)

entities_parser = subparsers.add_parser('entities', help="Provide a report containing the entities from the collection and their associated frequencies.")
entities_parser.set_defaults(which='entities', exec=report_entities)

entities_parser.add_argument('--entity-types', 
    help="A comma-separated list of the types of entities to report, from https://spacy.io/api/annotation#named-entities",
    dest='entity_types',
    default=default_entity_types_str,
    type=str
)

seedstatistics_parser = subparsers.add_parser('seed-statistics', help="Provide a report containing statistics on the original-resources derived from the input.")
seedstatistics_parser.set_defaults(which='seed-statistics', exec=report_seedstats)

growth_parser = subparsers.add_parser('growth', help="Provide a report containing statistics growth of mementos derived from the input.")
growth_parser.set_defaults(which='growth', exec=report_growth_curve_stats)

growth_parser.add_argument('--growth-curve-file', dest='growthcurve_filename',
    help="If present, draw a growth curve and write it to the filename specified.",
    default=None, required=False)

metadatastatistics_parser = subparsers.add_parser('metadata-statistics', help="Discover the collection metadata in a web archive collection.")
metadatastatistics_parser.set_defaults(which='metadata-statistics', exec=report_metadatastats)

htmlmetadata_parser = subparsers.add_parser('html-metadata', help="Provide a report on the HTML metadata of the mementos discovered in the input.")
htmlmetadata_parser.set_defaults(which='html-metadata', exec=report_html_metadata)

htmlmetadata_parser.add_argument('--use-urirs', required=False,
    dest='use_urirs', action='store_true',
    help="Regardless of headers, assume the input are URI-Rs and do not try to archive or convert them to URI-Ms."
)

httpstatus_parser = subparsers.add_parser('http-status', help="Provide a report on all URI-Ms, their HTTP response status (before redirects), whether they are a redirect, datetime of check, and memento header information.")
httpstatus_parser.set_defaults(which='http-status', exec=report_http_status)

generatequeries_parser = subparsers.add_parser('generate-queries', help="Apply techniques to generate queries from the text of the input documents.")
generatequeries_parser.set_defaults(which='generate-queries', exec=report_generated_queries)

generatequeries_parser.add_argument('--query-count', 
    dest='query_count',
    help="create this many queries per document, only applies to 'doc2query-T5', ignored otherwise", default=5, required=False, type=int
)

generatequeries_parser.add_argument('--use-metadata', 
    dest='use_metadata', action='store_true',
    help="use collection metadata to generate queries instead of documents from input, requires that input be a collection type"
)

generatequeries_parser.add_argument('--generation-method', 
    dest='generation_method',
    help="apply the given generation method for queries, valid values are 'topNentities', 'doc2query-T5', 'lexical-signature'",
    default='doc2query-T5', required=False
)

generatequeries_parser.add_argument('--term-count',
    dest='term_count',
    help="create queries with a maximum of this many terms",
    default=10, required=False, type=int
)

generatequeries_parser.add_argument('--entity-types', 
    help="A comma-separated list of the types of entities to report, from https://spacy.io/api/annotation#named-entities -- only applies to 'topNentities', ignored otherwise", 
    dest='entity_types',
    default=default_entity_types_str, 
    type=str
)
