import logging
import hypercane.errors

module_logger = logging.getLogger('hypercane.synthesize.warcs')

def synthesize_warc(urim, session, output_directory):

    import otmt
    import glob
    from warcio.warcwriter import WARCWriter
    from warcio.statusandheaders import StatusAndHeaders
    from hashlib import md5
    from datetime import datetime
    import traceback

    m = md5()
    m.update(urim.encode('utf8'))
    urlhash = m.hexdigest()

    if len( glob.glob('{}/{}*.warc.gz'.format(output_directory, urlhash)) ) > 0:
        module_logger.warning("Detected existing WARC for URI-M, skipping {}".format(urim))
        return

    resp = session.get(urim, stream=True)
    resp.raise_for_status()

    headers_list = resp.raw.headers.items()

    # we use response.url instead of urim to (hopefully) avoid raw redirects
    raw_urim = otmt.generate_raw_urim(resp.url)

    raw_response = session.get(raw_urim, stream=True)

    warc_target_uri = None

    # we have to implement this construct in case the archive combines original with other relations
    for link in resp.links:

        if 'original' in link:
            warc_target_uri = resp.links[link]['url']

    if warc_target_uri is None:
        module_logger.warning("could not find this memento's original resource, skipping {}".format(urim))
        return

    try:
        mdt = resp.headers['Memento-Datetime']

    except KeyError:
        module_logger.warning("could not find this memento's memento-datetime, skipping {}".format(urim))
        return

    http_headers = StatusAndHeaders('200 OK',
        headers_list, protocol='HTTP/1.0')

    module_logger.debug("mdt formatted by strptime and converted by strftime: {}".format(
        datetime.strptime(
            mdt, "%a, %d %b %Y %H:%M:%S GMT"
        ).strftime('%Y-%m-%dT%H:%M:%SZ')
    ))

    warc_headers_dict = {}
    warc_headers_dict['WARC-Date'] = datetime.strptime(
        mdt, "%a, %d %b %Y %H:%M:%S GMT"
    ).strftime('%Y-%m-%dT%H:%M:%SZ')

    with open("{}/{}-{}.warc.gz".format(output_directory, urlhash, datetime.now().strftime('%Y%m%d%H%M%S')), 'wb') as output:
        writer = WARCWriter(output, gzip=True)

        record = writer.create_warc_record(
            warc_target_uri, 'response',
            payload=raw_response.raw,
            http_headers=http_headers,
            warc_headers_dict=warc_headers_dict
            )

        writer.write_record(record)

