import os
import time
import logging
import csv
import traceback

from datetime import datetime
from urllib.parse import urlparse, urljoin, quote
from pymongo import MongoClient
import pymongo
import pymongo.errors
from requests import Session
from requests_cache import CachedSession
from requests_cache.backends import MongoCache
from guess_language import guess_language
from justext import justext, get_stoplist
from simhash import Simhash
from newspaper import Article
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from mementoembed.mementoresource import memento_resource_factory, \
    get_original_uri_from_response, NotAMementoError, \
    MementoMetaRedirectParsingError

from .version import __useragent__
import hypercane.errors
import re

module_logger = logging.getLogger("hypercane.utils")

def get_web_session(cache_storage=None):

    proxies = None

    http_proxy = os.getenv('HTTP_PROXY')
    https_proxy = os.getenv('HTTPS_PROXY')

    if http_proxy is not None and https_proxy is not None:
        proxies = {
            'http': http_proxy,
            'https': https_proxy
        }

    if cache_storage is not None:

        o = urlparse(cache_storage)
        if o.scheme == "mongodb":
            # these requests-cache internals gymnastics are necessary
            # because it will not create a database with the desired name otherwise
            dbname = o.path.replace('/', '')
            dbconn = MongoClient(cache_storage)
            session = CachedSession(backend='mongodb')
            session.cache = MongoCache(connection=dbconn, db_name=dbname)
            session.cache_storage = cache_storage
        else:
            session = CachedSession(cache_name=cache_storage, extension='')
    else:
        session = Session()

    retry = Retry(
        total=10,
        read=10,
        connect=10,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    session.proxies = proxies
    session.headers.update({'User-Agent': __useragent__})

    return session

def get_memento_http_metadata(urim, cache_storage, metadata_fields=[]):

    dbconn = MongoClient(cache_storage)
    session = get_web_session(cache_storage)
    db = dbconn.get_default_database()

    module_logger.debug("using database host [{}], port [{}], name[{}]".format(dbconn.HOST, dbconn.PORT, dbconn.get_default_database().name))

    output_values = []

    # if memento metadata in cache, return it
    try:

        for field in metadata_fields:

            if field == 'memento-datetime':

                try:
                    mdt = db.derivedvalues.find_one(
                        { "urim": urim }
                    )['memento-datetime']
                except pymongo.errors.AutoReconnect:
                    # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
                    module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
                    time.sleep(2)
                    mdt = db.derivedvalues.find_one(
                        { "urim": urim }
                    )['memento-datetime']

                try:
                    mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")
                except ValueError:
                    # sometimes, when returned from MongoDB, the memento-datetime comes back in a different format
                    mdt = datetime.strptime(mdt, "%Y-%m-%d %H:%M:%S")

                module_logger.debug("returning cached memento-datetime of type {} with value [{}]".format(type(mdt), mdt))

                output_values.append( mdt )

            else:

                try:
                    value = db.derivedvalues.find_one(
                            { "urim": urim }
                    )[field]
                except pymongo.errors.AutoReconnect:
                    # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
                    module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
                    time.sleep(2)
                    value = db.derivedvalues.find_one(
                            { "urim": urim }
                    )[field]

                module_logger.debug("returning cached data for field {} with value [{}]".format(field, value))

                output_values.append(value)

        return output_values

    except (KeyError, TypeError):

        r = session.get(urim)
        r.raise_for_status

        memento_compliant_archive = True

        try:
            mr = memento_resource_factory(urim, session)
        except NotAMementoError:
            # TODO: this is dangerous, how do we protect the system from users who submit URI-Rs by accident?
            module_logger.warning("URI-M {} does not appear to come from a Memento-Compliant archive, resorting to heuristics which may be inaccurate...".format(urim))
            memento_compliant_archive = False
        # TODO: MementoMetaRedirectParsingError is not handled here and it fires before NotAMementoError

        for field in metadata_fields:

            if field == 'memento-datetime':

                # mdt = r.headers['memento-datetime']
                if memento_compliant_archive == True:
                    mdt = mr.memento_datetime
                else:
                    mdt = r.url[r.url.find('/http') - 14 : r.url.find('/http')]
                    mdt = datetime.strptime(mdt, "%Y%m%d%H%M%S")
                    module_logger.warning("Non-Compliant Memento: guessing memento-datetime of {} from URI-M {}".format(mdt, urim))

                try:
                    mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")
                except ValueError:
                    # sometimes, when returned from MongoDB, the memento-datetime comes back in a different format
                    mdt = datetime.strptime(mdt, "%Y-%m-%d %H:%M:%S")
                except TypeError:
                    # since the Trove work, mdt is now a datetime object
                    pass

                module_logger.info("returning memento-datetime of type {} with value [{}]".format(type(mdt), mdt))

                output_values.append( mdt )
                
                try:
                    db.derivedvalues.update(
                        { "urim": urim },
                        { "$set": { "memento-datetime": str(mdt) }},
                        upsert=True
                    )
                except pymongo.errors.AutoReconnect:
                    # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
                    module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
                    time.sleep(2)
                    db.derivedvalues.update(
                        { "urim": urim },
                        { "$set": { "memento-datetime": str(mdt) }},
                        upsert=True
                    )

            elif field == 'original':

                if memento_compliant_archive == True:
                    # urir = get_original_uri_from_response(r)
                    urir = mr.original_uri
                else:
                    urir = r.url[r.url.find('/http') + 1:]
                    module_logger.warning("Non-Compliant Memento: guessing original-resource of {} from URI-M {}".format(urir, urim))
                
                output_values.append( urir )
                try:
                    db.derivedvalues.update(
                        { "urim": urim },
                        { "$set": { "original": urir }},
                        upsert=True
                    )
                except pymongo.errors.AutoReconnect:
                    # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
                    module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
                    time.sleep(2)
                    db.derivedvalues.update(
                        { "urim": urim },
                        { "$set": { "original": urir }},
                        upsert=True
                    )

            elif field == 'timegate':

                if memento_compliant_archive == True:
                    urig = mr.timegate
                else:
                    urig = None
                    module_logger.error("Non-Compliant Memento: cannot guess TimeGate for URI-M {}".format(urim))

                output_values.append( urig )

                try:
                    db.derivedvalues.update(
                        { "urim": urim },
                        { "$set": { "timegate": urig }},
                        upsert=True
                    )
                except pymongo.errors.AutoReconnect:
                    # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
                    module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
                    time.sleep(2)
                    db.derivedvalues.update(
                        { "urim": urim },
                        { "$set": { "timegate": urig }},
                        upsert=True
                    )

            else:

                if memento_compliant_archive == True:
                    r = mr.response
                else:
                    module_logger.warning("Non-Compliant Memento: attempting to derive field {} from headers for URI-M {}".format(field, urim))
                    # reuse r from above

                uri = r.links[field]["url"]
                module_logger.debug("extracted uri {} for field {}".format(uri, field))
                output_values.append( uri )

                try:
                    db.derivedvalues.update(
                        { "urim": urim },
                        { "$set": { field: uri }},
                        upsert=True
                    )
                except pymongo.errors.AutoReconnect:
                    # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
                    module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
                    time.sleep(2)
                    db.derivedvalues.update(
                        { "urim": urim },
                        { "$set": { field: uri }},
                        upsert=True
                    )


        return output_values

def get_language(urim, cache_storage):

    dbconn = MongoClient(cache_storage)
    # session = get_web_session(cache_storage)
    db = dbconn.get_default_database()

    # 1 if lang of urim in cache, return it
    try:
        try:
            return db.derivedvalues.find_one(
                { "urim": urim }
            )["language"]
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            return db.derivedvalues.find_one(
                { "urim": urim }
            )["language"]

    except (KeyError, TypeError):

        content = get_boilerplate_free_content(
            urim, cache_storage=cache_storage, dbconn=dbconn
        ).decode('utf8')

        language = guess_language(content)

        try:
            db.derivedvalues.update(
                { "urim": urim },
                { "$set": { "language": language }},
                upsert=True
            )
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            db.derivedvalues.update(
                { "urim": urim },
                { "$set": { "language": language }},
                upsert=True
            )

        return language

def get_raw_simhash(urim, cache_storage):

    import otmt

    dbconn = MongoClient(cache_storage)
    session = get_web_session(cache_storage)
    db = dbconn.get_default_database()

    # 1 if lang of urim in cache, return it
    try:
        try:
            return db.derivedvalues.find_one(
                { "urim": urim }
            )["raw simhash"]
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            return db.derivedvalues.find_one(
                { "urim": urim }
            )["raw simhash"]

    except (KeyError, TypeError):

        r = session.get(urim)

        if len(r.history) == 0:
            raw_urim = generate_raw_urim(urim)
        else:
            raw_urim = generate_raw_urim(r.url)

        r2 = session.get(raw_urim)
        r2.raise_for_status()

        if 'text/html' not in r2.headers['content-type']:
            raise Exception("Hypercane currently only operates with HTML resources, refusing to compute Simhash on {}".format(urim))

        simhash = Simhash(r2.text).value

        try:
            db.derivedvalues.update(
                { "urim": urim },
                { "$set": { "raw simhash": str(simhash) }},
                upsert=True
            )
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            db.derivedvalues.update(
                { "urim": urim },
                { "$set": { "raw simhash": str(simhash) }},
                upsert=True
            )

        return str(simhash)

def get_tf_simhash(urim, cache_storage):

    dbconn = MongoClient(cache_storage)
    # session = get_web_session(cache_storage)
    db = dbconn.get_default_database()

    # 1 if lang of urim in cache, return it
    try:
        try:
            return db.derivedvalues.find_one(
                { "urim": urim }
            )["tf simhash"]
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            return db.derivedvalues.find_one(
                { "urim": urim }
            )["tf simhash"]

    except (KeyError, TypeError):

        content = get_boilerplate_free_content(
            urim, cache_storage=cache_storage, dbconn=dbconn
        ).decode('utf8')

        # break text into words
        words = content.split()
        # sort words
        words.sort()
        # submit to Simhash library
        simhash = Simhash(" ".join(words)).value

        try:
            db.derivedvalues.update(
                { "urim": urim },
                { "$set": { "tf simhash": str(simhash) }},
                upsert=True
            )
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            db.derivedvalues.update(
                { "urim": urim },
                { "$set": { "tf simhash": str(simhash) }},
                upsert=True
            )

        return str(simhash)

def get_html_free_content_from_solrwayback(urim, urir, crawl_date):

    import requests
    import io
    import csv

    session = requests.Session()

    bpfree_content = ""

    query_url = urljoin(
        urim,
        "/solrwayback/services/export/csv?query=url:%22{}%22%20AND%20crawl_date:%22{}%22&fields=content".format(
            quote(urir), crawl_date
        )
    )

    module_logger.warning("visiting URL {} at SolrWayback".format(query_url))
    r = session.get(query_url)
    
    csvfileobj = io.StringIO(r.text) # because we need a file-like object
    reader = csv.DictReader(csvfileobj) # because we need a CSV parser
    numrecords = len(list(reader)) # because we want to count the # of records
    csvfileobj.seek(0) # because counting the number of records iterates to the end of the file object
    reader = csv.DictReader(csvfileobj) # so we can read the CSV file for real this time 

    module_logger.warning("discovered {} records in the response from SolrWayback...".format(numrecords))

    if numrecords != 1:
        module_logger.warning("There are {} records in the response from SolrWayback, we expected 1, we will try to take the first one available".format(numrecords))

    module_logger.warning("searching for memento at SolrWayback coordinates {} and {}".format(
        urir, crawl_date
    ))

    for row in reader:
        # print("examining row {}".format(row))
        bpfree_content = bytes(row['content'], encoding='utf8')
        break

    return bpfree_content

# def generate_raw_memento_from_solrwayback_urim(urim):

#     raw_urim = urljoin(
#         urim,

#     )

def generate_raw_urim(urim):

    import otmt

    o = urlparse(urim)

    # note: I have found no way to identify SolrWayback through headers, it does not identify itself
    if o.path[0:13] == '/solrwayback/':
        module_logger.warning("SolrWayback is not Memento-compliant and support is very experimental. We do not recommend using Hypercane with SolrWayback until they implement the Memento Protocol.")
        # examples:
        # aug memento: http://localhost:8080/solrwayback/services/viewForward?source_file_path=/Volumes/nerfherder-extern-3/archive-it-collections/download-from-do-server/694-warcs/06621867d0bf3074679c0a773c1efd07-20210508002237.warc.gz&offset=0
        # raw memento: http://localhost:8080/solrwayback/services/downloadRaw?source_file_path=/Volumes/nerfherder-extern-3/archive-it-collections/download-from-do-server/694-warcs/532bc3af7e0114db49b20383be1704dc-20210508005926.warc.gz&offset=0

        if '/solrwayback/services/viewForward' in o.path:
            raw_urim = urim.replace(
                '/solrwayback/services/viewForward?source_file_path=',
                '/solrwayback/services/downloadRaw?source_file_path=')
        else:
            # other: http://localhost:8080/solrwayback/services/web/20080418011213/http://planetblacksburg.com/
            # not sure how to get from here to downloadRaw
            raw_urim = otmt.generate_raw_urim(urim) # this is just a noop

    # TODO: we need a better way to handle all of the different raw URI-Ms across all DSA tools
    elif 'webarchive.nla.gov.au' in urim:

        from mementoembed.mementoresource import wayback_pattern

        raw_urim = urim.replace("webarchive.nla.gov.au", "web.archive.org.au")
        raw_urim = wayback_pattern.sub(r'\1id_/', raw_urim)

    else:
        # OTMT handles all standard Wayback id_ tricks
        raw_urim = otmt.generate_raw_urim(urim)

    return raw_urim

def get_boilerplate_free_content(urim, cache_storage="", dbconn=None, session=None):

    import otmt
    from boilerpy3 import extractors

    if dbconn is None:
        dbconn = MongoClient(cache_storage)

    if session is None:
        session = get_web_session(cache_storage)

    db = dbconn.get_default_database()

    # 1. if boilerplate free content in cache, return it
    try:
        module_logger.debug("returning boilerplate free content from cache for {}".format(urim))
        try:
            bpfree = db.derivedvalues.find_one(
                { "urim": urim }
            )["boilerplate free content"]
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            bpfree = db.derivedvalues.find_one(
                { "urim": urim }
            )["boilerplate free content"]

        return bytes(bpfree, "utf8")
    except (KeyError, TypeError):

        module_logger.info("generating boilerplate free content for {}".format(urim))

        r = session.get(urim)

        module_logger.debug("attempting to extract boilerplate free content from {}".format(urim))

        extractor = extractors.ArticleExtractor()

        try:
            
            if 'memento-datetime' not in r.headers:
                # short-circuit here because memento_resource_factory may throw an unnecessary exception
                module_logger.warning("URI-M {} does not appear to come from a Memento-Compliant archive, resorting to heuristics which may be inaccurate...".format(urim))
                raw_urim = generate_raw_urim(urim)
                module_logger.warning("attempting to remove boilerplate from raw URI-M {}...".format(raw_urim))
                raw_response = session.get(raw_urim)
                bpfree = extractor.get_content(raw_response.text)
            else:

                try:
                    mr = memento_resource_factory(urim, session)
                    bpfree = extractor.get_content(mr.raw_content)
                except NotAMementoError:
                    # TODO: this is dangerous, how do we protect the system from users who submit URI-Rs by accident?
                    module_logger.warning("URI-M {} does not appear to come from a Memento-Compliant archive, resorting to heuristics which may be inaccurate...".format(urim))
                    raw_urim = generate_raw_urim(urim)
                    module_logger.warning("attempting to remove boilerplate from raw URI-M {}...".format(raw_urim))
                    raw_response = session.get(raw_urim)
                    bpfree = extractor.get_content(raw_response.text)

            module_logger.info("storing boilerplate free content in cache {}".format(urim))

            try:
                db.derivedvalues.update(
                    { "urim": urim },
                    { "$set": { "boilerplate free content": bpfree } },
                    upsert=True
                )
            except pymongo.errors.AutoReconnect:
                # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
                module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
                time.sleep(2)
                db.derivedvalues.update(
                    { "urim": urim },
                    { "$set": { "boilerplate free content": bpfree } },
                    upsert=True
                )

        except Exception:
            module_logger.exception("failed to extract boilerplate from {}, setting value to empty string".format(urim))
            hypercane.errors.errorstore.add(urim, traceback.format_exc())
            return bytes()

        return bytes(bpfree, "utf8")

def match_pattern(urim, cache_storage, compiled_pattern):

    bpfree = get_boilerplate_free_content(urim, cache_storage=cache_storage)

    return compiled_pattern.match(bpfree)

def get_newspaper_publication_date(urim, cache_storage):

    import otmt

    dbconn = MongoClient(cache_storage)
    session = get_web_session(cache_storage)
    db = dbconn.get_default_database()

    try:
        try:
            return db.derivedvalues.find_one(
                { "urim": urim }
            )["newspaper publication date"]
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            return db.derivedvalues.find_one(
                { "urim": urim }
            )["newspaper publication date"]
        
    except (KeyError, TypeError):
        raw_urim = generate_raw_urim(urim)

        r = session.get(raw_urim)
        r.raise_for_status()

        article = Article(urim)
        article.download(r.text)
        article.parse()
        article.nlp()
        pd = article.publish_date

        if pd is None:
            # pd = r.headers['memento-datetime']
            pd = get_memento_http_metadata(urim, cache_storage, metadata_fields=['memento-datetime'])[0]
        else:
            pd = pd.strftime("%a, %d %b %Y %H:%M:%S GMT")

        try:
            db.derivedvalues.update(
                { "urim": urim },
                { "$set": { "newspaper publication date": str(pd) } },
                upsert=True
            )
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            db.derivedvalues.update(
                { "urim": urim },
                { "$set": { "newspaper publication date": str(pd) } },
                upsert=True
            )

        return pd

def process_input_for_cluster_and_rank(filename, input_type_field):

    urim_data = {}

    module_logger.info("processing file {} for input type {}".format(filename, input_type_field))

    with open(filename) as f:
        csvreader = csv.DictReader(f, delimiter='\t')

        module_logger.debug("input type field [{}] == first field name [{}]".format(
            input_type_field, csvreader.fieldnames[0]
        ))

        if input_type_field == csvreader.fieldnames[0]:
            # make sure the headers are valid

            module_logger.debug("iterating through file {}".format(filename))

            for row in csvreader:

                module_logger.debug("reading row {}".format(row))

                module_logger.debug("row.keys: {}".format(row.keys()))

                rowdata = {}
                urim = row[input_type_field].strip()

                module_logger.debug("rowdata: {}".format(rowdata))

                for key in row.keys():
                    module_logger.debug("examining field {} in input".format(key))
                    if key != input_type_field:
                        rowdata[key] = row[key]

                module_logger.debug("rowdata now: {}".format(rowdata))

                urim_data[urim] = rowdata

    module_logger.info("read in {} URIs from file {} for input type {}".format(len(urim_data), filename, input_type_field))

    if len(urim_data) == 0:
        # assume we are just dealing with a list of URI-Ms

        with open(filename) as f:

            csvreader = csv.reader(f)

            for row in csvreader:

                rowdata = {}

                try:
                    urim = row[0]

                    # in case we have a TSV file of just headers
                    if urim == input_type_field:
                        break

                    urim_data[urim] = rowdata

                except IndexError:
                    #we've reached the end, but there was an extra newline
                    pass

    # module_logger.info("urimdata from file: {}".format(urim_data))

    return urim_data

def save_resource_data(output_filename, resource_data, output_type, urilist):

    output_type_keys = {
        'mementos': 'URI-M',
        'timemaps': 'URI-T',
        'original-resources': 'URI-R'
    }

    type_key = output_type_keys[output_type]

    module_logger.info("attempting to write {} URIs with resource data to {}".format(
        len(urilist), output_filename
    ))

    with open(output_filename, 'w') as output:

        fieldnames = [ type_key ]

        for uri in resource_data:
            if len(list(resource_data[uri].keys())) > 0:
                fieldnames.extend(list(resource_data[uri].keys()))
            # just do it once
            break

        module_logger.info("fieldnames will be {}".format(fieldnames))

        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter='\t')

        writer.writeheader()

        for uri in urilist:

            # if uri in urilist:

            row = {}
            row[ type_key ] = uri

            for key in resource_data[uri].keys():
                module_logger.debug("working with key {} for uri {}".format(key, uri))
                if key != type_key:
                    if key in resource_data[uri]:
                        row[key] = resource_data[uri][key]
                    else:
                        # in case we are writing out data that was not filled
                        row[key] = None

            writer.writerow(row)

def create_html_metadata_kv_pairs(urim, session):

    from bs4 import BeautifulSoup

    r = session.get(urim)

    soup = BeautifulSoup(r.text, 'html5lib')

    meta_tags = soup.find_all('meta')

    meta_kv_pairs = {}

    for meta in meta_tags:

        value_attrib = None
        key_attrib = None

        for ivalueattrib in ['content', 'value', 'href']:
            module_logger.debug("VALUE: looking for {} in {}".format(ivalueattrib, meta))

            if ivalueattrib in meta.attrs:
                value_attrib = ivalueattrib
                break

        module_logger.debug("value_attrib is now {}".format(value_attrib))

        for ikeyattrib in ['property', 'name']:
            module_logger.debug("KEY: looking for {} in {}".format(ikeyattrib, meta))

            if ikeyattrib in meta.attrs:
                key_attrib = ikeyattrib
                break

        module_logger.debug("key_attrib is now {}".format(key_attrib))

        if value_attrib is None:
            module_logger.debug("value is none, skipping...")
            continue

        if key_attrib is None:
            module_logger.debug("key is none, skipping...")
            continue

        meta_kv_pairs[ meta[key_attrib] ] = meta[value_attrib]

    return meta_kv_pairs

def organize_mementos_by_cluster(urimdata):

    memento_clusters = {}

    for urim in urimdata:

        memento_clusters.setdefault( urimdata[urim]['Cluster'], []).append(urim)

    return memento_clusters

def get_faux_TimeMap_json(faux_urit, urims, cache_storage):

    dbconn = MongoClient(cache_storage)
    db = dbconn.get_default_database()

    module_logger.debug("searching for faux TimeMap at {}".format(faux_urit))

    try:
        try:          
            timemap_json = db.derivedvalues.find_one(
                { "fauxurit": faux_urit }
            )["timemap_json"]
            module_logger.debug("successfully extracted cached faux TimeMap for {}".format(faux_urit))
            return timemap_json
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)

            timemap_json = db.derivedvalues.find_one(
                { "fauxurit": faux_urit }
            )["timemap_json"]
            module_logger.debug("after hiccup, successfully extracted cached faux TimeMap for {}".format(faux_urit))
            return timemap_json

    except (KeyError, TypeError):

        from hypercane.identify import generate_faux_urit

        faux_urit_urim_list = {}

        module_logger.info("creating faux TimeMaps for {} URI-Ms".format(len(urims)))

        for urim in urims:

            module_logger.debug("generating faux TimeMap for {}".format(urim))
            faux_urit_i = generate_faux_urit(urim, cache_storage)
            faux_urit_urim_list.setdefault( faux_urit_i, [] ).append(urim)

        for faux_urit_i in faux_urit_urim_list:

            # urir = faux_urit_i.replace('fauxtm://', '')
            test_urim = faux_urit_urim_list[faux_urit_i][0]
            urir = get_memento_http_metadata(test_urim, cache_storage, metadata_fields=['original'])[0]

            module_logger.info("adding URI-R {} to TimeMap".format(urir))

            timemap_json = {
                'original_uri': urir,
                'timegate_uri': None,
                'timemap_uri': {
                    "json_format": faux_urit_i
                },
                'mementos': {
                    'first': {},
                    'last': {},
                    'list': {}
                }
            }

            mementos_list = []
            mementos_by_datetime = []

            for urim in faux_urit_urim_list[faux_urit_i]:

                mdt = get_memento_http_metadata(urim, cache_storage, metadata_fields=['memento-datetime'])[0]

                memento_entry = {
                    "datetime": mdt.strftime("%Y-%m-%dT%H%M%SZ"),
                    "uri": urim
                }

                mementos_list.append(memento_entry)
                mementos_by_datetime.append( ( mdt, urim ) )

            timemap_json['mementos']['list'] = mementos_list

            mementos_by_datetime.sort()

            timemap_json['mementos']['first']['datetime'] = mementos_by_datetime[0][0].strftime("%Y-%m-%dT%H%M%SZ")
            timemap_json['mementos']['first']['uri'] = mementos_by_datetime[0][1]

            timemap_json['mementos']['last']['datetime'] = mementos_by_datetime[-1][0].strftime("%Y-%m-%dT%H%M%SZ")
            timemap_json['mementos']['last']['uri'] = mementos_by_datetime[-1][1]

            module_logger.info("writing {} to the database".format(faux_urit_i))

            try:
                db.derivedvalues.update(
                    { "fauxurit": faux_urit_i },
                    { "$set": { "timemap_json" : timemap_json } },
                    upsert=True
                )
            except pymongo.errors.AutoReconnect:
                # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
                module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
                time.sleep(2)
                db.derivedvalues.update(
                    { "fauxurit": faux_urit_i },
                    { "$set": { "timemap_json" : timemap_json } },
                    upsert=True
                )

        try:
            return db.derivedvalues.find_one(
                { "fauxurit": faux_urit }
            )["timemap_json"]
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            return db.derivedvalues.find_one(
                { "fauxurit": faux_urit }
            )["timemap_json"]
        except TypeError as e:
            module_logger.exception("Cannot find TimeMap for {}".format(faux_urit))
            raise e

def generate_all_faux_TimeMaps(urims, cache_storage):

    from hypercane.identify import generate_faux_urit

    dbconn = MongoClient(cache_storage)
    db = dbconn.get_default_database()

    faux_urit_urim_list = {}

    module_logger.info("creating faux TimeMaps for {} URI-Ms".format(len(urims)))

    for urim in urims:

        module_logger.debug("generating faux TimeMap for {}".format(urim))
        faux_urit_i = generate_faux_urit(urim, cache_storage)
        faux_urit_urim_list.setdefault( faux_urit_i, [] ).append(urim)

    for faux_urit_i in faux_urit_urim_list:

        # urir = faux_urit_i.replace('fauxtm://', '')
        test_urim = faux_urit_urim_list[faux_urit_i][0]
        urir = get_memento_http_metadata(test_urim, cache_storage, metadata_fields=['original'])[0]

        module_logger.info("adding URI-R {} to TimeMap".format(urir))

        timemap_json = {
            'original_uri': urir,
            'timegate_uri': None,
            'timemap_uri': {
                "json_format": faux_urit_i
            },
            'mementos': {
                'first': {},
                'last': {},
                'list': {}
            }
        }

        mementos_list = []
        mementos_by_datetime = []

        for urim in faux_urit_urim_list[faux_urit_i]:

            mdt = get_memento_http_metadata(urim, cache_storage, metadata_fields=['memento-datetime'])[0]

            memento_entry = {
                "datetime": mdt.strftime("%Y-%m-%dT%H%M%SZ"),
                "uri": urim
            }

            mementos_list.append(memento_entry)
            mementos_by_datetime.append( ( mdt, urim ) )

        timemap_json['mementos']['list'] = mementos_list

        mementos_by_datetime.sort()

        timemap_json['mementos']['first']['datetime'] = mementos_by_datetime[0][0].strftime("%Y-%m-%dT%H%M%SZ")
        timemap_json['mementos']['first']['uri'] = mementos_by_datetime[0][1]

        timemap_json['mementos']['last']['datetime'] = mementos_by_datetime[-1][0].strftime("%Y-%m-%dT%H%M%SZ")
        timemap_json['mementos']['last']['uri'] = mementos_by_datetime[-1][1]

        module_logger.info("writing {} to the database".format(faux_urit_i))

        try:
            db.derivedvalues.update(
                { "fauxurit": faux_urit_i },
                { "$set": { "timemap_json" : timemap_json } },
                upsert=True
            )
        except pymongo.errors.AutoReconnect:
            # TODO: apply a proxy, decorator, or some other method to wrap MongoDB calls
            module_logger.warning("MongoDB lost the connection, sleeping for 2 seconds and retrying action")
            time.sleep(2)
            db.derivedvalues.update(
                { "fauxurit": faux_urit_i },
                { "$set": { "timemap_json" : timemap_json } },
                upsert=True
            )

        return faux_urit_urim_list
