import sys
import hypercane.errors
import logging

module_logger = logging.getLogger("hypercane.actions.score")

def combine_files(args):

    import csv

    module_logger.info("Starting combination of files from input")

    if args.input_type == 'archiveit':
        msg = "Input type archiveit not yet implemented, choose mementos, timemaps, or orignal-resources instead"
        module_logger.exception(msg)
        raise NotImplementedError(msg)

    allfiles = []
    allfiles.append( args.input_arguments )
    allfiles.extend( args.append_files )

    fieldnames = []

    for filename in allfiles:

        with open(filename) as g:

            csvreader = csv.reader(g, delimiter='\t')
            fieldnames.extend( next(csvreader) )

    module_logger.info("detected fieldnames: {}".format(fieldnames))

    firstfield = None

    for input_field in ['URI-M', 'URI-T', 'URI-R']:

        input_field_count = fieldnames.count(input_field)

        if input_field_count == len(allfiles):
            if input_field_count > 0:
                firstfield = input_field
                break
        else:
            msg = "All input files must contain the same input type, either mementos, timemaps, or original-resources"
            module_logger.critical(msg)
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

    module_logger.info("Writing new file to {}".format(args.output_filename))


def raintale_story(args):

    import json
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Starting generation of files from input")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

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
            module_logger.critical("Cannot continue, either supply a title with --title or a collection metadata file containing a title with --collection_metadata")
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
                    module_logger.exception("row caused type error, skipping: {}".format(row))

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

    module_logger.info("Writing Raintale JSON out to {}".format(
        args.output_filename
    ))

    with open(args.output_filename, 'w') as f:
        json.dump(story_json, f, indent=4)

    module_logger.info("Done generating Raintale JSON output at {}".format(args.output_filename))


def synthesize_warcs(args):

    from hypercane.actions import get_logger, calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    import os
    import traceback

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Starting generation of files from input")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

    if not os.path.exists(args.output_directory):
        module_logger.info("Output directory {} does not exist, creating...".format(args.output_directory))
        os.makedirs(args.output_directory)

    from hypercane.synthesize.warcs import synthesize_warc

    # TODO: make this multithreaded
    for urim in urimdata.keys():
        try:
            synthesize_warc(urim, session, args.output_directory, collect_embedded_resources=(not args.no_download_embedded))
        except Exception:
            module_logger.exception("failed to generate WARC for URI-M {}".format(urim))
            hypercane.errors.errorstore.add(urim, traceback.format_exc())

    module_logger.info("Done generating directory of files, output is at {}".format(args.output_directory))

def synthesize_files(args):

    import os
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hashlib import md5
    import traceback

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Starting generation of files from input")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

    if not os.path.exists(args.output_directory):
        module_logger.info("Output directory {} does not exist, creating...".format(args.output_directory))
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

                module_logger.info("writing out data for URI-M {}".format(urim))
                with open("{}/{}".format(
                    args.output_directory, newfilename), 'wb') as newfile:
                    newfile.write(data)

                metadatafile.write("{}\t{}\n".format(urim, newfilename))

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, repr(exc)))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    module_logger.info("Done generating directory of files, output is at {}".format(args.output_directory))

def synthesize_bpfree_files(args):

    import os
    from hypercane.utils import get_web_session, get_boilerplate_free_content
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hashlib import md5
    import traceback

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Starting generation of boilerplate-free files from input")

    urimdata = discover_resource_data_by_input_type(
        args.input_type, output_type, args.input_arguments, args.crawl_depth,
        session, discover_mementos_by_input_type
    )

    module_logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

    if not os.path.exists(args.output_directory):
        module_logger.info("Output directory {} does not exist, creating...".format(args.output_directory))
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

                module_logger.info("writing out data for URI-M {}".format(urim))
                with open("{}/{}".format(
                    args.output_directory, newfilename), 'wb') as newfile:
                    newfile.write(bpfree)

                metadatafile.write("{}\t{}\n".format(urim, newfilename))

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, repr(exc)))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    module_logger.info("Done generating directory of boilerplate-free files, output is at {}".format(args.output_directory))

def remove_clusters(args):

    from hypercane.utils import get_web_session, save_resource_data
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type

    output_type = 'mementos'

    session = get_web_session(cache_storage=args.cache_storage)

    module_logger.info("Starting removal of cluster data from input")

    if args.input_type == 'mementos':

        urimdata = discover_resource_data_by_input_type(
            args.input_type, output_type, args.input_arguments, args.crawl_depth,
            session, discover_mementos_by_input_type
        )
    else:
        NotImplementedError("Removing clusters only works for lists of URI-Ms")

    module_logger.info("discovered {} URI-Ms from the input".format(len(urimdata)))

    urimdata_output = {}

    for urim in urimdata:

        urimdata_output.setdefault(urim, {})

        for key in urimdata[urim]:

            if key != 'Cluster':
                urimdata_output[urim][key] = urimdata[urim][key]

    module_logger.info("removed cluster data, there will be {} URI-Ms in the output".format(len(urimdata)))

    save_resource_data(args.output_filename, urimdata_output, 'mementos', list(urimdata.keys()))

    module_logger.info("Removal of cluster information is complete,"
        "output is available in {}".format(args.output_filename))
