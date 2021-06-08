import logging
import hypercane.errors

module_logger = logging.getLogger('hypercane.synthesize.warcs')

def extract_image_uris(html):

    from bs4 import BeautifulSoup

    imageurls = []
    soup = BeautifulSoup(html, 'html5lib')

    for img in soup.find_all('img'):
        if 'src' in img.attrs:
            if img['src'] != '':
                imageurls.append(img['src'])


    # images from metadata
    for field in ['og:image', 'twitter:image', 'twitter:image:src', 'og:image:url', 'image']:

        for attribute in ['property', 'name', 'itemprop']:

            discovered_fields = soup.find_all('meta', { attribute: field } )

            if len(discovered_fields) > 0:

                for value_attribute in ['content', 'value']:

                    if value_attribute in discovered_fields[0]:

                        imageurls.append(
                            discovered_fields[0][value_attribute]
                        )

    return imageurls

def extract_javascript_uris(html):

    from bs4 import BeautifulSoup

    javascripturls = []
    soup = BeautifulSoup(html, 'html5lib')

    for script in soup.find_all('script'):
        if 'src' in script.attrs:
            if script['src'] != '':
                javascripturls.append(script['src'])

    return javascripturls

def extract_stylesheet_uris(html):

    from bs4 import BeautifulSoup

    cssurls = []
    soup = BeautifulSoup(html, 'html5lib')

    for link in soup.find_all('link'):
        if 'href' in link.attrs:
            if link['href'] != '':
                cssurls.append(link['href'])

    return cssurls

def generate_warc_record_for_urim(warcwriter, urim, session, get_raw=True):

    from warcio.statusandheaders import StatusAndHeaders
    from datetime import datetime
    from ..utils import generate_raw_urim

    warc_target_uri = None

    resp = session.get(urim, stream=True)
    resp.raise_for_status()
    headers_list = resp.raw.headers.items()

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

    # we use response.url instead of urim to (hopefully) avoid raw redirects

    if get_raw == True:
        raw_urim = generate_raw_urim(resp.url)
        raw_response = session.get(raw_urim, stream=True)
    else:
        raw_urim = urim
        raw_response = resp

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

    record = warcwriter.create_warc_record(
        warc_target_uri, 'response',
        payload=raw_response.raw,
        http_headers=http_headers,
        warc_headers_dict=warc_headers_dict
    )

    return record

def synthesize_warc(base_urim, session, output_directory, collect_embedded_resources=True):

    import glob
    from hashlib import md5
    from datetime import datetime
    from warcio.warcwriter import WARCWriter
    from requests.exceptions import HTTPError
    from urllib.parse import urljoin
    
    m = md5()
    m.update(base_urim.encode('utf8'))
    urlhash = m.hexdigest()

    if len( glob.glob('{}/{}*.warc.gz'.format(output_directory, urlhash)) ) > 0:
        module_logger.warning("Detected existing WARC for URI-M, skipping {}".format(base_urim))
        return

    resp = session.get(base_urim, stream=True)
    resp.raise_for_status()
    imageurims = []
    javascripturims = []
    cssurims = []

    if collect_embedded_resources == True:

        # generate list of image URI-Ms
        imageurims = extract_image_uris(resp.text)

        # generate list of JavaScript URI-Ms
        javascripturims = extract_javascript_uris(resp.text)

        # generate list of CSS URI-Ms
        cssurims = extract_stylesheet_uris(resp.text)

    with open("{}/{}-{}.warc.gz".format(output_directory, urlhash, datetime.now().strftime('%Y%m%d%H%M%S')), 'wb') as output:
        writer = WARCWriter(output, gzip=True)

        record = generate_warc_record_for_urim(writer, base_urim, session, get_raw=True)
        writer.write_record(record)

        # loop through images
        for urim in imageurims:
            urim = urljoin(base_urim, urim)
            try:
                record = generate_warc_record_for_urim(writer, urim, session, get_raw=False)
                writer.write_record(record)
            except HTTPError:
                module_logger.warning("Could not download {}, skipping...".format(urim))
            except AttributeError:
                module_logger.warning("Issue adding {} to WARC, skipping...".format(urim))


        # loop through JavaScript
        for urim in javascripturims:
            urim = urljoin(base_urim, urim)
            try:
                record = generate_warc_record_for_urim(writer, urim, session, get_raw=False)
                writer.write_record(record)
            except HTTPError:
                module_logger.warning("Could not download {}, skipping...".format(urim))
            except AttributeError:
                module_logger.warning("Issue adding {} to WARC, skipping...".format(urim))

        # loop through CSS
        for urim in cssurims:
            urim = urljoin(base_urim, urim)
            try:
                record = generate_warc_record_for_urim(writer, urim, session, get_raw=False)
                writer.write_record(record)
            except HTTPError:
                module_logger.warning("Could not download {}, skipping...".format(urim))
            except AttributeError:
                module_logger.warning("Issue adding {} to WARC, skipping...".format(urim))



