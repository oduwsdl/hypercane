import os
import otmt

from urllib.parse import urlparse
from pymongo import MongoClient
from requests import Session
from requests_cache import CachedSession
from requests_cache.backends import MongoCache
from guess_language import guess_language
from justext import justext, get_stoplist
from simhash import Simhash

from .version import __useragent__

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
        else:
            session = CachedSession(cache_name=cache_storage, extension='')
    else:
        session = Session()

    session.proxies = proxies
    session.headers.update({'User-Agent': __useragent__})

    return session

def get_memento_datetime_and_timemap(urim, cache_storage):

    dbconn = MongoClient(cache_storage)
    session = get_web_session(cache_storage)
    db = dbconn.get_default_database()

    # 1 if lang of urim in cache, return it
    try:
        return (
            db.derivedvalues.find_one(
                { "urim": urim }
                )["memento-datetime"],
            db.derivedvalues.find_one(
                { "urim": urim }
                )["timemap"]
            )
    except (KeyError, TypeError):
        r = session.get(urim)
        mdt = r.headers['memento-datetime']
        urit = r.links["timemap"]["url"]

        db.derivedvalues.update(
            { "urim": urim },
            { "$set": { "memento-datetime": str(mdt), "timemap": str(urit) }},
            upsert=True
        )
    
        return str(mdt), urit

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
        )

        language = guess_language(content)

        db.derivedvalues.update(
            { "urim": urim },
            { "$set": { "language": language }},
            upsert=True
        )
    
        return language

def get_raw_simhash(urim, cache_storage):

    dbconn = MongoClient(cache_storage)
    session = get_web_session(cache_storage)
    db = dbconn.get_default_database()

    # 1 if lang of urim in cache, return it
    try:
        return db.derivedvalues.find_one(
            { "urim": urim }
        )["raw simhash"]
    except (KeyError, TypeError):
        raw_urim = otmt.generate_raw_urim(urim)
        r = session.get(raw_urim)

        simhash = Simhash(r.text).value

        db.derivedvalues.update(
            { "urim": urim },
            { "$set": { "raw simhash": str(simhash) }},
            upsert=True
        )
    
        return str(simhash)

def get_boilerplate_free_content(urim, cache_storage="", dbconn=None, session=None):

    if dbconn is None:
        dbconn = MongoClient(cache_storage)
    
    if session is None:
        session = get_web_session(cache_storage)

    db = dbconn.get_default_database()

    # 1. if boilerplate free content in cache, return it
    try:
        return db.derivedvalues.find_one(
            { "urim": urim }
        )["boilerplate free content"]
    except (KeyError, TypeError):
        raw_urim = otmt.generate_raw_urim(urim)
        r = session.get(raw_urim)

        paragraphs = justext(
            r.text, get_stoplist('English')
        )

        bpfree = ""

        for paragraph in paragraphs:
            bpfree += "{}\n".format(paragraph.text)

        db.derivedvalues.update(
            { "urim": urim },
            { "$set": { "boilerplate free content": bpfree } },
            upsert=True
        )

        return bpfree
            