import os
import sys
import logging
import csv
import traceback

from datetime import datetime
from urllib.parse import urlparse
from pymongo import MongoClient
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
    get_original_uri_from_response

from .version import __useragent__
import hypercane.errors

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

    output_values = []

    # if memento metadata in cache, return it
    try:

        for field in metadata_fields:

            if field == 'memento-datetime':

                mdt = db.derivedvalues.find_one(
                    { "urim": urim }
                )['memento-datetime']

                try:
                    mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")
                except ValueError:
                    # sometimes, when returned from MongoDB, the memento-datetime comes back in a different format
                    mdt = datetime.strptime(mdt, "%Y-%m-%d %H:%M:%S")

                module_logger.info("returning cached memento-datetime of type {} with value [{}]".format(type(mdt), mdt))

                output_values.append( mdt )

            else:

                output_values.append(
                    db.derivedvalues.find_one(
                        { "urim": urim }
                    )[field] )

        return output_values

    except (KeyError, TypeError):

        r = session.get(urim)
        r.raise_for_status

        mr = memento_resource_factory(urim, session)

        for field in metadata_fields:

            if field == 'memento-datetime':

                # mdt = r.headers['memento-datetime']
                mdt = mr.memento_datetime

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
                db.derivedvalues.update(
                    { "urim": urim },
                    { "$set": { "memento-datetime": str(mdt) }},
                    upsert=True
                )

            elif field == 'original':

                # urir = get_original_uri_from_response(r)
                urir = mr.original_uri
                output_values.append( urir )
                db.derivedvalues.update(
                    { "urim": urim },
                    { "$set": { "original": urir }},
                    upsert=True
                )

            elif field == 'timegate':

                urig = mr.timegate
                output_values.append( urig )
                db.derivedvalues.update(
                    { "urim": urim },
                    { "$set": { "timegate": urir }},
                    upsert=True
                )

            else:

                r = mr.response
                uri = r.links[field]["url"]
                output_values.append( uri )
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
        return db.derivedvalues.find_one(
            { "urim": urim }
        )["language"]
    except (KeyError, TypeError):

        content = get_boilerplate_free_content(
            urim, cache_storage=cache_storage, dbconn=dbconn
        ).decode('utf8')

        language = guess_language(content)

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
        return db.derivedvalues.find_one(
            { "urim": urim }
        )["raw simhash"]
    except (KeyError, TypeError):

        r = session.get(urim)

        if len(r.history) == 0:
            raw_urim = otmt.generate_raw_urim(urim)
        else:
            raw_urim = otmt.generate_raw_urim(r.url)

        r2 = session.get(raw_urim)
        r2.raise_for_status()

        if 'text/html' not in r2.headers['content-type']:
            raise Exception("Hypercane currently only operates with HTML resources, refusing to compute Simhash on {}".format(urim))

        simhash = Simhash(r2.text).value

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

        db.derivedvalues.update(
            { "urim": urim },
            { "$set": { "tf simhash": str(simhash) }},
            upsert=True
        )

        return str(simhash)

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
        module_logger.info("returing boilerplate free content from cache for {}".format(urim))
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
            mr = memento_resource_factory(urim, session)
            bpfree = extractor.get_content(mr.raw_content)

            module_logger.info("storing boilerplate free content in cache {}".format(urim))

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
        return db.derivedvalues.find_one(
            { "urim": urim }
        )["newspaper publication date"]
    except (KeyError, TypeError):
        raw_urim = otmt.generate_raw_urim(urim)

        r = session.get(raw_urim)
        r.raise_for_status()

        article = Article(urim)
        article.download(r.text)
        article.parse()
        article.nlp()
        pd = article.publish_date

        if pd is None:
            pd = r.headers['memento-datetime']
        else:
            pd = pd.strftime("%a, %d %b %Y %H:%M:%S GMT")

        db.derivedvalues.update(
            { "urim": urim },
            { "$set": { "newspaper publication date": str(pd) } }
        )

        return pd

def process_input_for_cluster_and_rank(filename, input_type_field):

    urim_data = {}

    with open(filename) as f:
        csvreader = csv.DictReader(f, delimiter='\t')

        if input_type_field == csvreader.fieldnames[0]:
            # make sure the headers are valid

            for row in csvreader:

                # module_logger.info("reading row {}".format(row))

                # module_logger.info("row.keys: {}".format(row.keys()))

                rowdata = {}
                urim = row[input_type_field]

                # module_logger.info("rowdata: {}".format(rowdata))

                for key in row.keys():
                    # module_logger.info("examining field {} in input".format(key))
                    if key != input_type_field:
                        rowdata[key] = row[key]

                # module_logger.info("rowdata now: {}".format(rowdata))

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

        for uri in resource_data.keys():

            if uri in urilist:

                row = {}
                row[ type_key ] = uri

                for key in resource_data[uri].keys():
                    module_logger.info("working with key {} for uri {}".format(key, uri))
                    if key != type_key:
                        if key in resource_data[uri]:
                            row[key] = resource_data[uri][key]
                        else:
                            # in case we are writing out data that was not filled
                            row[key] = None

                writer.writerow(row)
