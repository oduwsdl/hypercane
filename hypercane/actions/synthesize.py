import sys

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

    return args

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

    # TODO: make this multithreaded
    for urim in urimdata.keys():
        raw_urim = otmt.generate_raw_urim(urim)
        resp = session.get(urim, stream=True)

        headers_list = resp.raw.headers.items()

        raw_resp = session.get(raw_urim, stream=True)

        for link in resp.links:
            if 'original' in link:
                warc_target_uri = resp.links[link]['url']

        http_headers = StatusAndHeaders('200 OK', 
            headers_list, protocol='HTTP/1.0')

        m = md5()
        m.update(urim.encode('utf8'))
        urlhash = m.hexdigest()

        warc_headers_dict = {}
        warc_headers_dict['WARC-Date'] = datetime.strptime(
            resp.headers['Memento-Datetime'],
            "%a, %d %b %Y %H:%M:%S GMT"
        ).strftime('%Y-%d-%mT%H:%M:%SZ')

        with open("{}/{}.warc.gz".format(args.output_directory, urlhash), 'wb') as output:
            writer = WARCWriter(output, gzip=True)

            record = writer.create_warc_record(
                warc_target_uri, 'response', 
                payload=raw_resp.raw, 
                http_headers=http_headers,
                warc_headers_dict=warc_headers_dict
                )

            writer.write_record(record)

    logger.info("Done generating directory of files, output is at {}".format(args.output_directory))

def synthesize_files(args):

    import os
    import argparse
    from hypercane.actions import get_logger, calculate_loglevel
    from hypercane.utils import get_web_session
    from hypercane.identify import discover_resource_data_by_input_type, \
        discover_mementos_by_input_type
    from hashlib import md5

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

    # TODO: make this multithreaded
    with open("{}/metadata.tsv".format(args.output_directory), 'w') as metadatafile:

        for urim in urimdata.keys():
            r = session.get(urim)
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

            raw_urim = otmt.generate_raw_urim(urim)
            r = session.get(raw_urim)

            paragraphs = justext(
                r.text, get_stoplist('English')
            )

            bpfree = ""

            for paragraph in paragraphs:
                bpfree += "{}\n".format(paragraph.text)

            m = md5()
            m.update(urim.encode('utf8'))
            urlhash = m.hexdigest()
            newfilename = urlhash + '.dat'

            logger.info("writing out data for URI-M {}".format(urim))
            with open("{}/{}".format(
                args.output_directory, newfilename), 'wb') as newfile:
                newfile.write(bytes(bpfree, "utf8"))

            metadatafile.write("{}\t{}\n".format(urim, newfilename))

    logger.info("Done generating directory of boilerplate-free files, output is at {}".format(args.output_directory))

def print_usage():

    print("""'hc synthesize' is used to synthesize a web archive collection into other formats, like WARC, WAT, or a set of files in a directory

    Supported commands:
    * warcs - for generating a directory of WARCs
    * files - for generating a directory of files

""")

supported_commands = {
    "warcs": synthesize_warcs,
    "files": synthesize_files,
    "bpfree-files": synthesize_bpfree_files
}
