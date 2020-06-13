import sys
import hypercane.errors

def process_input_args(args, parser):

    from hypercane.actions import add_input_args, \
        add_default_args, test_input_args

    parser = add_input_args(parser)

    parser = add_default_args(parser)

    for action in parser._actions:
        if action.dest == 'output_filename':
            action.help = "the directory to which we write the files in the output"
            action.dest = 'output_directory'

    args = parser.parse_args(args)

    args = test_input_args(args)

    args = parser.parse_args(args)

    if args.errorfilename is not None:
        hypercane.errors.errorstore = \
            hypercane.errors.FileErrorStore(
                args.errorfilename
            )

    return args

def combine_files(args):

    import argparse
    import json
    import csv

    from hypercane.actions import get_logger, calculate_loglevel, \
        process_input_args

    parser = argparse.ArgumentParser(
        description="Combine the output from several Hypercane commands into one TSV file.",
        prog="hc synthesize combine"
    )

    parser.add_argument('--append-files', dest='append_files',
        help='the Hypercane files to append to the file specified by the -a command',
        nargs='*'
    )

    args = process_input_args(args, parser)

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    logger.info("Starting combination of files from input")

    if args.input_type == 'archiveit':
        msg = "Input type archiveit not yet implemented, choose mementos, timemaps, or orignal-resources instead"
        logger.exception(msg)
        raise NotImplementedError(msg)

    allfiles = []
    allfiles.append( args.input_arguments )
    allfiles.extend( args.append_files )

    fieldnames = []

    for filename in allfiles:

        with open(filename) as g:

            csvreader = csv.reader(g, delimiter='\t')
            fieldnames.extend( next(csvreader) )

    logger.info("detected fieldnames: {}".format(fieldnames))

    firstfield = None

    for input_field in ['URI-M', 'URI-T', 'URI-R']:

        input_field_count = fieldnames.count(input_field)

        if input_field_count == len(allfiles):
            if input_field_count > 0:
                firstfield = input_field
                break
        else:
            msg = "All input files must contain the same input type, either mementos, timemaps, or original-resources"
            logger.critical(msg)
            raise RuntimeError(msg)

    output_fieldnames = list(set(fieldnames))
    output_fieldnames.remove(firstfield)
    output_fieldnames.insert(0, firstfield)

    with open(args.output_filename, 'w') as f:

        writer = csv.DictWriter(f, delimiter='\t', fieldnames=output_fieldnames)
        writer.writeheader()

        for filename in allfiles:

            with open(filename) as g:

                csvreader = csv.DictReader(g, delimiter='\t')

                for row in csvreader:

                    outputrow = {}
                    outputrow[firstfield] = row[firstfield]

                    for fieldname in output_fieldnames:

                        try:
                            outputrow[fieldname] = row[fieldname]
                        except KeyError:
                            outputrow[fieldname] = None

                    writer.writerow(outputrow)

    logger.info("Writing new file to {}".format(args.output_filename))


def raintale_story(args):

    import argparse
    import json
    import hypercane.actions
    from hypercane.actions import get_logger, calculate_loglevel, \
        process_input_args
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    parser = argparse.ArgumentParser(
        description="Generate a story suitable as input to Raintale.",
        prog="hc synthesize raintale-story"
    )

    parser.add_argument('--title', dest='title',
        help='The title of the story', required=False, default=None
    )

    parser.add_argument('--imagedata', dest='imagedata_filename',
        help='A file containing image data, as produced by hc report image-data',
        required=False, default=None
    )

    parser.add_argument('--termdata', dest='termdata_filename',
        help='A file containing term data, as produced by hc report terms',
        required=False, default=None
    )

    parser.add_argument('--term-count', dest='term_count',
        help='The number of top terms to select from the term data.',
        required=False, default=5
    )

    parser.add_argument('--entitydata', dest='entitydata_filename',
        help='A file containing term data, as produced by hc report entities',
        required=False, default=None
    )

    parser.add_argument('--collection_metadata', dest='collection_metadata_filename',
        help='A file containing Archive-It colleciton metadata, as produced by hc report metadata',
        required=False, default=None
    )

    parser.add_argument('--entity-count', dest='entity_count',
        help='The number of top terms to select from the term data.',
        required=False, default=5
    )

    parser.add_argument('--extradata', dest='extra_data',
        help='a JSON file containing extra data that will be included in the Raintale JSON, '
        'multiple filenames may follow this argument, '
        'the name of the file without the extension will be the JSON key', nargs='*',
        default=[]
    )

    args = hypercane.actions.process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting generation of files from input")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

    story_json = {
        'metadata': {}
    }

    if args.collection_metadata_filename is not None:
        with open(args.collection_metadata_filename) as f:
            jdata = json.load(f)

            if 'name' in jdata:
                story_json['title'] = jdata['name']

            for key in jdata:

                if key != 'seed_metadata':
                    story_json['metadata'][key] = jdata[key]

    if args.title is None:
        if args.collection_metadata_filename is None:
            logger.critical("Cannot continue, either supply a title with --title or a collection metadata file containing a title with --collection_metadata")
            sys.exit(255)
        else:
            # if we get here, the title should already be set
            pass
    else:
        story_json['title'] = args.title

        if args.title == "Archive-It Collection":

            if 'id' in jdata:
                story_json['title'] = args.title + " " + jdata['id']

            if 'name' in jdata:
                story_json['title'] = story_json['title'] + ': ' + jdata['name']


    story_json['elements'] = []

    if args.imagedata_filename is not None:
        with open(args.imagedata_filename) as f:
            jdata = json.load(f)
            story_json['story image'] = sorted(jdata['ranked data'], reverse=True)[0][-1]

    if args.termdata_filename is not None:
        import csv
        with open(args.termdata_filename) as f:
            reader = csv.DictReader(f, delimiter='\t')
            tf = []
            for row in reader:
                tf.append( ( int(row['Frequency in Corpus']), row['Term'] ) )

            story_json.setdefault('metadata', {})
            story_json['metadata']['terms'] = {}

            for term in sorted(tf, reverse=True)[0:args.term_count]:
                # story_json['metadata']['terms'].append(term[1])
                story_json['metadata'].setdefault('terms', {})
                story_json['metadata']['terms'][term[1]] = term[0]

    if args.entitydata_filename is not None:
        import csv
        with open(args.entitydata_filename) as f:
            reader = csv.DictReader(f, delimiter='\t')
            tf = []
            for row in reader:

                try:
                    tf.append( ( float(row['Corpus TF-IDF']), row['Entity'] ) )
                except TypeError:
                    logger.exception("row caused type error, skipping: {}".format(row))

            story_json.setdefault('metadata', {})
            story_json['metadata']['entities'] = {}

            for entity in sorted(tf, reverse=True)[0:args.entity_count]:
                # story_json['metadata']['entities'].append(entity[1])
                story_json['metadata'].setdefault('entities', {})
                story_json['metadata']['entities'][entity[1]] = entity[0]

    for urim in urimdata.keys():

        story_element = {
            "type": "link",
            "value": urim
        }

        story_json['elements'].append(story_element)

    for filename in args.extra_data:
        with open(filename) as f:
            edata = json.load(f)
            fname = filename.rsplit('.', 1)[0]
            story_json.setdefault('extra', {})
            story_json['extra'][fname] = edata

    logger.info("Writing Raintale JSON out to {}".format(
        args.output_filename
    ))

    with open(args.output_filename, 'w') as f:
        json.dump(story_json, f, indent=4)

    logger.info("Done generating Raintale JSON output at {}".format(args.output_filename))


def synthesize_warcs(args):

    import argparse
    from hypercane.actions import get_logger, calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from warcio.warcwriter import WARCWriter
    from warcio.statusandheaders import StatusAndHeaders
    import os
    from datetime import datetime
    import otmt
    from hashlib import md5
    import traceback

    parser = argparse.ArgumentParser(
        description="Discover the mementos in a web archive collection.",
        prog="hc synthesize files"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting generation of files from input")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

    if not os.path.exists(args.output_directory):
        logger.info("Output directory {} does not exist, creating...".format(args.output_directory))
        os.makedirs(args.output_directory)

    from hypercane.synthesize.warcs import synthesize_warc

    # TODO: make this multithreaded
    for urim in urimdata.keys():
        try:
            synthesize_warc(urim, session, args.output_directory)
        except Exception:
            logger.exception("failed to generate WARC for URI-M {}".format(urim))
            hypercane.errors.errorstore.add(urim, traceback.format_exc())

    logger.info("Done generating directory of files, output is at {}".format(args.output_directory))

def synthesize_files(args):

    import os
    import argparse
    from hypercane.actions import get_logger, calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hashlib import md5
    import traceback

    parser = argparse.ArgumentParser(
        description="Save copies of mementos as files from a web archive collection.",
        prog="hc synthesize files"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting generation of files from input")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

    if not os.path.exists(args.output_directory):
        logger.info("Output directory {} does not exist, creating...".format(args.output_directory))
        os.makedirs(args.output_directory)

    # TODO: make this multithreaded
    with open("{}/metadata.tsv".format(args.output_directory), 'w') as metadatafile:

        for urim in urimdata.keys():

            try:

                r = session.get(urim)
                r.raise_for_status()

                data = r.content

                m = md5()
                m.update(urim.encode('utf8'))
                urlhash = m.hexdigest()
                newfilename = urlhash + '.dat'

                logger.info("writing out data for URI-M {}".format(urim))
                with open("{}/{}".format(
                    args.output_directory, newfilename), 'wb') as newfile:
                    newfile.write(data)

                metadatafile.write("{}\t{}\n".format(urim, newfilename))

            except Exception as exc:
                logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, repr(exc)))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    logger.info("Done generating directory of files, output is at {}".format(args.output_directory))

def synthesize_bpfree_files(args):

    import os
    import argparse
    from hypercane.actions import get_logger, calculate_loglevel
    from hypercane.utils import get_web_session, get_boilerplate_free_content
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hashlib import md5
    import otmt
    from justext import justext, get_stoplist
    import traceback

    parser = argparse.ArgumentParser(
        description="Save boilerplate-free copies of mementos as files from a web archive collection.",
        prog="hc synthesize bpfree-files"
    )

    args = process_input_args(args, parser)
    output_type = 'mementos'

    logger = get_logger(
        __name__,
        calculate_loglevel(verbose=args.verbose, quiet=args.quiet),
        args.logfile
    )

    session = get_web_session(cache_storage=args.cache_storage)

    logger.info("Starting generation of boilerplate-free files from input")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

    if not os.path.exists(args.output_directory):
        logger.info("Output directory {} does not exist, creating...".format(args.output_directory))
        os.makedirs(args.output_directory)

    # TODO: make this multithreaded
    with open("{}/metadata.tsv".format(args.output_directory), 'w') as metadatafile:

        for urim in urimdata.keys():

            try:

                bpfree = get_boilerplate_free_content(urim, cache_storage=args.cache_storage)

                m = md5()
                m.update(urim.encode('utf8'))
                urlhash = m.hexdigest()
                newfilename = urlhash + '.dat'

                logger.info("writing out data for URI-M {}".format(urim))
                with open("{}/{}".format(
                    args.output_directory, newfilename), 'wb') as newfile:
                    newfile.write(bpfree)

                metadatafile.write("{}\t{}\n".format(urim, newfilename))

            except Exception as exc:
                logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, repr(exc)))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    logger.info("Done generating directory of boilerplate-free files, output is at {}".format(args.output_directory))

def print_usage():

    print("""'hc synthesize' is used to synthesize a web archive collection into other formats, like WARC, JSON, or a set of files in a directory

    Supported commands:
    * warcs - for generating a directory of WARCs
    * files - for generating a directory of mementos
    * bpfree-files - for generating a directory of boilerplate-free mementos
    * raintale-story - for generating a JSON file suitable as input for Raintale
    * combine - combine the output from several Hypercane runs together

    Examples:

    hc synthesize warcs -i archiveit -a 694 --depth 2 -o output-directory -cs mongodb://localhost/cache

    hc synthesize files -i timemaps -a timemap-file.tsv -o output-directory -cs mongodb://localhost/cache

    hc synthesize raintale-story -i mementos -a memento-file.tsv -o story.json -cs mongodb://localhost/cache

""")

supported_commands = {
    "warcs": synthesize_warcs,
    "files": synthesize_files,
    "bpfree-files": synthesize_bpfree_files,
    "raintale-story": raintale_story,
    "combine": combine_files
}
